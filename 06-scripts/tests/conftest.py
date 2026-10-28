#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pytest 公共 fixtures。"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)  # 06-scripts/
FIXTURES = os.path.join(HERE, "fixtures")

# 把 06-scripts 加进 path，方便 import 脚本模块
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


@pytest.fixture
def fixtures_dir():
    return FIXTURES


@pytest.fixture
def bible_dir(fixtures_dir):
    # fixtures 里 characters/scenes/props 直接平铺，构造一个 bible 目录视图
    # 校验函数按文件名找，这里直接返回 fixtures_dir（三文件都在）
    return fixtures_dir


@pytest.fixture
def storyboard_csv(fixtures_dir):
    return os.path.join(fixtures_dir, "storyboard.csv")


@pytest.fixture
def storyboard_json(fixtures_dir):
    return os.path.join(fixtures_dir, "storyboard.json")


@pytest.fixture
def storyboard_bad_json(fixtures_dir):
    return os.path.join(fixtures_dir, "storyboard_bad.json")
