---
name: pipeline-orchestrator
description: 资产生产全链路总调度。把「剧本 → 分镜 → 资产 → 出图」四环串成一张导航图，定义每一环交什么、验什么、下一步用谁。用户不知道该从哪个 skill 开始时，先看这里。Use when the user asks about the overall pipeline, what to do next, or how the three skills connect.
agent_created: true
---

# 资产生产全链路总调度（pipeline-orchestrator）

> 本 skill **不含任何生产逻辑**——不写剧本、不做分镜、不产提示词。只做三件事：全链路图、交接表、路由表。

## 目录 ↔ skill 映射（工程化目录树）

| 目录 | skill name | 链路位置 |
|---|---|---|
| `01-pipeline-orchestrator/` | `pipeline-orchestrator` | 调度层（本文件） |
| `02-ip-script/` | `ip-script-pipeline` | ① 剧本层 |
| `03-storyboard/` | `storyboard-table` | ② 分镜层 |
| `04-asset-prompts/` | `character-design-sheet` | ③ 资产层 |
| `05-data-center/` | —（数据，非 skill） | 数据中台 |
| `06-scripts/` | —（脚本，非 skill） | 自动化脚本 |

> 字段契约（JSON 交换格式）见 `references/api-contracts.md`；数据/脚本层结构见下方「八、数据中台与脚本层」。

---


## 一、全链路图

```
① 剧本层 ip-script-pipeline
└─ 产出：剧本定稿 + 人物定妆单 + 简介单
↓ 交接
② 分镜层 storyboard-table
└─ 产出：分镜表（10 列）+ 资产清单表（分镜后统计）
↓ 交接
③ 资产层 character-design-sheet
└─ 产出：定妆照/多视图/三视图/色卡 + 提示词
↓ 交接
④ 生成层（外部工具：MJ / SD / 即梦 / ComfyUI）
└─ 产出：图片 / 视频
```

> **两个入口**：①从零改编 → 从阶段 0 进；②已有剧本 → 直接从 C5 提取进（跳过阶段 0/A/B/C1~C4）。详见 `ip-script-pipeline` 的「两个入口」。

---

## 二、交接表（每个交接点：交什么、验什么）

| 交接点 | 交什么 | 验什么（不过不进下一环） |
|---|---|---|
| ①→② | 剧本定稿 + 人物定妆单（15 字段）+ 简介单（5 部分） | 定妆单每字段填满？简介单五部分齐？ |
| ②→③ | 分镜表（10 列）+ 资产清单表（四子表 + 汇总 + 命名规则）+ `EPxxx_scene_states.jsonl`（S0/S1 场景的状态） | 每镜写「本镜无台词」？同一分镜景别有递进？备注列有资产？资产清单四子表填满？S0/S1 场景状态码写 `SC-xx@SSx`？ |
| ③→④ | 提示词（七段式）+ 参考图（定妆照/场景图） | 提示词有负面词？参考图锁脸了？ |

---

## 三、路由表（用户说什么 → 进哪个 skill 的哪一步）

| 用户说 | 进哪个 skill | 从哪开始 |
|---|---|---|
| 「把小说改成剧本」 | `ip-script-pipeline` | 阶段 0 |
| 「我已经有剧本了，接下来怎么做」 | `ip-script-pipeline` → `storyboard-table` | **从 C5 提取切入**（出人物定妆单 + 简介单）→ 分镜 |
| 「写先导片」 | `ip-script-pipeline` | 阶段 B |
| 「扩展成分集」 | `ip-script-pipeline` | 阶段 C |
| 「做分镜表」 | `storyboard-table` | 从头 |
| 「出资产清单」 | `storyboard-table` | 分镜表定稿后，统计产出 |
| 「出角色定妆照」 | `character-design-sheet` | 分支 A |
| 「出多视图/三视图」 | `character-design-sheet` | 分支 B/F |
| 「出场景/道具」 | `character-design-sheet` | 分支 H/I |
| 「出场景设计 / 场景库 / 竖屏 blocking / 场景状态」 | `character-design-sheet` | 读 `scene-system.md`（画幅三层铁律 + 权力空间 + 状态阶梯） |
| 「出提示词」 | `character-design-sheet` | 模板一~五 |
| 「我要做暗黑哥特 / 赛博朋克 / 国风古韵风」 | `character-design-sheet` | 读取 `style-recipes.md` 第五节「题材氛围词库」，挑对应风格、套子档 |

---

## 四、资产清单表（全链路唯一出处）

> **字段规范、命名规则、汇总表以 `ip-script-pipeline/references/make-spec.md` 第 3 节为准**（严格按《3_资产清单表_规范与模板》的 3.1~3.6）。
>
> **产出时机（A1）**：**由 `storyboard-table` 在分镜表定稿后统计产出**。原因——「出场镜头数 / 累计时长 / 镜头号」是镜头数据，剧本里数不出来，只有分镜表才有。剧本层 C5 不产资产清单，只产「人物定妆单 + 简介单」两件。
>
> **预算预判**：不靠资产清单，靠人物定妆单的「身份定位」字段（主角/配角/反派/见证者/群演，已隐含资产量级）。

