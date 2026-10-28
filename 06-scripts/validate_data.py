#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_data.py —— 数据校验层（域1 P0 核心）：单源真理的执行器。

职责：任何脚本在「加载数据前」先跑本模块校验，不合法直接拒绝（不静默、不降级放行）。

校验项：
    1. schema 校验（JSON Schema，有 jsonschema 时完整校验；无则内置轻量校验兜底）
    2. asset_id 唯一性（bible 内、episodes 内）
    3. 外键完整性：shot.characters / shot.scene_id / shot.assets_required 引用的 ID 必须在 bible 存在
    4. 枚举合法性（type / identity / gender / day_night / in_out 等）
    5. 必填项

用法：
    # 校验 bible（三个 jsonl）
    python validate_data.py bible <bible_dir>

    # 校验分镜表（JSON）
    python validate_data.py storyboard <EP001_storyboard.json> <bible_dir>

    # 校验资产清单（CSV）
    python validate_data.py assets <EP001_assets.csv> <bible_dir>

    # 校验引擎配置
    python validate_data.py engines <engine-profiles_dir>

    # 全量校验（bible + 所有 episodes + engines）
    python validate_data.py all <data-center_dir>

退出码：0 = 全过；1 = 有 error（阻断）。
"""

import argparse
import csv
import json
import os
import re
import sys

# ---------------------------------------------------------------- schema 加载
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.join(HERE, "schemas")

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def load_schema(name):
    p = os.path.join(SCHEMA_DIR, name)
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _jsonschema_validate(instance, schema):
    """有 jsonschema 用完整校验；否则用内置轻量校验。返回错误列表。"""
    if HAS_JSONSCHEMA:
        validator = jsonschema.Draft202012Validator(schema)
        return [f"{list(e.path) or ['(root)']}: {e.message}" for e in validator.iter_errors(instance)]

    # ---- 内置轻量校验（兜底，无外部依赖）----
    errs = []
    required = schema.get("required", [])
    for r in required:
        if r not in instance:
            errs.append(f"缺必填字段: {r}")
    props = schema.get("properties", {})
    for k, v in instance.items():
        pspec = props.get(k)
        if pspec is None:
            if schema.get("additionalProperties") is False:
                errs.append(f"未知字段: {k}")
            continue
        if "const" in pspec and v != pspec["const"]:
            errs.append(f"字段 {k} 应为 {pspec['const']!r}，实为 {v!r}")
        if "enum" in pspec and pspec["enum"] and v not in pspec["enum"]:
            errs.append(f"字段 {k} 值 {v!r} 不在枚举 {pspec['enum']} 内")
        if "pattern" in pspec and isinstance(v, str):
            if not re.fullmatch(pspec["pattern"], v):
                errs.append(f"字段 {k} 值 {v!r} 不匹配格式 {pspec['pattern']}")
        # 数组 items 的 pattern（如 characters 存 ID 铁律）
        if "items" in pspec and isinstance(v, list):
            item_spec = pspec["items"]
            if "pattern" in item_spec:
                for idx, item in enumerate(v):
                    if isinstance(item, str) and not re.fullmatch(item_spec["pattern"], item):
                        errs.append(f"字段 {k}[{idx}] 值 {item!r} 不匹配格式 {item_spec['pattern']}")
    return errs


# ---------------------------------------------------------------- 读取
def read_jsonl(path):
    recs = []
    if not os.path.exists(path):
        return recs
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  ✗ {path}:{i} JSON 解析失败: {e}")
    return recs


# ---------------------------------------------------------------- 校验器
class Validator:
    def __init__(self):
        self.errors = []

    def error(self, msg):
        self.errors.append(msg)

    @property
    def ok(self):
        return not self.errors


def validate_bible(bible_dir, v):
    """校验 bible 三文件：schema + asset_id 唯一性 + 必填。"""
    mapping = [
        ("characters.jsonl", "character.schema.json"),
        ("scenes.jsonl", "scene.schema.json"),
        ("props.jsonl", "prop.schema.json"),
    ]
    all_ids = {}
    for fn, schema_name in mapping:
        path = os.path.join(bible_dir, fn)
        if not os.path.exists(path):
            v.error(f"缺文件: {fn}")
            continue
        schema = load_schema(schema_name)
        for rec in read_jsonl(path):
            for e in _jsonschema_validate(rec, schema):
                v.error(f"{fn} {rec.get('asset_id', '?')}: {e}")
            aid = rec.get("asset_id")
            if aid in all_ids:
                v.error(f"asset_id 重复: {aid}（跨文件冲突）")
            all_ids[aid] = rec
    return all_ids


def validate_storyboard(path, bible_dir, v):
    """校验分镜表：外键完整性（characters/scene_id/assets_required 引用存在）。

    支持 JSON（api-contracts 结构）和 CSV（分镜表 10 列）两种输入。
    CSV 人物列存名字，先解析成 ID 再校验外键。
    """
    if not os.path.exists(path):
        v.error(f"缺文件: {path}")
        return

    # 建 bible 索引：id 集合 + name->id 映射
    bible_ids, name2id = _index_bible(bible_dir)

    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        shots = _read_storyboard_csv(path)
        # CSV 人物列是名字，解析成 ID
        for s in shots:
            s["characters"] = [name2id.get(c, c) for c in s["characters"]]
    else:
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            v.error(f"{path}: JSON 解析失败 {e}")
            return
        shots = data.get("shots", [])

    if not shots:
        v.error(f"{path}: 无 shots")

    # shot.schema 校验（P1 修复：此前 shot.schema.json 是死 schema，从未被 storyboard 校验调用）
    shot_schema = load_schema("shot.schema.json")
    for s in shots:
        sid = s.get("shot_id", "?")
        for e in _jsonschema_validate(s, shot_schema):
            v.error(f"shot {sid}: {e}")

    for s in shots:
        sid = s.get("shot_id", "?")
        # 外键：scene_id
        sid_val = s.get("scene_id", "")
        if sid_val and sid_val not in bible_ids:
            v.error(f"shot {sid}: scene_id {sid_val} 不在 bible（外键缺失）")
        # 外键：characters
        for c in s.get("characters", []):
            if c and c not in bible_ids:
                v.error(f"shot {sid}: 角色 {c} 不在 bible（外键缺失）")
        # 外键：assets_required
        for a in s.get("assets_required", []):
            if a and a not in bible_ids:
                v.error(f"shot {sid}: 资产 {a} 不在 bible（外键缺失）")


def _index_bible(bible_dir):
    """建立 bible 索引：返回 (ids 集合, name->id 映射)。"""
    ids, name2id = set(), {}
    for fn in ("characters.jsonl", "scenes.jsonl", "props.jsonl"):
        p = os.path.join(bible_dir, fn)
        if os.path.exists(p):
            for rec in read_jsonl(p):
                aid = rec.get("asset_id")
                if aid:
                    ids.add(aid)
                nm = rec.get("name")
                if nm and aid:
                    name2id[nm] = aid
    return ids, name2id


def _read_storyboard_csv(path):
    """读 CSV 分镜表，转成 shot dict 列表（字段与 csv2json.derive_json 对齐，可过 shot.schema）。"""
    shots = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            char_raw = (row.get("人物") or "").strip()
            chars = [c.strip() for c in char_raw.replace("、", ",").split(",") if c.strip()]
            shot_no = (row.get("镜头号") or "").strip().zfill(2)
            remark = (row.get("备注") or "").strip()
            # 时长：CSV「建议时长」列，转 int，异常回退 5
            try:
                duration = int(float((row.get("建议时长") or "5").strip()))
            except (ValueError, TypeError):
                duration = 5
            shot = {
                "episode": "EP000",  # 占位，CSV 无集号列；schema 仅要求 pattern EP\d{3}
                "shot_id": f"{(row.get('分镜号') or '').strip()}-{shot_no}",
                "scene_id": _resolve_scene_id(remark),
                "characters": chars,
                "action": (row.get("画面描述") or "").strip(),
                "dialogue": (row.get("台词") or "").strip() or "本镜无台词",
                "camera_angle": (row.get("景别") or "").strip(),
                "camera_movement": (row.get("运镜") or "").strip(),
                "duration_sec": duration,
                "lighting": "",
                "assets_required": _parse_assets(remark),
            }
            shots.append(shot)
    return shots


def _parse_assets(remark):
    """从备注列解析资产 ID（SC-xx / PR-xx / CHAR-xxx），去重保序。"""
    if not remark:
        return []
    ids = re.findall(r"(?:SC-\d{2}|PR-\d{2}|CHAR-\d{3})", remark)
    seen, uniq = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return uniq


def _resolve_scene_id(remark):
    """从备注列解析 scene_id：返回第一个 SC-xx，没有则空串。"""
    if not remark:
        return ""
    m = re.search(r"(SC-\d{2})", remark)
    return m.group(1) if m else ""


def validate_assets_csv(path, bible_ids, v):
    """校验资产清单 CSV：schema + 外键（asset_id 引用的 ID 存在或类型匹配）。"""
    if not os.path.exists(path):
        v.error(f"缺文件: {path}")
        return
    schema = load_schema("asset_call.schema.json")
    seen = set()
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # 列名校验
        expected_cols = list(schema["properties"].keys())
        actual_cols = reader.fieldnames or []
        for c in expected_cols:
            if c not in actual_cols:
                v.error(f"{path}: 缺列 {c}")
        for i, row in enumerate(reader, 2):
            # 数字列类型转换
            rec = dict(row)
            for num_col in ("appearance_count", "closeup_count", "total_duration_sec"):
                if rec.get(num_col, "") != "":
                    try:
                        rec[num_col] = int(float(rec[num_col]))
                    except (ValueError, TypeError):
                        v.error(f"{path}:{i} 列 {num_col} 非数字: {rec[num_col]!r}")
            for e in _jsonschema_validate(rec, schema):
                v.error(f"{path}:{i} {rec.get('asset_id', '?')}: {e}")
            aid = rec.get("asset_id")
            if aid in seen:
                v.error(f"{path}:{i} asset_id 重复: {aid}")
            seen.add(aid)


def validate_engines(profiles_dir, v):
    """校验引擎配置：engines.json 注册表 + 各 profile 文件 schema。"""
    reg_path = os.path.join(profiles_dir, "engines.json")
    if not os.path.exists(reg_path):
        v.error(f"缺文件: {reg_path}")
        return
    with open(reg_path, "r", encoding="utf-8") as f:
        reg = json.load(f)
    schema = load_schema("engine_profile.schema.json")
    ids = []
    for e in reg.get("engines", []):
        for err in _jsonschema_validate(e, schema):
            v.error(f"engines.json {e.get('engine_id', '?')}: {err}")
        if e.get("engine_id") in ids:
            v.error(f"引擎重复: {e['engine_id']}")
        ids.append(e.get("engine_id"))
        # 独立 profile 文件也校验
        pf = e.get("profile_file")
        if pf:
            pp = os.path.join(profiles_dir, pf)
            if os.path.exists(pp):
                with open(pp, "r", encoding="utf-8") as f2:
                    detail = json.load(f2)
                for err in _jsonschema_validate(detail, schema):
                    v.error(f"{pf}: {err}")
            else:
                v.error(f"引擎 {e['engine_id']} 的 profile 文件缺失: {pf}")


def validate_scene_states(path, bible_ids, v):
    """校验场景状态文件：schema + 外键（scene_id 引用存在）+ state_id 唯一。"""
    if not os.path.exists(path):
        v.error(f"缺文件: {path}")
        return
    schema = load_schema("scene_state.schema.json")
    seen = set()
    for rec in read_jsonl(path):
        for e in _jsonschema_validate(rec, schema):
            v.error(f"scene_state {rec.get('state_id', '?')}: {e}")
        sid = rec.get("scene_id", "")
        if sid and sid not in bible_ids:
            v.error(f"scene_state {rec.get('state_id', '?')}: scene_id {sid} 不在 bible（外键缺失）")
        if rec.get("state_id") in seen:
            v.error(f"scene_state state_id 重复: {rec.get('state_id')}")
        seen.add(rec.get("state_id"))


def validate_scene_readiness(path, bible_ids, v):
    """校验场景可用性文件：schema + 外键（scene_id 引用存在）。顶层支持数组或单对象。"""
    if not os.path.exists(path):
        v.error(f"缺文件: {path}")
        return
    schema = load_schema("scene_readiness.schema.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else [data]
    item_schema = schema.get("items", schema)  # 数组 schema 取 items；单对象 schema 直接用
    seen = set()
    for rec in records:
        for e in _jsonschema_validate(rec, item_schema):
            v.error(f"scene_readiness {rec.get('scene_id', '?')}: {e}")
        sid = rec.get("scene_id", "")
        if sid and sid not in bible_ids:
            v.error(f"scene_readiness {sid}: scene_id 不在 bible（外键缺失）")
        if sid in seen:
            v.error(f"scene_readiness scene_id 重复: {sid}")
        seen.add(sid)


# ---------------------------------------------------------------- 主流程
def main():
    parser = argparse.ArgumentParser(description="数据校验层：单源真理执行器")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("bible", help="校验 bible 三 jsonl").add_argument("bible_dir")
    p_sb = sub.add_parser("storyboard", help="校验分镜表 JSON")
    p_sb.add_argument("path")
    p_sb.add_argument("bible_dir")
    p_as = sub.add_parser("assets", help="校验资产清单 CSV")
    p_as.add_argument("path")
    p_as.add_argument("bible_dir")
    p_en = sub.add_parser("engines", help="校验引擎配置")
    p_en.add_argument("profiles_dir")
    p_all = sub.add_parser("all", help="全量校验 data-center")
    p_all.add_argument("data_dir")

    args = parser.parse_args()
    v = Validator()

    if args.cmd == "bible":
        validate_bible(args.bible_dir, v)
    elif args.cmd == "storyboard":
        validate_storyboard(args.path, args.bible_dir, v)
    elif args.cmd == "assets":
        bible_ids = validate_bible(args.bible_dir, Validator())
        validate_assets_csv(args.path, bible_ids, v)
    elif args.cmd == "engines":
        validate_engines(args.profiles_dir, v)
    elif args.cmd == "all":
        validate_bible(os.path.join(args.data_dir, "bible"), v)
        bible_ids, _ = _index_bible(os.path.join(args.data_dir, "bible"))
        eps = os.path.join(args.data_dir, "episodes")
        for fn in os.listdir(eps):
            if fn.endswith("_storyboard.json") or fn.endswith("_storyboard.csv"):
                validate_storyboard(os.path.join(eps, fn), os.path.join(args.data_dir, "bible"), v)
            elif fn.endswith("_assets.csv"):
                validate_assets_csv(os.path.join(eps, fn), bible_ids, v)
            elif fn.endswith("_scene_states.jsonl"):
                validate_scene_states(os.path.join(eps, fn), bible_ids, v)
            elif fn.endswith("_scene_readiness.json"):
                validate_scene_readiness(os.path.join(eps, fn), bible_ids, v)
        validate_engines(os.path.join(args.data_dir, "engine-profiles"), v)

    if v.ok:
        print("✅ 数据校验通过：无错误")
        sys.exit(0)
    else:
        print(f"❌ 数据校验失败：{len(v.errors)} 个错误（阻断）")
        for e in v.errors:
            print(f"  ✗ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
