#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_check_assets.py —— 换脸打回 / 废片打回 / 降级标 unverified（域4）。"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import check_assets as ca


def test_safe_join_blocks_traversal(tmp_path):
    """路径穿越防护：design_file 逃出 versions 根 → 返回 None。"""
    versions = str(tmp_path / "versions")
    os.makedirs(versions, exist_ok=True)
    # 越界：../../etc/passwd
    assert ca.safe_join(versions, "../../etc/passwd") is None
    # 合法：相对路径
    os.makedirs(os.path.join(versions), exist_ok=True)
    ok = ca.safe_join(versions, "CHAR-001_v1.png")
    assert ok is not None
    assert ok.startswith(os.path.realpath(versions))


def test_safe_join_absolute_within_root(tmp_path):
    versions = str(tmp_path / "versions")
    os.makedirs(versions, exist_ok=True)
    f = os.path.join(versions, "a.png")
    assert ca.safe_join(versions, f) == os.path.realpath(f)


def test_check_version_number():
    assert ca.check_version_number("CHAR-001_v1.png")
    assert not ca.check_version_number("CHAR-001.png")


def test_load_profile_default():
    p = ca.load_profile(None)
    assert p["faceid"]["threshold"] == 0.90
    assert p["unverified_policy"] == "block"


def test_detect_junk_no_pil():
    """无 PIL 时 detect_junk 返回空（不误判）。"""
    if ca.HAS_PIL:
        return  # 有 PIL 时此测试无意义（真检测）
    # 无 PIL 环境：detect_junk 直接返回空列表
    assert ca.detect_junk("/nonexistent", {}) == []


def test_check_scene_reads_tier_from_bible(tmp_path):
    """P0 修复：scene_tier 从 bible 反查，不依赖 CSV 行（CSV 无 scene_tier 列）。

    场景 S0 缺 blocking ref → 必须报 [缺 blocking]，证明反查生效。
    """
    versions = tmp_path / "versions"
    versions.mkdir()
    # 真实创建一个 design plate 文件（内容无所谓，blocking 检查不依赖图片解析）
    (versions / "SC-01_冰湖_design_v1.png").write_bytes(b"fake")

    # CSV 行（模拟 assets.csv 的一行：只有 design_file，无 scene_tier）
    row = {
        "asset_id": "SC-01",
        "type": "scene",
        "name": "冰湖营地",
        "design_file": "SC-01_冰湖_design_v1.png",
    }
    # bible 反查记录：S0，但缺 blocking_ref_image
    bible_refs = {
        "SC-01": {
            "scene_tier": "S0",
            "blocking_ref_image": "",  # 缺失
        }
    }
    errs = ca.check_scene(row, str(versions), bible_refs)
    # 关键断言：S0 缺 blocking 必须被报出（证明 tier 反查生效）
    assert any("[缺 blocking]" in e for e in errs), f"应报缺 blocking，实际: {errs}"


def test_check_scene_s2_no_blocking_required(tmp_path):
    """S2 场景不需要 blocking ref，不应报 [缺 blocking]。"""
    versions = tmp_path / "versions"
    versions.mkdir()
    (versions / "SC-03_车内_design_v1.png").write_bytes(b"fake")

    row = {
        "asset_id": "SC-03",
        "type": "scene",
        "name": "车内",
        "design_file": "SC-03_车内_design_v1.png",
    }
    bible_refs = {"SC-03": {"scene_tier": "S2"}}
    errs = ca.check_scene(row, str(versions), bible_refs)
    assert not any("[缺 blocking]" in e for e in errs), f"S2 不应报缺 blocking，实际: {errs}"
