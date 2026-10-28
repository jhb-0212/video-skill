# 第三阶段：工程化监控——N8N / Coze 编排对接

> 目标：把「分镜 → 提示词 → 出图 → 质检 → 推审」串成一条自动流水线，人工只在最后审片台介入。用 N8N（自托管）或 Coze（云端）做编排，脚本只做被编排的「原子步骤」。

---

## 一、事件流转图

```
[webhook 触发：分镜表 CSV 已就绪]
        │
        ▼
┌─────────────────────────────┐
│ Step 1  分镜 → 提示词         │  storyboard_to_prompts.py
│ 产出 txt / json / comfyui    │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Step 2  出图（外部）          │  ComfyUI Batch Queue / API
│ 生成图 → versions/           │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Step 3  质检 + 过滤           │  check_assets.py
│ FaceID < 阈值 / 废片 → 打回   │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Step 4  推审                 │  审片台 HTML + 通知
│ 只推 top 20% 优质候选         │  （邮件/企微/飞书）
└─────────────────────────────┘
```

---

## 二、N8N 编排配置（自托管）

N8N 工作流用 4 个节点串联，每个节点调一个脚本（Execute Command / HTTP Request）。

### 节点 1：Webhook（触发）
- **Trigger**: `Webhook`，路径 `/storyboard-ready`
- 收到 `{"episode": "EP001"}` 触发

### 节点 2：分镜 → 提示词
- **类型**: `Execute Command`
- **命令**:
  ```bash
  cd /path/to/06-scripts && \
  python storyboard_to_prompts.py \
    "../05-data-center/episodes/EP001_storyboard.csv" \
    "../05-data-center/bible" "EP001"
  ```
- **通过条件**: 输出含 `[3/3] 批量队列` → 进 Step 3

### 节点 3：出图（对接 ComfyUI API）
- **类型**: `HTTP Request`（POST 到 ComfyUI `/prompt` 接口）
- 把 `EP001_batch.json` 逐条提交 ComfyUI，出图回调存 `versions/`

### 节点 4：质检 + 推审
- **类型**: `Execute Command`
- **命令**:
  ```bash
  python check_assets.py \
    "../05-data-center/episodes/EP001_assets.csv" \
    "../05-data-center/bible" \
    "../05-data-center/versions" \
    --profile "../05-data-center/quality-profile.json" \
    --out-dir "out"
  ```
  - 阈值（FaceID ≥ 0.90）、推审比例（top 20%）等**都在 `quality-profile.json` 里配置**（`faceid.threshold` / `push.ratio`），不是命令行参数。
- **后续**: 把 `out/review_board.html`（产出名见 `quality-profile.json` 的 `report.board_path`）通过 `Send Email` / `企业微信机器人` / `飞书 Webhook` 推给审片人

---

## 三、Coze 编排配置（云端，无服务器）

Coze 用「工作流」+「插件」实现，无需自托管：

1. **触发器**: 定时任务 / 手动触发 / 企微消息触发
2. **代码节点**: 把上面两个脚本的逻辑封装成 Coze 插件（或用「代码节点」直接贴 Python）
3. **HTTP 节点**: 调 ComfyUI API 出图
4. **条件节点**: `相似度 < 0.90` → 走「打回」分支；`通过` → 走「推审」分支
5. **消息节点**: 推审片台链接到企微/飞书群

> 注意：Coze 代码节点有沙箱限制，FaceID（InsightFace）这类重型依赖在云端跑不动，建议 **FaceID 质检留在本地 N8N 或独立服务器跑**，Coze 只做「触发 + 通知 + 流程状态管理」这类轻活。

---

## 四、分工建议（谁在哪跑）

| 环节 | 跑在哪 | 原因 |
|---|---|---|
| 分镜 → 提示词 | N8N 本地 / Coze 均可 | 纯 CPU 轻量 |
| 出图 | ComfyUI 服务器（GPU） | 需要显卡 |
| FaceID 质检 | **本地 N8N / 独立服务器** | InsightFace 重依赖，云端沙箱跑不动 |
| 废片启发式过滤 | 本地（Pillow + NumPy） | 轻量，可云端 |
| 推审 + 通知 | Coze / N8N 均可 | 纯 API 调用 |

---

## 五、门禁规则（每个节点「不过不进下一步」）

| 节点 | 门禁条件 | 不过则 |
|---|---|---|
| Step 2 分镜→提示词 | 输出 3 份文件齐全 | 中止，报「分镜表有误」 |
| Step 3 出图 | 所有镜头图生成完毕 | 重试 / 补生成缺图 |
| Step 4 质检 | FaceID ≥ 阈值 且 无废片 | 打回重绘，标记待补 |
| Step 5 推审 | 只推 top 20% | 其余留档不打扰审片人 |

---

## 六、与第二阶段的关系

- **第二阶段**（已完成）：`storyboard_to_prompts.py` 读 Excel/CSV 分镜表 → 批量 Prompt + ComfyUI batch。
- **第三阶段**（本文）：把第二阶段的两个脚本用 N8N/Coze 编排起来，加**自动质检门禁**和**人工审片台**，实现「只把 20% 优质候选推给人，80% 废片机器自动挡掉」。

两个阶段共用同一套脚本，第三阶段只是给它们加了「编排层」和「质检门禁」，不改动脚本核心逻辑。
