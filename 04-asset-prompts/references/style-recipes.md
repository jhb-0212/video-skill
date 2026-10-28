# 风格词栈库（Style Recipes）

> 用途：prompt-templates.md 第 7 段「风格/质感」的扩充库。三大类（2D/3D/真人写实）下设子档，每档给完整中英词栈 + 适用题材 + 配套负面词 + 背景光约束。
> **原则：第 7 段先选大类，再选子档，把该子档的「中文词栈 / 英文词栈」整段贴进第 7 段，不要只写一句。**

## 速查表（先读这个，半页）

| 要什么 | 子档 | 背景光约束 |
|---|---|---|
| 定妆照 / 技术图 | R1 干净影棚 | 纯白底 + 平光 |
| 立绘 / 海报 / 活人感 | R2 呼吸感 | 浅灰底 + 可侧逆光；改纯白必砍 |
| 剧情 / 场景人像 | R3 剧情纪实 | 禁纯白底 |
| 古风 / 国风 / 东方古典 | D1 国漫温婉（方向按骨相+光自定，示例：温婉/清冷/英气） | 方向由骨相+光+色温三者匹配决定，示例见 D1 节 |
| 游戏 / 电影级 3D | D2 CG 写实 | 纯色 / 浅灰 |
| 少年 / 少女 / BJD | D3 BJD 半写实 | 浅灰纯色 |
| 动漫 / 番剧 | T1 赛璐璐 | 纯色 |
| 原画 / 厚涂 | T2 厚涂 | 纯色 / 渐变 |

> 选不准时：定妆照/多视图默认 R1；「动漫」→T1；「3D/CG/游戏」→D2；「国风 3D」→D1。**要贴完整词栈才往下读对应子档详表。**

---

## 详表（需要时再往下读）

## 词栈裁剪原则（B6：词栈太长时，按优先级砍）

每个子档词栈按优先级分三层，平台长度紧时逐层砍：

- **L1 核心（必留）**：风格定性 + 材质方向 + 光影类型（约 30 字）
- **L2 强化（按需留）**：具体质感词、氛围词（约 50 字）
- **L3 点缀（可删）**：可叠加的效果词（约 70 字）

平台长度紧 → 只留 L1；宽松 → L1+L2；追求极致质感 → 全留。例如 R2 呼吸感：L1 =「真人写实人像摄影、电影级柔和自然光影、次表面散射、原生毛孔」；L2 =「体积光、眼神光、微妙情绪」；L3 =「胶片颗粒、衣角摆动」。

> **3D 子档特别提示**：D1/D2/D3 的完整词栈偏长，**多数模型对 3D 长词栈的执行度低于真人写实 R2**——词一多，模型会抓几个关键词随机发挥，反而丢掉「材质细腻」这个核心。**用 3D 时优先只贴 L1 核心词栈**（约 30 字）；需要氛围时再加 L2；**不要一次贴全段**。

---

## 一、真人写实（Photorealistic）

### 子档 R1｜干净影棚（默认）

- **适用**：标准定妆照、技术设定图、需要「干净可读」的资产
- **中文词栈**：真人写实摄影，电影级质感，真实皮肤纹理，8K，纯白背景，平光均匀照明，无阴影
- **英文词栈**：photorealistic, cinematic photography, realistic skin texture, 8K, pure white background, flat studio lighting, no shadows
- **背景光约束**：**纯白底必须平光、砍侧逆光/轮廓光**（见 prompt-templates.md 光影表）
- **配套负面词**：见负面词清单「通用」+「单张定妆照追加」

### 子档 R2｜呼吸感 / 电影感（去 AI 感）

