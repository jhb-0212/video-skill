#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_schema.py —— 契约字段一致性（schema vs CSV vs make-spec）（域4）。"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.join(os.path.dirname(HERE), "schemas")
FIXTURES = os.path.join(HERE, "fixtures")


def _load_schema(name):
    with open(os.path.join(SCHEMA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


def test_asset_call_schema_fields_match_csv():
    """AssetCall schema 字段与 EP001_assets.csv 列一致。"""
    schema = _load_schema("asset_call.schema.json")
    schema_fields = set(schema["properties"].keys())
    with open(os.path.join(FIXTURES, "characters.jsonl"), "r", encoding="utf-8") as f:
        pass  # 占位，实际 assets csv 在 data-center
    # 直接读 data-center 的 assets.csv 列
    assets_csv = os.path.join(os.path.dirname(HERE), "..", "05-data-center", "episodes", "EP001_assets.csv")
    if os.path.exists(assets_csv):
        with open(assets_csv, "r", encoding="utf-8-sig") as f:
            cols = set(csv.DictReader(f).fieldnames)
        # CSV 列必须都在 schema 里（schema 是超集允许，CSV 不能有 schema 没定义的列）
        extra = cols - schema_fields
        assert not extra, f"CSV 有 schema 未定义的列: {extra}"


def test_shot_schema_required_fields():
    schema = _load_schema("shot.schema.json")
    required = set(schema["required"])
    assert "shot_id" in required
    assert "scene_id" in required
    assert "characters" in required or "characters" in schema["properties"]


def test_character_schema_required_fields():
    schema = _load_schema("character.schema.json")
    assert "asset_id" in schema["required"]
    assert "base_ref_image" in schema["required"]


def test_engine_profile_schema_fields():
    schema = _load_schema("engine_profile.schema.json")
    assert "engine_id" in schema["required"]
    assert "negative_map" in schema["required"]


def test_shot_schema_activated_catches_name_in_characters(tmp_path):
    """P1 修复：shot.schema 真正生效，characters 存名字（违反存ID铁律）被拦截。"""
    import validate_data as vd
    bad = {
        "episode": "EP001", "shot_id": "S01-01", "scene_id": "SC-01",
        "characters": ["梁大"], "action": "xx", "dialogue": "本镜无台词",
        "camera_angle": "中景", "camera_movement": "固定机位",
        "duration_sec": 5, "lighting": "", "assets_required": [],
    }
    tmp = tmp_path / "bad.json"
    tmp.write_text(json.dumps({"shots": [bad]}, ensure_ascii=False), encoding="utf-8")
    v = vd.Validator()
    vd.validate_storyboard(str(tmp), FIXTURES, v)
    # 应抓到 characters 格式违规（存名字而非 CHAR-xxx）
    assert any("characters" in e or "CHAR-" in e for e in v.errors), f"应拦截名字违规，实际: {v.errors}"


def test_shot_schema_activated_catches_bad_angle(tmp_path):
    """P1 修复：camera_angle 非法词被拦截。"""
    import validate_data as vd
    bad = {
        "episode": "EP001", "shot_id": "S01-01", "scene_id": "SC-01",
        "characters": ["CHAR-001"], "action": "xx", "dialogue": "本镜无台词",
        "camera_angle": "俯拍", "camera_movement": "固定机位",
        "duration_sec": 5, "lighting": "", "assets_required": [],
    }
    tmp = tmp_path / "bad_angle.json"
    tmp.write_text(json.dumps({"shots": [bad]}, ensure_ascii=False), encoding="utf-8")
    v = vd.Validator()
    vd.validate_storyboard(str(tmp), FIXTURES, v)
    assert any("camera_angle" in e for e in v.errors), f"应拦截非法景别，实际: {v.errors}"


def test_shot_schema_allows_changed_angle(tmp_path):
    """P1 修复：变化式景别「大远景→中景」应合法放行。"""
    import validate_data as vd
    ok = {
        "episode": "EP001", "shot_id": "S01-01", "scene_id": "",
        "characters": [], "action": "xx", "dialogue": "本镜无台词",
        "camera_angle": "大远景→中景", "camera_movement": "航拍",
        "duration_sec": 8, "lighting": "", "assets_required": [],
    }
    tmp = tmp_path / "ok.json"
    tmp.write_text(json.dumps({"shots": [ok]}, ensure_ascii=False), encoding="utf-8")
    v = vd.Validator()
    vd.validate_storyboard(str(tmp), FIXTURES, v)
    assert not v.errors, f"变化式景别应放行，实际: {v.errors}"
