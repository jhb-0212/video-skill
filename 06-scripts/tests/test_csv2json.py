#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_csv2json.py —— CSV 唯一源派生 + scene_id 回填（P1 修复）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import csv2json as cj


def test_resolve_scene_id():
    """从备注列解析 scene_id：取第一个 SC-xx，无则空串。"""
    assert cj._resolve_scene_id("SC-03 车内") == "SC-03"
    assert cj._resolve_scene_id("SC-02 PR-01 PR-02 陆巡 EVX-9 入镜") == "SC-02"
    assert cj._resolve_scene_id("PR-02 EVX-9") == ""  # 只有道具，无场景
    assert cj._resolve_scene_id("") == ""
    assert cj._resolve_scene_id(None) == ""


def test_derive_json_fills_scene_id(tmp_path):
    """derive_json 用备注列场景 ID 回填 scene_id，而非硬编码空串。"""
    # 造一个最小 CSV
    csv_path = tmp_path / "storyboard.csv"
    csv_path.write_text(
        "分镜号,镜头号,建议时长,画面描述,人物,台词,运镜,构图,景别,备注\n"
        "S02,2,5,切进车内,梁大,本镜无台词,固定机位,双人同框,中近景,SC-03 车内\n"
        "S01,1,8,公路行驶,,画外音,航拍,车队居中,大远景,SC-02 PR-01 入镜\n",
        encoding="utf-8-sig",
    )
    data = cj.derive_json(str(csv_path), "EP001", {})
    shots = {s["shot_id"]: s for s in data["shots"]}
    assert shots["S02-02"]["scene_id"] == "SC-03"
    assert shots["S01-01"]["scene_id"] == "SC-02"


def test_derive_json_scene_id_empty_when_no_scene(tmp_path):
    """备注列无 SC-xx 时 scene_id 为空串（空镜/纯道具镜）。"""
    csv_path = tmp_path / "storyboard.csv"
    csv_path.write_text(
        "分镜号,镜头号,建议时长,画面描述,人物,台词,运镜,构图,景别,备注\n"
        "S02,1,4,拍车轮,梁大,本镜无台词,贴地,特写,近景,PR-02 EVX-9\n",
        encoding="utf-8-sig",
    )
    data = cj.derive_json(str(csv_path), "EP001", {})
    assert data["shots"][0]["scene_id"] == ""
