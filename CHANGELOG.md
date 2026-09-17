# Changelog
## 2026-09-17 — PPT Team 修复回归、同步路径与示例交付门禁

- **同步**: `sync_user_scope.py` 在未继承 `CODEBUDDY_CONFIG_DIR` 时自动优先探测已有 `.workbuddy`，并拒绝无效 `--only` 参数；ZCode、Codex、Trae、WorkBuddy 用户级副本已重新同步并复检全 `ok`。
- **文档**: 修正 Zou profile 的字体描述，明确 Codex manifest 只原生注册技能、OfficeCLI `a14:m` schema 报告属于已知兼容项，补充根目录 `agend.md`。
- **示例重建**: 使用当前 `style.json` / `style.zou.json` 和 PowerPoint COM 重建 `FM_IQ_Receiver_RFIC2024.pptx`（19 页）与 `mvp_zou.pptx`（3 页）；FM 构建脚本现在自动执行 `build_eq.py`，恢复第 9 页旋转公式组；MVP 构建脚本自动注入第 3 页噪声因子 OMML 公式。
- **渲染与验证**: `export_slides.ps1` 现在将输入 PPTX 和输出目录解析为绝对路径；FM verify = **0 FAIL / 0 WARN / 7 INFO**，Zou verify = **0 FAIL / 2 WARN / 4 INFO**（两项 WARN 均为 `LogoLeft` 图片留白造成的图片×标题假阳性，视觉验收裁决通过）。
- **视觉门禁**: 当前渲染图经 `ppt-judge` 复审，FM 19/19 页、Zou 3/3 页通过；残留致谢/参考文献占位和 FM 第 7 页单位换行均为非阻断提示。
- **回归**: `test_verify_deck.py`、`test_omml_tex.py`、`sync_user_scope.py --check` 全部通过；备份保存在 `_backups/repair-20260917-171218/` 与 `_backups/repair-20260917-174500/`。

## 2026-09-17 — PPT Team 接入 WorkBuddy（自定义子代理通道，五个角色落盘 + 工具白名单）

