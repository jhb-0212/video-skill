# 七段式提示词模板

任何「人物定妆 / 角色设定图」的 prompt 都按以下七段组织。缺一段，模型就可能在那一处自由发挥导致翻车。

## 速查表（先读这个，半页）

| 任务 | 用哪个模板 | 位置 |
|---|---|---|
| 提示词写了但没生效（权重/词序/长度问题） | 提示词工程三原则（A1/A2/A3） | 下文「提示词工程三原则」 |
| 单张定妆照 | 模板一 | 下文「模板一」 |
| 多视图角色设定图 | 模板二（+ 参考图版开头） | 下文「模板二」 |
| 角色模型表/技术设定图 | 模板三 | 下文「模板三」 |
| 场景全景设定 | 模板四 | 下文「模板四」 |
| 道具三视图 | 模板五 | 下文「模板五」 |
| 负面提示词 | 负面词清单（通用/单张/质感类/多视图） | 下文「负面提示词清单」 |
| 翻车了怎么改 | 翻车点对照表 | 文末 |

**七段骨架**：`[1 图种] + [2 人物] + [3 妆造/服装] + [4 视图清单] + [5 排版] + [6 背景/光] + [7 风格/质感]`（段数按场景裁剪，单张用 3~5 段、多视图才 6~8 段）。

> 要具体模板正文 / 词栈，再往下读对应小节。

---

## 前置强制校验（写任何 prompt 前必过，缺一项拒绝执行）

> 连续剧/大型制作里，**没有参考图就写提示词 = 必然漂移**。动手前先确认两项硬条件齐全，缺一不产：

1. **参考图人像（只控脸）**：必须提供基准身份图（`bible/characters.jsonl` 的 `base_ref_image`），只控脸型/五官比例/骨相。
2. **构图图（只控框架）**：必须提供构图参考（分镜表的景别/运镜/构图信息，或构图参考图），只控画面怎么摆的框架。

**校验规则**：
- 缺参考图人像 → **拒绝执行 / 拒绝生成**，提示用户先补基准图（先出定妆照锁定，再做后续）。
- 缺构图图 → **拒绝执行**，提示用户先补分镜表构图信息或构图参考图。
- 有参考图但没写隔离声明 → 按「参考图权限隔离」补上（只控脸、不带入服装/背景）。
- 用「模板零：拼装指令」时，四要素（锁脸图 + 基础身份数据 + 当前变体状态 + 当前动作环境）**一个不能少**。

> 一句话：**没锁脸、没构图，就别出图**。宁可前面慢一步补基准图，不后面整批返工。

---

## 详表（需要时再往下读）

## 提示词工程三原则（A1 权重 / A2 词序 / A3 长度，写任何 prompt 前先看）

> 这节是提示词工程的「第一性原理」。规则写得再好，如果模型没给那条词足够权重、或词被截断，等于没写。

### A1 权重语法：强调哪个词，就得会加权

「规则写了但没生效」最常见的根因是**没加权**——写了「纯白背景」，但模型把 90% 权重给了人物，背景就飘成浅灰。

| 平台 | 语法 | 示例 |
|---|---|---|
| MJ V6/V7 | `word::2`（越靠前权重越高，局部加权用 `::`） | `pure white background::2, character portrait...` |
| SD / ComfyUI | `(word:1.3)` 括号加权，`[word]` 降权 | `(pure white background:1.4), (no shadows:1.3)` |
| 豆包 / 即梦 / 通义 / 文心 | 自然语言「重点是×× / 必须是×× / 绝对不要××」 | 「背景必须是纯白色，绝对不能有任何灰色或阴影」 |
| 通用原则 | 靠前 = 权重高；同一段内重复 2 次 = 加权 | 纯白背景写在第 6 段开头，比塞在末尾有效 |

**铁律**：图级硬约束（纯白底、不换脸、全身不裁脚）必须在 prompt **最前 50 字内**出现，不能塞在中后段。

### A2 词序原则：按模型注意力排序，不按人类阅读习惯

模型的注意力对**前 20% token 权重最高，后面衰减**。模板的「图种→人物→妆造→视图→排版→背景光→风格」是人类阅读顺序，不是模型注意力顺序。要把关键约束往前放：

- **最前 50 字**：图种 + 图级硬约束（不换脸、16:9、纯白底、无重叠）——决定「模型先建立什么框架」。
- **前 30%**：人物核心特征（年龄/性别/脸型/眼鼻唇）——决定「像不像」。
- **中段**：妆造、视图清单。
- **后段**：排版、背景光、风格质感——这些是「修饰层」，权重可以低。
- **负面词不要塞在正文末尾**（很多模型会截断），单独用 negative 字段。

> 反面示例：把「不换脸」写在提示词第 500 字——模型生成时早就忘了，出图必然换脸。

### A3 长度适配：超限 = 截断 = 白写

不同平台单条提示词有硬上限，超了后半段被截断，用户却以为「写了就生效」。

| 平台 | 单条上限 | 应对策略 |
|---|---|---|
| SD 1.5 / SDXL（标准 CLIP） | 约 77 token / 60 英文词 | 只保留前 40% 核心词，长描述拆 2~3 条用 prompt weighting 合并；或换 BLIP/CLIP 长描述模型（SDXL 支持 2×77） |
| MJ V6/V7 | 约 6000 字符 | 可较长，但后 30% 权重明显衰减，核心约束前置 |
| 豆包 / 即梦 / 通义 | 约 2000 字 | 自然语言可长，但避免堆砌同义形容词 |
| 中文模型（文心） | 约 1000 字 | 更短，只保留核心 5 段 |

**长提示词裁剪口诀**：砍修饰词、砍重复词、砍可叠词，保留「图种 + 脸 + 服装 + 视图 + 背景 + 风格」这 6 项。

---

## 核心矛盾与化解（先读这节）

角色设定里常有一组互相打架的词，直接写进 prompt 会让 AI「精神分裂」。动手前先识别并化解：

