---
name: ppt-conference-style
description: IMS/RFIC 会议风格完整法典（RFIC2024 官方语料 87 deck/2536 页全量测量 + 4 份历史深测样本）+ PPTX 安全编辑管线。生成或修改会议风格幻灯片前必须加载。
---

# 〇、样本与置信度

- **主参照（v0.3 起）**: RFIC2024 官方演讲语料全量测量——`RFIC2024/2024_07_02_RMo01A_1/` 87 份 deck、
  2536 页，逐 span 扫描 + 50 页目检。测量记录：`_learnings/RFIC2024_corpus_constraints.md`
  （机读数据 `corpus_stats.json` / `deep_stats.json` / `layout_stats.json`，渲染样本 `renders_rmo01a/`）。
- **逐 deck 档案（v0.3.5 起）**: 每份 deck 一档的 8 维度实测（字体族/行距/层级字号/图线粗细/公式/图注/
  表格/版式）见 `_learnings/RFIC2024_perdeck_profiles.md`（机读 `perdeck_profiles.json`，
  逐 deck 拼图 `perdeck_renders/`）；复刻某一份的具体参数先查此档案再动手。
- 历史深测样本（保留作变体参照）: Tenghao Zou 28 页（Franklin 派）、RMo01B_2 25 页、Th01C_2 20 页。
- 本文件默认值 = **语料多数派（RFIC 官方模板）**。作者差异已收敛为"允许变体"，逐条标注。
  **每个项目开工时在项目 style.json 里声明所选变体，此后不得混用。**

# 一、页面骨架

- **身份元素豁免（用户指令 2026-09-15，最高优先级）**: RFIC/IMS 竖标、会议徽标、IEEE/MTT-S/SSCS 页脚
  logo、会话号是 RFIC 会议的**身份元素，不是风格**——用户项目默认**一律不带**；本文件对它们的几何/字号
  描述仅作语料事实记录，不构成建页要求。页脚 = 纯渐变色带 + 页码即可（`assets/footer_band.png` 无品牌
  素材）；`builder.logos` 传空即不铺 logo。风格学习与复刻只覆盖排版/字体/层级/行距/图线/公式/表格/版式。
- page: 959×540 pt (16:9)，纯白背景
- 内容带: y≈95–495pt；左边距 40–73pt（图纸主导页可缩至 8–15），右缘 ≤920pt
- 页脚色带: y≈502–540pt 全宽青绿渐变（顶部黄绿细条）**色带上**：
  - 左：IEEE + MTT-S (+SSCS) 白色 logo 组（语料事实；**默认不带**，见身份元素豁免）
  - 中：页码 20–22pt（封面计 0；黑字或白字两派皆可，全片统一）
  - 右：会话号 14pt（格式如 `RMo1A-1`；语料事实，**默认不带**）
- 每页左上：RFIC/IMS 竖式 logo（x≈7–70, y≈10–115）；右上：会议徽标（语料事实，**默认不带**）
- 中西文规则、页码交叉引用：见 三、九 两节与 AGENTS.md

# 二、标题（内容页）

- 字号: **48pt 默认**；长题降档 44/40（谱系 32–48 全允许，但须在档位表内）
- 字体: **Times New Roman-Bold**（中文/东亚字符统一微软雅黑；OMML 公式保留 Cambria Math）
- 颜色: **#197084 青绿默认**（变体: #000000 黑，但全片只能选一种）
- 对齐: **居中**（94% 语料），y≈20–75 单行；**无下划线、无横线、无色条**
- 标题 = 主题名词短语或结论短句，Title Case；系列页把 `(1)`/`<1/5>` 写进标题

# 三、正文与层级（glyph→text 实测配对，档位机检以此为准）