- **安装位置**: `C:\Users\wanglei\.workbuddy\agents\`（用户级 = 全项目可用），新增 `ppt-team.md` / `ppt-architect.md` / `ppt-builder.md` / `ppt-consolidator.md` / `ppt-judge.md` 五个文件。**真源 = 仓库 `adapters/workbuddy/agents/`**（随仓库版本化），经同步脚本单向部署。
- **同步脚本**: `scripts/sync_user_scope.py` 新增 WorkBuddy 目标 + `--only zcode|codex|trae|workbuddy` 单通道开关；`--only workbuddy` 已实跑（5 文件 synced，复检全 `ok`）。全通道 `--check` 另报存量 DRIFT 2 处（ZCode/Trae 的风格法典副本未随法典更新重分发），本轮**未**擅自全量同步。
- **路径依据**（从 `resources/app.asar.unpacked/cli/dist/codebuddy.js` 提取的常量）: `getHomeAgentsDir() = (CODEBUDDY_CONFIG_DIR || ~/.codebuddy)/agents`；`getProjectAgentsDir() = <WorkDir>/.codebuddy/agents`（项目级优先级更高）。本机 `CODEBUDDY_CONFIG_DIR = C:\Users\wanglei\.workbuddy`。
- **设计**: 文件为薄适配层——内置公共声明（PLUGIN_HOME 绝对路径）+ 职责摘要 + 硬边界，正文强制要求先完整读取仓库真源 `agents/<角色>.md` 与 `skills/ppt-conference-style/SKILL.md`，避免两份提示词漂移。
- **工具白名单即纪律**: builder=Read/Write/Edit/Glob/Grep/Bash/PowerShell（pptx 唯一写者）；consolidator=Read/Glob/Grep；judge=Read/Glob；architect=Read/Write/Glob/Grep；conductor 额外持有 Agent/AskUserQuestion/Task*。
- **验证**: 实跑派发 `ppt-judge` 成功——角色可被发现、可读取自身定义、工具白名单生效（只读）。磁盘新增子代理按官方语义于下次会话加载。
- **文档**: 新增 `workbuddy_custom_agents_ppt_team.md`（发现规则表 / 安装清单 / 用法 / 可选插件通道 `.codebuddy-plugin/plugin.json` / 四宿主对应关系）。
- **说明**: 未创建 `.codebuddy-plugin/plugin.json`——插件通道与用户级安装会产生同名重复代理，当前只开用户级通道。

## 2026-09-17 — PPT Team 工具层字体与行距默认值

- **建页工具**: `scripts/build_helpers.ps1` 新增 `Get-TypographyVal` / `Set-ParagraphSpacing`；`Add-TextBox`、标题和页脚默认应用段内 1.20× 行距、0.24× 段后距（bullet 基线节奏约 1.44×）。
- **字体默认**: 三份 style profile 和 COM 建页默认统一中文/东亚字体为微软雅黑、西文为 Times New Roman；OMML 数学区继续使用 Cambria Math。
- **自动检查**: 生产 style 的普通西文白名单收紧为 Times New Roman；回归测试夹具保留历史字体，仅用于验证几何/包完整性/违规检测机制。
## 2026-09-16 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx（勘误轮：6 处换图 r20 + 8 处文本修订 + 页码引用重映射，COM 编辑）

- **备份**: `*.pptx.bak-errata-20260916`（2459705 字节。**偏差**: 任务称 PowerPoint 打开中，实测 POWERPNT 未运行、无锁文件——按管线 §十.12 改用 COM 新启实例 Presentations.Open 挂载编辑，结束后保持打开不关进程；备份为磁盘当前态纯复制，无未保存内存态需先 Save）。
- **换图 6 处**（Shapes.AddPicture 重建、名字沿用、ZOrder 逐个回位，media sha1 经 python-pptx 只读核验与源 PNG 逐一相等）: 页 9 PicStage1→crop_stage1_r20.png（旧 500/197/420/158 Z12 宽扁切块 → 新 556.46/150/277.08/268，AR 1.0339 零拉伸，右栏 470–920 居中）；页 10 PicSpec→F_z1_spectrum_r20.png（64/150/424/259 原位，拉伸 +1.59%）；页 12 PicStage2→crop_stage2_r20.png（**实际只有一张图**，非任务所述两张 → 新 606.74/150/256.53/268 零拉伸）；页 14 PicBB/PicMir→F_bb_on/off_r20.png（各自原位，拉伸 +1.7/+1.8%）；页 16 PicEnvr19→F_bb_ripple_r20.png（245/140/470.1/252 原位，+0.12%）。**偏差**: A1/A3 图高取 268pt（任务建议 ≈300/275）——图注须落在图底与 takeaway(y438) 之间，268 为不压图注/不压 takeaway 的最大可行高；页 9/12 图注分别移至 515/420、607.5/419 随图居中。
- **文本 8 处**（全部经 UTF-8 JSON 传入，.Text 赋值后逐处重设 Times New Roman/SimHei + 原字号，读回校验 old 全匹配/new 逐字等于预期）: B1 页 2 四条大纲页码 P4–P5→P5–P7、P6–P8→P8–P10、P9–P13→P11–P16、P14–P16→P17–P19（run 级替换）；B2 页 9 边带条改为「均在 IF LPF 通带内，倾斜显著：600 Hz 已 −3.75 dB（f₃dB≈562 Hz，伏笔 → P16）」（原两段并一段）；B3 页 12「有用（DC±250 Hz，Carson）在通带内（f₃dB=241 Hz）…」；B4 页 12 takeaway「放行有用（DC±250 Hz），拒止 −800 Hz 镜像」；B5 页 13 takeaway P4→P5；B6 页 15「幅度起伏 ±27.4%（下页归因）」；B7 页 16「：|H(600)|=0.649 vs |H(200)|=0.993」；B8 页 20 表格 R9C3/R10C3 加注 f₃dB≈562/241 Hz。
- **微修**: 页 9 Bullets 文本框 H 195.58→235（新 B2 变长触发 overflow 启发式 WARN est216>196；加高后消除，框右缘 495<图注 515 无碰撞）。
- **verify**: 21 页 = **1522 FAIL / 33 WARN**；对备份基线同脚本实测 1472 FAIL / 33 WARN（任务给的 1466/34 与备份实测略有出入，以备份实测为权威），增量 **+50 FAIL 全部为 font_rules 白名单存量类**（Times New Roman/黑体不在 style.json 白名单），恰好分布在本轮改文本的 6 页（2:+8/9:+10/12:+12/13:+8/15:+4/20:+8，新文本 span 增多所致），**非 font_rules FAIL 为 0**；WARN 总数与基线持平（页 9 溢出 WARN 已修，其余 overflow/palette/font_tier 均存量），无新增相交/拉伸/越界/page_number 问题。
- **验收**: 9 张改动页渲染图（`FM/render_fontfix2/errata_slide_{2,9,10,12,13,14,15,16,20}.png`，1600px）逐页目检全过——Stage1 六块/Stage2 十块完整无切块、图注随图居中不被压、±/≈/−/₃/①–④/ψ 无字体回退、页 2 Bul3 因 +1 字符换行至第二行但与 ④ 行留白无碰撞、页码引用与实际内容页一致（P5=发射端理论、P16=体检 II 归因）。脚本 `_ppt_run/errata_20260916/`（errata_edit/fix9/render.ps1 + errata_verify.py）。
## 2026-09-16 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx（鉴频器实现页左侧 bullet 文案重写，COM 锁内单形状文本手术）

- **备份**: `*.pptx.bak-disc-redesign-20260916`（GetActiveObject 挂运行实例先 Save 落盘再复制，2459288 字节；失败即中止路径已验证——首轮脚本在 TextRange2.IndentLevel 处抛错中止，未触碰文本）。
- **改动（仅 1 个形状）**: 目标页按「FM_dI_dt」文本定位 = PowerPoint 索引 18（标题「鉴频器实现：Δ 支路 + I²+Q²+ε」，环节④徽章/进度条④/页脚 "18 of 21"），左侧形状 [Bullets]（L40/T225/W420/H150）旧文 250 字符单段软换行整段替换为 4 段一级 bullet（Δ 支路微分 / 分子 Num / 分母 Den / 输出定标，逐字含全角标点、Δεφπ、U+2212、上标²），中文经 UTF-8 文件（disc_newtext.txt）传入；沿用全片字面 `• ` 前缀惯例（auto-bullet 关闭不变），段落属性按改前快照恢复（align=1、段后 1pt、行距 1.09677 行），段属性用 v1 API（TextFrame.TextRange）设置——TextRange2 无 IndentLevel 属性（首轮教训）。
- **字体/字号**: .Text 赋值后 48 个 run 全部重设 Times New Roman / NameFarEast=SimHei；字号按任务规程溢出降档 16.5→15.5pt。**残余溢出如实报告**: 15.5pt 下 TextFrame2 BoundH=165.01 > 框高 150（verify 启发式 est 188 > 150），末行落入框底下 ~15pt 空白区——无裁切、无碰撞（takeaway y438 未被触及）、未再压版式或行距（任务降档阶梯止于 15.5，动框高/行距超出本轮范围）。后续修复建议：删「（ε=1e−6 防除零）」或行距降 1.0 可回收约 2 行。
- **核验**: Save 落盘（2459489 字节）+ python 只读核盘 slide18.xml：4 个 a:p、0 个 a:br、48 run 全 sz="1550"+Times New Roman+SimHei、U+2212×3、全文与任务文案逐字一致；verify_deck 21 页 = **1466 FAIL / 34 WARN / 44 INFO**，FAIL 增量 +32 与 WARN 增量 +1 全部为该形状新 span 的 font_rules 白名单误报与溢出启发式（est>box），slide 18 无任何相交/越界/拉伸/断链/页码类新增。
- **验收**: 本轮无 ppt-judge 工具，以 Slide.Export 1600px 目检代验收（`FM/render_fontfix2/disc_text_slide_18.png`）——4 条一级 bullet 缩进整齐、无子行，Δ/ε/φ/π/²/−/×/→/①④ 全部正常渲染无字体回退缺字，右侧模型图/图注/takeaway/页脚零牵动。通过页 = 18（残余溢出已报告，视觉可接受）；回炉页 = 无。脚本 `_ppt_run/assets/disc_edit.ps1` + `disc_fixup.ps1`。
## 2026-09-16 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx（基带体检两页三图字节级换新 r19 重导出版，几何冻结，无新备份）

- **换图**: 按 judge 意见重导出的三张 r19 PNG（图例改「半峰峰参考」、字号 +1pt、时域 ylim 放宽）原位换入——页 15 PicIQr19/PicTrajr19、页 16 PicEnvr19，COM GetActiveObject 删旧 AddPicture 重建，名字/z 序沿用；无新备份（沿用 .bak-bbsplit-20260916），几何/文本/页码零改动。
- **核验**: 三形状几何前后逐值一致（147.6/140/397.7/252、565.3/140/247/252、245/140/470.1/252 pt，Z=13/14/12），Save 成功；python 只读核盘 rels sha1 与源 PNG 逐一相等（media image28/29/30），拉伸 ≤0.009%，无孤立 media；verify_deck 21 页 = 1434 FAIL / 33 WARN / 44 INFO 与上轮基线逐字持平（零增量）。
- **目检**（本轮无 ppt-judge，Slide.Export 1600px 目检代验收，渲染 `FM/render_fontfix2/bbA_slide_15.png`、`bbB_slide_16.png`）: 页 15 左图图例已移出坐标区上方、不再压 I(t) 峰顶；页 15 右图与页 16 图例均出现「1±0.274 半峰峰参考」。通过页 = 15、16；回炉页 = 无。脚本 `_ppt_run/assets/bb_imgswap.ps1`。
## 2026-09-16 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx（基带体检页拆分 + 三图换新 r19 + 全片页码重排，COM 锁内结构手术）

- **备份**: `*.pptx.bak-bbsplit-20260916`（GetActiveObject 挂运行实例先 Save 落盘再复制，20 页当前态 2399701 字节；拆前总页数 20，页脚静态页码漂移为 "N of 19"——并行会话插页遗留，本轮一并修正）。
- **拆页**: 目标页按标题定位（「基带体检：正交对 · 圆轨迹 · 包络纹波」，PowerPoint 索引 15、页脚 "14 of 19"），Slide.Duplicate() 产生索引 16 副本；A 页（15）= I/Q 时域 + 矢量轨迹两图 + 新正文/takeaway，B 页（16）= 包络纹波单主图 + 原纹波正文 + 原 takeaway。B 页节徽章「3」与进度条③高亮随复制保留。
- **换图**: 三张 r19 新图删旧建新（Shapes.AddPicture 原位重建，名字 PicIQr19/PicTrajr19/PicEnvr19），几何按实测像素零拉伸放回——A 页 PicIQr19 147.6/140/397.7/252（AR 1.5782）、PicTrajr19 565.3/140/247/252（AR 0.9802）；B 页 PicEnvr19 245/140/470.1/252（AR 1.8656）。任务建议的 292/332pt 图高与页上正文行(y398)+takeaway(y438) 家具冲突，按"图注随图下、不压正文/takeaway、不越 495"重推最大可行高 252pt；正文/takeaway 两页统一微调至 y420/y448（takeaway 高 54→44，底 492<495）。python-pptx 只读核对：三图 rels sha1 与源 PNG 逐一相等。
- **文字**: 全部新文本经 UTF-8 文件传入（bb_strings.json），.Text 赋值后统一重设 Times New Roman/SimHei、字号取原值。**偏差一项**: B 页标题 40/36pt 实测均折行（BoundHeight 96/86 > 64，会压进度条），按档位表降档 32pt 后单行（BoundHeight 38）。
- **页码重排**: 拆后 21 页逐页 PageNo 改为 "实际索引 of 21"（含旧漂移修正与第 5/6 页并行会话重复页的顺延编号），字体保原值 + NameFarEast=SimHei。
- **verify**: verify_deck.py 21 页 = **1434 FAIL / 33 WARN**，基线 1358/33（20 页）；增量 +76 全部为同款 font_rules 白名单误报（新页 60 + 页 15 新文本 span 增多 16），page_number 检查 0 条问题，15/16 页无任何相交/拉伸/越界/溢出类新增，WARN 总数与类别与基线持平。
- **验收**: 本轮无 ppt-judge 工具，以 Slide.Export 1600px 目检代验收——A/B 两页渲染逐项过：新图无拉伸、图注居中随图、标题/正文/takeaway 无字体回退（④/±/≈/上标² 正常）、无形状重叠、页脚 "15 of 21"/"16 of 21" 正确。渲染图 `FM/render_fontfix2/bbA_slide_15.png`、`bbB_slide_16.png`，脚本 `_ppt_run/assets/bb_surgery.ps1`。
## 2026-09-16 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx（z₁ 星座图资产换新 r18，COM 锁内单图替换）

- **备份**: `*.pptx.bak-const-redraw-20260916`（文件被 PowerPoint 写锁——先 GetActiveObject 对运行实例 flush-Save 落盘再复制，20 页当前态，2408923 字节）。
- **改动（仅 1 张图）**: z₁ 星座图页（PowerPoint 索引第 10 张；静态页码 "9 of 19"=任务口径第 9 页，deck 被并行会话插页至 20 张）右侧 `PicConst` 删除后 `Shapes.AddPicture(F_z1_constellation_r18.png)` 原位重建——几何 570/150/261/265 pt、Z=13、形状名逐一保留；新图 1074×1094 (AR 0.9817) 入旧框 (AR 0.9849) 拉伸 0.33% < 5% 阈；盘面核对 slide10.xml 几何精确一致且 image20.png sha1=42de03dc7c54 与新 PNG 相等；同页其余 12 形状逐项比对零差异。全程 COM 改内存对象 + Presentation.Save()，未关/未重启 PowerPoint，未用 python-pptx/zip 写盘。
- **verify**: 改动前后 verify_deck.py 输出逐行零差异（同为 1358 FAIL/33 WARN——全部既有：共享 style.json 白名单未含本项目 Times New Roman+黑体 变体导致整片字体误报 + page_number "9 of 19" vs 20 张口径项，后者为并行会话插页遗留，本轮未动）；图片相关检查（拉伸/相交/越界/断链/孤立 media）两轮均干净。
- **验收**: 本轮无 ppt-judge 工具，以 Slide.Export 1600px 目检代验收——星座图已是新版（深蓝散点 + 蓝虚线内外双圆 + 灰点线平均半径圆 + 白底蓝框标注 + 右下图例），频谱/标题/图注/takeaway/页脚零牵动；渲染图 `FM/render_fontfix2/slide_10.png`，脚本 `_ppt_run/assets/replace_const_r18_v2.ps1`。


## v0.3.6 — 2026-09-16（接入 Trae Work）

- **Trae Work 接入**: 扩展 `scripts/sync_user_scope.py`，把 PPT Team 安装为 Trae Work 用户技能——
  `~/.trae-cn/skills/ppt-team/SKILL.md`（生成 Trae 适配副本：frontmatter 后插入 `PLUGIN_HOME` 绝对路径声明，
  并把 Codex 特有措辞改写为 Trae Work 派发写法——无一等 `agents/` 团队对象，由本技能派工读 `agents/*.md`，
  写入串行单写者纪律保留）+ `~/.trae-cn/skills/ppt-conference-style/SKILL.md`（风格法典原样复制）。
  Trae Work 自动发现 `~/.trae-cn/skills/` 下的技能目录，应用设置里可见即用。
- 真源仍为本插件目录，`--check` 可查漂移；新增目标不触碰 `installed-plugins.json`/`plugin-config.json`（不注册为
  marketplace 插件，走用户技能通道，可随时删除目录即卸载）。
- **正式插件登记裁决（不造假）**: 核验 Trae 运行时约定——`installed-plugins.json`/`plugin-config.json`/插件目录
  `.success` 由市场安装流程生成、含服务端校验和与市场 ID（如 remote_installed_plugin_id/checksum），不能手写复现，
  硬塞会让插件管理器状态错乱，故不伪造登记。改为 Trae 官方支持的自定义智能体通道：产出 `trae_custom_agents_ppt_team.md`，
  内附四个角色（ppt-architect/builder/consolidator/judge）的**英文标识名 + 何时调用 + 提示词**配置，供用户在
  `@`→创建智能体→手动创建 里粘贴导入，勾选"可被其他智能体调用"后由 Agent/ppt-team 按阶段调度。

## v0.3.5 — 2026-09-15（逐 deck 风格档案 87 份 + 拼图目检积淀）

- **逐 deck 档案新增**（用户指定"逐个学习每个 PPT"）: `_learnings/perdeck_profile.py` 对语料 87 份 PDF
  逐份实测 8 维度——西文字体族与粗斜变体、标题/封面/三级层级字号与 bullet 色、行距（分字号档中位倍率）、
  公式（Cambria Math span 数/字号/颜色/圈号）、图线（描边直方/主体线宽/≥2pt 强调占比/dashed）、
  图注下限、表格线与填充、版式（边距/图覆盖/页脚带/logo）。产出 `perdeck_profiles.json`（机读）+
  `RFIC2024_perdeck_profiles.md`（一 deck 一块）。
- **逐 deck 拼图存档**: `render_perdeck_sheets.py` 每份 deck 自动挑 6 代表页（封面/大纲/最大图/公式页/
  对比表页/密集正文页）拼 2×3 图，87 张全量存 `perdeck_renders/`；20 份代表 deck 逐张目检
  （覆盖全部字体派/大纲各派/对比表各流派/满版/波形条带/✔❌页/离群模板），
  注记 + 10 条跨 deck 目检新发现写入档案 MD 文末（公式页三位一体、状态两拍页、This-work 强调器件谱系、
  仪器截图标准画法、bullet glyph 谱系、手绘注释语汇、报告人下划线实证、RMo04B_1 溢出 bug 实证、
  die photo 标注四件套、配色跨页呼应）。
- **SKILL.md 同步（规范先行）**: 〇节挂逐 deck 档案指针；§三补 bullet glyph 谱系（全片统一原则）；
  §四补仪器截图标准画法（白底数值框/蓝圆角框/红卡尺/禁水印）；§七 G 型补"当前项加粗"第四派 +
  新增"状态两拍页"版式模式（RMo02C_5 p13→p18 样板）。
- 检测修正: 页脚渐变带在语料中多为位图条（非矢量填充）、RFIC 左上 logo 常出血到页外——
  profiler 检测逻辑已按真实几何修正后全量重跑，RMo01B_2 校验与旧目检笔记一致。
- **身份元素豁免（用户指令）**: RFIC/IMS logo、会议徽标、IEEE/MTT-S/SSCS 页脚 logo、会话号是会议身份
  不是风格，用户项目默认一律不带。SKILL.md §一新增豁免条款（语料几何描述降为事实记录）；
  style.json 默认 builder.logos 置空、footer.band 改指无品牌渐变带 assets/footer_band.png
  （footband_2024.png 等品牌素材仅语料复刻经用户确认后可用）；逐 deck 档案 MD 头部同注。
  sync_user_scope.py 已同步；test_verify_deck.py 回归 0 FAIL。

## v0.3.4 — 2026-09-15（行距档位纳入法典 + 版本回退铁律）

- **新增硬性禁令 5（用户指定）: 禁止擅自回退版本**——git reset/checkout/revert、恢复 `.bak-*`、旧版整片重建、回滚规范配置，一律先征得用户同意；修复走"向前修"（改→渲染→verify→judge）；严禁用回退清理并行会话改动。落点: AGENTS.md（禁令 5, 流程纪律重编号 6–9）、agents/ppt-builder.md、skills/ppt-team/SKILL.md（已 sync 至 Codex）。
- **行距双档规则实测并写入 SKILL.md 第三节**: 87 deck 全量扫描（tmp/measure_corpus_line_spacing.py,
  段内基线对过滤上下标）→ 倍率双峰 1.20×(34.3%)/1.45×(28.0%)。**段内换行 = 1.20×字号**（图注/References/
  封面标题换行）; **bullet 条目间 = 1.44×字号**（32pt→46pt、28pt→40pt; 等效 = 单倍行距 + 段后 ≈0.24×字号）。
  24pt 过渡档两档皆见; 44pt 标题换行 1.20×。Zou 深测样本同规（RFIC_Zou_CTTF_constraints.md 补行距节）。
- 测量记录同步: _learnings/RFIC2024_corpus_constraints.md（跨 deck 分字号统计）、RFIC_Zou_CTTF_constraints.md（28 页逐档）。
- 行距暂无 verify_deck 机检项（后续可加 lnSpc/spcAft 检查 + 夹具回归）; 现阶段 builder 按档自检, consolidator 构图审查核对。

## v0.3.3 — 2026-09-15（接入 officecli MCP 编辑通道）

- **officecli MCP 正式列为第三条合规编辑通道**（此前仅 COM + raw-zip）。往返实测（MVP deck 副本）:
  `set` 文本、`--type equation --prop formula` 原生增改公式 → OMML 幸存（m:oMath=1, m:r 18→20, \mathrm 转 m:sty="p" 顺带修正正体）
  → COM 可正常打开渲染 → verify_deck 仍 0 FAIL。仅新增无害的 docProps/custom.xml。
- **常驻内存纪律**（新增硬性规则）: officecli 编辑后必须 save/close，verify_deck/export_slides/COM 才允许读盘；
  officecli 常驻也算写者，纳入"写者唯一"约束。
- 审计能力入册: view stats|issues、validate（严格校验会报注入公式 a14:m 叶元素问题——PowerPoint 渲染正常,
  已知可接受偏差）、query equation。
- 同步更新: AGENTS.md 禁令1、agents/ppt-builder.md、SKILL.md 工具箱、Codex 适配技能（并重装到 ~/.codex/skills）。

## v0.3.2 — 2026-09-15（Codex 接入）

- 安装 ppt-team 到 Codex CLI(0.144.6): `~/.codex/skills/ppt-team/SKILL.md`（由仓库
  skills/ppt-team/SKILL.md 生成, frontmatter 后注入 PLUGIN_HOME 绝对路径声明, 可从任意工作目录触发）
- 新增 `~/.codex/prompts/make-ppt.md` 斜杠命令（流水线七步纪律 + $ARGUMENTS）
- 全局 `~/.codex/AGENTS.md` 增加触发指引（PPT 任务优先 ppt-team 技能）
- sync_user_scope.py 扩展双目标: ZCode SKILL.md + Codex ppt-team SKILL.md（--check 可查漂移）
- 仓库侧适配(并行会话先期完成, 本次收编): .codex-plugin/plugin.json 清单 + skills/ppt-team/SKILL.md 角色映射
  （Codex 单代理顺序扮演四角色, 写入串行, 只读任务才可并行）

## v0.3.1 — 2026-09-15（第二轮：Zou profile 建页能力 + 公式生成器 + 首个完整交付案例）

- **C10 永久修复**: 测试改用夹具 style(默认配置减 Times), 钉住机制而非配置值——不再随 style.json 的并行修改漂移;
  默认白名单再次收回 Times(并行会话曾加回), 裁决与 techshare profile 见 v0.3.0。
- **builder 读取 style profile**: style*.json 新增 builder 配置块(标题字号/颜色/字体/位置, 页脚素材与颜色, logo);
  build_helpers.ps1 新增 Import-StyleProfile/Get-ProfileVal/Add-TopLogos, Add-Title/Add-FooterBand 按 profile 取默认值;
  页脚色带按图片原始比例自动适配(防拉伸 FAIL); COM 图片路径绝对化。
- **LOGO/页脚素材**: 从用户合规语料 PDF 提取 —— assets/zou/footband.png(Zou 色带含 IEEE/MTT-S/SSCS 白标+DENVER2022,
  烤入文字已按 bbox 垂直插值修补) + rfic_logo.png; assets/footband_2024.png + badge_2024.png + rfic_logo_2024.png(2024 版)。
  仅供个人/内部学术使用, 不随仓库公开分发。
- **omml_tex.py**: mini-LaTeX→OMML 生成器(分式/上下标/根号/希腊/常用符号/	ext 中文正体/\left-
ight/matrix 族/多行),
  inject_omml.py 新增 --tex 直通与 --size; test_omml_tex.py 15 用例全绿。
  过程中实证: PPTX 数学必须 a14:m(drawing/2010) 包装; 注入形状必须带 <p:nvPr/>(缺失=PowerPoint 拒开)。
- **首个完整交付案例 examples/mvp_zou/**: 内容清单实例 + 数据来源表实例 + agenda + build.ps1(Zou profile)
  + mvp_zou.pptx(3页, 原生可编辑公式) + 渲染图 + verify_report.json(0 FAIL) + judge_report.json(3 pass,
  含第1轮 slide2 bullet 乱码 FAIL→回炉→复审 pass 的真实双门禁记录)。

## Codex adapter — 2026-09-15

- Added `.codex-plugin/plugin.json` without changing the existing `.zcode-plugin` manifest.
- Added `skills/ppt-team/SKILL.md` to map the ZCode architect/builder/consolidator/judge workflow to Codex.
- Codex loads the adapter through `skills/`; the original `agents/` and `commands/` remain reference material because their ZCode manifest fields are not Codex-native plugin fields.
- Codex plugin validation passed with the WorkBuddy Python runtime. Global marketplace installation is intentionally separate from this repository-layer addition.

## v0.3.0 — 2026-09-15（修复轮：双评审问题落地）

### verify_deck.py（验证器修复，16 用例回归全绿）
- 字体中英族名**别名归一化**：微软雅黑 = Microsoft YaHei；latin 槽允许 EA 族（混排运行）。修复此前把自家 COM 产物判 FAIL 的数百条误报（真实 deck 实测 925 FAIL 中 ~200 条 YaHei 误报清零）。
- **页码检查重写**：页码候选 = 形状名命中页脚白名单 或 底边伸入色带；`footer_regex` 锚定整串（`^(page[ ]*)?[0-9]+([ ]*(of|/)[ ]*[0-9]+)?$`）。修复 "31/0.5" 之类表格值被误判为页码 FAIL 的假阳性。
- **相交检测递归进组合形状**（grpSp 按 chOff/chExt 映射绝对坐标）——成组形状不再逃过检测。
- 新增**包完整性**检查：断链 rels=FAIL（真实 deck 实测抓出 44 处丢图）、孤立 media=WARN。
- 新增**公式可编辑性**检查：OMML 数学区=INFO、命名 Equation*/Formula* 的图片=WARN。
- 字号档位补 14pt（语料第 4 大档，此前缺档）。

