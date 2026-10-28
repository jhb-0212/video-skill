# 完整案例（Examples）

> 本文件**只保留四类「模板写不出来」的锚点**：成品锚点（案例二）、格式锚点（案例五/七）、过程锚点（案例八）、流程锚点（完整工作流）。**「成品展示」交给 `prompt-templates.md` 的模板 + 七段骨架示例**，本文件不再堆完整成品案例。
> 每个案例开头都标了「学什么 / 别抄什么」——抄结构、别抄具体内容。

## 速查表（先读这个，半页）

| 案例 | 内容 | 锚点类型 | 位置 |
|---|---|---|---|
| 零基础完整工作流 | 从判级到出图到交付的 7 步全流程 | 流程 | 文首 |
| 七段骨架填空示例 | 极简七段结构，不含具体角色，直接往里填 | 结构 | 文首 |
| 案例二 | 单张定妆照（七段填满长什么样） | 成品 | 下文 |
| 案例五 | 道具三视图（三视图 + 尺寸 + 色卡） | 格式 | 下文 |
| 案例七 | M0 主题配乐需求说明（音频） | 格式 | 下文 |
| 案例八 | 多视图翻车救援记（失败→诊断→修正） | 过程 | 文末 |

> 多视图、表情集、场景全景、3D 定妆照**没有独立案例**——结构见 `prompt-templates.md` 模板二/四 + 文首「七段骨架填空示例」；3D 定妆照见模板一「风格替换」+ `style-recipes.md` D1/D2/D3 子档。

---

## 零基础完整工作流（E2：拿到角色列表，从判级到出图到验收）

> 新手最需要这个。案例是「给定设定→给提示词」的片段，这里是「从 0 到 1」的全局流程。

**场景**：用户给 3 个角色（主角 / 配角 / 群演各 1），要产资产包。

1. **Step 1 判级**：主角 L0（双线贯穿、大量特写）、配角 L1（独立剧情线、高频出场）、群演 L3（氛围性）。理由写进回复。
2. **Step 2 列资产清单**：L0 8 项（立绘/三视图/拆解/特写×3/材质样卡/配色卡/表情集5款/道具卡）、L1 5 项（立绘/三视图/配色卡/表情集3款/道具卡）、L3 1 项（单张定妆照）。
3. **Step 3 出 L0 定妆照**：套模板一 + R1 风格，4 选 1，过验收 5 条（见 `view-spec.md`）。
4. **Step 4 出 L0 多视图**：用定妆照做参考图，套模板二，拆 2 张（面部四视图一张、身体四视图一张）。
5. **Step 5 出 L1 定妆照**：同流程，但只出三视图 + 配色卡（不拆解）。
6. **Step 6 出 L3 定妆照**：极速模式，单张 + 换 seed。
7. **Step 7 交付**：按接收方裁剪清单（coser 给什么、3D 建模师给什么，见 SKILL.md「交付物清单」）。

---

## 七段骨架填空示例（替代原案例三：不含具体角色，只示范每段写什么颗粒度）

> 比 8 个完整案例更有用——它告诉你七段每段写什么、写到多细，但不绑定任何具体角色，可直接往里填自己的内容。方括号是占位符。

```
[图种] 角色设定图，16:9 横版，纯白背景
[人物] 青年男性，窄长脸，高眉骨，桃花眼上挑，薄唇，黑短发侧分——眼神微偏一侧、嘴角平直、肩放松下沉
[妆造] 深色交领短打，白色内衬，护腕，腰间绦带
[视图] 面部四视图 / 身体四视图 / 姿势四视图 / 特写×3
[排版] 左右两列，等大等距，留白分隔，不画线框
[背景/光] 纯白 #FFFFFF，平光，5500K，无阴影
[风格] 真人写实，真实皮肤纹理，8K
```

> 颗粒度提示：人物段给「脸型 + 五官形状 + 一个神态动作」，妆造段给「款式 + 颜色 + 层叠」，视图段给「几个视图 + 每个视图范围」，背景段给「色值 + 光型 + 色温」。每段一个「看得见的形状」，不堆形容词。单张定妆照只用前 3 + 背景 + 风格共 5 段，多视图才 7 段。

---

## 案例二：单张定妆照（瘦身版 · 真人写实 · 9:16 竖版全身）

> **学什么**：①全身景怎么防裁脚（`minimal headroom and legroom`，中文才用「70%」）；②验收 5 条对应的写法（纯白底无阴影、双眼睁开视线明确、发型走向清楚）；③色温怎么写（5500K）。
> **别抄什么**：还是林梓泳的特定脸/服装，换成你自己的。

### 中文提示词