| 层级 | 字号 | 字体/字重 | bullet | 符号颜色 |
|---|---|---|---|---|
| Lead-in 引言行 | 32pt（密集页 24–28） | Times New Roman **粗斜体**，冒号结尾 | 无 | 黑 |
| L1 主条 | **32pt**（可整条 bold） | Times New Roman regular/bold | `•` | **#197084 青绿**（黑为变体） |
| L2 子条 | **28pt** | Times New Roman | `•` 或 `–` | 同 L1 |
| L3 次子条 | **24pt** | Times New Roman | `•`/`–` | 同 L1 |
| 密集页正文 | 20/22/26/30 过渡档 | Times New Roman | | |
| 图内注释 | **16pt 主力**，14/18/20；axes≥14 | Times New Roman；密集标注可用 Times New Roman Bold | | 黑/白/红/蓝 |
| 参考文献 | 15–20pt | Times New Roman | `[n]`/`•` | 黑 |

- **行距（2026-09-15 87 deck 全量实测，基线倍率双峰 1.20×/1.45× 合计 62%）**:
  段内换行 = **1.20×字号**（图注、References、封面标题/作者换行同此档）；**bullet 条目间 = 1.44×字号**
  （等效做法 = 单倍行距 + 段后距 ≈0.24×字号：32pt→46pt、28pt→40pt、24pt 档两档皆见）。
  行距暂无机检——builder 建页必须按本档设置 lnSpc/spcAft，consolidator 构图审查时核对。
- bullet 符号与文字**同字号**；一页 L1 通常 1–3 条，行内强调用 Times New Roman Bold
- **bullet glyph 谱系**（逐 deck 目检，2026-09-15）：`•` 主流；L2 允许 `–`；方块 `■`+圆 `●`（RMo03B_3）、
  `❖`/`•`/`–` 三级（RMo04B_1）、`◆` 表头前缀、`☺` 行尾装饰、`☑☐`（Keynote 派）为语料实证变体——
  glyph 可变但**全片统一**，颜色跟随层级主色；默认仍用 `•`
- 结果短语可整段换色（蓝 #0070C0 / 红 #FF0000）；"特征 → 结果"句式中结果部分加粗换色
- 封面: 会话号 32pt 粗体居中顶部 → 全题 44pt 粗体居中 2–4 行（长题 36–40）→ 作者 24–28pt 粗体带上标
  （报告人可加下划线）→ 单位 20pt 粗体；页码从 0 计
- **中西文字体规则（全片强制，`verify_deck.py font_rules` 机检，FAIL 级）**：
  - **东亚文字**（汉字、全角标点、带圈数字①–⑤）= **微软雅黑、正体**，全片唯一 EA 字体。
  - **西文正文** = **Times New Roman**，全片只能有这一种普通西文字体。
  - **数学公式**（OMML）= **Cambria Math**，唯一允许的第三种字体；严禁给公式改字体/颜色。
- **项目变体声明（FM_IQ_Receiver_模型讲解 15 页全量版, 2026-09-14 用户 Gate 指定）**: 版式以 FM_DDC_技术分享_noDDC.pptx 为权威来源——白底, 左上深蓝 #1F3864 加粗标题(约 28pt) + 蓝色短横条 #2E75B6, 小节标题亮蓝 #0070C0, 正文 12–14pt, 关键结论黄底高亮, 页脚三段式无色带; **全片中文统一微软雅黑、西文（含公式变量的普通文本）统一 Times New Roman**, 公式为原生可编辑文本 + 真 baseline 上下标（变量斜体）, 禁公式贴图。style.json、style.techshare.json、style.zou.json 已同步字体与行距配置。
  - 混排行内"中文雅黑正体 + 西文公式 Cambria Math 斜体"合法；**数学区含 EA 码点必须显式
    `<a:ea typeface="微软雅黑">` 且 `i="0"`**（否则回退衬线——2026-09-14 事故条目）。

# 四、图与图线规格（本风格的灵魂）

- **带图内容页 ≈87%**（语料实测）；图占版面 40–85%，无边框无底色；多图公共顶边对齐
- **线宽**: 主体轮廓/曲线/箭头 **1–2.25pt**；细节 0.5–0.75pt；**生成 deck 下限 1pt**（语料原件有 0.25pt
  CAD 导出线，投屏不可读，禁止模仿）；分组/强调框 2–3pt