### builder 工具箱（新增，端到端冒烟验证通过）
- `scripts/build_helpers.ps1`：COM 建页函数库。冒烟建 2 页 deck → 渲染 → verify 0 FAIL 全链路通。
  内置 `HexColor` 修正 COM 的 BGR 字节序（直接传 0x197084 会变反色 #847019，实测踩坑）。
- `scripts/inject_omml.py` + `scripts/omml/eq_*.xml`：OMML 公式注入。实测确认 PPTX 数学必须包
  `<a14:m xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main">`（裸 m:oMathPara 或命名空间写错=能打开但不渲染）；
  注入形状必须带 `<p:nvPr/>`（schema 必需，缺失=PowerPoint 拒开）。渲染目检：分数/斜体变量/正体中文正确。
- `scripts/make_footer_band.py` → `assets/footer_band.png` 渐变色带素材。

### 流程/文档
- **写入串行纪律**写进 make-ppt.md / ppt-team.md / AGENTS.md：同一时刻只允许一个 builder 持有 .pptx 句柄。
- SKILL.md 新增 第十一节（建页工具箱）、第十二节（形状命名契约）；第九节更新检查项与回归测试要求。
- 新增 `templates/content_manifest.md`（内容官产出合同）、`templates/data_provenance.md`（技术数据来源表，Gate C 必查）。
- 新增 `scripts/test_verify_deck.py`（16 用例回归集）与 `scripts/sync_user_scope.py`（用户作用域单向同步）。
- 风格 profile 拆分：`style.json`=官方模板多数派（默认）、`style.zou.json`=Zou 变体（44pt Franklin 黑题）。
- 修正学习档案：Zou deck p25 实为 Comparison 对比表（"全场零表格"系早期误读）。
- 卫生：备份收拢至 `_backups/<标签>/`；plugin.json 版本 0.1.0 → 0.3.0。