| 矛盾 | 为什么打架 | 化解方式 |
|---|---|---|
| **纯白背景 vs 侧逆光/轮廓光** | 侧逆光需要暗背景才显轮廓，纯白底下会糊、衣服边缘发灰过曝 | 定妆照坚持纯白背景时，**砍掉侧逆光/轮廓光**，改「正面柔和均匀光、无轮廓光」；要轮廓光就改浅灰渐变影棚背景，二者不可兼得 |
| **站姿松垮 vs 挺拔/清贵** | 「松垮」易画成弓背含胸，「挺拔」易画成军姿 | 用**几何姿态描述**替代情绪词：「脊柱直立、肩线放松不过度前倾、重心略偏一侧、双手自然垂放」；negative 里双向夹击 `slouching / hunched / rigid / military stance` |
| **气质反差（吊儿郎当 vs 清贵 / 机警 vs 茫然）** | 多组气质词并列会让模型各取一半 | **禁止写抽象气质词**（清贵/落拓/机灵/疏离都是 AI 画不出的空话）。把反差收敛成「眼神 + 表情」两个具体动作：如「眼睛没看向镜头、眼珠微微偏一侧、视线朝下」+「左边嘴角翘一点、眉毛微挑、下巴微收」，让"疏离+机灵"靠动作体现，而非堆词。翻译对照表见 `feature-catalog.md` 末尾 |

## 百集制作生死线：参考图权限隔离

连续剧中，绝不能笼统地对 AI 说“参考这张图”。必须在 prompt 里显式声明隔离边界：

- **给基础身份照**：`参考图A仅允许提供：脸型、五官比例、骨相。严禁带入：图A中的发型、服装、背景、光影。`
- **给场景空镜**：`参考图B仅允许提供：构图透视、光源方向。严禁带入：图B里的临时道具、人群、文字。`
- **给道具特写**：`参考图C仅允许提供：材质质感。严禁带入：图C里的形状、文字、背景。`

如果不写隔离，AI 就会把背景里的杂物、文字、甚至别人的衣服一起抄到你的新图里。

### REF 槽位：一张参考图只答一个问题（借鉴 `short-drama-image-prompts`）

光写「参考图 A 只控脸」还不够硬——要给它一个**稳定槽位 + 封闭用途词表**，逐字写死：

```
REF-<槽位>（顺序：<n>）· <项目相对路径>《<中文名称>》（用途：<用途>；控制：<范围>；不得控制：<范围>）
```

**用途是封闭词表，只能取这 9 个之一**：`身份 / 造型状态 / 地理 / 构图 / 尺度 / 效果 / 起始帧 / 结束帧 / 风格`。

- **一张图只答一个问题**——要答两件事就拆成两个槽位，禁止写「全参考」。
- **资产板通常只用到前六个**（身份/造型状态/地理/构图/尺度/效果）；`起始帧` 和 `结束帧` 属于镜头，不属于资产板。
- **调整顺序不改变槽位语义**；换图时在同一槽位明确修订路径，不把旧图的控制边界静默转给新图。
- **示例**：`REF-1（顺序：1）· bible/characters.jsonl#CHAR-001《梁大基准》（用途：身份；控制：脸型/五官比例/骨相；不得控制：发型/服装/背景/光影）`

**关键约束（三种参考图各守边界）**：
- **身份参考**不自动决定姿势、构图或临时造型；
- **构图/尺度参考**只借用占比、机位所在侧、留白或相对尺度，不带入图中人物与事件；
- **效果参考**只控制已接受目标的形态/范围，不让非目标对象一起消失、复制或变形。

## 光影与背景的固定搭配（避免自相矛盾）

| 背景 | 允许的光 | 禁止的光 |
|---|---|---|
| 纯白背景 | 正面柔和均匀光、平光 | 侧逆光、轮廓光、硬光、强阴影 |
| 浅灰渐变影棚背景 | 柔和主光 + 侧逆轮廓光 | 硬光、杂乱光影 |

**本技能默认纯白背景 → 默认砍掉侧逆光。** 除非用户明确要「电影感轮廓光」，才切换到浅灰渐变影棚背景并保留轮廓光。

摄影语言（85mm f1.4 / 浅景深 / 伦勃朗光 / 蝴蝶光 / 侧逆光 / 体积光 / 胶片颗粒）及其允许的背景条件见 `references/style-recipes.md` 第四节。写 prompt 时先定背景，再选该背景允许的光效，二者必须匹配——纯白底配侧逆光仍是红线。

## 布光词汇：按「要比较什么」选，不按身份/题材套（借鉴 `short-drama-image-prompts`）

> 上面的「背景 → 光效」是**反自相矛盾的底线**；这一节是**选光的正逻辑**——先问这张图要让下游比较什么，再选光。尤其做定妆图/参考板时，光的职责是「让识别特征可比较」，不是「好看」。

先确定这张板必须让下游比较什么——骨骼体积、表面材质、外轮廓与体量、服装层次，还是状态痕迹——再从下表选：

| 光型 | 让什么可比较 | 压掉什么 |
|---|---|---|
| 均匀正面光（平光） | 五官相对位置、妆面、服色与图案 | 颧骨、鼻梁、下颌等体积起伏 |
| 侧光 / 高位斜侧光 | 明暗交界线两侧的骨骼体积与轮廓起伏 | 暗侧细节；同时放大不对称 |
| 顶光 | 眼窝、鼻下、颌下的纵向结构关系 | 暗区中的识别细节与服装层次 |
| 底光 | （反转日常明暗）非常规体积读法 | 常规结构读法，**做识别板时不可用** |
| 大面积柔光 | 材质纹理、肤质、布料表面状态 | 形状边界与轮廓锐度 |
| 小面积硬光 | 反射差异、磨损、镜面高光与工艺痕迹 | 过渡信息；放大瑕疵与形变 |
| 轮廓光 / 逆光边缘光 | 外轮廓、发型剪影、服装廓形与前后分离 | 面部识别信息，**不单独承担身份板** |
| 场景内实际光源 | 状态板与环境内参考板的光向可核对性 | 中性比较条件，需与场景已接受光向一致 |

**解耦声明（反刻板印象）**：以上词汇只按「本图必须让人比较什么」选择，**不按性别、年龄、贫富或题材标签映射**。同一光型可用于任何角色。若项目里出现「女性一律柔光、男性一律侧光」这类默认，那是未经证据的模板化，先删除再按用途重选。

