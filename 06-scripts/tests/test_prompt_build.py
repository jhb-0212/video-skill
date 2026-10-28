#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_prompt_build.py —— 七段式拼装 + 状态变体按集过滤（域4）。"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import storyboard_to_prompts as stp


def _bible(fixtures_dir):
    return stp.load_bible(fixtures_dir)


def _shot():
    return {
        "shot_id": "S01-01",
        "characters": ["CHAR-001"],
        "action": "傍晚雪域峡谷公路蜿蜒入山",
        "camera_angle": "大远景",
        "camera_movement": "航拍缓推",
        "composition": "车队居中",
        "duration_sec": 8,
    }


def test_build_prompt_seven_sections(fixtures_dir):
    """七段式拼装：含图种/人物/画面/运镜/背景光/风格/参考图隔离。"""
    bible = _bible(fixtures_dir)
    p = stp.build_prompt(_shot(), bible)
    pos = p["positive"]
    assert "影视剧照" in pos          # 段1 图种
    assert "梁大" in pos              # 段2 人物
    assert "傍晚雪域峡谷公路" in pos  # 段3 画面
    assert "aerial push-in" in pos    # 段5 运镜
    assert "风格" in pos              # 段7 风格
    assert "参考图权限隔离" in pos    # 参考图隔离


def test_build_prompt_no_negative_inside(fixtures_dir):
    """前后端解耦：build_prompt 不产出负面词（负面词由后端注入）。"""
    bible = _bible(fixtures_dir)
    p = stp.build_prompt(_shot(), bible)
    assert "negative" not in p
    assert "negative" not in p["positive"]


def test_build_prompt_empty_char(fixtures_dir):
    """空镜（无人物）正确处理。"""
    bible = _bible(fixtures_dir)
    shot = _shot()
    shot["characters"] = []
    p = stp.build_prompt(shot, bible)
    assert "空镜" in p["positive"]


def test_resolve_look_delta_filters_by_episode():
    """状态变体按集过滤：EP001 不该出现 EP003-EP005 的夜行衣。"""
    bible = {
        "char": {
            "CHAR-001": {
                "name": "梁大",
                "looks": [
                    {"look_id": "V00", "desc": "基础造型", "valid_episodes": "全片"},
                    {"look_id": "V01", "desc": "夜行衣", "valid_episodes": "EP003-EP005"},
                ],
            }
        },
        "scene": {}, "prop": {},
    }
    # EP001：不该出现 V01（夜行衣是 EP003-EP005）
    delta_ep001 = stp._resolve_look_delta(["CHAR-001"], bible, episode="EP001")
    assert "夜行衣" not in delta_ep001, f"EP001 不应带出 EP003-EP005 的变体，实际: {delta_ep001}"

    # EP003：应该出现 V01
    delta_ep003 = stp._resolve_look_delta(["CHAR-001"], bible, episode="EP003")
    assert "夜行衣" in delta_ep003, f"EP003 应带出夜行衣，实际: {delta_ep003}"

    # 不传 episode：全列出（兼容旧行为）
    delta_all = stp._resolve_look_delta(["CHAR-001"], bible)
    assert "夜行衣" in delta_all


def test_look_applies_to_ranges():
    """valid_episodes 范围解析：单集/范围/全片/逗号分隔。"""
    assert stp._look_applies_to("全片", "EP010")
    assert stp._look_applies_to("EP003-EP005", "EP003")
    assert stp._look_applies_to("EP003-EP005", "EP005")
    assert not stp._look_applies_to("EP003-EP005", "EP002")
    assert not stp._look_applies_to("EP003-EP005", "EP006")
    assert stp._look_applies_to("EP003,EP004", "EP004")
    assert not stp._look_applies_to("EP003,EP004", "EP005")


def test_build_negative_core(fixtures_dir):
    """后端负面词注入：核心组必在。"""
    profile = {
        "engine_id": "comfyui",
        "negative_map": {
            "core": "deformed hands, extra limbs",
            "shot": "cropped feet",
        },
    }
    neg = stp.build_negative(profile, shot_kind="shot")
    assert "deformed hands" in neg
    assert "cropped feet" in neg


def test_build_negative_fallback():
    """无 profile 时回退到内置默认负面词。"""
    neg = stp.build_negative(None)
    assert "deformed hands" in neg


def test_orientation_of():
    """画幅 → 横竖版文案（P1 修复：16:9 不能再写「竖版」）。"""
    assert stp._orientation_of("16:9") == "横版"
    assert stp._orientation_of("9:16") == "竖版"
    assert stp._orientation_of("2.35:1") == "横版"
    assert stp._orientation_of("21:9") == "横版"


def test_build_prompt_aspect_orientation(fixtures_dir):
    """build_prompt 按 aspect 动态写横/竖版，不硬编码「竖版」。"""
    bible = _bible(fixtures_dir)
    p_h = stp.build_prompt(_shot(), bible, aspect="16:9")
    assert "16:9 横版" in p_h["positive"], "16:9 应标注横版"
    p_v = stp.build_prompt(_shot(), bible, aspect="9:16")
    assert "9:16 竖版" in p_v["positive"], "9:16 应标注竖版"
    assert "16:9 竖版" not in p_h["positive"], "禁止出现自相矛盾的「16:9 竖版」"


def test_anchor_line_reads_scene_id(fixtures_dir):
    """锚点注入优先读结构化 scene_id（P2 修复）。"""
    bible = _bible(fixtures_dir)
    # fixture scenes.jsonl 的 SC-01 有 fixed_anchors
    shot = {"scene_id": "SC-01", "assets_required": []}
    anchor = stp._build_anchor_line(shot, bible)
    assert "Keep consistent" in anchor
    assert "雪山" in anchor  # SC-01 的 fixed_anchor
