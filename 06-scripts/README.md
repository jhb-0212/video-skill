# 第二阶段：半自动化——Excel 分镜表 → 批量 Prompt → ComfyUI 批量出图

> 目标：美术在 Excel 里填好分镜表，一条命令把整集转成几百条可出图的 Prompt，丢进 ComfyUI 批量队列自动跑。人只做「填表 + 挑风格词 + 审片」，机械转换交给脚本。

> **第三阶段入口**：质检自动过滤废片 + 人工审片台 + N8N/Coze 编排，见 `orchestration.md`。

---

## 一、整体流程（4 步）

```
① 填分镜表（Excel 10 列） ──> 另存为 CSV
② 跑脚本 storyboard_to_prompts.py ──> 产出 txt + json + ComfyUI batch 三份
③ 跑脚本 prompt_check.py ──> 出图前编译期校验（结构漏洞/文字矛盾/命名越权/引擎越界）
④ 把 batch 送 ComfyUI Batch Queue 批量出图 ──> check_assets.py 出图后质检 ──> 人工审片
```

> 一条命令跑全程：`python pipeline_runner.py`（自动串 ②③④ 三步 + 门禁）。

---

## 二、第 1 步：填分镜表（Excel）

分镜表 10 列，字段与 `03-storyboard/SKILL.md` 完全一致：

| 列 | 说明 | 示例 |
|---|---|---|
| 分镜号 | 该分镜编号（S01/S02…） | S01 |
| 镜头号 | 该分镜内第几个镜头 | 1 |
| 建议时长 | 单镜秒数，纯数字 | 8 |
| 画面描述 | 这镜拍什么（一句话） | 傍晚雪域峡谷公路泥泞土石路蜿蜒入山 |
| 人物 | 出场角色，顿号分隔（写名字或 CHAR 编号都可） | 梁大、梁小 |
| 台词 | 谁说什么，无则写「本镜无台词」 | 梁小：咱这连个大屏都没有 |
| 运镜 | 主运镜（见 03-storyboard 5.4 运镜词库） | 固定机位 / 航拍缓推 |
| 构图 | 画面怎么摆 | 双人同框 / 车队居中 |
| 景别 | 拍多大范围（单景别或带变化「大远景→中景」） | 中近景 |
| 备注 | 资产编号（场景/道具），供资产统计 | SC-03 车内 |

**填表铁律**：
- 一个单元格里**不要用英文逗号 `,`**（CSV 用逗号分隔），内容里要分隔就用顿号 `、` 或空格。
- 台词里多个人的对话用 `/` 分隔（`梁小：…／梁大：…`）。
- 景别从「大远景/远景/大全景/全景/中景/中近景/近景/特写」里选；带运镜变化写「大远景→中景」，脚本取末端景别定焦段。

模板见 `05-data-center/episodes/EP001_storyboard.csv`（已带 5 镜示例）。

---

## 三、第 2 步：跑脚本

```bash
cd 06-scripts
python storyboard_to_prompts.py "../05-data-center/episodes/EP001_storyboard.csv" "../05-data-center/bible" "EP001"
# 指定目标引擎（默认读 engine-profiles 的 default_engine）：
python storyboard_to_prompts.py "../05-data-center/episodes/EP001_storyboard.csv" "../05-data-center/bible" "EP001" --engine comfyui
```

产出 3 份文件（前缀 EP001 可换）：

| 文件 | 用途 |
|---|---|
| `EP001_prompts.txt` | 每镜一条画面描述 + 注入的负面词，人读 / 手动粘贴 |
| `EP001_prompts.json` | 结构化提示词（shot_id / positive / negative / engine），脚本可再加工 |
| `EP001_batch.json` | 批量队列（positive + negative + engine_params 分离） |

**脚本做了什么**（前端画面描述 + 后端引擎参数，彻底解耦）：
1. 景别 → 镜头类型 + 焦段（大远景→extreme wide shot 24mm、近景→close-up 85mm…）
2. 运镜 → 镜头语言（固定机位→static shot、航拍缓推→aerial push-in…）
3. 人物 → 只写名字 + 锁脸声明（外貌从 bible 基准图取，**不重写长相**）
4. 状态变体 → 从 bible 的 `looks` 里取非基础造型的 delta（换装/受伤自动带出）
5. 参考图权限隔离 → 自动声明「只控脸，不带入服装/背景/光影」

**后端控制台（`05-data-center/engine-profiles/`）注入**：
6. 负面词 → 按引擎的 `negative_map` 拼（`core` 核心 10 个 + `shot` 剧情镜组），语言跟引擎走（豆包/即梦用中文）
7. 出图参数 → 采样器 / CFG / 步数 / 画幅 / 尺寸 / seed，从 `<engine_id>.json` 的 `params` 注入，**前端画面描述不含任何引擎参数**

> **换引擎只改 profile**：`--engine doubao` 就切中文负面词 + 豆包参数，前端七段式画面描述一字不动。

---

## 三·五、第 2.5 步：出图前编译期校验（prompt_check.py）

> 把废片挡在出图之前，比出图后靠 FaceID 兜底便宜得多。对应 04-asset-prompts 的「出图前自检量表」的机器化版。

```bash
python prompt_check.py EP001_prompts.json "../05-data-center/bible" [--engine MJ]
```

**校验 5 项**（命中即报 error/warning）：

| 校验项 | 级别 | 抓什么 |
|---|---|---|
| 引擎参数越界 | ✗ error | `--ar`/`--cref`/`(word:1.2)` 等与 `--engine` 声明不符（未声明引擎则任何专属参数都算越界） |
| 文字政策矛盾 | ✗ error | 「牌匾写着『青梧殿』」+「不要任何文字」同时出现 |
| 命名越权 | ✗ error | 人物列用了无语义命名（`1`/`站位`）或不在 bible 登记 |
| 参考图隔离缺失 | ⚠ warn | 引用了参考图但没写「仅允许提供/严禁带入」边界 |
| 负面词缺失 | ⚠ warn | 既无 negative 字段、正文也无规避措辞 |

退出码：`0` 全过 / `2` 仅警告（放行）/ `1` 有 error（阻断）。`--engine MJ/SD` 可声明目标引擎，允许该引擎专属参数、但仍拦其它引擎的越界参数。

---

## 四、第 4 步：ComfyUI 批量出图 + 质检

1. 把 `EP001_batch.json` 送入 ComfyUI Batch Queue（或用其 API 批量提交）。
2. 出图后存到 `05-data-center/versions/`（文件名带 `_v1`/`_v2` 版本号）。
3. 跑质检：
   ```bash
   python check_assets.py "../05-data-center/episodes/EP001_assets.csv" "../05-data-center/bible" "../05-data-center/versions" --profile "../05-data-center/quality-profile.json"
   ```
   - 缺图 → 提示补生成
   - 无版本号 → 警告
   - 接入 InsightFace 后，L0 主角相似度 < 0.90 自动打回

---

## 五、脚本职责边界（重要）

- 脚本只做**机械转换 + 门禁**：分镜数据 → 画面描述（前端）+ 引擎参数（后端，从 engine-profiles 注入）。
- **风格词/氛围词**（`style-recipes.md` 题材氛围词库）脚本**不自动填**——那段是「出好图」的艺术判断，留给美术按镜挑选填入。
- 脚本产出的提示词里「背景与光影」是**占位符**，美术出图前要补这一句。

一句话：脚本保证「不出错」（锁脸、不换脸、焦段对、负面词齐、引擎参数从后端注入），美术保证「出好图」（挑风格、补氛围）。