> 一句话：**「纯白底平光」是「要比五官/服色」时的 craft_default；但若这张图要比的是「骨相体积」，就该换成侧光/高位斜侧光**（此时可配浅灰渐变影棚背景，见上方光影表）。选光先回答「比什么」，再决定「用什么光 + 什么背景」。

## 模型适配（前端七段式 / 后端控制台解耦）

> **核心口径**：上面七段式是「**前端画面描述**」，只回答「画面长什么样」——模型无关，**不写死任何引擎参数**。采样器 / CFG / 步数 / 画幅 / 尺寸 / seed / 负面词这些「用什么引擎、什么参数出图」的能力，全部剥离到「**后端控制台**」`05-data-center/engine-profiles/`，由脚本注入。**换引擎只改 profile，前端一个字不动**——这才是资产「通用生产资料」的本质。
>
> 「禁引擎参数」不是限制创作，而是**解耦**：你在前端尽情用七段式写画面，参数全部交给后端，资产库才能无缝适配未来任何一款新出的 AI 模型。

**负面词也算引擎能力，随引擎走**（语言跟引擎走）：SD/MJ 用英文负面词、豆包/即梦用中文负面词。负面词分组（`core`/`shot`/`portrait`/`multi_view`/`photoreal`/`fx_scene`/`d1_donghua`）见 `05-data-center/engine-profiles/engines.json` 的 `negative_map`，前端只描述「要什么」，后端按分组拼「规避什么」。

- **Midjourney V6** 对英文关键词服从度远高于中文长段落；英文版用**关键词堆叠**（逗号分隔），不要照搬中文长句语法。MJ 参数（`--ar 9:16`/`--style raw`/换脸 `--iw`）在 `engine-profiles/midjourney.json`。
- **Stable Diffusion** 用英文 + negative prompt 效果最好；采样器/CFG/步数在 `engine-profiles/comfyui.json`。
- **MiniMax H3** 中英文均可，英文结构词（构图/裁切类）仍建议英文。
- **中文友好模型（豆包/即梦/通义万相/文心一格等）**：用中文自然语言 + 中文负面词，**不写 `--iw`/`--style raw`/`--ar`**；英文术语换成白话（`flat studio lighting`→「纯白背景、光线均匀柔和、无阴影」）。
- **不确定模型时**：中英双份都给，参数只写通用项（画幅、风格、同一种子），不写任何模型专属参数。

> **单人单张交付 vs 批量出图**：单人单张时把「画面描述 + 参数」合并写给人看没问题；但落到数据中台 + 脚本批量出图时，**前端只存画面描述（七段式）、后端只存引擎参数（engine-profiles）**，别把参数焊死在每张资产的正文里。

## 七段结构

```
[1 图种] + [2 人物] + [3 妆造/服装] + [4 视图清单] + [5 排版] + [6 背景/光] + [7 风格/质感]
```

### 各段含义与必写要点

| 段 | 作用 | 必写要点 |
|---|---|---|
| 1 图种 | 锁定「设定图」而非「海报/剧照」 | 角色设定图 / character design sheet / 定妆照 / 技术设定图 |
| 2 人物 | 性别年龄长相气质 | 年龄、脸型、眼、鼻、唇、眉、肤色，以及**眼神（看哪/睁多大）+ 表情（嘴角/眉/下颌怎么做）+ 姿态（肩/背/重心/手脚怎么放）**——形容词可留作定方向，但必须紧跟具体动作拆解 |
| 3 妆造/服装 | 发型 + 服饰 + 配饰 | 发型细节、服装款式颜色、材质、磨损感、是否戴眼镜 |
| 4 视图清单 | 告诉模型要几个格子、各是什么 | 逐条列出每个视图，不要只写「多视图」 |
| 5 排版 | 布局方式 | 整齐排列、几行、等大等距、不重叠，视图间靠留白分隔、不画网格线/框线 |
| 6 背景/光 | 定妆图要纯白底平光 | 纯白背景、平光无阴影（不要灰色、不要剧情场景） |
| 7 风格/质感 | 写实度与细节 | 2D / 3D / 真人写实（三选一，见下）+ 清晰度、纹理 |

---

## 三种人物风格（第 7 段必选其一）

人物风格决定整张图的呈现方式，生成前必须确定。三种风格互相独立，别混用：

| 风格 | 中文关键词 | 英文关键词 | 适合 |
|---|---|---|---|
| **2D** | 二维插画、扁平/厚涂、动漫、赛璐璐、水彩/漫画风 | 2D illustration, flat / painterly, anime, cel shading, comic style | 动漫、插画、漫画、海报 |
| **3D** | 三维渲染、CG、次世代、三渲二、PBR 材质 | 3D render, CG, next-gen, toon shading, PBR material | 游戏、动画、3D 建模展示 |
| **真人写实** | 写实摄影、电影级、真实皮肤纹理、8K | photorealistic, cinematic photography, realistic skin texture, 8K | 影视定妆照、真人剧照 |

> **3D 技术精度统一高精度质感词**：本 skill 的 3D 资产统一走高精度 CG 质感 + 真实材质反射 + 电影级光影层次 + 8K，L0~L3 全部不降档。**技术精度和风格词栈是两层**：BJD 走高精度渲染但不加写实词；2D 走高完成度但不加 3D 渲染词（见 `style-recipes.md` 技术精度节）。

**写法要求**：

- 第 7 段开头先写清风格类型，再写该风格的质感细节。
- 举例（风格词替换进模板）：
  - 2D：「2D 插画，厚涂，赛璐璐上色，线条干净利落」
  - 3D：「3D 渲染，次世代 PBR 材质，三渲二，柔和天光」
  - 真人写实：「真人写实摄影，电影级质感，真实皮肤纹理，8K」
- **不要混用**：别写「2D + 写实皮肤」，别写「动漫 + 8K 摄影」，会导致风格打架。
- 模型默认（用户未指定）时：**单张定妆照 / 多视图设定图默认「真人写实」**（本技能原模板即写实路线）；用户说「动漫风/插画/卡通风」→ 切 2D；说「3D/CG/游戏」→ 切 3D。