- **适用**：单人立绘、海报、需要「活人感」的展示图
- **中文词栈**：真人写实人像摄影，8K 超高清原生画质，电影级柔和自然光影，无畸变广角，还原真实人像质感；皮肤通透细腻，精准呈现肌肤次表面散射，自带自然原生珠光光泽，超逼真还原皮肤纹理、原生毛孔、面部细碎绒毛；五官立体精致，画面干净通透，光影过渡自然，整体真实有呼吸感，细节拉满。可叠加：体积光、空气悬浮微粒、自然胶片颗粒、眼神光清晰、面部微妙情绪、肢体真实重量感、衣角随动作自然摆动
- **英文词栈**：photorealistic portrait photography, 8K ultra-HD native quality, cinematic soft natural lighting, no wide-angle distortion, true-to-life human texture; translucent fine skin, subsurface scattering, natural pearlescent sheen, ultra-realistic skin texture, visible pores, fine facial vellus hair; sculpted features, clean and transparent image, natural light falloff, breathing lifelike feel. Optional: volumetric light, floating dust particles, natural film grain, clear catchlight, subtle micro-expression, real body weight, garment hem swinging naturally
- **背景光约束**：可配浅灰渐变影棚背景 + 柔和主光 + 侧逆轮廓光；**若改纯白底，必须砍侧逆光**（否则灰底过曝）
- **配套负面词**：**必须加「真人写实·质感类」组**（见 prompt-templates.md），这是本子档最关键的一道防线

### 子档 R3｜剧情纪实 / 生活感

- **适用**：剧情向剧照、场景内人像、有环境信息的镜头
- **中文词栈**：场景纪实写真，真实活人质感，去除 AI 感，场景含体积光与空气悬浮微粒，背景层次丰富有真实氛围，眼神光清晰、眼神灵动不呆滞，肢体有真实重量感、动作符合物理逻辑，衣物随动作自然摆动，姿态松弛舒展，皮肤原生真实、可见毛孔微细血管、肤色自然红润、保留真实微小皱纹；可加自然胶片颗粒
- **英文词栈**：documentary-style photographic portrait, real human texture, no AI feel, volumetric light with floating particles, rich layered background, clear catchlight, lively eyes not vacant, real body weight, physically plausible motion, garment swinging naturally, relaxed posture, native skin with visible pores and fine capillaries, natural flush, keeping real micro-wrinkles; optional natural film grain
- **背景光约束**：**不适用纯白底**（本子档靠环境层次，纯白底会丢氛围）；用真实场景或浅灰影棚
- **配套负面词**：**必须加「真人写实·质感类」组** + 通用组

---

## 二、3D 渲染（3D Render）

### 3D 质感精度：prompt 层统一高精度（不降档）

> **概念澄清（必读）**：prompt 里的「影视级 / 路径追踪 / 全局光照」是**质感描述词**，不是真的调用了 UE5 渲染管线。AI 生图模型没有「路径追踪」这个功能，这些词的作用是**暗示模型往高精度质感方向走**。写了不一定真用路径追踪，不写一定往廉价感走——所以**要写，但别把它当渲染器承诺**。

| 层 | 规则 |
|---|---|
| **prompt 质感词** | **统一高精度**：高精度 CG 质感、真实材质反射、电影级光影层次、8K 超高清。L0~L3 全部不降档 |
| **风格词栈** | 按子档选，**不混层**：BJD（D3）走「高精度 PBR 材质」但**不加**「写实皮肤/次表面散射」词；2D（T1/T2）走「高完成度」（精细线稿/厚涂层次），**不加** 3D 渲染词；真人写实 R2 本身即最高精度，不需额外加「影视级」词 |
| **实际渲染器** | 由用户所用的生图平台决定（MJ/SD/即梦等），**不是 prompt 能控制的**——prompt 只影响「往哪个质感方向走」 |

**为什么统一高精度质感词**：质感不够就是「廉价感」。高精度质感是质量下限，不是上限——**skill 默认输出就是这个下限，不需要切换模式**。

> **注**：D1/D2/D3 词栈里的「UE5 / 路径追踪」保留作为 prompt 质感词（它们有效），但理解成「质感暗示」而非「渲染器声明」。

### 子档 D1｜国漫温婉（东方氛围感 · 方向按骨相+光自定）

