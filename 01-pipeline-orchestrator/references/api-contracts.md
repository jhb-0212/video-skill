# 各层 JSON 交换契约（API Contracts）

> 本文件是数据中台（`05-data-center`）与自动化脚本（`06-scripts`）的**唯一字段契约来源**。所有脚本读写的 JSON/JSONL/CSV，字段名、类型、必填项以本文件为准，不另编字段。
>
> 作用：让 Python 脚本 / N8N / Airflow / Coze 等编排工具**能读懂并驱动**整条管线——剧本层产结构、分镜层产镜头、资产层产资产，全靠这里定义的 `Shot` / `Asset` 对象。

---

## 一、对象总览

| 对象 | 文件落点 | 由谁产出 | 由谁消费 |
|---|---|---|---|
| `Character`（角色基准） | `05-data-center/bible/characters.jsonl` | 剧本层 C5（人物定妆单） | 分镜层、资产层、脚本 |
| `Scene`（场景基准） | `05-data-center/bible/scenes.jsonl` | 资产层 | 分镜层、脚本 |
| `SceneState`（场景叙事状态） | `05-data-center/episodes/EPxxx_scene_states.jsonl` | 分镜层（分镜后统计） | 脚本、出图 |
| `SceneReadiness`（场景可用性门） | `05-data-center/episodes/EPxxx_scene_readiness.json` | `scene_check.py` | 编排门禁 |
| `Prop`（道具基准） | `05-data-center/bible/props.jsonl` | 资产层 | 分镜层、脚本 |
| `Shot`（镜头） | `05-data-center/episodes/EP001_storyboard.json` | 分镜层 | 资产层、`storyboard_to_prompts.py` |
| `Asset`（资产调用） | `05-data-center/episodes/EP001_assets.csv` | 分镜层（分镜后统计） | 资产层判级、美术审核 |
| `EngineProfile`（引擎配置） | `05-data-center/engine-profiles/*.json` | 资产层（后端控制台） | `storyboard_to_prompts.py` 注入参数 |

> **非机读对象（人读参考）**：`05-data-center/episodes/EPxxx_scenes.json` 是剧本→分镜的「场拆解」中间产物（场号/时间/地点/人物/事件/剧本行号），**仅供人读、辅助分镜拆场，不进入任何脚本的机读链路**。机器消费的「镜头→场景」关联以 `storyboard.json` 的 `scene_id` 为准（由分镜表备注列派生），不要维护 `scenes.json` 去指望脚本会读它——它是工作底稿，不是契约对象。

> **资产清单 CSV 的单源边界（P1 修复）**：`EP001_assets.csv` 是「资产调用关系」的权威源（谁出场、多少次、多少秒、需不需要设定图、设定图文件名），**只存调用关系，不存画幅/重要度**。
> 场景的 `scene_tier`（重要度）、`base_aspect`（画幅）、`blocking_ref_image`（竖屏图）这些**资产属性**一律从 `bible/scenes.jsonl` 按 `asset_id` 反查——`check_assets.py` 的 `check_scene()` 就是这么做，避免 CSV 与 bible 重复存储同一属性导致漂移。
> 命名对齐：CSV 的 `design_file` 与 bible 的 `base_ref_image` **必须同源同名**（场景用 `SC-xx_名称_design_vN.png`，见 `versions/README.md` 命名表），禁止一套数据两个名字。
> **CSV 编码约定**：所有 CSV（分镜表、资产清单）一律以 `encoding="utf-8-sig"` 读取——现有 CSV 可能带 UTF-8 BOM（表头首列会变成 `\ufeffxxx`），用普通 `utf-8` 读会导致列名漂移、列名校验误报「缺列」。脚本层已全部统一 `utf-8-sig`，新增读 CSV 的代码必须沿用此约定。

---

## 二、Shot 对象（storyboard.json 核心）

分镜表一行 = 一个 `Shot`。全片 = `Shot[]`。

```json
{
  "episode": "EP001",
  "shot_id": "S03-05",
  "scene_id": "SC-01",
  "characters": ["CHAR-001", "CHAR-002"],
  "action": "两人在冰湖前对峙，梁大回头看老炮",
  "dialogue": "本镜无台词",
  "camera_angle": "中近景",
  "camera_movement": "固定机位",
  "duration_sec": 5,
  "lighting": "冷蓝月色，暗调高对比",
  "assets_required": ["CHAR-001", "CHAR-002", "SC-01"]
}
```

### 字段契约（每个字段的类型 + 必填 + 说明）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `episode` | string | ✅ | 集号，`EP001` 这种 |
| `shot_id` | string | ✅ | 唯一镜头号，`S03-05` = 分镜 3 第 5 镜 |
| `scene_id` | string | ✅ | 所属场景编号，指向 `scenes.jsonl` 的 `scene_id` |
| `characters` | string[] | ✅ | 出场角色 ID 数组（**存 ID 不存名字**，外貌从 `characters.jsonl` 取） |
| `action` | string | ✅ | 画面描述（只写看得见的外部动作，不写心理） |
| `dialogue` | string | ✅ | 台词；无台词**必须写 `本镜无台词`**，不许空 |
| `camera_angle` | string | ✅ | 景别：大远景/远景/大全景/全景/中景/中近景/近景/特写（可带变化如「大远景→中景」）；机位视角（俯视/仰视/平视）**不在此字段**，归机位描述 |
| `camera_movement` | string | ⚠️ | 运镜；固定机位写 `固定机位` |
| `duration_sec` | number | ✅ | 单镜秒数，3–10，默认 5 |
| `lighting` | string | ⚠️ | 光影描述，从 `style-recipes.md` 词库取 |
| `assets_required` | string[] | ✅ | 本镜需要的资产 ID 数组（人物/场景/道具） |

> **铁律**：`characters` 存 **ID**，不是名字。分镜表「人物」列只写名字给人看，落到 JSON 里必须换成 `CHAR-xxx` ID——这样脚本才能精确追查每个角色在哪些镜头出现。

---

## 三、Asset 对象（bible 三文件的基准记录）

### Character（characters.jsonl 每行）

```json
{
  "asset_id": "CHAR-001",
  "type": "char",
  "name": "梁大",
  "identity": "主角",
  "base_ref_image": "05-data-center/versions/CHAR-001_梁大_v1.png",
  "lora_path": "models/lora/liangda_v1.safetensors",
  "looks": [
    {"look_id": "V00", "desc": "基础造型：深灰工装夹克", "valid_episodes": "全片"},
    {"look_id": "V01", "desc": "夜行衣", "valid_episodes": "EP003-EP005"}
  ]
}
```

### Scene（scenes.jsonl 每行）

```json
{
  "asset_id": "SC-01",
  "type": "scene",
  "name": "董事会会议室",
  "scene_tier": "S0",
  "base_ref_image": "05-data-center/versions/SC-01_董事会_design_v1.png",
  "base_aspect": "16:9",
  "blocking_ref_image": "05-data-center/versions/SC-01_董事会_blocking_v1.png",
  "blocking_aspect": "9:16",
  "power_layout": {
    "entry": "双开玻璃门，南侧",
    "power_seat": "长桌北端主位",
    "subordinate_positions": ["长桌两侧", "门口站立位"],
    "threshold_axis": "门→桌中轴",
    "handoff_zone": "桌角文件托盘",
    "fixed_anchors": ["落地窗", "长桌", "主位椅", "门轴"]
  },
  "vertical_lanes": {
    "foreground_pressure": "桌沿/文件堆",
    "center_actor_lane": "门到桌的纵向通道",
    "background_power_anchor": "落地窗+主位椅",
    "handoff_zone": "桌角"
  },
  "day_night": "日",
  "in_out": "内",
  "lighting": "顶光冷白 + 窗侧自然光"
}
```

**画幅铁律（三条不可破）**：

1. design plate（`base_ref_image`）**不得用 9:16**，只能是 16:9 或 2.35:1 横版；
2. blocking ref（`blocking_ref_image`）**不得用 16:9**，固定 9:16 竖版；
3. 成片 frame 固定 9:16。

三类资产是**三张图，不是一张图的三种裁法**。下游出成片时，只从 blocking ref 取构图逻辑，不从 design plate 直接裁。

### Prop（props.jsonl 每行）

```json
{
  "asset_id": "PR-01",
  "type": "prop",
  "name": "陆巡",
  "category": "交通",
  "base_ref_image": "05-data-center/versions/PR-01_陆巡_v1.png",
  "key_plot": true
}
```

### 字段契约

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `asset_id` | string | ✅ | 唯一资产编号，`CHAR-`/`SC-`/`PR-`/`V-` 前缀 |
| `type` | string | ✅ | `char` / `scene` / `prop` / `voice` |
| `name` | string | ✅ | 剧本原文名字，**不改字** |
| `base_ref_image` | string | ✅ | 基准图路径（锁脸/锁场景用） |
| `lora_path` | string | ⚠️ | 仅 L0 主角有，LoRA 模型路径 |
| `looks` | array | ⚠️ | 仅 char 有：状态变体列表（`V00` 基础 + `V01…` 变体） |

### Scene 新增字段契约

| 字段 | 类型 | 必填 | 硬规则 |
|---|---|---|---|
| `scene_tier` | string | ✅ | 只能 `S0`/`S1`/`S2`/`S3`（重要度分级，**与状态码无关**） |
| `base_aspect` | string | ✅ | 只能 `16:9` 或 `2.35:1`；出现 `9:16` 即 schema 校验失败 |
| `blocking_ref_image` | string | ⚠️ | S0/S1 必填，S2/S3 可空 |
| `blocking_aspect` | string | ⚠️ | 固定 `9:16` |
| `power_layout` | object | ⚠️ | S0/S1 必填，S2/S3 可空（权力空间结构） |
| `vertical_lanes` | object | ⚠️ | S0/S1 必填，S2/S3 可空（竖屏 lane 五要素） |

> **关键**：`base_aspect` 的 `enum: ["16:9", "2.35:1"]` 写进 JSON Schema（`schemas/scene.schema.json`），不是靠人记。这是「画幅纪律」的机器落点。

---

## 三·二、SceneState 对象（场景叙事状态，分镜后统计）

> **命名去撞铁律**：`SceneState.state_code` 只能取 `SS0–SS5` 六个值（叙事状态）；`Scene.scene_tier` 只能取 `S0–S3`（重要度分级）。**两个字段永不同名、永不互转**——`S0_normal` 这类写法是错的，状态码必须是 `SS0_normal_order`。

```json
{
  "state_id": "SC-01_EP003_SS2",
  "scene_id": "SC-01",
  "episode": "EP003",
  "state_code": "SS2_humiliation",
  "valid_shots": ["S03-02", "S03-04"],
  "door_state": "半开",
  "window_state": "百叶拉下",
  "surface_traces": ["桌面有水杯印", "地面有散落纸张"],
  "light_state": "顶光压暗，窗光偏冷",
  "actor_zone": "被迫站在桌角，未入座",
  "object_positions": {"文件": "被对方压在手边"},
  "inherits_from": "SC-01_EP002_SS1",
  "next_state": "SC-01_EP004_SS3"
}
```

**state_code 封闭枚举**（写进 `schemas/scene_state.schema.json` 的 enum）：

| code | 含义 |
|---|---|
| `SS0_normal_order` | 常态秩序 |
| `SS1_pressure_setup` | 压力铺垫 |
| `SS2_humiliation` | 公开羞辱/胁迫 |
| `SS3_reveal` | 证据/身份揭示 |
| `SS4_aftermath` | 余波残留 |
| `SS5_power_reversal` | 权力反转 |

---

## 三·三、SceneReadiness 对象（视频可用性门，scene_check.py 产出）

```json
{
  "scene_id": "SC-01",
  "base_scene_image": "SC-01_..._design_v1.png",
  "motion_test": "actor_enters_and_stops_center",
  "layout_stability": "pass",
  "light_stability": "pass",
  "prop_stability": "needs_prop_lock",
  "actor_lane_read": "pass",
  "readiness_label": "needs_prop_lock",
  "repair_instruction": "文件托盘位置每镜漂移，锁定桌角坐标"
}
```

**readiness_label 封闭枚举**：`scene_video_ready` / `needs_layout_lock` / `needs_light_lock` / `needs_prop_lock` / `image_only` / `reroll_scene`。

---

## 四、EngineProfile 对象（engine-profiles 后端控制台）