英文版在 prompt 末尾（或最前）加对应风格词，其余结构不变。

**子档扩展**：三大类下各有子档（真人写实 R1 / R2 / R3；3D D1 国漫温婉（方向按骨相+光自定）/ D2 CG 游戏写实 / D3 BJD 半写实；2D T1 赛璐璐 / T2 厚涂）。第 7 段不要只写一句风格词，应按子档贴入中英词栈 + 配套负面词 + 背景光约束，完整词栈见 `references/style-recipes.md`。**3D 子档优先只贴 L1 核心词栈**（约 30 字），贴全段反而丢材质。**3D 国漫（D1）尤其要写具体骨相**——只写「五官精致」会出通用脸，写到「脸型 + 眼型」才锁得住；负面词必压 `generic donghua face / western features / silicone skin`（见 `feature-catalog.md` 核心原则「骨相具体化」）。选不准时：定妆照/多视图默认 R1；「动漫」→ T1；「3D/CG/游戏」→ D2；「国风 3D」→ D1（方向由骨相+光+色温匹配决定，示例见 D1 节）。

---

## 模板零：拼装指令（美术只需输入四要素即可直接出图）

> 连续剧的 prompt 是拼装出来的，不要每次从零写。美术/操机员**只需输入下面四个要素**，就能直接出图：

```
[锁脸图]         （拿基础身份图做参考图，强锁脸型，禁止带入底图服装/背景）
[基础身份数据]   （从 make-spec 的基础身份复制：ID + 三维视图 + LoRA 锁死的脸型/五官/骨相）
[当前变体状态]   （从 make-spec 的 Delta 复制：深色夜行衣，左肩缠着渗血的布条）
[当前动作环境]   （本镜动作 + 背景光影：蹲伏在屋顶，破庙内景，伦勃朗光，冷蓝月色）
```

（示例）

> 角色设定图，9:16竖版。**（基础身份）**青年男性，23岁，窄长脸，桃花眼，黑短发。**（状态变体）**换穿深色夜行衣，左肩缠着渗血的布条。**（动作）**正蹲伏在屋顶，眼神向下看。**（隔离约束）**参考图A仅提供脸型，严禁带入图A的服装和背景；背景纯白，平光。绝不允许出现文字、乱码。

> 角色设定图，9:16竖版。**（基础身份）**青年男性，23岁，窄长脸，桃花眼，黑短发。**（状态变体）**换穿深色夜行衣，左肩缠着渗血的布条。**（动作）**正蹲伏在屋顶，眼神向下看。**（隔离约束）**参考图A仅提供脸型，严禁带入图A的服装和背景；背景纯白，平光。绝不允许出现文字、乱码。

## 模板一：单张定妆照（9:16 竖版 / 16:9 横版可选）

> **E5 说明**：下面是**填空版骨架**（方括号 `[...]` 是占位符，对照填写）；写完长什么样，看 `examples.md` 案例二的**完整示例版**。填空版用来对照填、示例版用来看成品，两者用途不同。

### 中文

> **背景说明**：模板默认「纯白背景」是 R1 干净影棚的默认。**切 R2 呼吸感时**，把「背景纯白、无渐变」替换为「浅灰影棚 #B8B8B8 + 柔和主光 + 侧逆轮廓光」——R2 的侧逆光需要浅灰底才成立，纯白底配侧逆光是红线（见 `prompt-templates.md` 光影表）。
>
> 人物定妆照，[画幅：9:16 竖版 / 16:9 横版，按用户指定]。[人物：年龄性别、脸型、眼鼻唇眉、肤色、气质表情]。[发型]。[服装：款式/颜色/材质/磨损感]。[姿态：脊柱直立、肩线放松不过度前倾、重心略偏一侧、双手自然垂放，身体微侧]。光影：正面柔和均匀主光，无侧逆光、无轮廓光、无投影。背景纯白、无渐变、无其他颜色。[风格：2D 插画 / 3D 渲染 / 真人写实摄影，三选一]。[按风格补质感：真人写实→真实皮肤纹理、8K / 3D→PBR 材质 / 2D→赛璐璐上色]。

### 英文（关键词堆叠，MJ V6 友好）

> Character portrait, [aspect ratio: 9:16 vertical / 16:9 landscape], close full-body shot, character fills the frame vertically, head near top edge, feet near bottom edge, minimal headroom and legroom, no cropping. [Character: age, gender, face shape, eyes nose lips brows, skin tone, expression]. [Hairstyle]. [Outfit: style/color/material/wear]. Standing front, body slightly turned, upright spine, relaxed shoulders, slight weight shift, hands relaxed at sides, not slouching, not rigid. Soft even frontal lighting, no rim light, no backlight, no shadows. Pure white background, no gradient, solid color. [Style: 2D illustration / 3D render / photorealistic, choose one]. [Quality per style: photorealistic→realistic skin texture, 8K / 3D→PBR material / 2D→cel shading].

### 全身图专用补丁（必加）

全身景有两个相反的风险，需同时用措辞化解：

1. **裁脚**：全身景极易裁掉脚部。
2. **人物太小（变远景）**：加了「完整入画 + 占 70%」后，模型可能把人物缩成远景小点。

对应写法：

> 从头到脚完整入画，脚底和鞋子完整可见，脚下留出地面空间，绝不裁切脚部，人物约占画面高度 70%。近景全身照（close full body shot），人物在画面中占比大、细节清晰，而非远景小点。

英文关键词（**注意：别用 `full figure occupies 70% of frame`**，具体数字会被模型误解成「画一个占 70% 高度的矩形框」，反而缩图/出构图线）：`close full-body shot`（拉近距离）、`character fills the frame vertically`（填满竖框）、`head near top edge, feet near bottom edge`（头顶贴顶边、脚贴底边）、`minimal headroom and legroom`（头顶脚下留白最少）、`no cropping`（不裁切）。

> **B1 说明**：中文「占画面 70%」可保留（中文模型对百分比理解 OK），但英文改成「minimal headroom and legroom」这类几何描述更可靠。

