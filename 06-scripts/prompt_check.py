#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prompt_check.py —— 提示词「编译期」结构校验（出图之前跑，把废片挡在生成前）。

与 check_assets.py 的分工：
    check_assets.py   = 出图之后质检（FaceID 相似度 / 废片过滤 / 推审）
    prompt_check.py   = 出图之前门禁（结构漏洞 / 文字矛盾 / 命名越权 / 引擎参数越界）

借鉴 short-drama-image-prompts 的 image_prompt_check.py 思路，但只做「机器能确定的
结构冲突」，语义质量仍交人工审查（对应 04-asset-prompts 的「出图前自检量表」）。

用法：
    # 校验 storyboard_to_prompts.py 产出的结构化提示词（_prompts.json）
    python prompt_check.py EP001_prompts.json <bible_dir> [--engine MJ]

    # 也支持直接校验分镜表 CSV（在转提示词之前先查命名/文字/越权）
    python prompt_check.py EP001_storyboard.csv <bible_dir>

    # 配合管线：storyboard_to_prompts.py 之后、ComfyUI 出图之前插入本脚本

校验项（每一项命中即报 error/warning）：
    1. 引擎参数越界：--ar/--cref/--iw/--style/--sref、(word:1.2) 等，与 --engine 声明不符
    2. 文字政策自相矛盾：既「写『青梧殿』」又「不要任何文字」
    3. 人物名与 bible 登记 ID 不一致（写 A 名生成 B 人 / 用了无语义命名）
    4. 参考图权限隔离声明缺失（没有「控制/不得控制」边界）
    5. 负面词缺失（positive 里没写负面、也没单独 negative 字段）

退出码：0 = 全过；1 = 存在 error（阻断）；2 = 仅 warning（放行但提醒）。
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------- 引擎参数词表
# 引擎专属参数/语法，按「目标模型」声明来判定是否越界。
# 若没声明引擎，默认按「最严格」——只允许通用描述，不允许任何引擎专属参数。
# 识别统一走 _PARAM_PATTERNS 正则（mj/sd 两族），不另维护 allowed 列表。

# 所有引擎专属参数的「识别正则」——出现在 positive 里即触发检查
_PARAM_PATTERNS = {
    "mj": re.compile(r"--(ar|cref|cw|sref|sw|iw|style\s+raw|no|seed)\b", re.IGNORECASE),
    "sd": re.compile(r"\((?:[^()]|\([^()]*\))*:\d+(?:\.\d+)?\)|\[[^\]]+\]"),
}

# ---------------------------------------------------------------- 文字矛盾检测
# 命中「要写具体文字」+「不要文字」同时出现 → 自相矛盾（对应反例 B）
_WANT_TEXT = re.compile(r"写着?[「『\"]?(.+?)[」』\"]?|封面.*写着|牌匾.*写着|刻着|署名|签名")
_NO_TEXT = re.compile(r"不要.{0,6}(任何)?文字|不出现.{0,6}(任何)?文字|无文字|no\s*text", re.IGNORECASE)

# ---------------------------------------------------------------- 无语义命名
_BAD_NAMES = {"1", "2", "3", "站位", "参考", "角色", "人物", "a", "b", "c"}


# ---------------------------------------------------------------- 加载
def load_bible_ids(bible_dir):
    """返回 bible 里所有已登记的 asset_id 与 name 集合（用于命名一致性校验）。"""
    ids, names = set(), set()
    for fn in ("characters.jsonl", "scenes.jsonl", "props.jsonl"):
        p = os.path.join(bible_dir, fn)
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("asset_id"):
                    ids.add(rec["asset_id"])
                if rec.get("name"):
                    names.add(rec["name"])
    return ids, names


# ---------------------------------------------------------------- 校验函数
def _normalize_engine(engine):
    """引擎名归一化：返回 (是否 MJ 族, 是否 SD 族)。

    引擎注册表（engine-profiles）的 engine_id 是小写（comfyui/midjourney/...），
    这里做大小写无关 + 别名映射，判断该引擎属于 MJ 族还是 SD/ComfyUI 族。
    """
    e = (engine or "").strip().lower()
    is_mj = any(k in e for k in ("midjourney", "mj"))
    # ComfyUI / SD / Stable Diffusion 都属 SD 族（权重语法 (word:1.2) 合法）
    is_sd = any(k in e for k in ("comfyui", "sd", "stable"))
    return is_mj, is_sd


def check_engine_params(positive, engine):
    """返回 (errors, warnings)。"""
    errs, warns = [], []
    is_mj, is_sd = _normalize_engine(engine)

    # 检测所有引擎专属参数
    found_mj = _PARAM_PATTERNS["mj"].search(positive)
    found_sd = _PARAM_PATTERNS["sd"].search(positive)

    if not engine:
        # 未声明引擎 → 不允许任何专属参数
        if found_mj:
            errs.append(f"[引擎越界] positive 含 MJ 专属参数 {found_mj.group(0)!r}，但未声明目标引擎（--engine）。")
        if found_sd:
            errs.append(f"[引擎越界] positive 含 SD/ComfyUI 权重语法，但未声明目标引擎（--engine）。")
        return errs, warns

    # 声明了引擎 → 允许该引擎专属，但其它引擎专属仍是越界
    if found_mj and not is_mj:
        errs.append(f"[引擎越界] 声明引擎 {engine}，但 positive 含 MJ 专属参数 {found_mj.group(0)!r}。")
    if found_sd and not is_sd:
        errs.append(f"[引擎越界] 声明引擎 {engine}，但 positive 含 SD/ComfyUI 权重语法。")

    return errs, warns