> 人物定妆照，9:16 竖版。青年男性，23 岁，184cm，肩膀比腰宽、腰窄、腿长，肩背挺直。眉骨高，眉毛上扬，眼睛是桃花眼、眼角向上挑、双眼皮，鼻梁又高又直，嘴唇薄，下巴偏尖，皮肤白。发型：黑色短发、鬓角剃干净、几缕碎发搭额前、刘海朝一侧、不是中分。眼神：没有看向镜头，眼珠微微偏向一侧、视线朝下。表情：左边嘴角向上翘一点、似笑非笑。服装：深色短打甲衣、交领右衽、领缘袖口露白色内衬、护腕、腰间绦带。姿态：肩膀向下放松、脊背挺直、重心压一只脚、双手自然垂两侧。从头到脚完整入画，脚底和鞋子完整可见，脚下留地面，绝不裁脚，人物约占画面高度 70%，近景全身照。光影：正面柔和均匀主光，5500K 日光白，无侧逆光、无轮廓光、无投影。背景纯白、无渐变。真人写实摄影，真实皮肤纹理，8K。

### 英文提示词

> Character portrait, 9:16 vertical, close full-body shot, character fills the frame vertically, head near top edge, feet near bottom edge, minimal headroom and legroom, no cropping. Young Chinese man, 23 years old, 184cm tall, shoulders wider than waist, narrow waist, long legs, straight back. High brow ridge, peach-blossom eyes, upturned outer corners, double eyelids, tall nose bridge, thin lips, fair skin. Black short hair, shaved sideburns, a few loose strands over forehead, fringe swept to one side. Eyes not looking at camera, pupils turned slightly to one side, gaze downward. Left mouth corner slightly raised, half-smiling. Dark short jacket armor, cross-collar right lapel, white inner lining, wrist guards, waist ribbon tassels. Shoulders relaxed, spine straight, weight on one foot, hands hanging naturally. Soft even frontal lighting, 5500K daylight white, no rim light, no backlight, no shadows. Pure white background, no gradient, solid color. Photorealistic, realistic skin texture, 8K.

### 负面提示词

```
cropped feet, cut off legs, missing feet, half body, head cut off, extra limbs, deformed hands, bad anatomy, blurry, low quality, watermark, text, logo, slouching, hunched, rigid, mole, blemish, rim light, harsh lighting, shadow, drop shadow
```

### 风格替换（换 3D 或 2D，只改第 7 段）

> **3D 替换请按题材选子档（D1/D2/D3），不要用通用替换词。** 通用替换词（如 `3D 渲染，次世代 PBR 材质`）只适用于快速草稿，**不用于交付级**——交付级 3D 必须选具体子档，贴该子档的 L1 词栈 + 背景光约束。完整词栈见 `style-recipes.md`。**切勿混写**「3D + 真实皮肤纹理」或「3D + 8K 摄影」。
> 2D：中文 `二维插画，赛璐璐上色，平涂+简单阴影`；英文 `2D illustration, cel shading, flat color`。

---

## 案例五：道具三视图（P0 · 青玉印 · 白底平光）

> **学什么**：道具三视图结构（三视图 + 尺寸比例 + 色卡 Hex + 材质），和角色线完全不同。
> **别抄什么**：青玉印是示例道具，换成你自己的道具即可。

### 中文提示词

> 道具三视图，青玉印：方形玉印，印体温润青玉、浅刻云纹，印纽雕成蜷曲瑞兽，顶部系暗红绦绳。三个视图同一画布水平排布、等大等距、不重叠、靠留白分隔、不画网格线框线：正面、侧面、背面。尺寸：印体约一掌宽（约 9cm 见方），适合单手持握。图底部配色卡：`#4E9E8A` 青玉 · 印体主色 / `#8A2F2F` 暗红 · 绦绳 / `#3B6E5F` 深青 · 云纹阴刻线 / `#D8C9A3` 米白 · 瑞兽高光。纯白背景、无渐变、平光均匀、无阴影。正交视图、无透视。3D PBR 渲染，玉质通透、高光柔和。

### 英文提示词

> Prop three-view sheet, a jade seal: square seal body of warm green jade with shallow carved cloud patterns, a crouching mythical beast finial, a dark red silk cord. Three views on one canvas, horizontal, equal size, no overlap, separated by white space, no grid lines: front, side, back. Scale: seal body about one palm wide (about 9cm square). Color palette at bottom: #4E9E8A green jade / #8A2F2F dark red cord / #3B6E5F deep green carved lines / #D8C9A3 off-white finial highlight. Pure white background, no gradient, flat even lighting, no shadows. Orthographic view, no perspective. 3D PBR render, translucent jade, soft highlights.

### 负面提示词

```
perspective distortion, split line, grid line, border frame, shadow, drop shadow, gray background, gradient background, watermark, text, logo, blurry, low quality, broken parts, floating fragments
```

