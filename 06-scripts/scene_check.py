#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scene_check.py —— 场景专用门禁（闸二），对应 SceneReadiness 对象。

校验 5 项：
    1. 画幅合规（error）：Scene.base_aspect / blocking_aspect 非枚举值，或 design plate 是 9:16
    2. 状态码合法（error）：SceneState.state_code 不在 SS0-SS5 枚举
    3. 状态连续性（warn）：inherits_from 指向的 state_id 不存在 / next_state 未定义
    4. 锚点缺失（warn）：S0/S1 场景的 power_layout.fixed_anchors 为空（场景基准层必须定义固定锚点）
    5. 可用性缺失（warn）：S0/S1 场景无 SceneReadiness 记录

用法：
    python scene_check.py <scene_states.jsonl> <scenes.jsonl> <versions_dir> [--readiness EP001_scene_readiness.json]

退出码：0 全过 / 2 仅警告 / 1 有 error。
"""

import argparse
import json
import os
import re
import sys

# 状态码封闭枚举（与 scene_state.schema.json 一致）
STATE_CODES = {
    "SS0_normal_order",
    "SS1_pressure_setup",
    "SS2_humiliation",
    "SS3_reveal",
    "SS4_aftermath",
    "SS5_power_reversal",
}

# 画幅枚举
DESIGN_ASPECTS = {"16:9", "2.35:1"}
BLOCKING_ASPECT = "9:16"

READINESS_LABELS = {
    "scene_video_ready",
    "needs_layout_lock",
    "needs_light_lock",
    "needs_prop_lock",
    "image_only",
    "reroll_scene",
}


def load_jsonl(path):
    records = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _episode_of(state_id):
    """从 state_id（SC-01_EP001_SS0）提取 episode（EP001）。"""
    m = re.search(r"(EP\d{3})", state_id or "")
    return m.group(1) if m else ""


def image_size(path):
    try:
        from PIL import Image
        return Image.open(path).size  # (w, h)
    except Exception:
        return None, None


def check(states_path, scenes_path, versions_dir, readiness_path=None):
    errors = []
    warnings = []

    scenes = load_jsonl(scenes_path)
    states = load_jsonl(states_path)

    scene_by_id = {s.get("asset_id"): s for s in scenes}
    state_ids = {s.get("state_id") for s in states}

    # 1. 画幅合规（Scene）
    for sc in scenes:
        sid = sc.get("asset_id")
        base_aspect = sc.get("base_aspect", "")
        blocking_aspect = sc.get("blocking_aspect", "")
        tier = sc.get("scene_tier", "")

        if base_aspect not in DESIGN_ASPECTS:
            errors.append(f"[画幅] {sid} base_aspect={base_aspect!r} 非法，只能 16:9 / 2.35:1")

        if tier in ("S0", "S1"):
            if blocking_aspect and blocking_aspect != BLOCKING_ASPECT:
                errors.append(f"[画幅] {sid} blocking_aspect={blocking_aspect!r} 非法，只能 9:16")
            if not sc.get("blocking_ref_image"):
                errors.append(f"[画幅] {sid} ({tier}) 缺 blocking_ref_image")
            # 4. 锚点缺失（warn）：S0/S1 场景基准层必须定义固定锚点
            pl = sc.get("power_layout", {})
            if not pl.get("fixed_anchors"):
                warnings.append(f"[锚点] {sid} ({tier}) power_layout.fixed_anchors 为空（跨镜会漂移）")

        # 用实际图片尺寸交叉验证（有 PIL 时）
        base_img = sc.get("base_ref_image", "")
        if base_img and os.path.isabs(base_img) is False:
            # base_ref_image 通常相对 versions 根，用 basename 定位
            p = os.path.join(versions_dir, os.path.basename(base_img))
            if os.path.exists(p):
                w, h = image_size(p)
                if w is not None and w <= h:
                    errors.append(f"[画幅] {sid} design plate 实际是 {w}x{h}（竖版），必须是横版")

    # 2. 状态码合法（SceneState）
    for st in states:
        scode = st.get("state_code", "")
        if scode not in STATE_CODES:
            errors.append(f"[状态码] {st.get('state_id')} state_code={scode!r} 不在 SS0-SS5 枚举")

        # 3. 状态连续性（warn）
        inherits = st.get("inherits_from")
        if inherits and inherits not in state_ids:
            warnings.append(f"[连续性] {st.get('state_id')} inherits_from={inherits!r} 不存在")
        # next_state 处理（P2 修复，避免首/末集误报）：
        #   - 为空：合法的集边界，不报；
        #   - 指向同集（当前集 episode）却不存在：真正的断链，warn；
        #   - 指向别的集（跨集，如 EP001 末态 next_state=..._EP002_...）：正常，不报。
        nxt = st.get("next_state")
        if nxt:
            same_ep = _episode_of(st.get("state_id", "")) == _episode_of(nxt)
            if same_ep and nxt not in state_ids:
                warnings.append(f"[连续性] {st.get('state_id')} next_state={nxt!r} 不存在（同集内断链）")

    # 5. 可用性缺失（S0/S1 无 SceneReadiness）+ readiness_label 合法性
    readiness = {}
    if readiness_path and os.path.exists(readiness_path):
        with open(readiness_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                readiness = {r.get("scene_id"): r for r in data}
            elif isinstance(data, dict) and "scene_id" in data:
                readiness = {data.get("scene_id"): data}
    # readiness_label 封闭枚举校验（此前定义了 READINESS_LABELS 却未使用）
    for sid, r in readiness.items():
        label = r.get("readiness_label")
        if label and label not in READINESS_LABELS:
            errors.append(f"[可用性] {sid} readiness_label={label!r} 不在封闭枚举")
    for sc in scenes:
        if sc.get("scene_tier") in ("S0", "S1") and sc.get("asset_id") not in readiness:
            warnings.append(f"[可用性] {sc.get('asset_id')} ({sc.get('scene_tier')}) 无 SceneReadiness 记录")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="场景专用门禁（SceneReadiness）")
    parser.add_argument("states_path", help="EPxxx_scene_states.jsonl")
    parser.add_argument("scenes_path", help="bible/scenes.jsonl")
    parser.add_argument("versions_dir", help="生成图目录")
    parser.add_argument("--readiness", help="EPxxx_scene_readiness.json")
    args = parser.parse_args()

    errors, warnings = check(args.states_path, args.scenes_path, args.versions_dir, args.readiness)

    if errors:
        print("❌ 场景门禁发现 error：")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("⚠️ 场景门禁发现 warning：")
        for w in warnings:
            print(f"  ⚠ {w}")
    if not errors and not warnings:
        print("✅ 场景门禁通过：画幅合规 + 状态码合法 + 连续性完整 + 可用性齐全")

    if errors:
        sys.exit(1)
    elif warnings:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
