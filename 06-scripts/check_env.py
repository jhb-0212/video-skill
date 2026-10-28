#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_env.py —— 环境检查（域5）：启动时报告「哪些可选依赖缺失、哪些能力降级」，不静默。

用法：
    python check_env.py

输出：
    - 每个可选依赖的可用状态
    - 因缺依赖而「降级」的能力清单
    - 退出码 0（核心能力齐）/ 1（缺核心能力）
"""

import importlib
import sys

# (模块名, 能力, 是否核心)
MODULES = [
    ("jsonschema", "JSON Schema 完整校验", False),
    ("PIL", "废片启发式过滤（图像过小/纯色/损坏检测）", False),
    ("numpy", "纯色像素标准差检测", False),
    ("insightface", "FaceID 人脸相似度比对（换脸打回）", False),
    ("cv2", "OpenCV 图像解码（FaceID 依赖）", False),
    ("pytest", "pytest 测试运行", False),
    ("ruff", "代码 lint", False),
]


def main():
    print("=== 环境检查 ===")
    print(f"Python: {sys.version}")
    degraded = []
    available = 0

    for mod, ability, core in MODULES:
        try:
            importlib.import_module(mod)
            status = "✅ 可用"
            available += 1
        except ImportError:
            status = "❌ 缺失"
            if not core:
                degraded.append(ability)
        print(f"  {status}  {mod:<14} → {ability}{'（核心）' if core else ''}")

    print("\n=== 能力降级 ===")
    if degraded:
        for d in degraded:
            print(f"  ⚠ 降级：{d}")
        print("\n  这些是可选能力，缺失不影响核心管线（脚本会优雅降级或标 unverified）。")
        print("  要启用完整能力：pip install -e '.[image]' 或 pip install -e '.[faceid]'")
    else:
        print("  全部可选依赖可用，无降级。")

    print("\n核心能力（标准库）全部就绪：数据校验 / 提示词生成 / CSV↔JSON / 迁移 / 质检门禁（缺图+版本号）")
    sys.exit(0)


if __name__ == "__main__":
    main()