> **场景全景同理**：结构 = [图种：场景设定图] + [主体/结构] + [陈设/道具] + [光照/时段] + [配色卡] + [风格]，套 `prompt-templates.md` 模板四即可，无需独立案例。

---

## 案例七：M0 主题配乐需求说明（音频 · 不产音频，只出需求）

> **学什么**：一段好的音频需求说明长什么样——情绪/速度/调式/配器/锚点五要素，这是规则写不出来的「格式示范」。
> **别抄什么**：林梓泳主题是示例，换成你的角色动机。

### M0 主题动机描述

- **主题名称**：林梓泳主题（「落拓风骨」动机）
- **情绪走向**：由**压抑/隐忍**（落拓、命运未卜）渐转**决绝/坚定**（扛起锚命之责），中段一处**怅然回落**再上扬。整体「冷的底色、暖的爆发」。
- **速度/节拍**：慢板起始（约 60 BPM），副歌转中板（约 90 BPM），收尾回慢板留余韵。
- **调式**：羽调式（古风五声，偏沉郁），副歌转宫调式上扬。
- **配器方向**：**古筝泛音引入**（清冷、留白）+ **低音弦乐（大提琴/大阮）铺底**（沉、稳）+ 副歌加**竹笛/箫**旋律线 + **磬/编钟**点状点缀（清贵感）；打击乐只用**轻量板鼓**，不用重鼓。
- **场景锚点**：男主出场、关键抉择、片尾主题；动机可拆「压抑段 / 决绝段 / 怅然段」三变奏复用。
- **参考曲风**：新古风影视配乐（苍凉孤寂 + 收尾一抹暖意）。

> 写法要点：M0 一定落到「情绪走向 + 速度 + 调式 + 配器方向 + 场景锚点」五要素，别只写「要有气势/要感人」；情绪词同样拆成「哪段什么情绪、配什么乐器怎么变化」。

---

## 案例八：多视图翻车救援记（E3：失败 → 诊断 → 修正）

> **学什么**：这是全文件最有价值的一节——示范的不是「怎么写 prompt」，是「翻车了怎么诊断」。过程性知识规则写不出来，只能靠案例。

**第一次出图**：面部四视图，脸清晰，但身体四视图里有两张脸漂移。

- **诊断**：单图塞了 8 个视图，超弱一致性模型上限。
- **修正**：拆成两张（面部四视图一张、身体四视图一张），同 seed。

**第二次出图**：脸不漂了，但身体视图带了头。

- **诊断**：「身体四视图」约束没写在前。
- **修正**：把「均颈部以下、不要头部」挪到身体四视图段的第一句。

**第三次出图**：通过。

**经验总结**：① 先减视图数再改措辞；② 约束前置比约束加粗更有效；③ 脸漂移优先用参考图加强，别急着拼接。

---

## 使用说明

> **E4：阅读版 vs 投喂版要分清**——每个案例的「中文提示词/英文提示词」是可直接复制粘贴给 AI 的纯 prompt；带 `>` 的解释、说明、要点是「为什么这么写」的人类阅读内容，**不要投喂给 AI**。

1. **抄结构、别抄内容**：每个案例开头都标了「学什么/别抄什么」。替换成自己的角色时，只保留结构（开头硬约束、视图清单、排版句、负面词、参数），脸/发型/服装换成你自己的（对照 `feature-catalog.md`）。
2. **全局铁律——形容词定方向 + 动作定执行**：案例里"桃花眼/清贵/落拓"都已配具体动作。你替换时，凡是「清冷/温柔/机灵/凌厉」这类词，保留它定方向，但必须紧跟「眼神/表情/姿态」具体拆解（对照 `feature-catalog.md` 末尾）。
3. **先定妆后多视图**：多视图建议先出单张定妆照锁定形象，再把该图作参考图上传，套 `prompt-templates.md` 模板二（参考图版开头）。
4. **特写按需挑**：多视图的细节特写按角色辨识度挑 0~3 个（如护腕/绦带/衣料），没有辨识度特写可整行省略。
5. **风格三选一**：真人写实 / 3D / 2D，只替换第 7 段风格词，不混用（见案例二「风格替换」）。
6. **按模型适配**：换中文模型时改中文自然语言、中文负面词、删 MJ 参数，多视图拆多张（每张 ≤4 视图）。完整适配规则见 `SKILL.md`「目标模型适配」。
7. **中文模型去标签（A5）**：投喂中文对话模型时删掉所有【】标签，改自然段落；投喂 MJ/SD 时标签可保留。
8. **版本管理（C2）**：一个角色出多版提示词时，用文件名 `{角色名}_{视图类型}_v{版本号}.txt`，文件头部记录改动、效果、出图、待试，每个角色建文件夹保留所有版本。
