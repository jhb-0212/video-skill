#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scene_check 与场景层 schema 校验的测试（第四轮 P1 修复）。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import scene_check as sc
import validate_data as vd


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def test_scene_check_anchor_missing_warns(tmp_path):
    """P1 修复：S0/S1 场景 power_layout.fixed_anchors 为空应报锚点 warning。"""
    scenes = tmp_path / "scenes.jsonl"
    _write(str(scenes), json.dumps({
        "asset_id": "SC-99", "type": "scene", "name": "x",
        "scene_tier": "S0", "base_aspect": "16:9",
        "base_ref_image": "SC-99_design_v1.png",
        "blocking_ref_image": "SC-99_blocking_v1.png",
        "blocking_aspect": "9:16", "power_layout": {},
    }, ensure_ascii=False) + "\n")
    states = tmp_path / "states.jsonl"
    _write(str(states), "")

    errors, warnings = sc.check(str(states), str(scenes), str(tmp_path))
    assert not errors
    assert any("锚点" in w and "fixed_anchors" in w for w in warnings), \
        f"应报锚点缺失，实际 warnings={warnings}"


def test_scene_check_anchor_present_no_warn(tmp_path):
    """S0 场景有 fixed_anchors 时不应报锚点 warning。"""
    scenes = tmp_path / "scenes.jsonl"
    _write(str(scenes), json.dumps({
        "asset_id": "SC-99", "type": "scene", "name": "x",
        "scene_tier": "S0", "base_aspect": "16:9",
        "base_ref_image": "SC-99_design_v1.png",
        "blocking_ref_image": "SC-99_blocking_v1.png",
        "blocking_aspect": "9:16",
        "power_layout": {"fixed_anchors": ["雪山", "冰湖"]},
    }, ensure_ascii=False) + "\n")
    states = tmp_path / "states.jsonl"
    _write(str(states), "")

    errors, warnings = sc.check(str(states), str(scenes), str(tmp_path))
    assert not any("锚点" in w for w in warnings), f"不应报锚点，实际={warnings}"


def test_validate_scene_states_catches_bad_state_code(tmp_path):
    """场景层 schema 接入：非法 state_code 应被拦截。"""
    states = tmp_path / "states.jsonl"
    _write(str(states), json.dumps({
        "state_id": "SC-99_EP001_SS0", "scene_id": "SC-99",
        "episode": "EP001", "state_code": "S3_reveal",
    }) + "\n")
    bible_ids = {"SC-99"}
    v = vd.Validator()
    vd.validate_scene_states(str(states), bible_ids, v)
    assert any("state_code" in e for e in v.errors), f"应报 state_code 非法，实际={v.errors}"


def test_validate_scene_states_catches_foreign_key(tmp_path):
    """场景层外键：scene_id 不在 bible 应被拦截。"""
    states = tmp_path / "states.jsonl"
    _write(str(states), json.dumps({
        "state_id": "SC-99_EP001_SS0", "scene_id": "SC-99",
        "episode": "EP001", "state_code": "SS0_normal_order",
    }) + "\n")
    bible_ids = {"SC-01"}  # 故意不含 SC-99
    v = vd.Validator()
    vd.validate_scene_states(str(states), bible_ids, v)
    assert any("外键" in e for e in v.errors), f"应报外键缺失，实际={v.errors}"


def test_validate_scene_readiness_catches_bad_label(tmp_path):
    """场景可用性：非法 readiness_label 应被拦截。"""
    rd = tmp_path / "readiness.json"
    _write(str(rd), json.dumps([{
        "scene_id": "SC-01", "readiness_label": "not_a_label",
    }]))
    bible_ids = {"SC-01"}
    v = vd.Validator()
    vd.validate_scene_readiness(str(rd), bible_ids, v)
    assert any("readiness_label" in e for e in v.errors), f"应报 label 非法，实际={v.errors}"
