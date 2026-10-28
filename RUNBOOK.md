# 运维手册（RUNBOOK）

> 常见故障的处理步骤。生产跑几十集时，先查这里，别从头排查。

## 1. FaceID 装不上（insightface / onnxruntime 安装失败）

**症状**：`check_assets.py` 报「未接 FaceID（依赖缺失）」，或 `pip install insightface` 失败。

**处理**：
1. 先跑 `python check_env.py` 确认缺哪个依赖。
2. 确认 Python 版本：insightface 只支持特定版本，建议 3.11（见 `.python-version`）。
3. 分开装（不要一次全装）：先 `onnxruntime`，再 `opencv-python`，最后 `insightface`。
4. 若 GPU 环境，用 `onnxruntime-gpu`（见 `Dockerfile.gpu`）。
5. **降级兜底**：装不上不阻断核心管线——`check_assets.py` 会把结果标 `unverified`，按 `quality-profile.json` 的 `unverified_policy`（默认 `block` 转人工）处理。若临时要放行，改 policy 为 `warn`（生产禁用 `pass`）。

## 2. 某一步失败、管线中止

**症状**：`pipeline_runner.py` 报 `[门禁失败]`。

**处理**：
1. 看是哪一步：数据校验 / 提示词 / 编译校验 / 质检。
2. **数据校验失败** → 看报的「外键缺失 / asset_id 重复 / 缺列」，去修 `bible/*.jsonl` 或分镜表，重跑 `python validate_data.py all 05-data-center`。
3. **编译校验失败** → 看 `prompt_check.py` 的 error（引擎越界/文字矛盾/命名越权），修提示词或分镜表。
4. **质检失败** → 看 `out/report.json` 的 failed 条目，缺图就补生成，换脸就重绘。

## 3. 数据不一致（CSV 与 JSON 漂移）

**症状**：`csv2json.py check` 报「不一致」。

**处理**：
1. 判断哪个是权威源（CSV 人工编辑 / JSON 脚本派生）。
2. 用 `python csv2json.py to-json <csv> <out.json>` 从 CSV 重新派生 JSON。
3. 或 `to-csv` 反向导出。
4. 重跑 `check` 确认一致。

## 4. 资产图缺失 / 版本号缺失

**症状**：`check_assets.py` 报「缺图」「无版本号」。

**处理**：
1. 缺图 → 补生成对应资产的定妆图/设定图，放回 `05-data-center/versions/`。
2. 无版本号 → 文件名补 `_v1`/`_v2`（命名规则见 `make-spec.md` 3.6）。

## 5. 结构变更导致旧数据读不了

**症状**：加了新字段后，旧 jsonl 校验失败。

**处理**：
1. 在 `06-scripts/migrations/` 写迁移脚本（`0002_<描述>.py`，实现 `upgrade(data_dir)`）。
2. 跑 `python migrate.py 05-data-center`。
3. 更新 `schemas/*.schema.json` 的 `schema_version`。