### 与并行工作流的冲突裁决
- 修复期间发现并行会话把 `Times New Roman` 加进了默认 style.json 白名单（为放行 AM_DDC 技术分享 deck）。
  裁决：默认法典保持纯净（Times 已移出），新增 `scripts/style.techshare.json` 宽松 profile 供非会议 deck 使用
  ——会议风格项目用默认/Zou profile，技术分享项目用 techshare profile。

### 明确不做的（诚实边界）
- verify_deck.py **查不了**技术数值真实性、图表拓扑、公式内容正确性——由 templates/data_provenance.md + Gate C 人工终审兜底。
- IEEE/MTT-S/RFIC logo 为版权素材不入库，需从合规 deck 提取或用户提供（放 `assets/`）。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 全量新建（builder / ppt-builder 代理）
- **deck**: `FM\FM_IQ_Receiver_Basic_模型讲解_会议版.pptx`，18 页（封面/大纲/总览 + 四环节公式·实现·验证 + LPF 双图 + 基带体检三图 + 参数表 + 总结），按 `_ppt_run/build_brief.md` 逐页构建，PowerPoint COM 管线（build_helpers + build_common）+ raw-zip 注入 OMML。
- **verify**: `verify_deck.py --style style.techshare.json` → **0 FAIL / 0 WARN / 6 INFO**（INFO 均为公式可编辑性提示，13 个原生 OMML 数学区分布在 P1/P4/P6/P9/P12/P14）；渲染 18 张 PNG 至 `FM\_ppt_run
enders`。
- **关键修复**：① COM 文本框 AutoSize 自动增高导致 Cap×Takeaway 相交 FAIL → 全片 AutoSize=0 并复原 Cap 高度；② PageNo 框 70→80pt 消除两位数页码溢出；③ #595959（brief 指定图注灰）补进 style.techshare.json 色板；④ omml_tex 对 `\int`/`\hat`/`z₂=`/`I²+Q²`/`\{\}` 存在静默错译 → 改手写 OMML 片段（m:nary/m:acc）经 `--omml` 通道重注 10 处公式；⑤ slide13 圆图注右移出图 bbox。
- **坑位记录**：PowerPoint COM 以 WithWindow=msoFalse 打开的演示文稿，`SaveAs(同路径)` 会**静默不写盘**（Saved 仍为 0）——分段建页必须用 `Save()+Close()`（build_common.ps1 Close-DeckSafe）；表格单元格在 PS COM 下 `Cell.TextFrame/Fill` 为 null，须走 `Cell.Shape.TextFrame/Shape.Fill`。
- 视觉质量评审未做，交 consolidator/judge。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 修复轮 round 2（consolidator 意见）
- **改前备份**: `*.pptx.bak-round2`。**改动页**: P1/P5/P7/P10/P13/P15/P18（7 页）。
- **必修落地**: P13 takeaway 收窄居中 (200,450,560,44)、包络图右移上移 (770,396,150×84) 并补图注 `包络纹波（sim.）`@482；P18 大框内四行行距拉开至 y=153/222/291/360；P10 新增全宽 takeaway 带 (130,438,700,54)、bullet 3 手动断行消除"增益"跨行、4 条 bullet 拉开至 y=200/255/310/365。
- **建议同步落地**: P15 bullet 悬挂缩进（续行 4 空格）+ 新增 takeaway `分母 I²+Q²+ε 天然抵消包络纹波` + 右图 280×278.9；P7 bullet1/3/4 手动断行 + 行距 45pt（y=150/195/240/285）；P1 行③④结果列右移对齐 x=592 竖列 + EQ_DISC 16→14pt 重注；P5 右图 417×267 + 图注上移（与 takeaway 净空 15pt）+ bullet1 断行点前移。
- **round2 追加修复**: 新建形状未关 AutoSize 导致 Cap3 底边 505 越页脚 + 3 个 15pt 图注估溢出 → 全片再关 AutoSize、图注高统一 16pt；P7 bullet 框(右缘470)压图 10pt → 示意图右移至 x=470。
- **verify**: **0 FAIL / 0 WARN / 6 INFO**（同 round1，公式可编辑性提示）；渲染**全片重出** 18 张至 `FM\_ppt_run
enders`。
- **坑位补充**: PowerPoint COM 保存会把 a14:m 公式包进 `mc:AlternateContent`（Choice+Fallback 双 cNvPr）——按 cNvPr 计数会翻倍，以 `<m:oMath>` 计数为准；对公式形状做正则删除时非贪婪 `.*?</p:sp>` 只会删掉 Choice 分支留下 Fallback 残影（round1 双影根因）。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 修复轮 round 3（judge 终审 16/18，修 P13/P15）
- **改前备份**: `*.pptx.bak-round3`。**改动页**: P13/P15。
- **P13**: 按资产更新，raw-zip 字节级替换 `ppt/media/image23.png`（PicCircle 专属 media，仅 slide13 引用）为新版 `F_iq_circle.png`（1117×1099, ar=1.0164，图内"一阶"改"4 阶"+注释白底）；页内位置/尺寸/形状名不变（250×246.1，摆放比差 0.05% 远小于 5% 拉伸阈）。
- **P15**: cap_rx_disc 等比缩宽 280→270×268.9（底 408.9），图注上移至 y=411（底 427），与 takeaway 框顶 438 净空 11pt（原 1pt，judge 阈 ≥8px）。
- **流程坑**: deck 当时被 PowerPoint 占用（用户开着评审）——按 SKILL.md §10.12 走 COM 编辑已打开副本→Save+Close→再 raw-zip 换 media；shutil.move 换成 os.replace 落盘。
- **verify**: **0 FAIL / 0 WARN / 6 INFO**（公式可编辑性提示，与前轮一致）；渲染全片重出 18 张。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 修复轮 round 4（用户反馈：SA 实拍图 + 子标题加粗）
- **改前备份**: `*.pptx.bak-round4`。**改动页**: P2/P4–P9/P11/P12/P16–P18（图换 5 页 + 加粗 6 类）。
- **A. 频谱图换 Spectrum Analyzer 实拍**（COM 删原形重插，按新 ar 重算 ext，宽保持/微调，严禁拉伸）:
  P5 `sa_tx` (480,138) 417×275.8；P8 `sa_z1` (260,138) 420×274.9；**P11** `sa_z2` (260,138) 420×273.1（用户写"P9"，F_stage2_spectrum 实际在 P11，已按内容对号）；P12 左 `sa_bb_on` (40,140) 420×274.9、右 `sa_bb_off` (500,150) 400×261.8。P12 图注换文字：左`镜像开：基带频谱（sim.）`、右`镜像关：−800 Hz 只剩底噪（sim.）`（用户手写"-800"按全片口径用 U+2212）。净空复核：所有图注底与 takeaway 顶 ≥5pt。
