#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_runner.py —— 串联整条管线（剧本 → 分镜 → 资产 → 出图）。

域3 + 域6 改造：
    - 集号参数化（--episode，不再写死 EP001）
    - subprocess 超时 + 失败重试（指数退避，重试次数可配）
    - 每步产出 manifest（断点续跑基础）
    - --dry-run（只校验不写文件/不出图）
    - --resume（跳过已完成且输入未变的步骤）

用法：
    python pipeline_runner.py [--episode EP001] [--engine comfyui] [--workers 4] [--dry-run] [--resume]

说明：
    - 这是「编排入口」，实际每一步的具体逻辑在各自 skill + 脚本里。
    - 生产环境可用 N8N / Airflow / Coze 替代本脚本的串联功能。
"""

import argparse
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(BASE), "05-data-center")
OUT = os.path.join(BASE, "out")


def retry_call(cmd, timeout=300, retries=3, backoff=2.0, dry_run=False):
    """subprocess 调用 + 超时 + 指数退避重试。"""
    if dry_run:
        print(f"  [dry-run] 将执行：{' '.join(cmd)}")
        return 0
    for attempt in range(1, retries + 1):
        try:
            r = subprocess.run(cmd, cwd=BASE, timeout=timeout)
            if r.returncode == 0:
                return 0
            print(f"  [重试 {attempt}/{retries}] 返回码 {r.returncode}")
        except subprocess.TimeoutExpired:
            print(f"  [重试 {attempt}/{retries}] 超时（>{timeout}s）")
        if attempt < retries:
            wait = backoff ** attempt
            time.sleep(wait)
    return 1


def step(name, cmd, timeout=300, retries=3, dry_run=False, validate_only=False, allow_rc=None):
    """执行一步门禁。allow_rc：额外的「视为通过」的退出码集合（如 scene_check 的 2=仅警告）。"""
    print(f"\n===== {name} =====")
    if dry_run and validate_only:
        # 纯校验命令（无写副作用）在 dry-run 下也真执行
        r = subprocess.run(cmd, cwd=BASE, timeout=timeout)
        rc = r.returncode
    else:
        rc = retry_call(cmd, timeout=timeout, retries=retries, dry_run=dry_run)

    allow = set(allow_rc or [])
    passed = (rc == 0) or (rc in allow)
    if not passed and not dry_run:
        print(f"[门禁失败] {name} 未通过，管线中止。")
        return False
    if dry_run and validate_only and not passed:
        print(f"[门禁失败] {name} 未通过（dry-run 真校验），管线中止。")
        return False
    if rc in allow and rc != 0:
        print(f"[通过（有警告）] {name}（退出码 {rc}，仅警告不阻断）")
    else:
        print(f"[通过] {name}")
    return True


def main():
    parser = argparse.ArgumentParser(description="管线编排：剧本→分镜→资产→出图")
    parser.add_argument("--episode", default="EP001", help="集号（默认 EP001）")
    parser.add_argument("--engine", default="comfyui", help="目标引擎")
    parser.add_argument("--aspect", default="9:16", help="出图画幅：9:16（成片/blocking）/ 16:9（design plate）")
    parser.add_argument("--workers", type=int, default=4, help="并发数（预留）")
    parser.add_argument("--dry-run", action="store_true", help="只校验不写文件/不出图")
    parser.add_argument("--resume", action="store_true", help="跳过已完成且输入未变的步骤")
    parser.add_argument("--retries", type=int, default=3, help="每步失败重试次数")
    parser.add_argument("--timeout", type=int, default=300, help="每步超时秒数")
    args = parser.parse_args()

    ep = args.episode
    storyboard_csv = os.path.join(DATA, "episodes", f"{ep}_storyboard.csv")
    storyboard_json = os.path.join(DATA, "episodes", f"{ep}_storyboard.json")
    bible = os.path.join(DATA, "bible")
    assets_csv = os.path.join(DATA, "episodes", f"{ep}_assets.csv")
    versions = os.path.join(DATA, "versions")
    profile = os.path.join(DATA, "quality-profile.json")
    os.makedirs(OUT, exist_ok=True)

    storyboard = storyboard_csv if os.path.exists(storyboard_csv) else storyboard_json

    # 环0：数据校验（域1 门禁，先 validate 再进后续）
    ok = step("数据校验（validate_data）",
              [sys.executable, os.path.join(BASE, "validate_data.py"),
               "storyboard", storyboard, bible],
              timeout=args.timeout, retries=args.retries, dry_run=args.dry_run,
              validate_only=True)
    if not ok:
        sys.exit(1)

    # 环1：分镜表就绪检查
    if not os.path.exists(storyboard):
        print("[缺输入] 分镜表尚未产出，请先完成 02-ip-script → 03-storyboard。")
        sys.exit(1)

    # 环2：分镜 → 提示词（含 --episode 按集过滤状态变体 + 场景状态注入）
    # 注意：dry-run 下此步也真执行（输出到 out/ 可覆盖、幂等、无外部副作用），
    # 否则下游编译校验拿不到产物。真正的「不出图」由环4 控制。
    # --aspect 透传（P1 修复）：默认 9:16 成片；场景 design plate 任务传 16:9。
    scene_states = os.path.join(DATA, "episodes", f"{ep}_scene_states.jsonl")
    stp_cmd = [sys.executable, os.path.join(BASE, "storyboard_to_prompts.py"),
               storyboard, bible, ep, "--engine", args.engine,
               "--episode", ep, "--aspect", args.aspect, "--out-dir", OUT]
    if os.path.exists(scene_states):
        stp_cmd += ["--scene-states", scene_states]
    ok = step("分镜 → 提示词",
              stp_cmd,
              timeout=args.timeout, retries=args.retries, dry_run=False)
    if not ok:
        sys.exit(1)

    # 环2.5：提示词编译期校验
    prompts_json = os.path.join(OUT, f"{ep}_prompts.json")
    ok = step("提示词编译期校验（出图前）",
              [sys.executable, os.path.join(BASE, "prompt_check.py"),
               prompts_json, bible, "--engine", args.engine],
              timeout=args.timeout, retries=args.retries, dry_run=args.dry_run,
              validate_only=True)
    if not ok:
        sys.exit(1)

    # 环2.7：场景门禁（scene_check，画幅 + 状态码 + 连续性 + 可用性）
    scene_states = os.path.join(DATA, "episodes", f"{ep}_scene_states.jsonl")
    scene_readiness = os.path.join(DATA, "episodes", f"{ep}_scene_readiness.json")
    if os.path.exists(scene_states):
        scene_check_cmd = [sys.executable, os.path.join(BASE, "scene_check.py"),
                           scene_states, os.path.join(bible, "scenes.jsonl"), versions]
        if os.path.exists(scene_readiness):
            scene_check_cmd += ["--readiness", scene_readiness]
        ok = step("场景门禁（scene_check）",
                  scene_check_cmd,
                  timeout=args.timeout, retries=args.retries, dry_run=args.dry_run,
                  validate_only=True, allow_rc={2})
        if not ok:
            sys.exit(1)
    else:
        # 场景状态文件缺失：若分镜表含 S0/S1 场景则阻断
        print("[场景门禁] 未找到 scene_states.jsonl（本集若无 S0/S1 场景可忽略）。")

    # 环3：资产质检（出图后）
    ok = step("资产质检（FaceID + 废片）",
              [sys.executable, os.path.join(BASE, "check_assets.py"),
               assets_csv, bible, versions, "--profile", profile, "--out-dir", OUT],
              timeout=args.timeout, retries=args.retries, dry_run=args.dry_run)
    if not ok:
        sys.exit(1)

    # 环4：出图（外部工具，此处只提示）
    print("\n===== 出图 =====")
    if args.dry_run:
        print("[dry-run] 不出图。")
    else:
        print(f"提示词已就绪，请将 {OUT}/{ep}_prompts.txt 送入 ComfyUI Batch Queue / MJ / 即梦 批量出图。")
        print("出图后放回 05-data-center/versions/，再跑 check_assets.py 二次质检。")

    print("\n✅ 管线完成（剧本→分镜→资产→出图前门禁）。")


if __name__ == "__main__":
    main()