---

## 模板二：多视图角色设定图（横版 16:9）

> **一致性约束放在 prompt 最开头**——在描述任何视图之前先锚定「不换脸、不漂移」，让模型把这条当作最高优先级。

### 中文

> **所有视图保持同一张脸、同一发型、同一服装、同一配色、同一五官比例，绝对一致，只扩展视角，不换脸、不改妆造、不漂移。** 角色设定图，多角度拼贴排版，横版 16:9，全图纯白底，无重叠、无遮挡、无明显分割线。
>
> 【人物】[年龄性别、脸型、眼鼻唇眉、肤色、胡须（精确到八字胡/山羊胡/络腮胡）]。[眼神：看哪里、睁多大]。[表情：嘴角/眉/下颌怎么做]。[姿态：肩/背/重心/手脚怎么放——形容词可留作定方向，但必须紧跟具体动作拆解]。
>
> 【妆造】[头饰/帽子 + 服装款式颜色材质 + 内衬 + 腰带配饰]。
>
> 【视图清单】头部四视图：四个头像等大等距、双眼睁开、状态一致。正脸、侧45°、侧90°、背面后脑。身体四视图：均颈部以下、不要头部。正面、45°、90°、背面。姿势视图：坐姿、蹲姿、站立仰视全身、站立俯视全身。细节特写（按需 0~3 个，均居中占满整格）：[按角色辨识度挑部位，没有可省略]。
>
> 【排版】画面左右两列分区：左列上下两行（第一行面部头部四视图，第二行身体四视图），右列上下两行（第一行姿势视图，第二行细节特写），所有视图等大等距、不重叠、靠留白分隔，不画网格线、不画框线、不画分隔线。
>
> 【背景/光】纯白背景、无渐变、无其他颜色，全程平光均匀照明、不产生明暗阴影、所有视图光影统一。
>
> 【风格】[三选一：写实影视定妆照 / 3D 渲染 / 2D 插画]，高清晰度，[按风格补质感：写实→织物纹理、皮肤纹理 / 3D→PBR 材质 / 2D→赛璐璐上色、干净线稿]。

> **参数（生成设置，不写进正文）**：整一张图固定同一个 seed（种子），不要反复随机刷新。

### 参考图版（有定妆照参考图时，加在 prompt 最前，替换上面的开头句）

> 用参考图片生成人物多视图，保持人物的绝对一致——同一张脸、同一发型、同一服装、同一配色、同一五官比例，只扩展视角，不换脸、不改妆造、不漂移。角色设定图，多角度拼贴排版，横版 16:9，全图纯白底，无重叠、无遮挡、无明显分割线。

> Using the reference image, generate a multi-view character sheet, keep the character absolutely consistent — same face, same hairstyle, same outfit, same color scheme, same facial proportions, only expand the viewing angles, no face swap, no makeup or costume change, no drift. Character design sheet, multi-view collage layout, 16:9 landscape, pure white background over the whole image, no overlap, no occlusion, no visible split lines.

### 英文

> Keep all views with the same face, same hairstyle, same outfit, same color scheme, same facial proportions, absolutely consistent, only expand the viewing angles, no face swap, no makeup or costume change, no drift. Character design sheet, multi-view collage layout, 16:9 landscape, pure white background over the whole image, no overlap, no occlusion, no visible split lines. [Character: age, gender, face, eyes, brows, skin, facial hair (precise), expression]. [Costume: headwear + garment style/color/material + inner layer + accessories]. Views: head four views, four heads equal size, both eyes open, consistent eye state, front / three-quarter / profile / back-of-head; body four views, all neck-down no head, front / three-quarter / profile / back; pose views, sitting / squatting / standing low-angle full body / standing high-angle full body; detail close-ups, 0-3 items as needed each centered filling its cell, [pick identifiable parts, may omit]. Layout: split into left and right columns; left column two rows (row 1 = head close-ups, row 2 = body views); right column two rows (row 1 = pose views, row 2 = detail close-ups); all views equal size and evenly spaced, no overlap, separated by white space only. Low angle shot: camera placed below the feet looking upward, from feet to top of head, full body in frame; high angle bird's-eye shot: camera placed directly above the head looking straight down, from top of head to feet, full body in frame. Pure white background, no gradient, no other colors, flat studio lighting, no shadows, no light and dark shading, uniform lighting across all views. [Style: photorealistic film costume / 3D render / 2D illustration, choose one], high detail, [quality per style: photorealistic→fabric texture, matte finish / 3D→PBR material / 2D→cel shading, clean lineart].

> **参数（生成设置，不写进正文）**：same seed for the entire image, do not reroll.

---

## 模板三：角色模型表 / 技术设定图（纯色背景 + 无文字）

与多视图设定图的差异：**纯色背景、无投影、无文字标签、平光**，通常左右两列分区（左列两行 + 右列两行）。

### 中文

> 角色技术设定图，角色模型表，正交设定图，全部内容生成在同一张 16:9 横版画布内，不拆图不拼接。画面左右两列分区：左列上下两行，右列上下两行，所有视图等大等距、比例一致、不重叠、不遮挡，**视图之间靠留白自然分隔，不画网格线、不画框线、不画分隔线**，背景纯白、无渐变、无其他颜色，不要任何光影效果（纯平光均匀照明、无投影无阴影无高光无轮廓光无环境光），无任何文字标签。
>
> 左列第一行：面部四视图：四个头像等大等距、双眼睁开。正脸、侧 45°、侧 90°、背面后脑。
>
> 左列第二行：身体四视图：均颈部以下、不要头部。正面、45°、90°、背面。
>
> 右列第一行：姿势视图：坐姿、蹲姿、站立仰视全身、站立俯视全身。
>
> 右列第二行：细节特写（按需 0~3 个，均居中占满整格）：[按角色辨识度挑部位，没有可省略]。
>
> 【风格】[三选一：写实影视定妆照 / 3D 渲染 / 2D 插画]，正交设定图（无透视），高清晰度，[按风格补质感：写实→织物纹理、皮肤纹理 / 3D→PBR 材质 / 2D→赛璐璐上色、干净线稿]。

