#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tests.py —— 无 pytest 依赖的测试运行器（pytest 未装时的兜底）。

用法：
    python run_tests.py            # 跑全部测试
    python run_tests.py test_mappings.py   # 只跑某个文件

标准用法仍是 `pytest tests/`（见 pyproject.toml），本脚本是 CI 或本地无 pytest 时的兜底。
"""

import importlib.util
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(HERE, "tests")
sys.path.insert(0, HERE)
sys.path.insert(0, TESTS_DIR)


def load_module(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_test_file(path):
    """跑一个测试文件里的所有 test_ 函数，返回 (通过数, 失败列表)。"""
    mod = load_module(path)
    passed, failures = 0, []
    tests = [(n, getattr(mod, n)) for n in dir(mod) if n.startswith("test_") and callable(getattr(mod, n))]
    for name, fn in tests:
        try:
            import pathlib
            import tempfile
            # 注入常见 fixture
            kwargs = {}
            params = fn.__code__.co_varnames[:fn.__code__.co_argcount]
            if "fixtures_dir" in params:
                kwargs["fixtures_dir"] = TESTS_DIR + os.sep + "fixtures"
            if "bible_dir" in params:
                kwargs["bible_dir"] = TESTS_DIR + os.sep + "fixtures"
            if "storyboard_csv" in params:
                kwargs["storyboard_csv"] = os.path.join(TESTS_DIR, "fixtures", "storyboard.csv")
            if "storyboard_json" in params:
                kwargs["storyboard_json"] = os.path.join(TESTS_DIR, "fixtures", "storyboard.json")
            if "storyboard_bad_json" in params:
                kwargs["storyboard_bad_json"] = os.path.join(TESTS_DIR, "fixtures", "storyboard_bad.json")
            if "tmp_path" in params:
                td = tempfile.TemporaryDirectory()
                kwargs["tmp_path"] = pathlib.Path(td.name)
                try:
                    fn(**kwargs)
                finally:
                    td.cleanup()
                passed += 1
                continue
            fn(**kwargs)
            passed += 1
        except Exception as e:
            failures.append((name, e, traceback.format_exc()))
    return passed, failures, os.path.basename(path)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        files = [os.path.join(TESTS_DIR, target)]
    else:
        files = sorted(
            os.path.join(TESTS_DIR, f)
            for f in os.listdir(TESTS_DIR)
            if f.startswith("test_") and f.endswith(".py")
        )

    total_pass, total_fail = 0, 0
    all_failures = []
    for path in files:
        if not os.path.exists(path):
            print(f"跳过（不存在）：{path}")
            continue
        passed, failures, fname = run_test_file(path)
        total_pass += passed
        total_fail += len(failures)
        for name, e, tb in failures:
            all_failures.append((fname, name, e, tb))
        print(f"{fname}: {passed} passed, {len(failures)} failed")

    print(f"\n=== 总计：{total_pass} passed, {total_fail} failed ===")
    for fname, name, e, tb in all_failures:
        print(f"\n✗ {fname}::{name}")
        print(f"  异常: {e}")
        print(tb)
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