- **适用**：古风/国风/东方古典角色
- **中文词栈**：新中式 3D 国漫角色，融合英式动画的柔和质感与东方古典审美，**具体骨相（按角色填，见下）**，虚拟引擎 5 超高清渲染，8K 极致精度；线条流畅灵动，五官精致舒展，自带古典故事感，光影柔和通透，色彩雅致高级；精准还原国风织锦、刺绣、纱质面料的细腻质感，发丝根根分明，皮肤纹理自然真实，材质表现细腻，整体画面唯美大气
- **英文词栈**：neo-Chinese 3D donghua character, blending soft British animation texture with oriental classical aesthetics, **specific bone structure (fill per character)**, UE5 ultra-HD render, 8K extreme precision; flowing lines, refined relaxed features, classical storytelling feel, soft translucent lighting, elegant refined colors; accurately rendered Chinese brocade / embroidery / gauze fabric, individual strands of hair, natural realistic skin texture, delicate material rendering, beautiful and grand overall
> 注：此处「UE5/超高清渲染」是 prompt 质感暗示词，不是渲染器承诺。

**方向怎么定（不限于固定几种）**：方向由「骨相 + 光 + 色温」三者匹配决定——**骨相写具体（脸型 + 眼型至少两项），光和色温跟着骨相的气质走**。暖光配圆润骨相（温婉/娇俏），冷光配清瘦骨相（清冷/英气），暗调配锐利骨相（妖冶/端庄）。

**三个示例组合**（覆盖最常见几类，不是穷举）：

| 方向 | 骨相（写具体，不能只写「五官精致」） | 背景光 |
|---|---|---|
| **温婉** | 中庭适中、鹅蛋脸、杏眼、唇形饱满 | 暖米 #E8E0D0 + 柔和影棚光 + 极淡侧后轮廓光 + 接触阴影，4500K |
| **清冷** | 中庭偏长下庭偏短、脸颊清瘦、开扇形双眼皮带内眦赘皮、S 形眼型、薄唇平直狭长 | 浅灰 #C4C4C4 或冷调纯色 + 柔和主光 + 极淡冷色轮廓光（不用暖黄），5500K |
| **英气** | 长脸或菱形脸、剑眉、上挑眼、薄唇 | 深灰 #6B6B6B + 稍硬的主光 + 冷色轮廓光，5500K |

**其他气质**（娇俏/端庄/妖冶/忧郁等）按同一规则自定：娇俏用圆脸圆眼 + 暖粉暖光，端庄用方圆脸丹凤眼 + 暖米伦勃朗光，妖冶用瓜子脸狐狸眼 + 深灰侧逆光。

**默认骨相和光匹配**（清冷配冷光、温婉配暖光、英气配冷硬光）——这是最稳的组合，大多数角色按这个走。

**允许刻意反差，但必须写清「反差在哪、想表达什么」**：比如「清冷骨相 + 3000K 暖黄侧光」，不写清模型会当成指令冲突、随机取一半；写清「脸是冷的、光是暖的，表达被暖意包裹的疏离感」，模型才知道这是设计而非矛盾。反差是高级手法，用在「角色有内外张力」时，不要无理由地反着来。

**要避免的是「无意打架」**——同一维度给互斥值（如「中庭偏长 + 鹅蛋脸 + 圆杏眼 + 尖下巴」），模型各取一半，出「五官打架」的脸。这和「骨相与光反差」是两回事：前者是词本身矛盾，后者是两个维度故意错位。

**骨相必须写具体**：只写「五官精致、气质温婉」会出通用脸；写到「脸型 + 眼型」这一档，脸才锁得住（见 `feature-catalog.md` 核心原则「骨相具体化」）。鼻唇细节是加分项，但脸型 + 眼型是决定项。

- **背景光约束**：光与色温跟着骨相气质走（暖光配圆润骨相 / 冷光配清瘦骨相 / 暗调配锐利骨相），**任何方向都避免「纯浅灰 + 无轮廓光 + 无阴影」三平叠加**（会出建模展示图、没有氛围）
- **配套负面词**：通用组 + 多视图组；**不要加质感类负面词**（会压制 3D 质感）；**两组失败模式都要压**：
  - 压渲染成真人：`photorealistic skin texture, real photography, plastic CG, flat lighting, low detail, over-rendered`
  - 压通用国漫脸：`generic donghua face, western features, double eyelid too wide, silicone skin, 网红脸, 欧式五官, 硅胶感`

