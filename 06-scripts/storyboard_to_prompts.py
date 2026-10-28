#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
storyboard_to_prompts.py —— 把「分镜表」一键转成批量提示词（前端画面描述 + 后端引擎参数）。

第二阶段核心：美术在 Excel 里填好分镜表（10 列），另存为 CSV（或直接给 JSON），
本脚本把它机械转成「画面描述」（七段式，模型无关）+「出图参数」（从 engine-profiles 注入）。

解耦原则（前端 / 后端分离）：
    - 前端（本脚本的 build_prompt）：只产「画面长什么样」——图种/人物/妆造/视图/背景光/风格，
      绝不硬编码采样器/CFG/步数/尺寸/负面词等引擎参数。
    - 后端（engine-profiles 配置）：提供「用什么引擎、什么参数、什么负面词出图」，
      换引擎只改 05-data-center/engine-profiles/*.json，前端一个字不动。

用法：
    # 1) CSV 分镜表（Excel 另存为 CSV，表头见模板）
    python storyboard_to_prompts.py 分镜表.csv <bible_dir> [输出前缀] [--engine comfyui]

    # 2) JSON 分镜表（api-contracts 定义的结构）
    python storyboard_to_prompts.py 分镜表.json <bible_dir> [输出前缀] [--engine comfyui]

输出（3 份，前缀默认 EP001）：
    <前缀>_prompts.txt        每镜一条画面描述 + 注入的负面词（人读 / 手动粘贴）
    <前缀>_batch.json         批量队列（positive + negative + 引擎参数分离）
    <前缀>_prompts.json       结构化提示词（脚本可再加工）

字段契约（分镜表 10 列，见 03-storyboard/SKILL.md）：
    分镜号 | 镜头号 | 建议时长 | 画面描述 | 人物 | 台词 | 运镜 | 构图 | 景别 | 备注
"""

import csv
import json
import os
import re
import sys

# ---------------------------------------------------------------- 映射表
# 景别 -> (镜头类型英文, 焦段)  来源：03-storyboard/SKILL.md「景别→焦段对应」
SHOT_TYPE_MAP = {
    "大远景": ("extreme wide shot", "24mm"),
    "远景": ("wide shot", "24mm"),
    "大全景": ("extreme full shot", "28mm"),
    "全景": ("full shot", "35mm"),
    "中景": ("medium shot", "50mm"),
    "中近景": ("medium close-up", "85mm"),
    "近景": ("close-up", "85mm"),
    "特写": ("extreme close-up", "100mm"),
}

# 运镜 -> 镜头语言英文  来源：03-storyboard/SKILL.md「运镜」列转换规则
CAMERA_MOVE_MAP = {
    "固定机位": "static shot",
    "缓慢推近": "slow push in",
    "缓慢横移": "slow lateral track",
    "缓慢上升": "slow rise",
    "手持": "handheld",
    "航拍": "aerial shot",
    "航拍缓推": "aerial push-in",
    "错车慢镜": "slow motion",
    "贴地跟拍": "low-angle tracking shot",
    "多镜快切": "rapid cuts",
    "上扬后拉": "pull-back crane-up",
}

# 负面词核心 10 个（任何图种都先写，来源 prompt-templates.md）
# 注意：负面词已迁到后端 engine-profiles 配置，这里仅保留 NEGATIVE_SHOT 作为
# 未配置引擎时的兜底。正式运行时负面词从 profile 的 negative_map 读取。
NEGATIVE_CORE = (
    "deformed hands, extra limbs, bad anatomy, blurry, low quality, "
    "watermark, text, logo, signature, inconsistent face"
)

# 影视剧情镜（非定妆照）追加负面词（兜底，正常从 profile 取）
NEGATIVE_SHOT = (
    "cropped feet, cut off legs, missing feet, half body, head cut off, "
    "cluttered background, glowing magic, energy aura, fire sparks, heavy smoke, "
    "multiple subjects, busy composition, messy composition"
)


# ---------------------------------------------------------------- 数据加载
def load_jsonl(path):
    records = {}
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            records[rec["asset_id"]] = rec
    return records


def load_bible(bible_dir):
    return {
        "char": load_jsonl(os.path.join(bible_dir, "characters.jsonl")),
        "scene": load_jsonl(os.path.join(bible_dir, "scenes.jsonl")),
        "prop": load_jsonl(os.path.join(bible_dir, "props.jsonl")),
    }


def load_scene_states(scene_states_path):
    """读 EPxxx_scene_states.jsonl，返回 shot_id -> 状态 dict 的映射。

    每个 SceneState 有 valid_shots（哪些 shot 属于该状态），
    反向索引成 shot_id -> {door_state/window_state/surface_traces/light_state/...}。
    """
    shot_state_map = {}
    if not scene_states_path or not os.path.exists(scene_states_path):
        return shot_state_map
    with open(scene_states_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for shot_id in rec.get("valid_shots", []):
                shot_state_map[shot_id] = rec
    return shot_state_map


# ---------------------------------------------------------------- 引擎配置加载（后端控制台）
def _find_engine_profiles_dir():
    """定位 engine-profiles 目录：优先脚本同级上层的 05-data-center。"""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "05-data-center", "engine-profiles"),
        os.path.join(here, "..", "..", "05-data-center", "engine-profiles"),
        os.path.join(os.getcwd(), "05-data-center", "engine-profiles"),
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "engines.json")):
            return c
    return None


def load_engine_profile(engine_id=None, profiles_dir=None):
    """从 engine-profiles 读取引擎配置（参数 + 负面词）。

    返回 dict：{engine_id, name, language, params, negative_map, ref_image}
    找不到配置时返回 None（调用方回退到默认负面词）。
    """
    profiles_dir = profiles_dir or _find_engine_profiles_dir()
    if not profiles_dir:
        return None

    registry_path = os.path.join(profiles_dir, "engines.json")
    if not os.path.exists(registry_path):
        return None

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    engines = registry.get("engines", [])
    if not engines:
        return None

    # 未指定引擎 → 用注册表 default_engine；指定了 → 匹配 engine_id
    if engine_id is None:
        engine_id = registry.get("default_engine")
    target = next((e for e in engines if e.get("engine_id") == engine_id), None)
    if target is None:
        target = engines[0]

    # 若该引擎有独立 profile 文件，读它覆盖 registry 里的内联参数
    profile_file = target.get("profile_file")
    if profile_file:
        p_path = os.path.join(profiles_dir, profile_file)
        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                detail = json.load(f)
            target = {**target, **detail}

    return target


def build_negative(profile, shot_kind="shot"):
    """从引擎 profile 的 negative_map 拼负面词。

    shot_kind 决定追加哪组：
      - "shot"      剧情镜（默认）
      - "portrait"  单张定妆照
      - "multi_view" 多视图/模型表
    核心组 core 永远拼在最前。
    """
    if not profile:
        return NEGATIVE_CORE + ", " + NEGATIVE_SHOT

    nm = profile.get("negative_map", {}) or {}
    parts = []
    core = nm.get("core")
    if core:
        parts.append(core)
    extra = nm.get(shot_kind)
    if extra:
        parts.append(extra)
    if not parts:  # 兜底
        return NEGATIVE_CORE + ", " + NEGATIVE_SHOT
    return ", ".join(parts)


def resolve_name(asset_id, bible):
    """按 ID 查基准名；查不到原样返回（可能是名字本身）。"""
    for recs in bible.values():
        if asset_id in recs:
            return recs[asset_id]["name"]
    return asset_id


# ---------------------------------------------------------------- 分镜表读取
def read_storyboard_csv(path):
    """读 CSV 分镜表（10 列），返回统一 shot dict 列表。

    CSV 列名（对齐 03-storyboard 分镜表 10 列）：
    分镜号,镜头号,建议时长,画面描述,人物,台词,运镜,构图,景别,备注
    """
    shots = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 人物列可能是「梁大、梁小」名字，也可能是「CHAR-001,CHAR-002」ID，
            # 统一按逗号/顿号切分存原样，拼装时再解析。
            char_raw = (row.get("人物") or "").strip()
            chars = [c.strip() for c in char_raw.replace("、", ",").split(",") if c.strip()]

            shot = {
                "storyboard_no": (row.get("分镜号") or "").strip(),
                "shot_no": (row.get("镜头号") or "").strip().zfill(2),
                "shot_id": f"{(row.get('分镜号') or '').strip()}-{(row.get('镜头号') or '').strip().zfill(2)}",
                "scene_id": _resolve_scene_id((row.get("备注") or "").strip()),
                "duration_sec": _to_int(row.get("建议时长")),
                "action": (row.get("画面描述") or "").strip(),
                "characters": chars,
                "dialogue": (row.get("台词") or "").strip() or "本镜无台词",
                "camera_movement": (row.get("运镜") or "").strip(),
                "composition": (row.get("构图") or "").strip(),
                "camera_angle": (row.get("景别") or "").strip(),
                "remark": (row.get("备注") or "").strip(),
            }
            shots.append(shot)
    return shots


def read_storyboard_json(path):
    """读 JSON 分镜表（api-contracts 结构），返回统一 shot dict 列表。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shots = []
    for s in data.get("shots", []):
        shot = {
            "storyboard_no": s.get("shot_id", "").rsplit("-", 1)[0],
            "shot_no": s.get("shot_id", "").rsplit("-", 1)[-1],
            "shot_id": s.get("shot_id", ""),
            "scene_id": s.get("scene_id", ""),
            "duration_sec": _to_int(s.get("duration_sec")),
            "action": s.get("action", ""),
            "characters": s.get("characters", []),
            "dialogue": s.get("dialogue", "") or "本镜无台词",
            "camera_movement": s.get("camera_movement", ""),
            "composition": "",
            "camera_angle": s.get("camera_angle", ""),
            "remark": "",
        }
        shots.append(shot)
    return shots


def _to_int(v):
    try:
        return int(float(str(v).strip()))
    except (ValueError, TypeError):
        return 5


def _resolve_scene_id(remark):
    """从备注列解析 scene_id：返回第一个 SC-xx，没有则空串。"""
    if not remark:
        return ""
    m = re.search(r"(SC-\d{2})", remark)
    return m.group(1) if m else ""


def _parse_assets_from_remark(remark):
    """从备注列解析场景 ID（SC-xx）等资产 ID。

    备注列如「SC-03 车内」「PR-01 PR-02 陆巡 EVX-9 入镜」，
    抽取 SC-xx / PR-xx / CHAR-xxx 形式的标准 ID，返回 ID 列表。
    """
    if not remark:
        return []
    ids = re.findall(r"(?:SC-\d{2}|PR-\d{2}|CHAR-\d{3}|V-\d{2})", remark)
    # 去重保持顺序
    seen, uniq = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return uniq


# ---------------------------------------------------------------- 提示词拼装
def parse_angle(angle_str):
    """景别可能是「中近景」或「大远景→中景」，取最后一个景别做镜头类型，
    但保留完整景别变化信息。"""
    parts = [p.strip() for p in angle_str.replace("→", "->").split("->") if p.strip()]
    last = parts[-1] if parts else ""
    shot_type, focal = SHOT_TYPE_MAP.get(last, ("shot", ""))
    return last, shot_type, focal, parts


def _orientation_of(aspect):
    """画幅 → 横竖版文案（P1 修复：此前硬编码「竖版」，16:9 会产出自相矛盾的「16:9 竖版」）。

    约定：横版写「宽:高」（16:9、2.35:1），竖版写「高:宽」（9:16）。
    第一个数 > 第二个数 = 横版；反之竖版。
    """
    aspect = (aspect or "").strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)$", aspect)
    if m:
        w, h = float(m.group(1)), float(m.group(2))
        return "横版" if w > h else "竖版"
    return "竖版"  # 兜底：默认成片竖屏


def build_prompt(shot, bible, episode=None, aspect="9:16", scene_state=None):
    """把一个 shot 拼成完整七段式**画面描述**（前端，模型无关）。

    注意：负面词和出图参数（采样器/CFG/步数/尺寸/seed）不在这里写，
    由调用方从 engine-profiles 注入（后端）。本函数只回答「画面长什么样」。

    画幅（aspect）：默认 9:16（成片）；design plate 任务传 16:9。
    """
    lines = []
    chars = shot["characters"]
    angle_last, shot_type, focal, angle_parts = parse_angle(shot["camera_angle"])

    # [1 图种 + 硬约束]（前 50 字锁框架）
    orientation = _orientation_of(aspect)
    lines.append(f"影视剧照，{shot_type}，{aspect} {orientation}，电影级质感。")

    # [2 人物 + 锁脸] —— 只写名字 + 锁脸声明，外貌从 bible 基准图取，不重写
    if chars:
        names = [resolve_name(c, bible) for c in chars]
        lines.append(f"出场角色：{'、'.join(names)}。")
        lines.append("人物外貌以基准身份图为参考，锁脸型/五官比例/骨相，不换脸、不漂移。")
    else:
        lines.append("空镜，无人物出场（纯环境/风景）。")

    # [3 画面内容] —— 分镜表「画面描述」列
    if shot["action"]:
        lines.append(f"画面内容：{shot['action']}。")

    # [4 妆造/状态变体] —— 从 bible 的 looks 里取当前集数的 delta（若有）
    look_delta = _resolve_look_delta(chars, bible, episode)
    if look_delta:
        lines.append(f"当前造型（状态变体 delta）：{look_delta}。")

    # [5 运镜/构图/景别/焦段] —— 分镜表镜头语言转参数
    cam = CAMERA_MOVE_MAP.get(shot["camera_movement"], shot["camera_movement"])
    line5 = f"镜头语言：{cam}"
    if focal:
        line5 += f"，{shot_type}，{focal} 焦段"
    if shot["composition"]:
        line5 += f"，构图：{shot['composition']}"
    line5 += f"。时长 {shot['duration_sec']} 秒。"
    lines.append(line5)

    # [6 背景/光影] —— 场景状态（door/window/surface/light）优先，否则占位待美术补
    bg_line = _build_background_line(shot, bible, scene_state)
    lines.append(bg_line)

    # [7 风格/质感] —— 默认真人写实（影视剧照）
    lines.append("风格：真人写实摄影，电影级质感，真实皮肤纹理，8K。")

    # 场景固定锚点注入（Keep consistent）
    anchor_line = _build_anchor_line(shot, bible)
    if anchor_line:
        lines.append(anchor_line)

    # 参考图权限隔离（关键）
    lines.append(
        "参考图权限隔离：参考图仅允许提供脸型/五官比例/骨相，严禁带入参考图的服装、发型、背景、光影。"
    )

    positive = "\n".join(lines)

    return {
        "shot_id": shot["shot_id"],
        "positive": positive,
        "characters": chars,
        "camera_angle": shot["camera_angle"],
    }


def _build_background_line(shot, bible, scene_state):
    """背景与光影段：优先取场景状态（door/window/surface/light），否则占位。"""
    parts = []
    if scene_state:
        door = scene_state.get("door_state")
        window = scene_state.get("window_state")
        light = scene_state.get("light_state")
        traces = scene_state.get("surface_traces", [])
        if door and door != "无门（露天营地）" and door != "无门（露天公路）" and door != "无窗":
            parts.append(f"门状态：{door}")
        if window and window not in ("无窗",):
            parts.append(f"窗状态：{window}")
        if traces:
            parts.append(f"表面痕迹：{'、'.join(traces)}")
        if light:
            parts.append(f"光线：{light}")
    if parts:
        return "背景与光影：" + "；".join(parts) + "。"
    return "背景与光影：从 style-recipes 题材氛围词库挑选，填入本段。"


def _build_anchor_line(shot, bible):
    """场景固定锚点注入：从 scenes.jsonl 的 power_layout.fixed_anchors 取，写 Keep consistent。

    场景定位（P2 修复）：优先用 shot["scene_id"]（结构化外键，唯一权威），
    缺失时回退到从 assets_required 里找 SC-xx（兼容旧数据）。
    """
    scene_ids = []
    sid = shot.get("scene_id", "")
    if sid and sid in bible.get("scene", {}):
        scene_ids.append(sid)
    if not scene_ids:
        # 回退：assets_required 里的场景 ID（旧数据无 scene_id 字段）
        for aid in shot.get("assets_required", []):
            if aid in bible.get("scene", {}):
                scene_ids.append(aid)

    anchors = []
    for aid in scene_ids:
        pl = bible["scene"][aid].get("power_layout", {})
        fa = pl.get("fixed_anchors", [])
        anchors.extend(fa)
    if anchors:
        # 去重保持顺序
        seen, uniq = set(), []
        for a in anchors:
            if a not in seen:
                seen.add(a)
                uniq.append(a)
        return f"场景固定锚点（Keep consistent）：{'、'.join(uniq)}。"
    return ""


def _resolve_look_delta(chars, bible, episode=None):
    """从 bible 取当前角色的状态变体 delta，按集数过滤（域3 修复）。

    - 只取非基础造型（V00 之外）的 delta；
    - 若传入 episode（如 EP003），按 looks[].valid_episodes 过滤——
      只有「生效范围覆盖当前集」的变体才列出（第 10 集不带第 3 集的夜行衣）。
    - valid_episodes 支持「全片」「EP003-EP005」或单集「EP003」。
    """
    deltas = []
    for c in chars:
        rec = bible["char"].get(c)
        if not rec:
            continue
        for lk in rec.get("looks", []):
            if lk.get("look_id", "V00") == "V00":
                continue
            if not _look_applies_to(lk.get("valid_episodes", "全片"), episode):
                continue
            deltas.append(f"{rec['name']}：{lk.get('desc', '')}")
    return "；".join(deltas) if deltas else ""


def _look_applies_to(valid_episodes, episode):
    """判断某变体的生效范围是否覆盖 episode（None = 不按集过滤，全列出）。"""
    if episode is None:
        return True
    valid = (valid_episodes or "").strip()
    if not valid or valid == "全片":
        return True
    # 范围「EP003-EP005」
    m = re.match(r"^(EP\d{3})\s*[-~～]\s*(EP\d{3})$", valid)
    if m:
        lo, hi = m.group(1), m.group(2)
        return lo <= episode <= hi
    # 单集「EP003」或逗号分隔「EP003,EP004」
    eps = {e.strip() for e in valid.replace("、", ",").split(",") if e.strip()}
    return episode in eps


# ---------------------------------------------------------------- 输出
def main():
    import argparse
    parser = argparse.ArgumentParser(description="分镜表 → 七段式画面描述 + 引擎参数注入")
    parser.add_argument("src_path", help="分镜表 CSV 或 JSON")
    parser.add_argument("bible_dir", help="bible 目录（characters/scenes/props.jsonl）")
    parser.add_argument("prefix", nargs="?", default="EP001", help="输出前缀（默认 EP001）")
    parser.add_argument("--engine", default=None, help="目标引擎（comfyui/midjourney/doubao/jimeng/minimax_h3）")
    parser.add_argument("--episode", default=None, help="集号（EP001 这种），状态变体按此过滤")
    parser.add_argument("--aspect", default="9:16", help="出图画幅：9:16（成片/blocking）/ 16:9（design plate）")
    parser.add_argument("--scene-states", default=None, help="EPxxx_scene_states.jsonl 路径（读场景状态）")
    parser.add_argument("--out-dir", default=None, help="输出目录（默认 06-scripts/out/）")
    args = parser.parse_args()

    # 输出目录：默认 06-scripts/out/
    if args.out_dir:
        out_dir = args.out_dir
    else:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)

    # 路径设防：src_path 和 bible_dir 的 realpath 校验（域3/域9）
    if not os.path.exists(args.src_path):
        print(f"[错误] 分镜表不存在：{args.src_path}")
        sys.exit(1)

    ext = os.path.splitext(args.src_path)[1].lower()
    if ext == ".csv":
        shots = read_storyboard_csv(args.src_path)
    elif ext == ".json":
        shots = read_storyboard_json(args.src_path)
    else:
        print(f"[错误] 不支持的文件类型：{ext}（只支持 .csv / .json）")
        sys.exit(1)

    bible = load_bible(args.bible_dir)
    profile = load_engine_profile(args.engine)
    episode = args.episode
    scene_state_map = load_scene_states(args.scene_states)

    if profile:
        engine_name = profile.get("name", args.engine or "默认引擎")
        print(f"[引擎] 后端控制台已加载：{engine_name}（engine_id={profile.get('engine_id')}）")
    else:
        print("[警告] 未找到 engine-profiles 配置，负面词回退到内置默认值。")
    if episode:
        print(f"[集号] 状态变体按 {episode} 过滤。")

    # 前端：产画面描述；后端：注入负面词 + 出图参数
    prompts = []
    for s in shots:
        # 从备注列解析场景 ID（SC-xx），补进 assets_required 供锚点注入
        s["assets_required"] = _parse_assets_from_remark(s.get("remark", ""))
        state = scene_state_map.get(s["shot_id"])
        p = build_prompt(s, bible, episode, aspect=args.aspect, scene_state=state)
        p["negative"] = build_negative(profile, shot_kind="shot")
        p["engine"] = profile.get("engine_id") if profile else None
        prompts.append(p)

    prefix = args.prefix

    # 输出 1：纯文本（人读/手动粘贴）
    txt_path = os.path.join(out_dir, f"{prefix}_prompts.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(f"===== {p['shot_id']} =====\n")
            f.write(p["positive"] + "\n")
            f.write(f"[负面] {p['negative']}\n\n")
    print(f"[1/3] 纯文本提示词 -> {txt_path}")

    # 输出 2：结构化 JSON（脚本可再加工）
    json_path = os.path.join(out_dir, f"{prefix}_prompts.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    print(f"[2/3] 结构化提示词 -> {json_path}")

    # 输出 3：批量队列（positive + negative + 引擎参数分离）
    batch_path = os.path.join(out_dir, f"{prefix}_batch.json")
    batch = {
        "engine": profile.get("engine_id") if profile else None,
        "engine_params": profile.get("params", {}) if profile else {},
        "batch": [
            {
                "shot_id": p["shot_id"],
                "positive": p["positive"],
                "negative": p["negative"],
            }
            for p in prompts
        ],
    }
    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"[3/3] 批量队列 -> {batch_path}")

    print(f"\n共 {len(prompts)} 个镜头。引擎参数已从后端控制台注入（见 {batch_path} 的 engine_params）。")


if __name__ == "__main__":
    main()