- **颜色语义**（跨 deck 共识，生成时必须遵守）:
  - 黑 = 主体电路/结构；**灰 #BFC0BF/#7F807F = 非激活/参考路径**（弱化但不删除）
  - 红 #FF0000 = 关键结果/警示；蓝 #0070C0/#1A6EDF = 高亮路径/改进项；橙 #DF6C0E = 第二高亮
  - 绿 #00B050 = 正向/✔；紫 #7030A0 = 条件/备选
- **虚线** = 分组框（红/深绿 dashed 圆角矩形）、域边界、外推；**点线 = sim，实线 = meas**
- 曲线图: MATLAB 默认色序 1.5pt（#0072BD #D95319 #EDB120 #7E2F8E #77AC30 #4DBEEE）
- 标注件: 白底蓝 2pt 直角框（优点列表）；红虚线框 = 放大 callout；黑双箭头 + μm = 尺寸标注；
  行尾 ✔(绿)/❌(红)；色块分组（圆角矩形底 + 白色子模块）
- **仪器截图标准画法**（逐 deck 目检实证）：截图上叠**白底黑字数值框**或黑粗体小表（RMo01A_5/RMo02B_2/
  RMo02A_2），或蓝圆角框（RMo04B_1），红/蓝游标与红色卡尺对（RMo01C_3/RTu04B_1）；关键值红字；
  手绘圈圈数据点合法（RMo01B_2）；"Educational License" 类水印是原件瑕疵，禁止模仿
- 图例: 框内右下或图外底部横排；波形条带左侧粗体彩色信号名须与对应曲线/路径同色

# 五、公式规范（Cambria Math 实测 3624 span）

- 公式一律**原生 OMML/Cambria Math**，禁止截图公式、禁止斜体 Times 假公式（语料已弃用）
- 字号: 展示公式 **24–32pt**，行内/展开 16–20pt，上下标 10–14pt（档位表内取值）
- **术语着色**: 同一推导内不同项不同色（#0070C0 蓝 / #FF0000 红=关键 / #7030A0 紫 / #00B050 绿），
  并与后文波形、框图颜色呼应；关键结果行整行红或加粗
- **步骤编号 ①②③**（18.5–24.5pt，黑/蓝/红）放公式行首或关键项上方
- **术语括线**: 公式下方大括号（黑/olive）+ 粗体短标签（"DC Term"）
- 推导链 `→`/`=` 串联；公式为主角页（J 型）版式见 §七

# 六、表格规范（对比表是标准收尾，三流派开工时选一并全片统一）

| 流派 | 表头 | 行带 | 线 | This Work 强调 | 字号/对齐 |
|---|---|---|---|---|---|
| A 学术三线表 | 白底黑粗体 | 无 | 横线 0.5–1pt，表头上下 2–3pt，无竖线 | 整列 #0070C0 蓝 | 18–22pt 居中 |
| B 黑头填色带 | **黑底白粗体** | #D9D9D9/#D3D3D3 交替 | 无网格（纯填充） | 表头字金黄 #FFC000 | 18–22pt 左对齐 |
| C 蓝头带（IMS Th01C） | #58AECA 黑字 | #D1E3EC/#EAF2F6 | 白 1pt 分隔，表头下 3pt | 行 #B3A2C7 紫 | 18pt 居中 |

- 可用行带色: 绿系 #D0E6CF/#E9F3E9、灰系 #D3D3D3/#CACACA、蓝灰 #DBE4F0/#DEEEF4、米色 #FCEADA
- 首列=参数名左对齐，数据居中；**"本工作"列/行必须视觉突出**；表下脚注上标 a/b/c + 18–20pt
- 对比表维度惯例: Technology / Architecture / Frequency / Gain/NF / P sat/OP1dB / Power / Area

