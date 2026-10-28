# 场景体系（Scene System）—— 基准 / 状态 / 画幅三层 / 可用性门

> 方法论来源：scene-design skill（外部源，MIT）。
> 本文档已修正其 `--ar 9:16` 的误用：design plate 必须是 16:9，
> 9:16 只用于 blocking ref 与成片。
>
> **画幅铁律（R1，三条不可破）**：
> 1. design plate（场景设计图/全景）**不得用 9:16**，只能是 16:9 或 2.35:1 横版；
> 2. blocking ref（竖屏构图验证）**不得用 16:9**，固定 9:16 竖版；
> 3. 成片 frame 固定 9:16。
>
> design plate(16:9) / blocking ref(9:16) / 成片(9:16) 三张图，**不是一张图三种裁法**。
> 下游出成片时，只从 blocking ref 取构图逻辑，不从 design plate 直接裁。

---

## 一、基准 vs 状态（Scene / SceneState 的边界）

场景资产分两层建模，**永不混用**：

| 层 | 对象 | 回答什么问题 | 变不变 |
|---|---|---|---|
| 基准（Scene） | `bible/scenes.jsonl` | 这个场景「长什么样」：布局、锚点、权力结构、光照基线 | 跨集不变（除非场景本身重搭） |
| 状态（SceneState） | `episodes/EPxxx_scene_states.jsonl` | 某集某镜「此刻什么状态」：门窗、痕迹、光、演员区 | 每集每镜可变 |

**命名去撞（R3）**：

- 场景**重要度分级**保留 `S0–S3`（`asset-tiering.md`，决定做多深）；
- 场景**叙事状态阶梯**改 `SS0–SS5`（本文件，Scene State）；
- 两个编号**永不同名、永不互转**。状态码写法 `SC-01@SS2`，绝不写 `SC-01@S2`。

---

## 二、权力空间机制表（机构类型 → 固定锚点 → 动作杠杆）

> 用于 design plate（16:9）的设计。机构空间都有「权力结构」，不是中性的盒子。

| 机构类型 | 固定锚点（fixed_anchors） | 动作杠杆（action lever） |
|---|---|---|
| 董事会/会议室 | 长桌、主位椅、落地窗、门轴、文件托盘 | 谁坐主位、谁站着、文件被谁压住 |
| 办公室/权力走廊 | 工位区、主管独立间、饮水机、打卡机 | 谁在格子间、谁有独立间 |
| 家宅/客厅 | 沙发主位、餐桌、电视、门 | 谁坐主位、谁站着、谁靠门 |
| 营地/野外 | 火堆、帐篷、折叠桌、车 | 谁靠火堆、谁站在边缘 |
| 公路/追逐 | 道路中轴、车队、暗冰、错车点 | 谁在前、谁被逼停 |

**设计原则**：design plate 里「固定锚点」必须可辨认且位置稳定，否则跨镜会漂移。

---

## 三、竖屏 blocking 五要素（blocking ref，9:16）

> 竖屏 9:16 是「构图验证」，不是 design plate。五要素决定竖屏里画面怎么分层。

1. **前景压迫（foreground_pressure）**：桌沿/文件堆/炊具堆，压在画面下三分之一，制造纵深与压迫感；
2. **中景通道（center_actor_lane）**：演员走位的纵向通道，必须干净可读；
3. **背景锚点（background_power_anchor）**：落地窗+主位椅 / 雪山+冰湖，权力/环境锚点；
4. **门槛轴（threshold_axis）**：门→桌中轴，权力的物理轴线；
5. **交接区（handoff_zone）**：桌角文件托盘等，动作交接的物理落点。

对应字段：`Scene.vertical_lanes`（`foreground_pressure` / `center_actor_lane` / `background_power_anchor` / `handoff_zone`）。

---

## 四、状态阶梯 SS0–SS5

> 场景叙事状态的封闭枚举（写进 `schemas/scene_state.schema.json`）。

| code | 含义 |
|---|---|
| `SS0_normal_order` | 常态秩序 |
| `SS1_pressure_setup` | 压力铺垫 |
| `SS2_humiliation` | 公开羞辱/胁迫 |
| `SS3_reveal` | 证据/身份揭示 |
| `SS4_aftermath` | 余波残留 |
| `SS5_power_reversal` | 权力反转 |

**铁律**：`SceneState.state_code` 只能取上表六个值；`Scene.scene_tier` 只能用 `S0–S3`。两者永不混用同一套编号。

---

## 五、连续性账本字段（SceneState 每行必须能回答）

一个 SceneState 状态条目要交代清「从哪来、变什么、到哪去、牵连谁」：

| 字段 | 说明 |
|---|---|
| `base identity`（base identity） | scene_id + 基准，不可变 |
| `door_state` | 门的状态（开/半开/关） |
| `window_state` | 窗的状态（拉下百叶/开/关） |
| `surface_traces` | 表面痕迹（桌面水杯印、地面散落纸张） |
| `light_state` | 光的状态（顶光压暗、窗光偏冷） |
| `actor_zone` | 演员区（被迫站桌角、未入座） |
| `object_positions` | 关键物位置（文件被对方压在手边） |
| `camera_axis`（相机轴） | 本状态下的拍摄轴（隐式，从 valid_shots 反推） |
| `inherits_from` | 从哪个 state 继承 |
| `next_state` | 下一状态 |
| `valid_shots` | 哪些镜头属于此状态 |

---

## 六、视频可用性门（SceneReadiness）

场景要能拍成视频，光有 design plate 不够，要过「可用性门」（`scene_check.py` 产出）：

**motion test 7 项**：actor_enters_and_stops_center（演员进入并停中心）/ layout_stability / light_stability / prop_stability / actor_lane_read / 以及门窗开合状态一致性、锚点位置稳定性。

**6 个 readiness 标签（封闭枚举）**：

| label | 含义 |
|---|---|
| `scene_video_ready` | 场景可直接进视频 |
| `needs_layout_lock` | 布局未锁定，需修 |
| `needs_light_lock` | 光照未锁定 |
| `needs_prop_lock` | 道具位置漂移，需锁坐标 |
| `image_only` | 只能当静图，不能进视频 |
| `reroll_scene` | 场景需重出 |

---

## 七、场景失败台账（常见翻车，逐条对照）

| 失败模式 | 症状 | 对策 |
|---|---|---|
| luxury-hotel drift | 场景越画越奢华，脱离设定 | 锁 fixed_anchors + 材质逻辑 |
| empty pretty room | 好看但空，没有权力结构 | 补 power_layout 的 entry/power_seat/subordinate_positions |
| horizontal-room drift | 横版构图思维，竖屏用不上 | 出 blocking ref（9:16）验证 |
| door-window drift | 门窗每镜状态不一致 | 用 SceneState.door_state/window_state 锁定 |
| prop disappears | 道具每镜消失/换位 | prop_stability=needs_prop_lock，锁坐标 |
| light resets | 光每镜重设 | light_state 锁定 |
| American-in-name-only | 场景名义上是某国但无该国特征 | 锚点里加地域性固定锚 |

---

## 八、画幅选择决策（出图时用哪个模板）

| 任务 | 模板 | 画幅 |
|---|---|---|
| 场景库 / 场景设计图 | 模板四 A（design plate） | 16:9 |
| 竖屏 blocking 验证 | 模板四 B（blocking ref） | 9:16 |
| 成片单镜出图 | 模板一/二 + SceneState | 9:16 |

**铁律**：模板四 A 禁止 `--ar 9:16`；模板四 B 禁止 `--ar 16:9`。
