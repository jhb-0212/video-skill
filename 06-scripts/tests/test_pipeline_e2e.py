#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pipeline_e2e.py —— 端到端：CSV → prompts → check → report.json（域4）。"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
FIXTURES = os.path.join(HERE, "fixtures")
DATA = os.path.join(os.path.dirname(HERE), "..", "05-data-center")


def test_storyboard_to_prompts_e2e(tmp_path):
    """端到端：CSV 分镜表 → 提示词（前端画面描述 + 后端引擎参数分离）。"""
    csv_path = os.path.join(FIXTURES, "storyboard.csv")
    bible = FIXTURES  # 三 jsonl 都在 fixtures
    out_prefix = str(tmp_path / "EP001")
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "storyboard_to_prompts.py"),
         csv_path, bible, out_prefix, "--engine", "comfyui"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr

    # 检查 batch.json 前端/后端分离
    batch_path = out_prefix + "_batch.json"
    assert os.path.exists(batch_path)
    with open(batch_path, "r", encoding="utf-8") as f:
        batch = json.load(f)
    assert batch["engine"] == "comfyui"
    assert "sampler" in batch["engine_params"] or "cfg" in batch["engine_params"]
    for item in batch["batch"]:
        # 前端 positive 不应含引擎参数（采样器/CFG/负面词）
        assert "negative" in item
        # 后端参数不在 positive 里（前后端分离）
        assert "cfg" not in item["positive"].lower()


def test_validate_data_catches_foreign_key(tmp_path):
    """端到端：validate_data 抓到外键缺失（坏数据）。"""
    bad_json = os.path.join(FIXTURES, "storyboard_bad.json")
    bible = FIXTURES
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "validate_data.py"),
         "storyboard", bad_json, bible],
        capture_output=True, text=True,
    )
    # SC-999 / CHAR-999 不在 bible → 应报错
    assert r.returncode == 1
    assert "外键" in r.stdout or "CHAR-999" in r.stdout


def test_validate_data_bible_ok():
    """端到端：正常 bible 校验通过。"""
    bible = FIXTURES
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "validate_data.py"), "bible", bible],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout
