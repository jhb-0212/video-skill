# 引擎配置层（后端控制台）

> **一句话**：前端七段式只回答「画面长什么样」，本目录回答「用什么引擎、什么参数、什么负面词出图」。

## 为什么要有这一层

「禁引擎参数」不是限制创作，而是把**资产解耦成真正的通用生产资料**。核心矛盾是：

- **出图质量**（画面内容、光影、构图、风格）→ 由 04-asset-prompts 的七段式负责，**模型无关**。
- **出图方式**（采样器、CFG、步数、画幅、尺寸、seed、负面词）→ 由本目录负责，**引擎相关**。

如果把两者绑死在同一个产物里，换一个模型（比如从 ComfyUI 切到豆包）就要**改掉每一张资产的提示词**——资产库就废了。拆开之后，换引擎只改这一层的配置，前端七段式一个字都不用动。

## 目录结构

```
engine-profiles/
├── engines.json        # 引擎注册表（默认引擎 + 参数分组 + 负面词映射汇总）
├── comfyui.json        # ComfyUI / SD 后端参数（采样器/CFG/步数/尺寸/负面词）
├── midjourney.json     # Midjourney 后端参数（--ar/--style/--cref 等）
├── doubao.json         # 豆包后端参数（中文负面词）
├── jimeng.json         # 即梦后端参数
└── minimax_h3.json     # MiniMax H3 后端参数
```

## 分层边界（铁律）

| 层 | 归属 | 谁负责 | 内容 |
|---|---|---|---|
| **前端** | 04-asset-prompts | 七段式画面描述 | 图种/人物/妆造/视图/背景光/风格 |
| **后端** | engine-profiles | 引擎参数注入 | 采样器/CFG/步数/画幅/尺寸/seed/负面词 |

- **负面词算引擎能力**，归后端：SD/MJ 用英文负面词，豆包/即梦用中文负面词，语言跟引擎走。
- **换引擎 = 换 profile**，不碰前端七段式。
- **新模型接入**：在 `engines.json` 注册 + 加一个 `<engine_id>.json`，前端零改动。

## 字段契约

`engines.json` 的字段定义见 `01-pipeline-orchestrator/references/api-contracts.md` 的 `EngineProfile` 对象。要点：

- `engine_id`：唯一引擎号（`comfyui`/`midjourney`/`doubao`/`jimeng`/`minimax_h3`）
- `language`：该引擎负面词/描述的语言（`en`/`zh`/`zh_en`）
- `params`：该引擎的出图参数（采样器/CFG/步数/画幅/尺寸/seed 等）
- `negative_map`：负面词分组（`core` 核心 / `shot` 剧情镜 / `portrait` 定妆 / `multi_view` 多视图 / `photoreal` 质感 / `fx_scene` 特效 / `d1_donghua` 国漫）
- `ref_image`：该引擎的参考图入口（锁脸/锁风格/锁骨架）

## 消费方

- `06-scripts/storyboard_to_prompts.py`：读分镜表 → 产七段式**画面描述**（前端），再从 `engines.json` + 对应 profile 注入**参数 + 负面词**（后端）。