- **B. 加粗**: 全片 StageLabel 24pt 粗体、框 290×36（原 330 宽为给 P8/P11/P16 大图让位而收窄）；P2 四行行首引导短语（7/6/13/6 字符）加粗；P6 谱搬移红/蓝两行整行加粗；P18 四行总结整行加粗；P17 表头确认为粗体（幂等再设）。
- **round4 追加修复**: StageLabel 加高(底 146)后与 P16 PicRec(y=136) 交叠 10pt 触发 WARN → PicRec 调 (260,140) 430×272.7、图注随移，净空恢复。
- **verify**: **0 FAIL / 0 WARN / 6 INFO**；渲染全片重出 18 张。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 修复轮 round 5（用户反馈补做：SA 截图重采集去瑕疵）
- **改前备份**: `*.pptx.bak-round5`。**改动页**: P5/P8/P11/P12（5 张频谱图全部换为重采集版）。
- **动机**: round 4 首次 SA 抓图有三处瑕疵——(a) P5 截图左缘混入相邻窗口残影；(b) 三张临时频谱仪窗口标题为 `tmp_sa_*`（暴露临时命名）；(c) P11 的 z2 截图底部混入 Windows 任务栏缩略图弹层（鼠标停在任务栏触发）。
- **重采集方法**: 临时频谱仪改名 `z1_IF_Spectrum` / `z2_ZeroIF_Spectrum` / `Baseband_Spectrum`（模型不保存，仿真 0.6s，SpectrumAverages=8）；新增抓图脚本 `_ppt_run/capture.ps1`——DPI 感知（SetProcessDPIAware）+ EnumWindows 找窗口（Simulink 频谱仪是 CEF 窗口，java.awt.Window 枚举不到）+ HWND_TOPMOST 置顶（不依赖前台权限）+ 光标移离任务栏防弹层 + 按 GetWindowRect 精确裁剪。z2 因窗口被挤出屏幕致首抓失败，用 `capture2.ps1`（SW_RESTORE + SetWindowPos 固定几何并回读确认）重抓成功。5 张统一裁至窗口可视边界（1402×913 或 1296×820），无残影、无任务栏。
- **替换方式**: raw-zip 字节级替换 `ppt/media/image10/14/18/19/20.png`（脚本 `_ppt_run/replace_sa.py`，含"形状名→r:embed→rels→media"映射与旧图尺寸断言）。摆放 ext 未改（新图 ar 与摆放比差 1.6%~2.7%，均在 5% 拉伸阈内）。
- **verify**: **0 FAIL / 0 WARN / 6 INFO**（INFO 同为公式可编辑性提示）；渲染全片重出 18 张至 `FM/_ppt_run/renders`。
- **验收**: judge 子代理因账户 5 小时配额不可用（15:01 重置），按门禁纪律改由总指挥目检改动页（P5/P8/P11/P12 图区 + P2/P4/P6/P18 加粗区）逐页确认。
- **遗留**: 截图夹带仪器 UI 外壳（标题栏/标签栏/状态栏）为用户指定的"直接截图频谱仪"形态，非瑕疵。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 修复轮 round 6（技术一致性 + 正文字体放大）
- **改前备份**: `FM_IQ_Receiver_Basic_模型讲解_会议版.pptx.bak-round6`；保留原始 deck 不覆盖。
- **技术修复**: P4/P11 统一为 `20lgγ = −12.04 dBc`；P13/P15 说明改为“归一化抑制但不消除滤波/微分链误差”；P16 将 214 Hz 解释为实测残余误差；P7/P10/P15 图注明确为局部图。
- **可读性**: 主要正文由 15→16 pt、16→17 pt，图注由 13→14 pt；P13 包络纹波小图放大；P15 补回鉴频后的输出缩放局部链。
- **公式可编辑**: P18 四环节摘要的三条公式改为 OMML（`Equation_P18_2/3/4`），分母保留 `I²+Q²+ε`。
- **频谱图处理**: 保留用户要求的 Spectrum Analyzer 实拍证据，仅用 `a:srcRect` 裁去窗口外壳/底部状态区，避免改变原图比例。
- **verify**: `verify_deck.py --style style.techshare.json` → **0 FAIL / 28 WARN / 7 INFO**；WARN 为既有图注估算溢出/字号档位提示，无结构失败。18 页全量渲染至 `FM_meeting_render_round6`，总指挥完成改动页及全片抽检，视觉门禁通过。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 修复轮 round 7（正文排版与行距优化）
- **改前备份**: `FM_IQ_Receiver_Basic_模型讲解_会议版.pptx.bak-round7`。
- **正文层级**: 正文调整到 15.5–16 pt；说明/注释使用 13–14 pt；P18 四行总结取消整行粗体，保留公式与阶段标签层次。
- **行距与内边距**: 正文文本框统一约 1.1 倍行距、段前归零、段后轻微留白，并统一上下内边距，减少“文字漂浮”和行间断裂。
- **布局**: P10 四条实现说明改为紧凑等距排列；P7/P15/P18 维持公式、图注和 takeaway 的安全间距。
- **verify**: **0 FAIL / 14 WARN / 7 INFO**；18 页重新渲染至 `FM_meeting_render_round7`，总指挥完成全片视觉抽检，排版门禁通过。

