#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csv2json.py —— CSV 分镜表 → JSON 分镜表（CSV 是唯一人工源，JSON 是纯函数派生物）。

核心原则（根治漂移）：
    - CSV 是唯一人工编辑入口（美术在 Excel 填表 → 另存 CSV）。
    - JSON 由本脚本从 CSV 机械生成，只读、带 _source_hash、禁止手工编辑。
    - 场景细节（fixed_anchors 等）归位到 scenes.jsonl，不留在分镜表每镜重复写。
    - 不做 LLM 扩写、不做启发式补全，字段一一映射、画面描述原样搬运。

用法：
    # CSV -> JSON（派生，带 _source_hash）
    python csv2json.py to-json <storyboard.csv> <out.json> <bible_dir>

    # 一致性 check（字段级严格相等，不做模糊比对）
    python csv2json.py check <storyboard.csv> <storyboard.json> <bible_dir>

退出码：0 一致 / 1 不一致（阻断）。
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys

# 分镜表 10 列 -> JSON Shot 字段映射
CSV_TO_JSON = {
    "分镜号": "storyboard_no",
    "镜头号": "shot_no",
    "建议时长": "duration_sec",
    "画面描述": "action",
    "人物": "characters",
    "台词": "dialogue",
    "运镜": "camera_movement",
    "构图": "composition",
    "景别": "camera_angle",
    "备注": "remark",
}


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_assets_from_remark(remark):
    """从备注列解析资产 ID（SC-xx / PR-xx / CHAR-xxx）。"""
    if not remark:
        return []
    ids = re.findall(r"(?:SC-\d{2}|PR-\d{2}|CHAR-\d{3})", remark)
    seen, uniq = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return uniq


def read_csv(path):
    """读 CSV 分镜表，返回 shot dict 列表（用 JSON 字段名）。"""
    shots = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            shot = {}
            for csv_col, json_col in CSV_TO_JSON.items():
                val = (row.get(csv_col) or "").strip()
                shot[json_col] = val
            # 人物列转数组
            char_raw = shot.get("characters", "")
            shot["characters"] = [c.strip() for c in char_raw.replace("、", ",").split(",") if c.strip()]
            # 时长转数字
            try:
                shot["duration_sec"] = int(float(shot.get("duration_sec", "5")))
            except (ValueError, TypeError):
                shot["duration_sec"] = 5
            # 镜头号补零对齐标准 SXX-XX 格式（CSV 人填「1」，规范化为「01」）
            shot["shot_no"] = str(shot.get("shot_no", "")).zfill(2)
            shot["shot_id"] = f"{shot.get('storyboard_no', '')}-{shot.get('shot_no', '')}"
            shots.append(shot)
    return shots


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("shots", [])


def resolve_name2id(bible_dir):
    """从 bible/characters.jsonl 建 name -> asset_id 映射。"""
    name2id = {}
    if not bible_dir:
        return name2id
    p = os.path.join(bible_dir, "characters.jsonl")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    name2id[r.get("name", "")] = r.get("asset_id")
    return name2id


def derive_json(csv_path, episode, name2id=None):
    """从 CSV 机械派生 JSON 结构（纯函数，不做任何智能补全）。

    characters 按 api-contracts 铁律存 ID（用 name2id 解析），不是名字。
    scene_id 从备注列解析的场景 ID（SC-xx）回填——一镜只属于一个场景，
    备注列含多个 SC-xx 时取第一个，都不含则留空（空镜/纯环境镜可无场景）。
    """
    name2id = name2id or {}
    shots = read_csv(csv_path)
    return {
        "episode": episode,
        "shots": [
            {
                "episode": episode,
                "shot_id": s["shot_id"],
                "scene_id": _resolve_scene_id(s.get("remark", "")),
                "characters": [name2id.get(c, c) for c in s["characters"]],
                "action": s["action"],
                "dialogue": s["dialogue"] or "本镜无台词",
                "camera_angle": s["camera_angle"],
                "camera_movement": s["camera_movement"],
                "duration_sec": s["duration_sec"],
                "lighting": "",
                "assets_required": _parse_assets_from_remark(s.get("remark", "")),
            }
            for s in shots
        ],
    }


def _resolve_scene_id(remark):
    """从备注列解析 scene_id：返回第一个 SC-xx，没有则空串。

    备注列如「SC-03 车内」「PR-01 PR-02 陆巡 EVX-9 入镜」，
    只取场景 ID（SC-xx），一镜只属一个场景。
    """
    if not remark:
        return ""
    m = re.search(r"(SC-\d{2})", remark)
    return m.group(1) if m else ""