# 七、版式原型（布局艺术；新建页必须落入某一原型， consolidator 按此审查）

| 代号 | 原型 | 结构要点 | 用途 |
|---|---|---|---|
| A | 左文右图 | 左 1/3 bullets，右 2/3 主图，图与 bullet 一一对应 | 默认内容页 |
| B | 双图并排 2-up | 各带小标题/各自 bullet，公共顶边对齐，中缝 x≈490 | 对比/两机制 |
| C | 满版原理图 | 图 85–100%，标题压图，旋转 90° 侧标签，色块分块 | 电路实现系列页 |
| D | 大图 + 底部 takeaway | 图占上部 70%，底部 1–2 条 "X → Y"，Y 蓝/红粗体 | 电路/测量 |
| E | 图左 + 波形条带右 | 右侧 3–4 条波形竖排，信号名颜色与左图路径同色 | 工作原理 |
| F | 概念示意 hero | 中央三角/五边形 tradeoff 图，大胆留白，中心红字命题 | Motivation |
| G | Outline 进度页 | 灰化未到项 / 灰底条+当前蓝底条 / checkbox 当前黑粗 / **当前项加粗**（RMo01A_5 等） | 每节前可选 |
| H | 对比表页 | §六三流派之一 + 脚注 | 收尾对比 |
| I | 照片页 | setup 实拍 + die micrograph 白框标注 + 尺寸箭头 + 红虚线 callout | 芯片照片 |
| J | 公式推导页 | §五规格，公式为主角，圈号步骤，括线术语 | Theory |
| K | 纯文字页 | Conclusion 3–4 条 32pt bullets；Acknowledgments + 居中 "Thank you for your attention." | 收尾 |
| L | References 页 | 15–20pt，[n] 编号 IEEE 格式 | 末页 |

- 对齐纪律: 图公共顶边对齐、bullet 左缘对齐、内容不压页脚带（内容底 ≤495 < 502）
- 密度: 一页一口令——Lead-in 或底部 takeaway 承担唯一结论；大片死区只允许出现在 F 型
- 版式配色跨页呼应: 同一信号/模块在 schematic、波形、bullet 中保持同色
- **状态两拍页**（RMo02C_5 p13→p18 实证）: 目标/痛点列表先整列红色提出；方案页复现同一列表——
  已达成项灰化 + 行右绿✓短语标注，冲突项红✗ + "Conflict" 双箭头；用于 Motivation→方案 收束

# 八、结构与节奏（87 deck 归纳）

1 封面 → 2 Outline（3–6 条 32pt，首展全黑或进度式）→ 3–N 技术主体
（Motivation → Prior Art → Theory/公式 → 电路实现系列 → 仿真 → Die Photo → 测量 setup → 分项测量 → **Comparison 表**）
→ Conclusion → Acknowledgments（必须）→ References
- 章节中途可重复插进度大纲页（G 型）；系列实现页标题 `(n)`/`<n/N>`
- Appendix/备份页合法（长 deck 常见），放 References 之后；无 disclosure/Q&A 页
- 正式讲 15–35 页；会话号 2–3 处（封面顶部 + 每页页脚右）

# 九、确定性检查（"Lean"层，先于任何 LLM 评审）

```
C:/Python314/python.exe scripts/verify_deck.py <deck.pptx> --style scripts/style.json
```
检查项：形状越界 / 图片拉伸(>5%) / 字号越档 / 越版色 / 文本溢出(启发式,WARN) / 禁用文本 / 页码一致性
        / 形状相交(**递归含组合形状**, 白名单豁免) / 页脚色带越界 / 字体规则(中英族名别名归一化 + 数学区 EA 显式声明)
        / 包完整性(断链 rels=FAIL, 孤立 media=WARN) / 公式可编辑性(OMML 数学区=INFO, 公式图片命名=WARN)。
