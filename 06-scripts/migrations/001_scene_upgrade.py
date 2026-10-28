#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
001_scene_upgrade.py —— 存量 scenes.jsonl 升级迁移（场景三对象 + 画幅三层）。

把旧版 Scene（只有 base_ref_image/day_night/in_out/lighting）升级到新版：
    - 补 scene_tier（从 EP001_assets.csv 的 remark 回填 S0/S1/S2/S3）
    - 补 base_aspect = "16:9"（旧图默认当 design plate，标 16:9；若旧图实际是 9:16 则需人工重出）
    - 补 power_layout / vertical_lanes（S0/S1 置空标 pending，S2/S3 留空）
    - blocking_ref_image / blocking_aspect 留空（S0/S1 需后续补 blocking ref）

用法：
    python migrate.py run 001_scene_upgrade.py --bible ../05-data-center/bible --assets ../05-data-center/episodes/EP001_assets.csv

本文件是迁移步骤实现，由 migrate.py 驱动；也可独立 import 调用 apply(scenes_path, assets_csv_path)。
"""

import csv
import json
import os


def _read_assets_remark(assets_csv):
    """从 EP001_assets.csv 读 scene_tier（remark 列里的 S0/S1/S2/S3）。"""
    tier_map = {}
    if not assets_csv or not os.path.exists(assets_csv):
        return tier_map
    with open(assets_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("type") != "scene":
                continue
            asset_id = row.get("asset_id")
            remark = row.get("remark", "")
            # remark 形如「主场景 S0」「重要场景 S1」「过场 S2」
            for tier in ("S0", "S1", "S2", "S3"):
                if tier in remark:
                    tier_map[asset_id] = tier
                    break
    return tier_map


def apply(scenes_path, assets_csv=None):
    """升级 scenes.jsonl，返回 (升级后的记录列表, 需人工重出的旧 9:16 图列表)。"""
    tier_map = _read_assets_remark(assets_csv)
    upgraded = []
    needs_reroll = []

    with open(scenes_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)

            # 已升级（有 scene_tier）则跳过
            if "scene_tier" in rec:
                upgraded.append(rec)
                continue

            asset_id = rec.get("asset_id", "")
            tier = tier_map.get(asset_id, "S3")  # 回填不到默认 S3（氛围，最低权重）

            rec["scene_tier"] = tier
            rec["base_aspect"] = "16:9"  # 旧图默认当 design plate 标 16:9

            # S0/S1 需要 power_layout + vertical_lanes + blocking ref，先置空标 pending
            if tier in ("S0", "S1"):
                rec["power_layout"] = {
                    "entry": "",
                    "power_seat": "",
                    "subordinate_positions": [],
                    "threshold_axis": "",
                    "handoff_zone": "",
                    "fixed_anchors": [],
                }
                rec["vertical_lanes"] = {
                    "foreground_pressure": "",
                    "center_actor_lane": "",
                    "background_power_anchor": "",
                    "handoff_zone": "",
                }
                rec["blocking_ref_image"] = ""
                rec["blocking_aspect"] = "9:16"

            # 旧图若文件名暗示 9:16（无 _design 后缀），标 legacy 待重出
            base_img = rec.get("base_ref_image", "")
            if base_img and "_design_" not in base_img:
                needs_reroll.append(f"{asset_id}: {base_img}（旧图，需重出 16:9 design plate）")

            upgraded.append(rec)

    return upgraded, needs_reroll


def main(argv):
    scenes_path = argv.get("bible", "")
    assets_csv = argv.get("assets", "")
    if not scenes_path or not os.path.exists(scenes_path):
        print("[迁移] 未找到 scenes.jsonl，跳过。")
        return 0

    upgraded, needs_reroll = apply(scenes_path, assets_csv)

    # 写回
    with open(scenes_path, "w", encoding="utf-8") as f:
        for rec in upgraded:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"[迁移 001] scenes.jsonl 升级完成：{len(upgraded)} 条")
    if needs_reroll:
        print("[迁移 001] 待重出清单（旧 9:16 图 → 重出 16:9 design plate）：")
        for item in needs_reroll:
            print(f"  - {item}")
    return 0