## 2026-09-15 round8/9 排版优化（用户诉求：文字布局/行距/大小）
- 公式页 P4/P6/P9/P14 垂直节奏重排（消除结论条上方死区）；P13 重排为三栏网格（原右下图压结论条/图注压页脚）；P11 频谱图下移避开环节标题；P12 两图顶边对齐；P1 封面 KeyBox 行对齐（Row3S 两行、Row4S/Equation_P1_Disc 对中）；P16/P18 居中与公式列对齐；S3/S5/S7/S10/S15 bullet 悬挂缩进（FirstMargin=0/LeftMargin=12）。
- 伪数学改真上下标：P6/P10 结论条 e^{-jψ}→e 上标、P9 标题 e^(-jψ)→e 上标、P9 结论条 ω_IF→ω 下标（COM SetRich：改 Text 后重设字体/颜色/对齐）。
- P18 OMML 手术：Eq2 补 LPF{r} 花括号；Eq3 把困在 z₁ 下标里的 e 重构为 sSup（z₂=z₁·e^{−jψ}），公式框加宽 300→500 消除折行。
- S3/S5 单段落假 bullet 拆为真段落（关键坑：旧 <a:br> 软换行经 COM .Text 返回 VT，未剥离会在每段边界渲染空行 → 行距翻倍；part 必须 Trim 再 join）。
- 验收：verify_deck 0 FAIL（34 WARN 均为既有灰图注/15.5pt 档位等全片一致性选择）；judge 整片 14→修复后改动页 3/3 pass；S9 “2πr”为验收误读（实为 2π·400t，放大图证据）。备份链 .bak-round8/.bak-round9。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 参考稿风格迁移
- **目标**：`FM\FM_IQ_Receiver_Basic_模型讲解_会议版.pptx`；参考：`hartley_weaver_share\Weaver_两模型复频域讲解_会议版.pptx`。
- **改动**：保留 18 页内容/图片/OMML；公共字体与几何对齐到参考稿——Arial、40pt 居中标题、40×40 章节圆、24pt 章节标签、右上进度条、参考稿页脚三段式位置、封面标题/摘要框节奏。
- **备份**：`FM\FM_IQ_Receiver_Basic_模型讲解_会议版.pptx.bak-reference-style-20260915`。
- **验收**：18 页渲染完成；`verify_deck.py` 0 FAIL；OfficeCLI validate 0 errors、issues 0；改动页视觉抽检通过，未修改公式对象。

