# 版本控制目录

存放历史结果回溯（`EP001_Shot03_v1.png` / `EP001_Shot03_v2.png`）。

- 每次重绘升版本号，旧版不删，留档对比。
- 命名规则见 `make-spec.md` 3.6：`编号_名称_版本_扩展名`。
- L0 主角基准图（锁脸/LoRA 训练源）也放这里，路径写入 `bible/characters.jsonl` 的 `base_ref_image`。

## 场景三类资产命名（画幅分层）

场景资产按画幅角色分三类，**禁止混用**：

| 类型 | 命名 | 画幅 |
|---|---|---|
| design plate（场景设计图/全景） | `SC-xx_名称_design_vN.png` | 16:9 或 2.35:1 横版 |
| blocking ref（竖屏构图验证） | `SC-xx_名称_blocking_vN.png` | 9:16 竖版 |
| state 参考（某状态成片参考） | `SC-xx_名称_state-SSx_vN.png` | 9:16 竖版 |

> **禁止：把 design plate 存成 9:16**。三类资产是三张图，不是一张图的三种裁法。