> **解耦核心**：前端七段式（04-asset-prompts）只写「画面长什么样」，引擎参数（采样器/CFG/步数/画幅/尺寸/seed/负面词）全部剥离到本对象。**换引擎只改 profile，前端一个字不动。**

`engines.json` 是注册表，每个引擎的 `profile_file` 指向独立文件。字段契约如下：

```json
{
  "engine_id": "comfyui",
  "name": "ComfyUI / SD",
  "language": "en",
  "params": {
    "width": 1080,
    "height": 1920,
    "seed": -1,
    "sampler": "dpmpp_2m_karras",
    "steps": 28,
    "cfg": 6.5
  },
  "negative_map": {
    "core": "deformed hands, extra limbs, ...",
    "shot": "cropped feet, ..."
  },
  "ref_image": {
    "lock_face": "IPAdapter / ControlNet (face)"
  }
}
```

### 字段契约

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `engine_id` | string | ✅ | 唯一引擎号：`comfyui`/`midjourney`/`doubao`/`jimeng`/`minimax_h3` |
| `name` | string | ✅ | 引擎显示名 |
| `language` | string | ✅ | 负面词/描述语言：`en`（英文）/ `zh`（中文）/ `zh_en`（中英） |
| `params` | object | ✅ | 出图参数：画幅/尺寸/seed/采样器/CFG/步数等，**随引擎而定，不强求统一** |
| `negative_map` | object | ✅ | 负面词分组，key 为用途：`core`/`shot`/`portrait`/`multi_view`/`photoreal`/`fx_scene`/`d1_donghua` |
| `ref_image` | object | ⚠️ | 该引擎的参考图入口（锁脸/锁风格/锁骨架） |

### 负面词分组（negative_map 的 key 约定）

| key | 用途 | 何时拼入 |
|---|---|---|
| `core` | 核心 10 个 | 任何图种必拼 |
| `shot` | 剧情镜追加 | 影视剧照/分镜图 |
| `portrait` | 单张定妆追加 | 定妆照 |
| `multi_view` | 多视图追加 | 多视图/模型表 |
| `photoreal` | 真人写实质感 | R2/R3 真人写实 |
| `fx_scene` | 特效/复杂场景 | 使用题材氛围词库时 |
| `d1_donghua` | 国漫压脸 | D1 国漫子档 |

> **铁律**：负面词是引擎能力（语言跟引擎走），**不写进前端七段式正文**。前端只描述「要什么」，后端按 `negative_map` 拼「规避什么」。

---

## 五、资产复用列（防重复描述）

> 落到 JSON 里，资产复用就是：**`characters` / `assets_required` 只存 ID，不重复写外貌/材质**。谁要外貌，用 ID 去 `bible/*.jsonl` 查 `base_ref_image` + `name`。
>
> 举例：分镜第 30 镜又出现梁大，`characters: ["CHAR-001"]`——**不再写「52 岁方圆脸寸头」**，外貌只在 `characters.jsonl` 里写一次。

---

## 六、脚本对契约的消费

| 脚本 | 读 | 写 | 逻辑 |
|---|---|---|---|
| `storyboard_to_prompts.py` | `EP001_storyboard.json` + `bible/*.jsonl` + `engine-profiles/*.json` | `EP001_prompts.txt` | 每个 Shot 拼装成七段式**画面描述**（前端），再从 engine-profiles 注入**参数 + 负面词**（后端） |
| `check_assets.py` | `EP001_assets.csv` + `versions/*.png` | 质检报告 | FaceID 相似度 <90% 打回 |
| `pipeline_runner.py` | 上两者 | 日志 | 串联剧本→分镜→资产→出图四环 |

---

## 七、与 Markdown 文档的关系（不重复、不打架）

- **字段规范的老家**：`make-spec.md` 第 3 节（资产清单表 3.1~3.6）仍是**人读的字段规范**，本文件是它的**机读版**——同一套字段，一个给人填、一个给脚本跑。
- **不一致时**：以 `make-spec.md` 为准（人是最终裁判），脚本契约随它同步改。
- **编号一致性**：`CHAR-xxx` / `SC-xxx` / `PR-xxx` 的编号规则见 `make-spec.md` 3.6 命名规则，脚本不另定编号。