## 2026-09-15 round10-12 左栏 bullet 重构（用户复验：S7 等距四框布局仍丑）
- S7/S10 由 4 个独立文本框（等 pitch 摆放、行数不齐→间距 16/35/16 交替）合并为单 Bullets 文本框：标签段+子行段（二级缩进 IndentLevel=2，Levels(2) 14/14），段距分级（标签后 2pt、子行后 14pt、末段 0），16.5pt、行距 1.12、悬挂 14pt，BoundHeight 居中于 y150-420 版心。
- S3/S5/S15 正文字号统一 16.5（S15 框高 150）。
- 新坑：COM 给 .Text 赋含  的串，PowerPoint 会把每个  序列化成两个 <a:br>（读回 ）——软换行路线废弃，子行一律用真段落+IndentLevel；IndentLevel 在 TextRange 上不在 ParagraphFormat 上。
- 验收：verify 0 FAIL（30 WARN），judge 改动页 5/5 pass。备份 .bak-round10。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 中西文字体分离
- **改动**：普通文本中文显式设为微软雅黑，西文显式设为 Times New Roman；公式形状跳过并保留原生 OMML/Cambria Math。
- **备份**：`FM\FM_IQ_Receiver_Basic_模型讲解_会议版.pptx.bak-bilingual-fonts-20260915`。
- **验收**：18 页重新渲染；OpenXML 字体计数 `Arial=0`、`Times New Roman=1568`、`微软雅黑=784`、`OMML=16`；`verify_deck.py` 0 FAIL；OfficeCLI validate 0 errors、issues 0。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 发射频谱双边重绘
- **改动**：重新运行当前 `FM_IQ_Receiver_Basic.slx`，从 `fm_signal` 生成 `-2…+2 kHz` 双边归一化 dBc 频谱；替换第 5 页 `PicSpec` 原图，保持左侧发射机框图与现有版式不变。
- **证据**：仿真 `0.08 s`，频谱窗 `20–80 ms`，重采样 `20 kHz`，实数输出正负频率对称性误差 `0 dB`；输出资产为 `F_tx_spectrum_bisided_20260915.png`。
- **备份**：`FM_IQ_Receiver_Basic_模型讲解_会议版.pptx.bak-tx-spectrum-bisided-20260915-corrected2`。
- **验收**：改动页视觉验收通过；18 页全量渲染，`verify_deck.py` **0 FAIL / 11 WARN / 38 INFO**；OfficeCLI validate **0 errors**，issues **0**。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 第 6 页补充 RF 公式
- **改动**：第 6 页“一次变频”标题右侧新增两条原生 OMML 公式：`r(t)=s_u(t)+γs_im(t)` 与 `φ_m(t)=β(1−cos(ω_m t))`，并给出模型参数 `β=4`、`γ=0.25`；原有 `z₁`、I/Q 及 ±400 Hz 频移说明保持不变。
- **依据**：公式对应当前 `FM_IQ_Receiver_Basic.slx` 的双 FM 合路 RF 信号，有用载频 1 kHz、镜像载频 0.2 kHz、共享 FM 相位。
- **备份**：`FM_IQ_Receiver_Basic_模型讲解_会议版.pptx.bak-rf-formula-20260915`；**预览**：`_ppt_run\renders_rf_formula_20260915_v4\slide06.png`。
- **验收**：18 页 `verify_deck.py` **0 FAIL / 11 WARN / 40 INFO**；OfficeCLI validate **0 errors**、issues **0**。

## 2026-09-15 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 双边频谱可读性增强
- **改动**：第 5 页频谱图坐标轴、谱线加粗，刻度与轴标签放大并加粗；双边频率范围和数据内容保持不变。
- **参数**：谱线 `2.2 pt`、坐标轴 `1.8 pt`、刻度 `17 pt`、轴标签 `19 pt`；仍由当前 `FM_IQ_Receiver_Basic.slx` 仿真生成。
- **备份**：`FM_IQ_Receiver_Basic_模型讲解_会议版.pptx.bak-tx-spectrum-bold-20260915`。
- **验收**：改动页视觉验收通过；18 页全量渲染，`verify_deck.py` **0 FAIL / 11 WARN / 38 INFO**；OfficeCLI validate **0 errors**，issues **0**。

## 2026-09-15 round13 P6 补全上/下变频 RF 公式（用户手动加了 r(t)/φ_m 后求补全）
- 用户版本已保存落盘并备份 .bak-user-rf；P6 按信号流重排：φ_m(消息相位+β/γ) → s_u/s_im 上变频(ω_c=2π·1000, ω_2=2π·200, inject_omml --tex 经 UTF-8 文件+进程内 argv 注入，绕开 GBK 命令行) → r(t) 合路 → z₁ 下变频 → I/Q → 结果行。
- 用户 Equation 13/14 统一 20pt 并居中；verify 0 FAIL，judge P6 pass。注意：用户已自行改版（边距 32pt/标题 40pt/页脚重排），后续迭代以其版本为基线。

## 2026-09-15 round14 P6 公式与 P4 字形统一
- 用户 PowerPoint 保存时已自动把 OMML 规范化为数学斜体字符（𝜑𝜔𝛽𝜋+ ，20pt Cambria Math），字符归一补丁实际仅余 φ→𝜑 等 3 处；P6 五组公式现与 P4 同套字形。
- 信号流行序：φ_m → s_u/s_im(上变频) → r(t) → z₁(下变频) → I/Q；judge 指出首行与环节标题同高相触+行距不均，整体下移按 35pt 均匀节拍重排（y158/194/229/264/299），复验 pass。
- 教训：整页渲染目测比例不可靠——像素 band 实测才准（本次曾误判“整体下坠 35pt”，实为测量映射错位）。

## 2026-09-15 round15 P4/P7(发射端/一次变频)符号统一 + 页码修正
- 用户重构 deck：新插总览截图页(位4)，全片 19 页，页脚静态页码全部过期 → 按实际位次重写 "N of 19"（COM 保留字体/颜色）。
- 符号统一（以 P7 记号为准）：发射端页 s(t)→s_u(t)、s_i(t)→s_im(t)、ω_i→ω_2、镜像相位 β sin(2πf_m t)→φ_m(t)（与有用共享相位，呼应 fm_phase_integrator）；φ_m 积分定义行保留；s_im 定义不含 γ（γ 在 P7 r(t)=s_u+γ s_im 合路时出现），20lgγ=−12.04 dB 保留。两页 OMML 全部以 omml_tex 重注入（20pt Cambria Math）。
- 用户要求工作方式：PPT 保持打开、不回退版本——流程改为 GetActiveObject 附着→Save 落盘→(仅 OMML 手术时) Close→zip 操作→重开并选中目标页，全程秒级。

## 2026-09-15 round16 重仿频谱 + z1 星座 + P15 推导链
- 用户再次重构 deck（新插总览截图页后删除，现 19 页 → PageNo 全部重写 N of 19，修 19 个 FAIL）。
- 重新仿真：模型信号日志用 DataLogging 端口参数开启（z1_i/q=Stage1_LPFE 输出、z2_i/q=Stage2_Combine、bb=Baseband_LPF），镜像开/关两遍 sim → assets/simdata_r15.mat。
- 频谱重绘（regen_spec_r14.m，离散线谱、k×50Hz bin、全局归一化保留镜像 -12dB 相对幅度）：P6 发射、P9 z1、P12 z2、P13 基带开/关；原“功率(dBm) 无窗连续谱”的泄漏地板问题消除。
- P9 新增 z1 星座图 v2（regen_const_r15.m）：发散成因 = 有用(+400 正转)+镜像(-400 反转)两相量拍频 → 半径在 A(1±γ) 环带起伏（实测 ±52.3
## 2026-09-15 round16 重仿频谱 + z1 星座 + P15 推导链
- 用户再次重构 deck（新插总览截图页，现 19 页）→ PageNo 全部重写 "N of 19"，修 19 个 FAIL。
- 重新仿真：信号日志用 DataLogging 端口参数开启（z1_i/q=Stage1_LPF 输出、z2_i/q=Stage2_Combine、bb=Baseband_LPF），镜像开/关两遍 sim → assets/simdata_r15.mat。
- 频谱重绘（regen_spec_r14.m，离散线谱、k×50Hz bin、全局归一化保留镜像 −12dB 相对幅度）：P6 发射、P9 z1、P12 z2、P13 基带开/关；原“功率(dBm) 无窗连续谱”的泄漏地板问题消除。
- P9 新增 z1 星座图 v2（regen_const_r15.m）：发散成因 = 有用(+400 正转)+镜像(−400 反转)两相量拍频 → 半径在 A(1±γ) 环带起伏（实测 ±52.3%，含 LPF 倾斜），图上画 A(1±γ) 边界环+成因标注；图注更新。
- P15 推导链：新增 z=Ae^{jθ} 定义行与关键恒等式 dθ/dt=Im[(dz/dt)z⁻¹]=(I·dQ̇−Q·dİ)/(I²+Q²)=2πΔf·m(t)（omml_tex 注入），原 ω̂/m̂ 两式下移为实现+尺度还原；删除冗余 Note；takeaway 扩展“分母|z|²抵消幅度纹波”。
- 坑：heredoc/printf 会吃 \f(→换页符)、\c——tex 文件一律用 python chr(92) 拼接写入；exportgraphics 会裁边，PNG 实际宽高比必须实测后摆位（image_ratio FAIL）。
- verify 0 FAIL；judge P9/P15 pass。

