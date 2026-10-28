#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_assets.py —— 生成图质检引擎（域2 重写）：真实质量门禁。

修复域2 的所有「假门禁」问题：
    1. FaceID 真比对：从 bible/characters.jsonl 读 base_ref_image，与生成图真比对（原版比的是自己，恒为 1.0）
    2. 降级不静默：无 insightface → verification_status = "unverified"，按 quality-profile 策略处理（默认阻断）
    3. 覆盖 scene/prop：不只查 char，场景图存在性+尺寸、道具图存在性都查
    4. 机器可读报告：输出 report.json（每条 asset_id/状态/分数/原因/耗时），CI 消费
    5. 阈值外置：从 quality-profile.json 读，换项目不改代码
    6. 路径穿越防护：design_file 的 realpath 必须落在 versions 白名单根内

用法：
    python check_assets.py <assets.csv> <bible_dir> <versions_dir> [--profile quality-profile.json] [--out-dir 06-scripts/out]

退出码：0 全过（含 warn 放行）/ 1 有阻断（failed 或 unverified 阻断）。
"""

import argparse
import base64
import csv
import html
import json
import os
import re
import sys
import time

# ---------------------------------------------------------------- 依赖探测
try:
    from PIL import Image  # noqa: F401
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import numpy as np  # noqa: F401
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import insightface  # noqa: F401
    HAS_INSIGHTFACE = True
except ImportError:
    HAS_INSIGHTFACE = False


# ---------------------------------------------------------------- 配置加载
def load_profile(path=None):
    """加载 quality-profile.json；不存在则用内置默认。"""
    default = {
        "faceid": {"threshold": 0.90, "model": "buffalo_l", "det_size": [640, 640]},
        "push": {"ratio": 0.20, "min_push": 1},
        "junk": {"min_long_edge": 512, "min_file_bytes": 5120, "max_solid_std": 8.0},
        "unverified_policy": "block",
        "coverage": ["char", "scene", "prop"],
        "report": {"path": "report.json", "board_path": "review_board.html"},
    }
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        default.update(loaded)
    return default


# ---------------------------------------------------------------- FaceID
class FaceID:
    """封装 InsightFace。未装依赖时 self.app=None，比对结果标 unverified。"""

    def __init__(self, model="buffalo_l", det_size=(640, 640)):
        self.app = None
        if HAS_INSIGHTFACE:
            try:
                self.app = insightface.app.FaceAnalysis(name=model)
                self.app.prepare(ctx_id=0, det_size=det_size)
            except Exception:
                self.app = None

    def embedding(self, img_path):
        if self.app is None:
            return None
        import numpy as np
        try:
            import cv2
            img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        except Exception:
            return None
        if img is None:
            return None
        faces = self.app.get(img)
        if not faces:
            return None
        return faces[0].normed_embedding

    @staticmethod
    def cosine(a, b):
        import numpy as np
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


# ---------------------------------------------------------------- 废片启发式
def detect_junk(img_path, profile):
    reasons = []
    if not HAS_PIL:
        return reasons
    junk_cfg = profile.get("junk", {})
    try:
        from PIL import Image
        im = Image.open(img_path).convert("RGB")
        w, h = im.size
        if max(w, h) < junk_cfg.get("min_long_edge", 512):
            reasons.append("低清（长边<阈值）")
        if os.path.getsize(img_path) < junk_cfg.get("min_file_bytes", 5120):
            reasons.append("文件异常（<阈值）")
        if HAS_NUMPY:
            import numpy as np
            arr = np.asarray(im, dtype=np.uint8).reshape(-1, 3)
            if float(arr.std(axis=0).mean()) < junk_cfg.get("max_solid_std", 8.0):
                reasons.append("纯色/空白（像素标准差过低）")
    except Exception as e:
        reasons.append(f"无法读取图像（{e}）")
    return reasons


def check_version_number(filename):
    return bool(re.search(r"v\d+", filename))


def image_size(img_path):
    """读图像尺寸 (w, h)；无 PIL 或读取失败返回 (None, None)。"""
    if not HAS_PIL:
        return None, None
    try:
        from PIL import Image
        im = Image.open(img_path)
        return im.size  # (w, h)
    except Exception:
        return None, None


def check_scene(row, versions_dir, bible_refs=None):
    """场景资产画幅校验（域2 补：场景不再被跳过）。

    硬规则（画幅三层铁律）：
      - design plate（design_file）必须是 16:9 或 2.35:1 横版（宽>高），宽 ≥1920；
      - S0/S1 场景必须有 blocking ref（blocking_ref_image），且必须是 9:16 竖版（高>宽）。

    字段来源（P0 修复）：
      - design_file / asset_id / name 来自资产清单 CSV 行（CSV 是唯一人工源）；
      - scene_tier / blocking_ref_image 从 bible 的 scenes.jsonl 按 asset_id 反查——
        CSV 无这两列，若从 CSV 行读将永远拿不到，导致 blocking 门禁成为哑弹。
    """
    errs = []
    asset_id = row.get("asset_id")

    # 从 bible 反查 scene_tier / blocking_ref_image（CSV 行没有这两列）
    tier = None
    blocking = None
    if bible_refs is not None and asset_id in bible_refs:
        sc = bible_refs[asset_id]
        tier = sc.get("scene_tier")
        blocking = sc.get("blocking_ref_image")

    design = row.get("design_file") or row.get("base_ref_image")
    if not design:
        errs.append(f"[缺图] scene {asset_id} 无 design plate 路径")
        return errs

    p = safe_join(versions_dir, design)
    if p is None:
        errs.append(f"[越界] scene {asset_id} design plate 路径逃出 versions 根目录")
        return errs
    if not os.path.exists(p):
        errs.append(f"[缺图] scene {asset_id} design plate 不存在")
        return errs

    w, h = image_size(p)
    if w is not None:
        # 硬规则：design plate 必须是横版（16:9 / 2.35:1），不能是竖版
        if w <= h:
            errs.append(
                f"[画幅错误] {asset_id} design plate 是 {w}x{h}（竖版），"
                f"必须是 16:9 或 2.35:1 横版"
            )
        elif w < 1920:
            errs.append(f"[低清] {asset_id} design plate 宽 {w} < 1920")

    # S0/S1 必须有 blocking ref（9:16）
    if tier in ("S0", "S1"):
        if not blocking:
            errs.append(f"[缺 blocking] {asset_id} {tier} 缺 9:16 blocking ref")
        else:
            bp = safe_join(versions_dir, blocking)
            if bp is None:
                errs.append(f"[越界] {asset_id} blocking ref 路径越界")
            elif not os.path.exists(bp):
                errs.append(f"[缺图] {asset_id} blocking ref 不存在")
            else:
                bw, bh = image_size(bp)
                if bw is not None and bw >= bh:
                    errs.append(
                        f"[画幅错误] {asset_id} blocking ref 是 {bw}x{bh}（横版），"
                        f"必须是 9:16 竖版"
                    )
    return errs


def safe_join(versions_dir, design_file):
    """路径穿越防护：design_file 的 realpath 必须落在 versions 白名单根内。"""
    root = os.path.realpath(versions_dir)
    if not design_file:
        return None
    # 允许相对 versions 的路径，或绝对路径，但 realpath 必须在 root 内
    candidate = design_file
    if not os.path.isabs(candidate):
        candidate = os.path.join(versions_dir, candidate)
    real = os.path.realpath(candidate)
    if real == root or real.startswith(root + os.sep):
        return real
    return None  # 越界，拒绝


# ---------------------------------------------------------------- 主流程
def main():
    parser = argparse.ArgumentParser(description="生成图质检：真实质量门禁")
    parser.add_argument("assets_csv", help="资产清单 CSV")
    parser.add_argument("bible_dir", help="bible 目录（读 base_ref_image 真比对）")
    parser.add_argument("versions_dir", help="生成图存放目录")
    parser.add_argument("--profile", help="quality-profile.json 路径")
    parser.add_argument("--out-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"),
                        help="输出目录（默认 06-scripts/out/）")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    os.makedirs(args.out_dir, exist_ok=True)

    # 读 bible，建立 asset_id -> 完整记录（P0 修复：不止 base_ref_image，
    # scene 质检还需要 scene_tier / blocking_ref_image）
    bible_refs = {}
    for fn in ("characters.jsonl", "scenes.jsonl", "props.jsonl"):
        p = os.path.join(args.bible_dir, fn)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        r = json.loads(line)
                        bible_refs[r.get("asset_id")] = r

    faceid = FaceID(profile["faceid"].get("model", "buffalo_l"),
                    tuple(profile["faceid"].get("det_size", [640, 640])))

    results = []
    report_entries = []
    t_start = time.time()

    with open(args.assets_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            asset_id = row.get("asset_id", "")
            asset_type = row.get("type", "")
            name = row.get("name", "")
            design_file = row.get("design_file", "")

            # 只查 profile 声明的覆盖类型
            if asset_type not in profile.get("coverage", ["char", "scene", "prop"]):
                continue

            entry = {
                "asset_id": asset_id,
                "type": asset_type,
                "name": name,
                "design_file": design_file,
                "status": "passed",
                "score": None,
                "verification_status": "verified" if (faceid.app is not None and asset_type == "char") else "not_applicable",
                "reasons": [],
                "elapsed_ms": 0,
                "img_path": None,
            }
            t0 = time.time()

            # 0. 路径穿越防护 + 文件存在性
            img_path = safe_join(args.versions_dir, design_file)
            if img_path is None:
                entry["status"] = "failed"
                entry["reasons"].append("路径越界（design_file 逃出 versions 根目录）")
            elif not os.path.exists(img_path):
                entry["status"] = "failed"
                entry["reasons"].append("缺图（需补生成）")
            else:
                entry["img_path"] = img_path
                # 1. 版本号
                if not check_version_number(design_file):
                    entry["reasons"].append("无版本号（建议 v1/v2）")

                # 2. 废片启发式
                junk = detect_junk(img_path, profile)
                if junk:
                    entry["status"] = "failed"
                    entry["reasons"].extend(junk)
                else:
                    # 3. FaceID 真比对（仅 char；从 bible 读 base_ref_image）
                    if asset_type == "char":
                        base_ref_rec = bible_refs.get(asset_id, {})
                        base_ref = base_ref_rec.get("base_ref_image", "") if isinstance(base_ref_rec, dict) else base_ref_rec
                        base_path = safe_join(args.versions_dir, base_ref) if base_ref else None
                        if faceid.app is None:
                            entry["verification_status"] = "unverified"
                            entry["reasons"].append("未接 FaceID（依赖缺失），无法比对")
                        elif base_path is None or not os.path.exists(base_path):
                            entry["verification_status"] = "unverified"
                            entry["reasons"].append(f"基准图缺失或越界：{base_ref}")
                        else:
                            emb_gen = faceid.embedding(img_path)
                            emb_base = faceid.embedding(base_path)
                            if emb_gen is None or emb_base is None:
                                entry["verification_status"] = "unverified"
                                entry["reasons"].append("人脸检测失败（无法提取 embedding）")
                            else:
                                score = FaceID.cosine(emb_gen, emb_base)
                                entry["score"] = round(score, 4)
                                if score < profile["faceid"].get("threshold", 0.90):
                                    entry["status"] = "failed"
                                    entry["reasons"].append(f"换脸/漂移（相似度 {score:.3f} < 阈值 {profile['faceid']['threshold']}）")
                    else:
                        # scene：画幅校验 + 废片启发式；prop：只查存在性 + 版本号
                        entry["verification_status"] = "not_applicable"
                        if asset_type == "scene":
                            scene_errs = check_scene(row, args.versions_dir, bible_refs)
                            if scene_errs:
                                entry["status"] = "failed"
                                entry["reasons"].extend(scene_errs)
                            else:
                                junk = detect_junk(img_path, profile)
                                if junk:
                                    entry["status"] = "failed"
                                    entry["reasons"].extend(junk)

            # unverified 策略：默认 block（阻断转人工），不静默通过
            if entry["verification_status"] == "unverified":
                policy = profile.get("unverified_policy", "block")
                if policy == "block":
                    entry["status"] = "failed"
                    entry["reasons"].append("未验证（unverified_policy=block，转人工）")

            entry["elapsed_ms"] = int((time.time() - t0) * 1000)
            results.append(entry)
            report_entries.append(entry)

    # 排序：通过的按 score 降序；failed 排后
    passed = [r for r in results if r["status"] == "passed"]
    failed = [r for r in results if r["status"] != "passed"]
    passed.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0)))

    # 推审 top N%
    push_cfg = profile.get("push", {})
    push_count = max(push_cfg.get("min_push", 1), int(len(passed) * push_cfg.get("ratio", 0.20)))
    for i, r in enumerate(passed):
        r["priority"] = (i < push_count)

    # 输出 report.json（机器可读，CI 消费）
    report = {
        "run_id": f"check_{int(t_start)}",
        "episode": os.path.basename(args.assets_csv).split("_")[0],
        "total": len(results),
        "passed": len(passed),
        "failed": len(failed),
        "unverified": len([r for r in results if r["verification_status"] == "unverified"]),
        "threshold": profile["faceid"].get("threshold", 0.90),
        "push_count": push_count,
        "elapsed_ms": int((time.time() - t_start) * 1000),
        "entries": report_entries,
    }
    report_path = os.path.join(args.out_dir, profile.get("report", {}).get("path", "report.json"))
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 终端报告
    for r in results:
        if r["status"] != "passed":
            print(f"[{r['status']}] {r['asset_id']} {r['name']} -> {'；'.join(r['reasons'])}")
    print(f"\n共 {len(results)} 条：通过 {len(passed)}，失败/阻断 {len(failed)}"
          f"（未验证 {report['unverified']}，推审前 {push_count} 条）")
    print(f"报告 -> {report_path}")

    # 审片台 HTML（只列通过 + 未验证候选）
    board_path = os.path.join(args.out_dir, profile.get("report", {}).get("board_path", "review_board.html"))
    write_review_board(board_path, passed)
    print(f"审片台 -> {board_path}")

    # 退出码：有 failed 即阻断
    sys.exit(1 if failed else 0)


# ---------------------------------------------------------------- 审片台 HTML
def write_review_board(out_path, results):
    rows = []
    for r in results:
        img_path = r.get("img_path")
        thumb = _img_to_data_uri(img_path, max_size=256) if (HAS_PIL and img_path) else ""
        score_txt = f"{r['score']:.3f}" if r["score"] is not None else "—"
        badge = "★ 优先审" if r.get("priority") else "待审"
        badge_color = "#d4edda" if r.get("priority") else "#fff3cd"
        # HTML 转义防注入
        aid = html.escape(r["asset_id"])
        nm = html.escape(r["name"])
        df = html.escape(r["design_file"])
        rows.append(
            f'<tr><td>{thumb}</td><td>{aid}</td><td>{nm}</td>'
            f'<td>{df}</td><td>{score_txt}</td>'
            f'<td><span style="background:{badge_color};padding:2px 8px;border-radius:4px">{badge}</span></td></tr>'
        )
    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>人工审片台</title>
<style>
body{{font-family:-apple-system,'Microsoft YaHei',sans-serif;margin:24px;color:#222}}
h1{{font-size:20px}} .sub{{color:#888;font-size:13px}}
table{{border-collapse:collapse;width:100%;margin-top:16px}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left;font-size:14px}}
th{{background:#f5f5f5}}
img{{width:80px;border-radius:4px}}
</style></head><body>
<h1>人工审片台</h1>
<div class="sub">已通过自动质检的候选，按相似度降序，前 N 条标「★ 优先审」</div>
<table>
<thead><tr><th>缩略图</th><th>资产ID</th><th>名称</th><th>文件</th><th>相似度</th><th>状态</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody></table>
</body></html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)


def _img_to_data_uri(path, max_size=256):
    try:
        from PIL import Image
        import io
        im = Image.open(path).convert("RGB")
        im.thumbnail((max_size, max_size))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=70)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f'<img src="data:image/jpeg;base64,{b64}">'
    except Exception:
        return ""


if __name__ == "__main__":
    main()