---

## 五、三个生产 skill 的入口

| skill | 链路位置 | 上游 | 下游 |
|---|---|---|---|
| `ip-script-pipeline` | ① 剧本层 | 网文 IP | `storyboard-table` |
| `storyboard-table` | ② 分镜层 | `ip-script-pipeline` | `character-design-sheet` |
| `character-design-sheet` | ③ 资产层 | `storyboard-table` | 生成层 |

---

## 六、术语统一

| 术语 | 统一叫法 | 不叫 |
|---|---|---|
| 资产清单 | **资产清单表** | 资产清单、资产表 |
| 人物定妆单 | **人物定妆单** | 定妆单、人物卡 |
| 分镜表 | **分镜表** | 镜头表、shot list |
| 提示词 | **提示词（七段式）** | prompt、17 段式（若指 character-design-sheet 的模板） |
| 交接物 | **交接物** | 交付物、接口文件 |
| design plate | **design plate（场景设计图，16:9）** | 场景全景、横版设定 |
| blocking ref | **blocking ref（竖屏构图验证，9:16）** | 竖屏参考、9:16 场景图 |

---

## 七、百集级重工业管线架构（百集级必读）

当项目达到几十集、上百集时，仅靠 Markdown 文件维持一致性必崩。团队需建立：

1. **资产数据库（JSONL/Excel）**：将 `make-spec` 表格转化为结构化数据，用脚本追查每套 Look 的生效集数。
2. **模型侧外挂**：L0 主角必须训练 LoRA；复杂动作必须 ControlNet 锁骨架。
3. **自动化质检与后期**：跑图后必须用脚本（FaceID）校验人脸相似度（<90%打回），牌匾告示强制后期加字（AE/PS）。

---

## 八、数据中台与脚本层（工程化落地）

> 从「文档驱动」升级到「数据 + 脚本驱动」——百集级必须引入数据层（`05-data-center`）和脚本层（`06-scripts`）。字段契约见 `references/api-contracts.md`。

### 目录结构

```
05-data-center/                 # 数据中台
├── bible/                      # 开发圣经/设定库（基准资料）
│   ├── characters.jsonl        # 角色基准（姓名、三视图、LoRA 路径、状态变体）
│   ├── scenes.jsonl            # 场景基准（全景、光照）
│   └── props.jsonl             # 道具基准
├── episodes/                   # 分集数据
│   ├── EP001_scenes.json       # 剧本场景拆解
│   ├── EP001_storyboard.json   # 分镜表（镜头号、角色ID、动作、背景）
│   └── EP001_assets.csv        # 本集资产调用清单（供美术审核）
└── versions/                   # 版本控制与历史回溯

06-scripts/                     # 自动化脚本层
├── storyboard_to_prompts.py    # 读 storyboard.json 自动拼装 Prompt
├── check_assets.py             # FaceID 校验生成图与基准图相似度
└── pipeline_runner.py          # 串联管线（可用 N8N/Airflow 替代）
```

### 三个脚本的职责

| 脚本 | 读什么 | 产什么 | 何时跑 |
|---|---|---|---|
| `storyboard_to_prompts.py` | `EP001_storyboard.json` + `bible/*.jsonl` | `EP001_prompts.txt`（七段式提示词骨架） | 分镜表定稿后 |
| `check_assets.py` | `EP001_assets.csv` + `versions/*.png` | 质检报告（缺图/版本号/待审） | 出图后、二次质检时 |
| `pipeline_runner.py` | 上两者 | 管线日志 | 全链路串联时 |

> **脚本只做「机械转换 + 门禁」**，不产艺术——词库/负面词/风格词栈仍在 `04-asset-prompts` 的 `prompt-templates.md` + `style-recipes.md`。脚本把「分镜表的镜头数据」转成「提示词骨架」，美术/操机员再按模板补风格词。

### 实施路线（三阶段）

1. **第一阶段（手工原型验证）**：不急着写代码。先拿一个主角手动跑一遍——写定妆单 → 训练 LoRA → 写分镜表 → 用「权限隔离的七段式」写提示词 → 出图。验证这套 `make-spec` + `prompt-templates` 出的图是否「不崩且好看」。
2. **第二阶段（半自动化）**：用 `storyboard_to_prompts.py` 把 Excel 填的分镜表一键转成几百条 Prompt，丢进 ComfyUI Batch Queue 批量跑。
3. **第三阶段（工程化监控）**：接入 N8N/Coze 编排，跑 `check_assets.py` 自动过滤废片（大脸崩/乱码字/缺手脚），只把 20% 优质候选推人工审片台，确认可用图存入 `05-data-center` 对应集数文件夹。