FAIL 必须清零；WARN 逐条裁决（**档位表以第三节为准，不得临场自定**）。
回归测试：`python scripts/test_verify_deck.py`（16 个合成用例，改 verify_deck/style.json 前后各跑一次）。
配套渲染：`powershell -File scripts/export_slides.ps1 -Pptx <...> -OutDir <...>`

# 十一、建页工具箱（builder 必用，勿徒手写 COM 脚本）

- `scripts/build_helpers.ps1`（dot-source 后用）：New-Deck / Add-BlankSlide / Add-TextBox（中文走 UTF-8 文件）
  / Add-Picture / Add-FooterBand（按契约命名并放色带）/ Add-Title / Close-Deck / HexColor。
  **COM 的 Font.Color.RGB 是 BGR 字节序——十六进制色必须经 `HexColor 'RRGGBB'` 转换，直接传 0x197084 会得到反色**。
- `scripts/inject_omml.py`：raw-zip 注入 OMML 公式，自动加 a14:m 包装（命名空间 =
  `http://schemas.microsoft.com/office/drawing/2010/main`；裸 m:oMathPara 或写错命名空间 = 文件能打开但公式不渲染，2026-09-15 实测）。
  片段库 `scripts/omml/eq_*.xml`（含 EA 正体 run 样板）。
- `scripts/omml_tex.py`: **mini-LaTeX → OMML 公式生成器**（分式/上下标/根号/希腊/符号/矩阵/多行/	ext 中文正体），
  经 `inject_omml.py --tex "..."` 直接调用；回归测试 `scripts/test_omml_tex.py`（15 用例）。
- `Import-StyleProfile`（build_helpers.ps1 内）: builder 装入 style*.json 的 builder 配置块，
  Add-Title/Add-FooterBand/Add-TopLogos 自动按 profile 取字号/颜色/字体/素材——**builder 不要硬编码风格值**。
  回归测试 `scripts/test_verify_deck.py` 使用夹具 style, 不随共享配置漂移。
- `scripts/make_footer_band.py`：生成 `assets/footer_band.png` 页脚渐变色带素材。
- 风格 profile：`scripts/style.json` = 官方模板多数派（默认）；`scripts/style.zou.json` = Zou 变体
  （44pt Franklin Gothic 黑题）。项目开工时二选一并写进项目记录。
- **officecli MCP**（ZCode/Codex 均已挂载时可用）: 只读审计 `view stats|issues`、`validate`（严格 OpenXML 校验,
  会报告注入公式 a14:m 叶元素问题——PowerPoint 可正常打开渲染, 属已知可接受偏差）、`query equation` 列公式;
  编辑 `set/add` 文本形状、`--type equation --prop formula="LaTeX"` 原生增改公式（实测 OMML 往返无损、COM 可开、
  verify 0 FAIL, \mathrm 转为 m:sty="p" 顺带修正正体）。**常驻内存模型: 编辑后必须 save/close 再让外部工具读盘**;
  保存会新增 docProps/custom.xml（无害）。
- 页脚 logo（IEEE/MTT-S/RFIC）为版权素材，不入库——从既有合规 deck 提取或由用户提供，放 `assets/` 后经 Add-Picture 使用。

# 十二、形状命名契约（builder 建形状必须遵守，verify 依赖它豁免/判定）

| 名字 | 角色 |
|---|---|
| `FooterBand` | 页脚渐变色带（豁免相交检测/页脚区判定） |
| `PageNo` / `SessionId` | 页码 / 会话号（页码一致性检查只认这两类或位于色带内的形状） |
| `Footer*` / `CoverFoot*` / `CoverPage` / `CoverC` / `FooterRule` | 其他页脚件（豁免） |
| `KeyBox*` / `Capsule` / `NoteBox` / `TakeawayStrip` / `Takeaway4` / `CoverKey` | 容器/结论条（"容器盖住子元素"=FAIL 的判定对象） |
| `RowPanel<数字>` / `HLbar` / `TitleHairline` / `CoverRule*` / `CoverBG` | 装饰/背景件（豁免） |
| `Equation*` | 公式形状——**必须是 OMML 数学区**，命名成 Equation 的图片会被 WARN |