---

## 画幅选择决策（场景资产三类，先看这张表）

> **画幅铁律**：design plate 禁止 9:16；blocking ref 禁止 16:9；成片固定 9:16。三类资产是三张图，不是一张图三种裁法（详见 `scene-system.md` 文首）。

| 任务 | 用哪个模板 | 画幅 |
|---|---|---|
| 场景库 / 场景设计图 | 模板四 A | 16:9（或 2.35:1） |
| 竖屏 blocking 验证 | 模板四 B | 9:16 |
| 成片单镜出图 | 模板一/二 + SceneState | 9:16 |

**铁律**：模板四 A 禁止 `--ar 9:16`；模板四 B 禁止 `--ar 16:9`。

---

## 模板四 A：场景设计图（design plate，16:9）

> 场景全景设计图，横版 16:9（或 2.35:1），是「空间布局 + 权力结构」的母版，不是竖屏成片。S0 补多角度/拆解，S2/S3 只出单张（见 `asset-tiering.md` 场景分级）。

### 中文

> 场景设计图，16:9 横版，[空间类型与布局：地理位置、主体建筑/空间格局、大小纵深]。[权力空间结构：入口 entry / 中心 center / 主位 power seat / 从属位置 subordinate positions / 交接区 handoff zone]。[固定锚点 fixed anchors：落地窗、长桌、主位椅、门轴等，位置稳定可辨认]。[光源与方向：顶光/侧光/自然光 + 方向与氛围]。[色彩与材质逻辑：主材质、主色调、配色卡]。[风格：真人写实制作设计图]，无人物，演员走位通道清晰，前景/中景/背景纵深分明，接近正交可读，完整空间布局一目了然，高清晰度。

### 英文

> Scene design plate, 16:9 horizontal, [space type and layout], [power layout: entry / center / power seat / subordinate positions / handoff zone], [fixed anchors], [light source and direction], [color and material logic], realistic production design plate, practical shootable space, no people, clear floor path for actors, foreground / midground / background depth, orthographic-friendly, full spatial layout readable, high detail. --ar 16:9

---

## 模板四 B：竖屏 blocking 参考（blocking ref，9:16）

> 竖屏 9:16 构图验证，基于 design plate 的竖屏走位/分层验证，**不是 design plate 的裁切**。

### 中文

> 竖屏 9:16 blocking 参考图，基于 [@场景标签] 的 design plate，中景演员通道干净可读，前景压迫物压在下三分之一，背景权力锚点可辨认，门槛轴可见，[双人对峙走位（如适用）]，真人写实，电影级质感。

### 英文

> Vertical 9:16 blocking reference, based on [@SceneTag] design plate, central actor lane clear, foreground pressure object frames lower third, background power anchor readable, threshold axis visible, [two-character confrontation lane if applicable], photorealistic, cinematic. --ar 9:16

### 补充（S0 才做）

- **多角度**：平视 + 俯视 + 局部近景，2~3 个角度，每个角度单独成图或分块，别一张图塞满（场景同多视图拆图规则）。
- **关键结构拆解**：仅拆「独立可分离结构」（主体建筑/主要陈设分区），禁假拆解（判定法同人物，见 `asset-tiering.md`），标尺寸/配色。
- **材质/配色卡**：S0/S1 标配色卡，材质样卡 ≤5 类。

---

## 模板五：道具三视图（P0 · 白底平光）

> 道具线按「图种 + 主体材质 + 三视图清单 + 尺寸比例 + 配色 + 风格」骨架组织。P0 做三视图，P1 正/侧面，P2/P3 单张或文字（见 `asset-tiering.md` 道具分级）。

### 中文

> 道具三视图，[道具主体/材质：名称、形状、材质、颜色、关键结构/纹样/铭文]。三个视图同一画布内水平排布、等大等距、不重叠、靠留白分隔、不画网格线框线：正面、侧面、背面。[尺寸比例：与角色或已知参照物的比例关系]。图底部标注配色卡：[一排色块，每块 Hex + 色名 + 对应部件]。纯白背景、无渐变、平光均匀照明、无阴影。正交视图、无透视。[风格：2D 线稿 / 3D PBR 渲染，打版建模不选真人写实]。

### 英文

> Prop three-view sheet, [prop subject/material: name, shape, material, color, key structure/pattern/inscription]. Three views on one canvas, arranged horizontally, equal size, evenly spaced, no overlap, separated by white space, no grid lines or border frames: front, side, back. [Scale: size ratio relative to character or known reference]. Color palette at the bottom: [row of swatches, each with hex + color name + part]. Pure white background, no gradient, flat even lighting, no shadows. Orthographic view, no perspective. [Style: 2D lineart / 3D PBR render; for pattern-making or modeling, do not use photorealistic].

### 补充（P0 才做）

- **关键结构/铭文特写**：纹样、铭文、机关等辨识度特写，居中占满整格。
- **使用态参考**：手持/持握姿态，标注与角色的比例关系。
- **材质/配色卡**：P0/P1 标配色卡，材质样卡 ≤5 类。

---

## 负面提示词清单（Negative Prompt）

配负面提示词，压住这些高频翻车。按图种勾选相关项。

**负面词优先级（A6：先保证核心生效，再按模型能力加补充）**：负面词也受长度限制（SD 同样 77 token），超了就截断、后面的词无效。所以按「核心 10 个必写 + 补充按需」两级组织，**先写核心、再按图种/模型加补充**：

```
【核心必写 10 个】（任何图种都先写这 10 个）
deformed hands, extra limbs, bad anatomy, blurry, low quality, watermark, text, logo, signature, inconsistent face

【单张定妆照追加 5 个】
cropped feet, cut off legs, missing feet, half body, head cut off

【多视图追加 10 个】
different faces, inconsistent hairstyle, different outfit, split line, grid line, border frame, gray background, gradient background, shadow, wandering eyes

【真人写实追加 5 个】（R2/R3 必加）
plastic skin, over-smoothed skin, flawless fake face, dead eyes, stiff facial expression

【补充 30+ 个】（平台支持长负面词时再加，见下方完整清单）
```

