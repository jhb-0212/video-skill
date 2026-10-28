# 变更记录（CHANGELOG）

> 脚本/契约的变更记录。**契约破坏性变更必须标 `[breaking]`**，下游要跟着改。

## [0.2.0] - 2026-10-28（场景层升级 + 画幅分层 + 命名去撞 + CSV 权威源）

### 新增

- `06-scripts/schemas/scene_state.schema.json` + `scene_readiness.schema.json` —— SceneState（SS0-SS5）/ SceneReadiness 机读契约
- `06-scripts/scene_check.py` —— 场景专用门禁（画幅 + 状态码 + 连续性 + 可用性，退出码 0/1/2）
- `04-asset-prompts/references/scene-system.md` —— 场景体系（基准/状态分离、画幅三层铁律、权力空间、状态阶梯、失败台账）
- `05-data-center/episodes/EP001_scene_states.jsonl` + `EP001_scene_readiness.json` —— 场景状态与可用性数据
- `06-scripts/migrations/001_scene_upgrade.py` —— 存量 scenes.jsonl 升级迁移
- `SOURCE.md` —— 来源与授权登记（scene-design MIT / short-drama-image-prompts）

### 变更（[breaking]）

- `api-contracts.md`：**[breaking]** Scene 对象新增 `scene_tier`/`base_aspect`/`blocking_ref_image`/`blocking_aspect`/`power_layout`/`vertical_lanes`；新增 SceneState、SceneReadiness 对象
- `scenes.jsonl`：**[breaking]** 升级为三对象画幅结构（design plate 16:9 + blocking ref 9:16）
- `scene.schema.json`：**[breaking]** `base_aspect` enum 限制 16:9/2.35:1，`scene_tier` enum S0-S3
- `check_assets.py`：场景分支改为画幅校验（design plate 横版 ≥1920、S0/S1 blocking ref 9:16）
- `storyboard_to_prompts.py`：新增 `--aspect`（默认 9:16）、`--scene-states`、场景状态注入 + 固定锚点注入
- `csv2json.py`：**[breaking]** CSV 为权威源，JSON 为派生物（带 `_source_hash`/`_generated`），check 改字段级严格相等（去掉模糊启发式），人物列存 ID
- `engine-profiles/*.json`：新增 `aspect_presets`（character/scene_design_plate/scene_blocking/final_frame）

### 文档

- `asset-tiering.md` 场景分级加命名护栏（S0-S3 vs SS0-SS5）+ 画幅分层说明
- `prompt-templates.md` 模板四拆 A/B（design plate 16:9 / blocking ref 9:16）+ 画幅选择决策表
- `make-spec.md` 场景清单加「重要度」列；`03-storyboard/SKILL.md` 补 scene_states 产出
- `01-pipeline-orchestrator/SKILL.md` 交接表/路由表/术语表补场景项
- `versions/README.md` 补三类画幅命名规则

## [0.1.0] - 2026-10-28

### 新增（生产级工程化改造）

- `06-scripts/schemas/` —— JSON Schema 机读契约（shot/character/scene/prop/asset_call/engine_profile）
- `06-scripts/validate_data.py` —— 数据校验层（schema + 外键 + 唯一性 + 枚举 + 必填）
- `06-scripts/csv2json.py` —— CSV↔JSON 转换 + 一致性 check
- `06-scripts/migrate.py` + `migrations/` —— 数据结构迁移
- `06-scripts/tests/` —— pytest 测试框架（34 用例）+ `run_tests.py` 兜底运行器
- `06-scripts/check_env.py` —— 环境检查（可选依赖缺失报告）
- `05-data-center/quality-profile.json` —— 质量门禁阈值配置
- `06-scripts/pyproject.toml` / `requirements*.txt` —— 依赖锁定（Python 3.11）
- `Dockerfile` / `Dockerfile.gpu` / `docker-compose.yml` —— 容器化
- `06-scripts/Makefile` / `.github/workflows/ci.yml` / `n8n_pipeline_workflow.json` —— 编排
- `RUNBOOK.md` / `ADR.md` / `CHANGELOG.md` —— 运维交接

### 变更（修复假门禁）

- `check_assets.py` 重写：**[breaking]** FaceID 从 bible 读 base_ref_image 真比对（原版比的是自己恒为 1.0）；降级标 `unverified` 不静默通过；覆盖 scene/prop；输出 `report.json`；阈值进 profile
- `storyboard_to_prompts.py`：**[breaking]** `_resolve_look_delta` 按集过滤状态变体（新增 `--episode`）；参数解析改 argparse；新增 `--out-dir`；输出改名 `*_batch.json`
- `pipeline_runner.py`：**[breaking]** 集号参数化（`--episode`）；新增 `--dry-run`/`--retries`/`--timeout`；subprocess 超时重试
- `validate_data.py` storyboard 子命令支持 CSV + JSON 两种输入

### 文档

- `02-ip-script/references/make-spec.md` → 改为指针，唯一源迁至 `03-storyboard/references/make-spec.md`
- `api-contracts.md` 新增 `EngineProfile` 对象 + 章节顺延
- `04-asset-prompts` 前后端解耦口径写死

### 已知问题（数据漂移，待人工同步）

- `EP001_storyboard.csv` 与 `EP001_storyboard.json` 画面描述存在语义级修饰词差异（CSV 简写 / JSON 扩充），`csv2json.py check` 会报警，需人工决定以哪个为权威源后重新派生。
