#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate.py —— 数据结构迁移执行器（域1：无版本与迁移）。

数据 schema 变更时，旧 jsonl/json 需要迁移到新版本。本脚本按 schema_version 找对应迁移脚本执行。

用法：
    python migrate.py <data_dir> [--to <version>]

迁移脚本放在 migrations/ 目录，命名：`0001_<描述>.py`，每个脚本实现 `upgrade(data_dir)`。
迁移记录写进 `05-data-center/versions/` 或 `data_dir/.migration_state.json`，避免重复执行。
"""

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(HERE, "migrations")


def list_migrations():
    if not os.path.isdir(MIGRATIONS_DIR):
        return []
    migs = []
    for fn in sorted(os.listdir(MIGRATIONS_DIR)):
        if fn.endswith(".py") and fn[0].isdigit():
            migs.append(fn)
    return migs


def load_state(data_dir):
    state_path = os.path.join(data_dir, ".migration_state.json")
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"applied": []}


def save_state(data_dir, state):
    state_path = os.path.join(data_dir, ".migration_state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def run_migration(data_dir, filename):
    path = os.path.join(MIGRATIONS_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "upgrade"):
        print(f"  ⚠ {filename} 缺少 upgrade(data_dir) 函数，跳过")
        return False
    mod.upgrade(data_dir)
    return True


def main():
    parser = argparse.ArgumentParser(description="数据结构迁移执行器")
    parser.add_argument("data_dir", help="05-data-center 目录")
    args = parser.parse_args()

    migrations = list_migrations()
    if not migrations:
        print("无迁移脚本。")
        return

    state = load_state(args.data_dir)
    applied = set(state.get("applied", []))

    for fn in migrations:
        if fn in applied:
            print(f"  ✓ 已迁移（跳过）：{fn}")
            continue
        print(f"  → 执行迁移：{fn}")
        try:
            run_migration(args.data_dir, fn)
            applied.add(fn)
            save_state(args.data_dir, {"applied": sorted(applied)})
            print(f"  ✓ 完成：{fn}")
        except Exception as e:
            print(f"  ✗ 失败：{fn} -> {e}")
            sys.exit(1)

    print(f"迁移完成，共 {len(applied)} 个已应用。")


if __name__ == "__main__":
    main()