原则：**先保证核心 10 个生效，再按模型能力加补充词**，不要一上来就甩 50 个。

### 通用（所有图种）

```
extra limbs, extra fingers, deformed hands, bad anatomy, blurry, low quality, watermark, text, logo, signature
```

### 单张定妆照（9:16 竖版）追加

```
cropped feet, cut off legs, missing feet, half body, head cut off
```

### 真人写实·质感类追加（R2 呼吸感 / R3 剧情纪实必加）

治「塑料感 / 假脸 / 僵硬」——这是真人写实风格最易翻的车，通用组压不住。

```
plastic skin, ceramic smooth skin, over-smoothed skin, flawless fake face, porcelain doll skin, AI-distorted look, over-perfect unrealistic texture, dead eyes, vacant stare, stiff facial expression, stiff floating limbs, physically impossible pose, unnatural motion, clean featureless background, no ambient depth
```

中文版（中文模型用）：

```
塑料感皮肤、陶瓷般光滑肌肤、过度磨皮、无瑕假脸、AI 失真感、过度完美的不真实质感、眼神空洞无神、面部表情僵硬、肢体僵硬漂浮、动作不符合物理逻辑、干净无层次的背景
```

### 多视图 / 模型表追加

```
different faces, inconsistent face, different hairstyle, inconsistent hairstyle, messy hair, uneven sideburns, different outfit, split line, grid line, border frame, gray background, gradient background, off-white background, colored background, textured background, shadow, drop shadow, rim light, harsh lighting, head on body view, extra limbs, wrong body part, misplaced close-up, wandering eyes, unfocused gaze, crossed eyes, looking off-screen, one eye closed, winking, asymmetric eyes, asymmetric eyelids
```

### 特效/复杂场景类追加（当使用「题材氛围词库」时必须加）

治「背景元素抢戏、主体被吞没、画面太乱」——使用《10 大题材风格词》时，必须用这组负面词压住。

```
cluttered background, glowing magic, energy aura, fire sparks, heavy smoke, rain drops, motion blur, exploded particles, flying debris, over-decorated, gaudy gold, busy composition, messy composition, distracting background elements, multiple subjects, glowing lights
```

### 中英对照速查

| 中文要规避 | 英文 |
|---|---|
| 多余肢体/手指 | extra limbs / extra fingers |
| 变形的手 | deformed hands |
| 解剖错误 | bad anatomy |
| 脚被裁切 | cropped feet / cut off legs |
| 缺脚/半身 | missing feet / half body |
| 换脸/脸不一致 | different faces / inconsistent face |
| 发型不一致 | different hairstyle / inconsistent hairstyle / messy hair / uneven sideburns |
| 服装不一致 | different outfit |
| 分割线/框线 | split line / grid line / border frame |
| 灰色背景 | gray background |
| 渐变背景 | gradient background |
| 阴影/投影 | shadow / drop shadow |
| 轮廓光/硬光 | rim light / harsh lighting |
| 身体视图带头部 | head on body view |
| 水印/文字/logo | watermark / text / logo |
| 背景非纯白（偏灰/偏色/带纹理） | off-white background / colored background / textured background |
| 眼珠乱飘/视线不稳/对眼/看镜头外 | wandering eyes / unfocused gaze / crossed eyes / looking off-screen |
| 特写部位错误/串位 | wrong body part / misplaced close-up |
| 睁一眼闭一眼/眨眼/双眼不对称 | one eye closed / winking / asymmetric eyes / asymmetric eyelids |
| 塑料感皮肤/陶瓷肌 | plastic skin / ceramic smooth skin |
| 过度磨皮/无瑕假脸 | over-smoothed skin / flawless fake face |
| 眼神空洞/表情僵硬 | dead eyes / vacant stare / stiff facial expression |
| 肢体僵硬漂浮/动作不合物理 | stiff floating limbs / physically impossible pose |
| AI 失真感 | AI-distorted look |

---

## 常见翻车点对照表

