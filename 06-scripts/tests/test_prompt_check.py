#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_prompt_check.py —— 5 类埋雷全部抓中 + 正常数据 0 error（域4）。"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import prompt_check as pc


def _base_positive():
    return "影视剧照，中近景，9:16 竖版，电影级质感。参考图权限隔离：仅允许提供脸型，严禁带入服装背景。"


def test_engine_param_overrun_caught():
    """引擎参数越界：positive 含 MJ 专属参数但未声明引擎 → 报错。"""
    errs, warns = pc.check_engine_params("影视剧照 --ar 9:16 --cref xxx", None)
    assert errs, "应抓到 MJ 专属参数越界"


def test_engine_param_ok_when_declared():
    """声明引擎后，该引擎专属参数不再越界。"""
    errs, warns = pc.check_engine_params("影视剧照 --ar 9:16", "MJ")
    assert not errs


def test_text_conflict_caught():
    """文字政策矛盾：「写着青梧殿」+「不要文字」→ 报错。"""
    pos = "牌匾写着『青梧殿』，画面不要任何文字"
    errs = pc.check_text_conflict(pos)
    assert errs


def test_text_conflict_none():
    pos = "纯白背景，无文字"
    assert not pc.check_text_conflict(pos)


def test_name_binding_bad():
    """无语义命名 → 报错。"""
    errs, warns = pc.check_name_binding(["1"], set(), set())
    assert errs


def test_name_binding_ok():
    errs, warns = pc.check_name_binding(["CHAR-001"], {"CHAR-001"}, {"梁大"})
    assert not errs


def test_ref_isolation_missing():
    """参考图隔离缺失 → 警告。"""
    pos = "用参考图生成人物多视图"  # 有参考图，无边界声明
    warns = pc.check_ref_isolation(pos)
    assert warns


def test_ref_isolation_present():
    pos = "参考图权限隔离：仅允许提供脸型，严禁带入服装背景。"
    assert not pc.check_ref_isolation(pos)


def test_negative_missing():
    """负面词缺失 → 警告。"""
    warns = pc.check_negative({"positive": "纯描述", "negative": ""})
    assert warns


def test_negative_present():
    assert not pc.check_negative({"positive": "纯描述", "negative": "deformed hands"})
