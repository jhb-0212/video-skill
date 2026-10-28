# 资产生产全链路 · 项目目录结构

```
video-skill/
│
├── 01-pipeline-orchestrator/        # 调度层 · 总调度 / 路由表 / 字段契约
│   ├── SKILL.md
│   └── references/
│       └── api-contracts.md         # Shot / Asset 对象 JSON 字段契约
│
├── 02-ip-script/                    # 剧本层
│   ├── SKILL.md
│   └── references/
│       ├── make-spec.md             # 指针文件（唯一源见 03-storyboard）
│       ├── stage-a.md               # 阶段 A
│       ├── stage-b.md               # 阶段 B
│       ├── stage-c.md               # 阶段 C（C5 产出定妆单+简介单）
│       ├── economy.md               # 经济性
│       ├── packages.md              # 交付包
│       └── quality-modules.md       # 质量模块
│
├── 03-storyboard/                   # 分镜层
│   ├── SKILL.md                     # 分镜表 10 列标准
│   └── references/
│       └── make-spec.md             # 核心交接物（跨剧本层+分镜层）
│
├── 04-asset-prompts/                # 资产层 · 提示词生成
│   ├── SKILL.md
│   └── references/
│       ├── asset-tiering.md         # 状态隔离 / 文字政策 / DAM
│       ├── prompt-templates.md      # 七段式 / 参考图权限隔离 / 模板零
│       ├── style-recipes.md         # 词库 / 题材氛围词库
│       ├── feature-catalog.md       # 特征库
│       ├── view-spec.md             # 视图规范
│       └── examples.md              # 示例
│
├── 05-data-center/                  # 数据中台 · 结构化资产
│   ├── bible/                       # 角色/场景/道具基准（跨集一致）
│   │   ├── characters.jsonl         # CHAR-xxx + LoRA 路径 + 状态变体
│   │   ├── scenes.jsonl             # SC-xx + scene_tier + 画幅三层（design/blocking）
│   │   └── props.jsonl              # PR-xx + 关键剧情道具标记
│   ├── engine-profiles/             # 后端控制台 · 引擎参数（前端七段式不碰）
│   │   ├── engines.json             # 引擎注册表（默认引擎 + 参数 + 负面词映射）
│   │   ├── comfyui.json             # ComfyUI/SD：采样器/CFG/步数/尺寸/负面词 + aspect_presets
│   │   ├── midjourney.json          # MJ：--ar/--style/--cref 等 + aspect_presets
│   │   ├── doubao.json              # 豆包：中文负面词 + aspect_presets
│   │   ├── jimeng.json              # 即梦：中文负面词 + aspect_presets
│   │   ├── minimax_h3.json          # MiniMax H3 + aspect_presets
│   │   └── README.md                # 前后端解耦说明
│   ├── quality-profile.json         # 质量门禁阈值（FaceID 阈值/推审比例/unverified 策略）
│   ├── episodes/                    # 分集数据
│   │   ├── EP001_scenes.json        # 剧本场景拆解
│   │   ├── EP001_storyboard.json    # 分镜表（机读，CSV 派生物 + _source_hash）
│   │   ├── EP001_storyboard.csv     # 分镜表（Excel 另存，唯一人工源）
│   │   ├── EP001_assets.csv         # 资产调用清单
│   │   ├── EP001_scene_states.jsonl # 场景叙事状态（SceneState，SS0-SS5）
│   │   └── EP001_scene_readiness.json # 场景可用性门（SceneReadiness）
│   └── versions/                    # 生成图版本留存
│       └── README.md                # 三类画幅命名规则（design/blocking/state）
│
├── 06-scripts/                      # 自动化脚本层
│   ├── schemas/                     # JSON Schema 机读契约（shot/character/scene/scene_state/scene_readiness/prop/asset_call/engine_profile）
│   ├── config/mappings.yaml         # 景别/运镜/CSV 列名映射（外置可扩展）
│   ├── migrations/                  # 数据结构迁移脚本（0001 schema_version / 001 scene_upgrade）
│   ├── tests/                       # pytest 测试 + fixtures（34 用例）
│   ├── storyboard_to_prompts.py     # 分镜表 → 七段式画面描述 + 引擎参数注入 + 场景状态 + 锚点
│   ├── check_assets.py              # 真实质量门禁（FaceID 真比对/废片/场景画幅校验/report.json）
│   ├── scene_check.py               # 场景专用门禁（画幅 + 状态码 SS0-SS5 + 连续性 + 可用性）
│   ├── prompt_check.py              # 出图前编译期校验
│   ├── validate_data.py             # 数据校验层（schema + 外键 + 唯一性）
│   ├── csv2json.py                  # CSV（权威源）→ JSON（派生物 + _source_hash）+ 严格一致性 check
│   ├── migrate.py                   # 数据迁移执行器
│   ├── check_env.py                 # 环境检查（可选依赖降级报告）
│   ├── run_tests.py                 # 无 pytest 兜底测试运行器
│   ├── pipeline_runner.py           # 串联管线（集号参数化 + 重试 + dry-run + 场景门禁）
│   ├── pyproject.toml               # 依赖锁定（Python 3.11 + optional 分组）
│   ├── Makefile                     # make run EP=EP001 编排入口
│   ├── n8n_pipeline_workflow.json   # N8N 工作流（可导入）
│   ├── README.md                    # 操作手册
│   └── orchestration.md             # 编排文档
│
├── .github/workflows/ci.yml         # CI：lint → test → schema 校验 → dry-run
├── Dockerfile / Dockerfile.gpu      # 容器化（基础 + GPU 变体）
├── docker-compose.yml               # 编排 data-center + scripts
├── RUNBOOK.md                       # 运维手册（故障处理）
├── ADR.md                           # 架构决策记录
├── CHANGELOG.md                     # 变更记录（breaking 标注）
├── GOVERNANCE.md                    # 权限矩阵 + 备份恢复 + 敏感数据
├── SOURCE.md                        # 来源与授权登记（scene-design / short-drama-image-prompts）
│
└── short-drama-image-prompts/       # 参考技能（工程锁体系）
    ├── SKILL.md
    ├── references/                  # 规则分级 / REF 槽位 / 文字两层分离
    ├── scripts/
    ├── agents/
    ├── assets/
    └── examples/
```

## 数据流

```
01 调度 → 02 剧本 → 03 分镜 → 04 资产 → 05 数据中台 → 06 脚本自动化
```

## 全链路

```
剧本 → 分镜 → 资产 → 出图 → 质检 → 推审
```
