# 权限矩阵与数据治理（域10）

## 谁能改什么

| 数据 | 谁能改 | 谁能审 | 说明 |
|---|---|---|---|
| `05-data-center/bible/*.jsonl`（角色/场景/道具基准） | 美术主管 / 资产 owner | 导演/监制 | 改基准 = 全片受影响，需评审 |
| `05-data-center/engine-profiles/*.json`（引擎参数） | 技术美术 / 操机员 | 技术主管 | 换引擎只改这里，不影响画面描述 |
| `05-data-center/episodes/*.csv`（分镜表人工源） | 分镜师 / 美术 | 导演 | CSV 是人工权威源 |
| `05-data-center/episodes/*.json`（分镜表派生物） | 脚本（csv2json） | — | 不手改，由 CSV 派生 |
| `05-data-center/quality-profile.json`（质检阈值） | 技术主管 | — | 换项目/集数调阈值 |
| `06-scripts/schemas/*.schema.json`（字段契约） | 架构/技术主管 | — | 改契约 = breaking，需 ADR + 迁移 |
| `05-data-center/versions/`（生成图） | 出图工具 | 美术/导演（审片台） | 只增不删，旧版留档 |

## 备份 / 恢复

- **备份对象**：`05-data-center/`（bible + episodes + engine-profiles + quality-profile + versions）
- **策略**：每日增量备份 `bible/`（跨集一致性的根），每周全量备份整个 `05-data-center/`。
- **恢复演练**：每季度一次——从备份恢复到临时目录，跑 `python validate_data.py all <恢复目录>` 确认数据完整。
- **迁移状态**：`.migration_state.json` 记录已应用的迁移，恢复时一并恢复，避免重复迁移。

## 敏感数据

- 若 `bible/*.jsonl` 含真实人脸照片路径（换脸用真人原型），`versions/` 需加访问控制——真人照片不在 git 里提交（已在 `.gitignore` 排除 `versions/*.png`）。
- 接 ComfyUI API / 模型下载的密钥走环境变量或 secrets（`$env.WEBHOOK_URL` 等），**不写进任何文件**。