def to_json(csv_path, out_path, bible_dir=None, episode="EP001"):
    name2id = resolve_name2id(bible_dir)
    data = derive_json(csv_path, episode, name2id)
    data["_generated"] = True
    data["_source"] = os.path.basename(csv_path)
    data["_source_hash"] = "sha256:" + sha256_of_file(csv_path)
    data["_generated_by"] = "csv2json.py"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"CSV -> JSON: {len(data['shots'])} 镜 -> {out_path}")
    print(f"  _source_hash: {data['_source_hash']}")


def check(csv_path, json_path, bible_dir=None):
    """一致性 check：字段级严格相等，不做 difflib/相似度/包含判断。

    关键：JSON 必须是 CSV 的确定性派生。若 JSON 带 _source_hash，
    直接比对 hash；否则逐字段严格比对（画面描述严格相等，人物经 name->id 解析）。
    """
    with open(json_path, "r", encoding="utf-8") as f:
        jdata = json.load(f)

    # 1. 来源 hash 校验（JSON 带 _source_hash 时）
    src_hash = jdata.get("_source_hash")
    if src_hash:
        cur_hash = "sha256:" + sha256_of_file(csv_path)
        if src_hash != cur_hash:
            print(f"❌ JSON 已被手工修改或 CSV 已变：")
            print(f"  JSON 记录的 _source_hash: {src_hash}")
            print(f"  当前 CSV 的 hash:        {cur_hash}")
            print(f"  请重新运行: python csv2json.py to-json <csv> <json> <bible>")
            sys.exit(1)

    csv_shots = read_csv(csv_path)
    json_shots = jdata.get("shots", [])

    errs = []
    if len(csv_shots) != len(json_shots):
        errs.append(f"镜头数不一致：CSV {len(csv_shots)} vs JSON {len(json_shots)}")

    name2id = resolve_name2id(bible_dir)

    def resolve_ids(chars):
        return [name2id.get(c, c) for c in chars]

    csv_by_id = {s["shot_id"]: s for s in csv_shots}
    json_by_id = {s["shot_id"]: s for s in json_shots}
    for sid in set(csv_by_id) | set(json_by_id):
        if sid not in csv_by_id:
            errs.append(f"镜头 {sid} 仅存在于 JSON（JSON 有 CSV 没有的镜头，禁止手工新增）")
            continue
        if sid not in json_by_id:
            errs.append(f"镜头 {sid} 仅存在于 CSV（需重新 to-json）")
            continue
        c, j = csv_by_id[sid], json_by_id[sid]

        # 字段级严格相等
        if c["action"].strip() != j.get("action", "").strip():
            errs.append(f"镜头 {sid} 画面描述不一致（CSV 与 JSON 漂移，禁止手工改 JSON）")
        if resolve_ids(c["characters"]) != j.get("characters", []):
            errs.append(f"镜头 {sid} 人物不一致：{c['characters']} vs {j.get('characters')}")
        if c["camera_angle"].strip() != j.get("camera_angle", "").strip():
            errs.append(f"镜头 {sid} 景别不一致：{c['camera_angle']} vs {j.get('camera_angle')}")
        if c["camera_movement"].strip() != j.get("camera_movement", "").strip():
            errs.append(f"镜头 {sid} 运镜不一致")

    if errs:
        print("❌ CSV/JSON 不一致：")
        for e in errs:
            print(f"  ✗ {e}")
        sys.exit(1)
    print(f"✅ CSV/JSON 一致：{len(csv_shots)} 镜全部严格对齐（字段级相等）")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="CSV 分镜表 → JSON 派生 + 一致性校验")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("to-json")
    p1.add_argument("csv")
    p1.add_argument("out")
    p1.add_argument("bible_dir", nargs="?")
    p1.add_argument("--episode", default="EP001")
    p2 = sub.add_parser("check")
    p2.add_argument("csv")
    p2.add_argument("json")
    p2.add_argument("bible_dir", nargs="?")
    args = parser.parse_args()

    if args.cmd == "to-json":
        to_json(args.csv, args.out, args.bible_dir, args.episode)
    elif args.cmd == "check":
        check(args.csv, args.json, getattr(args, "bible_dir", None))


if __name__ == "__main__":
    main()