### 子档 D2｜CG 游戏写实（电影级）

- **适用**：游戏角色、需要「电影级质感」的 3D 资产
- **中文词栈**：UE5 路径追踪渲染，次世代 CG 游戏角色，写实人像风格，精准还原皮肤次表面散射，超逼真呈现细腻肌肤纹理、原生毛孔与面部绒毛，肌肤自带自然健康光泽；五官立体精致；服装道具的皮革、金属、织物材质质感拉满，画面锐利干净
- **英文词栈**：UE5 path-traced render, next-gen CG game character, realistic portrait style, accurate skin subsurface scattering, ultra-realistic fine skin texture, visible pores and facial vellus hair, natural healthy skin sheen; sculpted refined features; leather / metal / fabric materials fully rendered, sharp and clean image
> 注：此处「UE5/路径追踪」是 prompt 质感暗示词，不是渲染器承诺。
- **背景光约束**：纯色或浅灰影棚背景 + 柔和影棚布光
- **配套负面词**：通用组 + 多视图组 + `photorealistic skin texture, real photography, flat lighting, low detail`（压渲染成真人/平光/低细节）

### 子档 D3｜BJD / 半写实国漫少年

- **适用**：少年/少女角色、需要「BJD 精致五官 + 东方清冷」的设定图
- **中文词栈**：高精度 3D 半写实国漫角色，融合 BJD 人偶精致五官、东方少年冷静利落气质与现代极简服饰审美；小头高颅顶、窄长精致瓜子脸、下巴尖巧、细长平眉、微上扬细长猫眼、双眼皮、清澈克制眼神、深灰湿润玻璃瞳、细窄笔直鼻梁、小巧鼻尖、偏薄自然淡粉唇、神态安静疏离；冷调白皙肤色带轻微自然红润；发丝根根分明，发梢带少量灰银色层次；高精度 3D 半写实国漫 CG 渲染，真实 PBR 材质，高清布料纹理，柔和影棚布光，浅灰纯色背景，轻微接触阴影，画面干净，无文字无水印
- **英文词栈**：high-precision 3D semi-realistic donghua character, blending refined BJD doll features, calm and sharp oriental youth temperament, modern minimalist outfit aesthetics; small head high cranial top, narrow refined oval face, delicate pointed chin, fine straight brows, slightly upturned narrow cat eyes, double eyelids, clear restrained gaze, deep gray moist glass pupils, narrow straight nose bridge, small nose tip, thin natural pale pink lips, quiet aloof expression; cool fair skin with slight natural flush; individually rendered hair strands with subtle gray-silver highlights at tips; high-precision 3D semi-realistic donghua CG render, realistic PBR material, HD fabric texture, soft studio lighting, light gray solid background, subtle contact shadow, clean image, no text no watermark
- **背景光约束**：**浅灰纯色背景**（不是纯白）+ 柔和影棚布光 + 轻微接触阴影
- **配套负面词**：通用组 + 多视图组 + `Q-version, chibi, adultified, photorealistic skin texture, real photography, flat lighting`（防 Q 版/成人化 + 压渲染成真人/平光）

---

## 三、2D 插画（2D Illustration）

### 子档 T1｜赛璐璐 / 动漫

- **适用**：动漫、番剧、漫画风设定
- **中文词栈**：二维插画，赛璐璐上色，动漫风，线条干净利落，平涂 + 简单阴影，色彩明快
- **英文词栈**：2D illustration, cel shading, anime style, clean crisp lineart, flat color with simple shading, bright colors
- **背景光约束**：纯色背景，无写实光影
- **配套负面词**：通用组 + `photorealistic, 3D render, realistic skin texture`

### 子档 T2｜厚涂 / 半写实插画