def check_text_conflict(positive):
    errs = []
    if _WANT_TEXT.search(positive) and _NO_TEXT.search(positive):
        errs.append(
            "[文字矛盾] 同一提示词既要求写具体文字、又写「不要任何文字」——"
            "两者不可兼得，请二选一（要么 readable 写对，要么 blank/postproduction 留白后期加）。"
        )
    return errs


def check_name_binding(chars, bible_ids, bible_names):
    """人物列里若出现「不在 bible 登记、且是无语义词」的名字 → 报错。"""
    errs, warns = [], []
    for c in chars:
        c = c.strip()
        if not c:
            continue
        if c in bible_ids or c in bible_names:
            continue
        # 不在登记里，且是明显无语义命名
        if c in _BAD_NAMES or len(c) <= 2:
            errs.append(f"[命名越权] 人物 '{c}' 不在 bible 登记，且疑似无语义命名（无法按名索引）。")
        else:
            warns.append(f"[命名提示] 人物 '{c}' 不在 bible 登记（可能是别名或未建档），请确认是否新建资产。")
    return errs, warns


def check_ref_isolation(positive):
    warns = []
    # 识别「有边界声明」的常见写法：控制/不得控制/仅允许提供/严禁带入/不得带入/不得控制
    has_control = any(k in positive for k in (
        "控制", "不得控制", "仅允许提供", "只允许提供", "允许提供",
        "严禁带入", "不得带入", "禁止带入", "只借用", "仅借用",
        "may_control", "must_not_control",
    ))
    has_ref = ("参考图" in positive or "reference" in positive.lower() or "REF-" in positive)
    if has_ref and not has_control:
        warns.append(
            "[参考图隔离缺失] 提示词引用了参考图，但没写「控制/不得控制」边界声明——"
            "可能把参考图的服装/背景/文字一起抄进去。请补「仅允许提供××，严禁带入××」。"
        )
    return warns


def check_negative(prompt):
    warns = []
    neg = prompt.get("negative", "")
    pos = prompt.get("positive", "")
    if not neg:
        # 没有独立 negative 字段，检查 positive 里有没有规避词
        if not re.search(r"不要|无|no\b|without|负面", pos):
            warns.append("[负面词缺失] 该镜头没有负面词（既无 negative 字段，正文也无规避措辞）。")
    return warns


# ---------------------------------------------------------------- 输入解析
def load_prompts(path):
    """支持两种输入：_prompts.json（结构化）或分镜表 CSV。"""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if "batch" in data:  # comfyui_batch 结构
            return data["batch"]
        if "shots" in data:
            return data["shots"]
        return [data]
    elif ext == ".csv":
        import csv
        with open(path, "r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        prompts = []
        for r in rows:
            char_raw = (r.get("人物") or "").strip()
            chars = [c.strip() for c in char_raw.replace("、", ",").split(",") if c.strip()]
            prompts.append({
                "shot_id": f"{r.get('分镜号','')}-{r.get('镜头号','')}",
                "positive": (r.get("画面描述") or "").strip(),
                "negative": "",
                "characters": chars,
            })
        return prompts
    else:
        print(f"[错误] 不支持的文件类型：{ext}（只支持 .json / .csv）")
        sys.exit(2)


# ---------------------------------------------------------------- 主流程
def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)

    src = sys.argv[1]
    bible_dir = sys.argv[2]
    engine = None
    if "--engine" in sys.argv:
        engine = sys.argv[sys.argv.index("--engine") + 1]

    prompts = load_prompts(src)
    bible_ids, bible_names = load_bible_ids(bible_dir)

    total_err, total_warn = 0, 0
    print(f"=== 提示词编译期校验：{src}（{len(prompts)} 条）===\n")

    for p in prompts:
        shot_id = p.get("shot_id", p.get("storyboard_no", "?"))
        positive = p.get("positive", "") or ""
        chars = p.get("characters", []) or []

        errs, warns = [], []

        e, w = check_engine_params(positive, engine)
        errs += e; warns += w
        errs += check_text_conflict(positive)
        e, w = check_name_binding(chars, bible_ids, bible_names)
        errs += e; warns += w
        warns += check_ref_isolation(positive)
        warns += check_negative(p)

        if errs or warns:
            print(f"--- {shot_id} ---")
            for x in errs:
                print(f"  ✗ ERROR  {x}")
            for x in warns:
                print(f"  ⚠ WARN   {x}")
            total_err += len(errs)
            total_warn += len(warns)

    print(f"\n=== 结果：{total_err} error / {total_warn} warning ===")
    if total_err:
        print("存在结构错误，出图前先修（阻断）。")
        sys.exit(1)
    elif total_warn:
        print("有警告项，建议人工复核后再出图（放行）。")
        sys.exit(2)
    else:
        print("全部通过，可送入出图。")
        sys.exit(0)


if __name__ == "__main__":
    main()