| 翻车现象 | 根因 | 解法 |
|---|---|---|
| 生成了单张剧情图而非设定图 | 漏「图种」段 | 显式写「角色设定图 / character design sheet」 |
| 多视图乱序、自由发挥 | 只写「多视图」没列清单 | 逐条列出每个视图 + 排版（几行几列） |
| 胡子跑偏（想山羊胡变络腮胡） | 只说「留胡须」 | 精确写「八字胡 + 下巴山羊胡，两颊干净」 |
| 眼镜去不掉 | 参考图带眼镜但没显式写 | 写「去掉眼镜 / no glasses」 |
| 全身图裁掉脚 | 未强调全身 | 加「从头到脚完整入画 + 人物占画面 70%」 |
| 人物太小变远景 | 只写「完整入画」被缩成远景 | 加「close full body shot / 近景全身照 + 人物占比大细节清晰」 |
| 多视图脸/发型/服装漂移 | 未强调一致性 | 写「同一张脸、同一发型、同一服装，绝对一致」 |
| 气质冲突（要机警却茫然） | 真人原型气质未覆盖 | 显式写「眼神改为××，去掉原表情」 |
| 背景有阴影/渐变 | 模型表没写纯色平光 | 写「纯色背景、平光、无投影无阴影」 |
| 背景出现光影效果（主光/轮廓光） | 只写「无阴影」没写「不要光影」 | 写「不要任何光影效果，纯平光，无高光无轮廓光」 |
| 视图大小不一、重叠 | 没写排版约束 | 写「等大等距、比例一致、不重叠」 |
| 身体视图带了头部 | 只写「裁切」没写「不要头部」 | 写「身体四视图：均颈部以下、不要头部。正面、45°、90°、背面」 |
| 视图之间出现框线/分割线 | 没写「无明显分割线」 | 写「无明显分割线，靠留白自然区分」 |
| 纯白背景却出现灰底/过曝边缘 | 纯白背景 + 侧逆光自相矛盾 | 纯白背景必须砍侧逆光，改「正面柔和均匀光、无轮廓光」 |
| 站姿画成弓背含胸或军姿 | 「松垮/挺拔」情绪词歧义 | 用几何描述「脊柱直立+肩线放松+重心偏移+手自然垂放」，negative 加 slouching/hunched/rigid |
| MJ 服从度差 | 用中文长段落 | 英文版改关键词堆叠，构图词用 full body / no cropping / 70% of frame |
| 仰视/俯视角度不明确 | 只写「仰视/俯视」模糊词，没讲机位朝向范围 | 写清三要素：仰视 `low angle shot, camera placed below the feet looking upward, from feet to top of head, full body in frame`；俯视 `high angle bird's-eye shot, camera placed directly above the head looking straight down, from top of head to feet, full body in frame` |
| 多视图人物漂移（反复随机刷新） | 每次生成换 seed | 整图固定同一个 seed，不反复刷新 |
| 各视图光影不一致 | 没锁光影 | 写「平光、无明暗阴影、所有视图光影统一」（英文模型可译 `flat studio lighting`） |
| 特写生成部位不稳定/串位 | 「手/脚/护腕」只写类别没写边界 | 每个特写写死「只拍该部位 + 居中 + 占满格」，如「手部特写：只拍双手，手掌手背，居中占满」；negative 加 `wrong body part / misplaced close-up` |
| 眼珠乱飘/视线不稳 | 没锁视线方向 | 写死「所有面部视图眼睛正视镜头、视线一致」，negative 加 `wandering eyes / unfocused gaze / crossed eyes / looking off-screen` |
| 背景非纯白（灰/偏色/带纹理） | 只写「纯白」不够，模型加噪点/纹理 | 写「纯白底、无渐变、无纹理、无噪点、纯色 #FFFFFF」，negative 加 `off-white background / colored background / textured background` |
| 发型在各视图间漂移 | 发型细节没逐项写死 | 写死「发型三要素 + 鬓角走向 + 刘海分布」，如「黑色短发、鬓角利落、几缕碎发搭额前，所有视图完全一致」，negative 加 `inconsistent hairstyle / uneven sideburns` |
| 睁一眼闭一眼/双眼不对称 | 没锁眼睛状态 | 正面写「双眼睁开、状态一致」，negative 加 `one eye closed / winking / asymmetric eyes / asymmetric eyelids` |
| 特写太多导致串位/漏格 | 特写塞太多 | 按需 0~3 个最能体现辨识度的部位，不要全列；没有辨识度特写可省略 |

---

## 出图前自检量表（借鉴 `short-drama-image-prompts`，写完 prompt 未出图先过一遍）

> `check_assets.py` 是**出图之后**的质检；这张表是**出图之前**的门禁——把废片挡在生成前，比生成后靠 FaceID 兜底便宜得多。逐项给 `PASS | REVISE | NOTE` 并引用证据。

| 维度 | 要问的问题 | 合格证据 |
|---|---|---|
| **绑定** | 是哪个身份 + 当前变体？ | bible 的可见 ID + prompt 里引用 |
| **区分度** | 不看显示名，能否认出/区分？ | 稳定锚点 + 当前变化 |
| **单一目的** | 是否把互斥的参考需求混在一起？ | 用途、构图、状态一致 |
| **空间/尺度** | 关系能否同时成立并复用？ | 地理/尺度事实 + 正文句子 |
| **文字** | 政策、内容、承载面、排除是否相容？ | 文字事实 + 呈现方法 |
| **经济性** | 参考已承载的内容是否被无意义重复？ | 可删句 + 未受影响事实 |
| **越权** | 是否新造了资产/故事/连续性事实？ | 来源事实 + 冲突句 |
| **可复制** | 去掉标题元信息后正文是否自足？ | 可复制正文（不含 ID/路径/占位符） |

**只可本地证明的结构冲突直接阻断**（如「封面写『设备复核记录』」+「画面中不要任何文字」同时出现）；语义问题由 reviewer 引用来源后给 `REVISE`。

### 反模式清单（出现即返工）

1. 声称做中性身份板，却让一次性场景光、动作或背景成了识别特征（反之亦然：该保留复用职责的状态板被机械清空）。
2. 表单字段直贴描述：`身份:女配 年龄身高:20岁`。
3. 描述没有足以识别、操作或核对状态的事实，无论文字长短。
4. **无语义命名**：资产名叫 `1`、`站位`、`参考`——下游无法按名索引。
5. 收到反馈后不诊断身份/构图/文字/状态风险，只重复同一描述。
6. 描述内角色名与资产登记名不一致（写 A 名生成 B 人）。

---

## 风格帧 Lookdev：铺量前先验证视觉方向（借鉴 `short-drama-image-prompts`）

> 正式铺几百张图之前，先挑几帧「最能暴露风格失效」的代表帧单独出图验证。方向错了，铺量就是成批返工。这不是可选项——大制作铺量前必过这一关。

### 三类测试轴（不要求每类都出若干张，选最能暴露方向失效的代表帧）

| 测试轴 | 绑定什么 | 检查什么 |
|---|---|---|
| `character_expression` | 准确 CHAR/LOOK | 身份锚点、材质/线条、表演可读性 |
| `core_location` | 准确 LOC/VIEW | 地理、材质、色彩层级、光源逻辑 |
| `high_pressure_scene` | 准确场景、人物状态、来源块 | 冲突中的注意中心、遮挡、密度 |

### 写条目

- 用 `IMG-...` 标题，写明用途为 Lookdev + 测试轴 + 对应的「项目视觉方向」章节；
- 高压力场景还要绑定真实场景 ID、动作和信息权限，**不能从提示词发明剧情状态**；
- 写清：稳定项、允许变化项、要保护的身份/地理/剧情事实，以及删除风格标签后真正改变的材质/光/色/边缘/景深/空间表达。

### 风格参考的边界

风格参考图标用途为「风格」时：
- **允许控制**：只列色彩层级、材质处理、阴影边缘、景深倾向、画面密度等本次准许内容；
- **不得控制**：保护角色身份、固定场景地理、剧情状态、人数、持物、道具文字；
- 每张真实参考图用稳定 `REF-...` 槽位（见上文「参考图权限隔离」节）。

**高压力测试帧不得为了「更有冲击力」提前泄露身份、发明动作结果或改变文字政策。**
