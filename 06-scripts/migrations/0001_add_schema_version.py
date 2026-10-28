#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
0001_add_schema_version.py —— 首迁移：给 bible jsonl 加 schema_version 字段。

迁移内容：
    为 characters.jsonl / scenes.jsonl / props.jsonl 每行补充 schema_version 标记，
    让后续 schema 变更可追踪、可迁移。

用法：由 migrate.py 自动调用，也可手动 `python 0001_add_schema_version.py <data_dir>`。
"""

import json
import os
import sys

CURRENT_VERSION = 1


def upgrade(data_dir):
    bible = os.path.join(data_dir, "bible")
    for fn in ("characters.jsonl", "scenes.jsonl", "props.jsonl"):
        path = os.path.join(bible, fn)
        if not os.path.exists(path):
            continue
        out_lines = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if "schema_version" not in rec:
                    rec["schema_version"] = CURRENT_VERSION
                out_lines.append(json.dumps(rec, ensure_ascii=False))
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines) + "\n")
        print(f"    ✓ {fn} 已加 schema_version={CURRENT_VERSION}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    upgrade(sys.argv[1])