- **适用**：游戏原画、海报插画、半写实风格
- **中文词栈**：2D 插画，厚涂，半写实，笔触可见，光影层次丰富，色彩高级，画面有绘画感
- **英文词栈**：2D illustration, painterly, semi-realistic, visible brushstrokes, rich light and shadow layers, refined colors, painterly feel
- **背景光约束**：纯色或渐变背景，光影按画面需要
- **配套负面词**：通用组 + `3D render, plastic texture`

---

## 四、摄影语言档（真人写实专用，按背景条件选）

> **前提：以下光效只在「非纯白背景」时可用。纯白底必须砍侧逆光/轮廓光，改平光。**

| 光效 | 中文 | 英文 | 适用背景 |
|---|---|---|---|
| 85mm 大光圈 | 85mm f1.4 大光圈镜头，浅景深，焦点精准锁在人物面部 | 85mm f1.4 lens, shallow depth of field, focus locked on face | 任意（尤其 R2/R3） |
| 伦勃朗光 | 电影级伦勃朗光，明暗对比强烈 | cinematic Rembrandt lighting, strong chiaroscuro | 浅灰/暗调背景 |
| 蝴蝶光 | 蝴蝶光，鼻下形成对称阴影 | butterfly lighting, symmetric shadow under nose | 浅灰影棚 |
| 侧逆光轮廓光 | 侧逆光轮廓光，柔和柔光打亮面部 | side-back rim light, soft fill on face | **仅浅灰/暗调背景，禁纯白** |
| 体积光 | 体积光，空气悬浮微粒 | volumetric light, floating dust particles | 场景内 / 暗调 |
| 胶片颗粒 | 自然胶片颗粒感 | natural film grain | R2/R3 |

**写进 prompt 的规则**：先写背景（纯白 / 浅灰 / 场景），再写允许的光效，**二者必须匹配**（见 prompt-templates.md「光影与背景的固定搭配」表）。

### 色温（B4：写光必须写色温，不只写「柔和」）

「柔和」是光的强度，「色温」才是氛围——同一个角色，3000K 暖黄 vs 7000K 冷白，气质完全不同。写背景/光段时，光效之后补一句色温：

| 色温 | 中文 | 英文 | 适合 |
|---|---|---|---|
| 3000K 暖黄 | 暖黄钨丝灯光，温馨柔和 | 3000K warm tungsten light, cozy and soft | 室内、黄昏、回忆镜头 |
| 4500K 中性暖 | 暖白光，日常自然 | 4500K neutral warm light, natural everyday | 大多数定妆照 |
| 5500K 日光 | 标准日光白，真实 | 5500K daylight white, true-to-life | 写实剧照、定妆 |
| 7000K 冷白 | 冷白光，清冷疏离 | 7000K cool white light, cool and aloof | 冷感角色、赛博、夜戏 |

> **铁律**：写光必写色温。默认定妆照用 4500~5500K（自然真实），冷感角色切 7000K、温馨场景切 3000K。

> 子档选择见文首速查表（要什么→选哪个子档→背景光约束），此处不重复。