反例：页脚色带不叫 FooterBand → 全片内容被判"越页脚区" WARN；容器不叫 KeyBox* → 容器盖字检测失效。

# 十、安全管线（踩过的坑，违反即损坏文件）

1. **禁止 python-pptx 保存**（重存破坏兼容性）；编辑走 PowerPoint COM（GetActiveObject 优先），文件级修改走 raw-zip 拼接。
2. **OMML 公式形状严禁 `.Text` 赋值**（特征：TextRange 文本呈 `??` 或 Runs()==0）；公式修改只走 XML 拼接；斜体数学字符码点：𝑗=U+1D457、𝜓=U+1D713。重建公式段落的可靠方法：从同 deck 兄弟公式形状复制 `<a:p>`，替换符号 run。
3. **PowerShell 中文必须经 UTF-8 文件**：`Get-Content -Encoding UTF8`；严禁内联中文（变 ANSI 乱码，①曾渲染成"9312"）；`printf` 会吃 `\E` 转义，路径一律用 python `os.path.abspath` 写入。
4. `Get-Content` 会把含换行的字符串拆成数组——多行文本索引会错位；多行用 `[char]11` join 后整体赋值。
5. 批量修改前备份（`.bak-<标签>`）；每轮记 changelog；**修复轮上限 5 轮**，超出升级给人。
6. COM 位置赋值用 `[single]` 强转；`.Text` 赋值后字体属性会被重置，须重新设字体。
7. 每轮循环 = 改 → `export_slides.ps1` 渲染 → `verify_deck.py` → changelog 记录一行。
8. **数学区字体只有 XML 一条路**：COM `.Font.Name/.NameFarEast` 对数学区字符**静默无效**（API 读回恒为 Cambria Math，写入被忽略）；唯一生效路径是 raw-zip 拼接，把 `<a:rPr>` 里的 `<a:ea typeface="微软雅黑">` + `i="0"` 直接写进 `m:r`（2026-09-14 实测：COM 改 ea 无效，拼接生效且渲染正确）。所以"数学区文字字体不对"这类问题不要试图用 COM 修，直接按第三节规则改 XML。
9. **OMML run 粒度 = 单字符级**：数学斜体字符（U+1D400–1D7FF）与标点/空格混在同一个 `<m:t>` 里时，该 run 会被按文本字排版、字体回退导致**缺字方框**（2026-09-15 实测：`<m:t>(𝑡)| = </m:t>` 渲染成 `()| =`）。修法：拆成独立 run —— `R('(')+R('𝑡')+R(')| = ')`，与 deck 既有公式的 run 粒度一致；纯标点 run（`= `、` + `）无此问题。
10. **表格宽度 = `a:tblGrid` 的 gridCol 之和**，不是 graphicFrame 的 `a:ext`：只改 `a:ext` 表格仍按原宽渲染并溢出框（2026-09-15 实测 720→545pt 无效）。必须按比例缩放每个 `<a:gridCol w="...">`；gridCol 常带 extLst 子节点而**非自闭合**，用属性级替换 `w="旧"` → `w="新"`（自闭合模式 `<a:gridCol w="..."/>` 匹配不到）。
11. **页脚页码是静态文本**：增删页后必须逐页改 `PageNo` 的 `a:t`（"N of M"）——删除一页后 22 页每页都会报 page_number FAIL；改完用 verify_deck 的 page_number 检查全片确认。
12. **改前先查 PowerPoint 是否开着**：`~$<文件名>` 锁文件存在时 zip 拼接必失败（WinError 32）。此时要么走 COM 编辑打开中的文件，要么先 `Presentations.Close()`（先查 `$pres.Saved`，未保存则 Save）再拼接、拼完 `Presentations.Open()` 重新打开——编辑期间保持文件在 PowerPoint 中打开是用户的常态。
