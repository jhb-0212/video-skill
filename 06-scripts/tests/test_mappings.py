#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_mappings.py —— 景别/运镜映射 golden case（域4）。"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import storyboard_to_prompts as stp


def test_shot_type_map_golden():
    """景别 → 镜头类型 + 焦段的 golden 映射。"""
    assert stp.SHOT_TYPE_MAP["大远景"] == ("extreme wide shot", "24mm")
    assert stp.SHOT_TYPE_MAP["远景"] == ("wide shot", "24mm")
    assert stp.SHOT_TYPE_MAP["大全景"] == ("extreme full shot", "28mm")
    assert stp.SHOT_TYPE_MAP["全景"] == ("full shot", "35mm")
    assert stp.SHOT_TYPE_MAP["中景"] == ("medium shot", "50mm")
    assert stp.SHOT_TYPE_MAP["中近景"] == ("medium close-up", "85mm")
    assert stp.SHOT_TYPE_MAP["近景"] == ("close-up", "85mm")
    assert stp.SHOT_TYPE_MAP["特写"] == ("extreme close-up", "100mm")


def test_camera_move_map_golden():
    assert stp.CAMERA_MOVE_MAP["固定机位"] == "static shot"
    assert stp.CAMERA_MOVE_MAP["缓慢推近"] == "slow push in"
    assert stp.CAMERA_MOVE_MAP["航拍缓推"] == "aerial push-in"
    assert stp.CAMERA_MOVE_MAP["贴地跟拍"] == "low-angle tracking shot"


def test_parse_angle_simple():
    last, shot_type, focal, parts = stp.parse_angle("近景")
    assert last == "近景"
    assert shot_type == "close-up"
    assert focal == "85mm"
    assert parts == ["近景"]


def test_parse_angle_with_change():
    """带变化的景别「大远景→中景」取末端定焦段。"""
    last, shot_type, focal, parts = stp.parse_angle("大远景→中景")
    assert last == "中景"
    assert shot_type == "medium shot"
    assert focal == "50mm"
    assert parts == ["大远景", "中景"]


def test_parse_angle_unknown():
    last, shot_type, focal, _ = stp.parse_angle("未知景别")
    assert shot_type == "shot"  # 兜底
    assert focal == ""