---
## 五、题材氛围词库（10 大类风格提炼）
> 来源：整理了 80 套 AI 画面提示词，去重提炼而成。**注意：这些是「场景/氛围词」，用于增强画面故事感。如果做角色设定图（纯白底），不要整段抄，只从中挑选 2~3 个质感和光影词即可；背景必须保持纯白。**
### 1. 暗黑哥特类（吸血鬼/魔法/诡异）
- **核心场景**：吸血鬼城堡、废弃教堂、夜雾墓园、巫师森林、血月仪式
- **光影**：月光透射光柱、烛光摇曳暖光、暗调高对比、冷蓝暗调、血红暗调
- **高频词**：乌鸦盘旋、浓雾弥漫、枯树剪影、彩色玻璃窗、黑袍人影、暗黑唯美
- **建议搭配子档**：真人写实 R3（剧情纪实）/ 3D D2（CG 游戏写实）
### 2. 未来科技类（机甲/赛博/太空）
- **核心场景**：全息实验室、机甲废墟战场、空中城市、火星基地、元宇宙网格
- **光影**：冷蓝光粒子、霓虹闪烁、金属反光、蓝光机械、全局光照真实
- **高频词**：悬浮岛屿、飞行器穿梭、能量核心发光、数字网格、赛博梦幻
- **建议搭配子档**：3D D2（CG 游戏写实）
### 3. 治愈日系类（青春/日常/温馨）
- **核心场景**：夏日教室、海边沙滩、咖啡馆、雪夜温泉、日式庭院
- **光影**：柔光焦段、电影级日系调色、胶片颗粒感、逆光光斑、柔光逆光
- **高频词**：白色窗帘飘动、少女回眸、木质感、热腾腾、画面有烟火气
- **建议搭配子档**：真人写实 R2（呼吸感）
### 4. 国风古韵类（大唐/江南/武侠）
- **核心场景**：大唐盛世长安、江南水乡乌篷船、故宫雪景、敦煌飞天、戏曲戏台
- **光影**：暖金黄色调、水墨淡雅、柔光朦胧、电影级暖调
- **高频词**：飞檐翘角、丝带飘扬、竹林对决、旗袍油纸伞、如梦似幻
- **建议搭配子档**：3D D1（温婉向） / 真人写实 R2（古风）
### 5. 玄幻仙侠类（仙宫/剑客/神兽）
- **核心场景**：仙宫云海、御剑飞行、上古神兽降临、修罗战场、仙气秘境
- **光影**：金色光柱、电闪雷鸣、灵力光晕、柔和逆光、全局光照
- **高频词**：仙鹤翱翔、白衣剑客、金色法力、紫色法力对撞、仙气飘渺、水墨意境
- **建议搭配子档**：3D D1（清冷向 / 温婉向）
### 6. 自然风光类（极光/火山/深海/星空）
- **核心场景**：极光雪山、火山熔岩、热带雨林、沙漠戈壁、海底珊瑚
- **光影**：星空繁星、长曝光感、全局光照、逆光柔焦、自然光
- **高频词**：长曝光感、微距特写、视觉震撼、史诗感
- **适用**：场景 S0/S1 资产（大景别），**不要用于人物定妆照**。
### 7. 动作大片类（爆炸/追逐/格斗）
- **核心场景**：爆炸枪战、飞车追逐、屋顶跑酷、雨夜街头格斗
- **光影**：高对比度、火光冲天、霓虹光影、慢镜头水花
- **高频词**：低角度跟拍、慢镜头、弹壳飞溅、城市天际线背景
- **适用**：分镜图 / 概念大图，**角色定妆照绝对不要用这套**。
### 8. 写实摄影类（人像/动物/美食/微距）
- **核心场景**：毛孔特写、毛发特写、美食断面、昆虫翅膀
- **光影**：自然柔光打底、背景虚化、暖色调灯光、微距特写、浅景深
- **高频词**：皮肤毛孔细节清晰、发丝逐根可辨、眼神光、水珠飞溅
- **建议搭配子档**：真人写实 R2（呼吸感） / R1（干净影棚）
### 9. 影视广告类（汽车/香水/3C/珠宝）
- **核心场景**：盘山公路飞驰、香水瓶特写、悬浮展示、钻石折射
- **光影**：金色光晕、冷调蓝光环境光、柔光打底、高对比度、硬光打亮
- **高频词**：金属车漆反光、光线扫过表面、水珠滚动、景深虚化
- **适用**：道具 P0 / 场景 S0 广告级质感，**人物不要用**。
### 10. 科幻悬疑类（赛博/时间循环/外星/深海）
- **核心场景**：赛博朋克街道、太空站密封空间、平行世界穿越、地下实验室
- **光影**：霓虹光影交错、冷色调光影、冷白光明、双重曝光效果
- **高频词**：全息投影、代码流动效果、路灯光影、虚实交织画面
- **建议搭配子档**：3D D2（CG 写实）/ 真人写实 R3（剧情纪实）
> **一句话：这套词库是「场景/分镜/氛围图」的加速器，做人物定妆照时请务必管住手，别把背景的「火光四溅、全息投影」抄进去，否则纯白底和面部特征全毁。**