## 2026-09-15 round17 用户核查四项修正（P8/P11 截图、P19 运算顺序、P17 时延符号、P16/P13 表述）
- P8/P11 模型局部图重截：Simulink print -s 渲染完整 Weaver_FM_Receiver（5650×1717，坐标线性映射无白边），按 Stage1_*/Stage2_* 模块包围盒裁剪，消除右/左缘截断。
- P19 总结页②式修正运算顺序：LPF{r}·2e^{...} → LPF{r(t)·2e^{−jω₁t}}（OMML run 级手术：} 移至 sSup 后、r 后补 (𝑡)）。
- P17 时延口径统一：xcorr(恢复,参考) 峰位即滞后量，取正 → 图内标注"恢复滞后参考 2.20 ms"（新 F_recovered_r17.png），与标题/结论一致。
- P16 自引用"见 P16"→"见下页"；P13"底噪"→"剩余谱底（数值泄漏，无噪声源）"（演示模型无噪声源）。
- 坑：多 PowerPoint 实例时 Shapes.Item(name) 可能偶发返回 null——用 foreach 遍历按名匹配 + 改后读回打印确认；COM Save 后必须用 python 读盘复核（round17c 的保存曾被后续旧实例覆盖）。
- verify 0 FAIL；judge：P8/P11/P13/P16/P17/P19 全 pass。

## 2026-09-15 round18 R1-R5 五轮评审修复（模型+PPT 全量交叉核查）
- R1 模型核查：读工作区 46 个参数 + 双 LPF 频响计算。发现 IF/BB LPF 实为【两节二阶级联 ζ=0.707（s²+√2ω₀s+ω₀²)²，−3dB=562/241 Hz】，并非"四阶 Butterworth"（ω₀ 处 −6dB）；DC 增益=1 ✓；其余 40+ 参数与 PPT 参数表一致。
- R2 全片核查：伪数学残留 0；P10 标题已是真上标；LPF 口径问题 5 处（P8 标题/bullet、P11 bullet、P12 公式、P18 两行）。
- R3 修复：P8 标题"四阶→四极点 LPF"；P8/P11 bullets"4 阶 Butterworth/4 阶"→"ω₀=700/300 Hz 四极点级联"；P18 表格"4 阶 Butterworth"→"4 极点级联"；P13 公式"f_3dB=300 Hz (4 order Butterworth)"→"f_3dB=241 Hz (4-pole cascade)"（f₃dB=0.803×ω₀ 由 1/(1+u⁴) 特性导出）。
- R4: P17 恢复图重绘（时延符号口径统一为"恢复滞后参考 2.20 ms"，xcorr(恢复,参考) 峰位即滞后量）。
- R5/R6: 渲染 + verify 0 FAIL + judge 8/11/13/16/17/19 全 pass。
- 教训：run 级删除若跨越 sp 边界会吞噬后续结构（本次 17d 事故根因）——跨形状编辑必须用整块重建；栈式配平校验器是定位 XML 损坏的最快工具。

## 2026-09-16 examples/fm_iq_receiver_rmo01a 交付 — ppt-team 全流程 + 对参考循环打磨 3 循环收敛
- 新 deck：`FM_IQ_Receiver_RFIC2024.pptx`（19 页，RFIC2024 多数派 style.json，无身份元素），由 `FM\FM_IQ_Receiver_Basic.slx` 生成。素材/溯源继承 FM\_ppt_run 18 轮已验证资产，47 个模型工作区参数经 MATLAB getVariable 当日复测全命中。
- 流水线：architect 三大纲变体（采纳"问题驱动型·镜像抑制主线"）→ builder COM 全量建页（13 个原生 OMML）→ judge/consolidator 双门禁循环。
- 循环1：judge r1 18/19 pass（p3 红蓝语义反色 FAIL）+ consolidator r1 对照 RMo01A 语料开 36 条指令（并抓到 judge 漏报的 p7 同根反色、否决 judge 对 p11 的错误蓝色建议）→ builder r1 全落地 → judge r2 全 pass。
- 循环2：consolidator r2 更高基准（新增 5 份语料拼图）开 G01–G09（takeaway 着色、数值框居中/露刻度、p6 改原生重绘 C 型、p16 常数写法与公式页闭环、封面块位）→ builder r2 全落地 → judge r3 全 pass。
- 循环3：Gate C 全新 judge 实例终审 19/19 pass + 24 项数值抽查 pass（禁用旧口径零出现）→ 3 个图内轻症（z1 谱底影与簇色反相、z2 空轴/字号、iq_circle"一阶 LPF"术语）经 MATLAB regen_c3.m 重生成（数据源 simdata_r15.mat 不重跑仿真，包络纹波 27.4% 与 deck 口径精确一致）→ builder r4 换图+p6 盒内块数 → judge r4 全 pass，连续三轮无回归。
- 终态：verify 0 FAIL / 0 WARN / 7 INFO（已裁决）；页码 0–18 连续；经验回写四个 agents/*.md"实战经验"节。
- 坑：exportgraphics 同参数重导出像素尺寸不保持（纵横比实测差 2.9%）——换图前必须实测新图尺寸再调框；text() 多行注释用 cell 数组，'\n' 字面量触发解释器警告。

## 2026-09-16 会议版 P18 左栏 Bullets 行距/段距微调（轻量格式轮，纯段落格式+框高，零文本/字体改动）
- COM(GetActiveObject) 改 P18 [Bullets](id=11) 全部 4 段：LineRuleWithin=msoTrue + SpaceWithin=1.2 行、LineRuleAfter=msoFalse + SpaceAfter=4pt、SpaceBefore=0 保持；框高 150→195pt（L40/T200/W420 不变；任务书 T225 系笔误，COM 实测 T=200，新框底 395pt 仍在 takeaway y=438 之上）。
- 验证：读回 4 段全部 1.2 行/4pt/0；TextFrame2 BoundHeight=188.43 ≤ 195 无溢出（改前 165.01/150 已紧）；Presentation.Save() 后 python 读盘核验 slide18.xml 4×lnSpc=120000(1.2)、spcAft=400(4pt)、无 spcBef、ext.cy=2476500(195pt)。
- verify 归因（techshare style）：全片 736 FAIL 均为存量"黑体不在 EA 白名单"（disc-redesign 改版前备份即 717）；探针实验（副本还原本轮间距/框高后仍 736、Bullets 50）证明 +19 全部来自 disc-redesign 轮的 P18 bullets 文本重写（run 数 31→50），与本轮格式改动正交。本轮零新增 FAIL/WARN。
- 渲染：FM/render_fontfix2/disc_spacing_slide_18.png（1600×900）。judge（改动页 P18）：**pass**——行距松弛、条目间距可辨、末行(≈388pt)与 takeaway(438pt) 间距充裕、无重叠无裁切；右侧 Simulink 局部图小字不可读按"佐证用途"接受；ε=1e−6 写法与 P20 参数表一致。

## 2026-09-16 — FM_IQ_Receiver_Basic_模型讲解_会议版.pptx 微修（errata3：P2 大纲第③条孤行）
- **改动**: Bul3 删一字「被」→「③ 二次旋转与基带 LPF —— 有用归 DC，镜像 −800 Hz 压 32.9 dB（P11–P16）」，消去行尾「P16）」孤行；run 级 COM 替换后重设 L=Times New Roman / EA=SimHei / 24pt（同框 Bul* 一致；首过误参照 ProgBar 12.5pt，v3 巡检已修回 24pt）。
- **验证**: Save 后逐 run 读回一致；形状级快照确认页内其余 10 个文本形状未动；渲染 1600x900 覆盖 FM/render_fontfix2/errata_slide_2.png，目检第③条单行完整、其余三条未动（改动页仅 P2，通过）。
- **工具**: _ppt_run/errata3_fix.ps1（参数经 UTF-8 文件 errata3_params.txt 传入），报告 _ppt_run/errata3_report.txt。本轮无新增 .bak（单字符微调，沿用 .bak-errata-20260916）。
