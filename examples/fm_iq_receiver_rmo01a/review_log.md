# review_log — FM_IQ_Receiver_RFIC2024（变体二·问题驱动型）

## round 4（仿真图换装轮）— 2026-09-16，builder

- MATLAB 侧重生成 5 张仿真图（assets/ 已就位，旧图 `*.png.bak-c3` 未动），deck 重建换入；备份 deck → `.bak-r4`。实测新图与旧图**像素尺寸并不相同**（任务口径"同尺寸"不成立），逐张核对纵横比后仅 p8 左图需要改框：
  - F_z1_spectrum_r14 1779×1057（ratio 1.6831，比旧图差 2.9%）→ p8 框高 269→261（440×261，0.16%），消拉伸；
  - F_z2_spectrum_r14 1728×1057（1.6348）、F_bb_on/off 1727×1057（1.6339）、F_iq_circle 1252×1231（1.0171）——与原框差 ≤0.2%，原框原位放回，零拉伸。
- p6 形状微修 ✓：两枚白底根图盒内各加块数小字"18 块"/"42 块"（14pt 深灰 #333333 居中，盒内空间充足，与端口 1/2 及箭头无相交；#595959 不在色板，取 #333333）。
- verify 摘要（最终）：**0 FAIL / 0 WARN / 7 INFO**（同 r3：6 条 OMML INFO + p6 Label6T 版心 INFO 已裁决）。改动页：**p6, p8, p10, p12, p14**（渲染已逐张目检：底影对色/空轴收紧/字号提档/术语更新全部生效，无拉伸、无裁切、无新增相交）。

## round 3（微修轮）— 2026-09-16，builder

- 唯一改动：p6 根图两根黑箭头（Arrow6a/6b，块状右箭头）高度 7pt→4pt（杆读数 ≈3.5pt→≈2pt），与 1pt 盒边协调；y 微调 416/438 保持视觉居中。p13 左缘截断维持现状（上级进入约定，不动）。备份 `.bak-r3`。verify：**0 FAIL / 0 WARN / 7 INFO**（与 r2 相同的 6 条 OMML INFO + p6 Label6T 版心 INFO，已裁决）。改动页：仅 p6（渲染已目检）。

## round 2（consolidator 抛光轮）— 2026-09-16，builder

- 输入：consolidator_r2.md（G01–G07 硬指令 + G08/G09 可选）+ judge_report_r2.json（r2 14 页全 pass，最弱 11/5/13）。
- 备份：deck → `.bak-r2`（资产无改动）。
- verify 摘要（最终）：**0 FAIL / 0 WARN / 7 INFO**（6 条 OMML 数学区 + 1 条 p6 Label6T 左缘 10pt < 40 版心——居中题注画注需要，裁决通过）。
- 改动页清单（9 页）：**p1, p3, p5, p6, p11, p12, p13, p16, p17**；未动：p2, p4, p7, p8, p9, p10, p14, p15, p18, p19。
- G01 ✓ p11：takeaway『50 Hz 消息』红粗（judge 唯一遗留闭合）；p17『恢复 50 Hz 消息』按联动约束保持黑字。
- G02 ✓ p5：cap_tx 下移 15pt（y=155），左右视觉顶边差 34px→≈5px；bullets 随移 y=296。
- G03 ✓ p13：disc 等比放大 6%（380×272→402×287 @ (518,124)），图注随移 y=421；左右底边差 65px→≈44px（A 型容差内，达 consolidator ≈25px 目标量级）。
- G04 ✓ p6：标题『全图/全景』去重 →『四道防线全景』；左下灰糊缩略截图删除，用原生形状重绘根图（2 个白底黑 1pt 框 + 端口 1/2 + 两根黑右箭头 + FM_Transmitter/Weaver_FM_Receiver 14pt 标签，RMo03A_1 纯盒画法）；takeaway 断行改冒号后，第二行『镜像』蓝粗。
- G05 ✓ p16：ε/G 行改『1×10⁻⁶ / 7.958×10⁻⁴』（Unicode U+207B/U+2076/U+2074，Calibri 蓝粗与整列一致，与 p13 公式写法闭环）；行名 f_m/fc/mixerGain 按指令保持 getVariable 查表键原样。
- G06 ✓ p3：两行注释去 ASCII 记法 →『有用：1000 Hz 载波，幅度 A』/『镜像：200 Hz 载波，幅度 γA（γ = 0.25）』。
- G07 ✓ p12：两数值框移至各图上部空白区（左 (90,180)、右 (528,180)），不压任何刻度/轴题/标签——"框叠图"代价清零。
- G08 ✓ p1：作者块 y=351、日期 y=420，内容底至页高 ≈85%（78–88% 语料带内）。
- G09 ✓ p17：bullet1『−400 Hz』蓝粗（与 p7 takeaway 同量同色，三 bullet 蓝/红/蓝节奏）——零风险单 run，做。
- 数值纪律复核：本轮无新数值；p16 上标写法与 provenance #8（ε=1e-6、G=7.958e-4）数值等同，仅记法统一。
- 遗留：无新增。p18/p19 占位仍待讲者内容。
- 待办：改动页 9 页（p1/p3/p5/p6/p11/p12/p13/p16/p17）交 ppt-judge 复审。

## round 1（judge/consolidator 修复轮）— 2026-09-16，builder

- 输入：judge_report_r1.json（FAIL 页 3；最弱 3/9/13）+ consolidator_r1.md（F01–F12 硬指令 + 6 条共性问题）。
- 备份：deck → `.bak-r1`；cap_rx_stage1/stage2/disc.png → `*.png.bak-r1`。
- verify 摘要（最终）：**0 FAIL / 0 WARN / 6 INFO**（INFO 均为 OMML 数学区检测）。过程 WARN（p6 Bullets6 启发式 3 行 vs 实际 2 行）已用 AutoSize 钉死 + h=80 消除；p9 Note9 页脚候选误报（run "4"）已用 y=466 消除。
- 改动页清单（14 页）：**p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p15, p17**；未动：p1, p14, p16, p18, p19。
- 截图重裁（共性#3）：以 `FM\_ppt_run\assets\F_receiver_full_r17.png`（5650×1717）为源，FFT 模板匹配定位三窗后按"完整收录信号名"重裁（比 25px 外扩更激进，因 25px 不足以容纳被切标签）：
  - cap_rx_stage1：窗 (0,155,1065,988)，1065×833（ratio 1.2785）→ p7 440×344 @ (480,110)；右缘收在 Stage2 混频器标签起点之前的线区，孤儿字 S/St/S 清零；
  - cap_rx_stage2：窗 (650,38,2133,1443)，1483×1405（ratio 1.0555）→ p9 382×362 @ (538,106)；左缘 Stage1_I/Q_LPF、Stage2_LO_* 标签全补；右缘仅框线/连线裁断（无文字，语料惯例）；
  - cap_rx_disc：窗 (1360,0,3761,1717)，2401×1717（ratio 1.3984）→ p13 380×272 @ (540,128)；左缘 Stage2_Q/I_Combine、Stage2_Q/I_Baseband_LPF 全补，-C- 框、Stage2_IF_Rate_Zero、FM_Phase_Rate 全完整。
- F01–F12 落地：F01 ✓（p3 轴标蓝/红互换 + 标题补空格，FAIL 清零）；F02 ✓（p7 映射行互换 + takeaway −400 Hz 蓝 + 截图重裁）；F03 ✓（p6 改 C 型满版：cap_rx 800×243 全宽 hero、图占比 ≈41%，4 个彩色描边白底 chip，KeyBox 叠图右上（文案精简 "LO1+LO2 = fc = 1000 Hz"），左列降密到底行；标题改"全图四道防线全景"——42pt 全形式链仍折行，改为标题不含链路短语、全形式由 chips+p2 承担）；F04 ✓（p9 公式组入白底黑框 RowPanel9 锚定 + 新增 takeaway "有用旋到 DC（红），镜像被推至 −800 Hz（蓝）"）；F05 ✓（p13 disc 重裁 + 图题贴图 + 新图注 + 左列三段均布）；F06 ✓（p17 段后 70pt 满高 + 短语加粗 + 收束条下移着色）；F07 ✓（p10 框组下移 72pt 居中 + 框2 −12.04 dB 蓝 + 两框对齐 x=660 w=260——consolidator 给的 render 坐标换算后越 920 版心，收敛到版心内）；F08 ✓（p15 框组下移 72pt + 定量闭环红 + 2.20/214 黑粗）；F09 ✓（p12 两框右移 24pt/下移 6pt 露刻度 + 过程量蓝）；F10 ✓（p11 lead-in 冒号 + 图帧 440×279；**着色按用户指示 SKIP**——p11 takeaway 不改色）；F11 ✓（p5 注定难分红 + 右谱 375×244 + 公共顶边 y=140）；F12 ✓（p4 m(t) 统一 + Carson 行上移 9pt + 底注下移 y=432）。F13/F14（可选）SKIP。
- 红蓝语义规则（本轮起全片固定）：**蓝 #0070C0=镜像路径/理论对照/过程量；红 #FF0000=有用/关键定量结果**。p3/p7 已互换，p8 图顶标与 p10/p12 图注为基准。
- 术语统一：p2 bullet3 与 p6 chips 全形式"复混频→旋转→基带滤波→鉴频"；p6 标题改"全图四道防线全景"（不含链路短语，规避 42pt 仍折行 + 短/长冲突）；outline 变体二 p6 原型 B→C 已同步。
- 遗留：①F10-3 右图加高受 1.577 固定纵横比限制仅 +2.2%（+6pt），左右底边差 53px→~28px，未完全对齐；②p13 截图左缘 Combine 求和块的输入连线在框外被切（无文字，语料惯例可接受）；③p18/p19 占位仍待讲者补充。
- 待办：改动页 14 页交 ppt-judge 复审（由 coordinator 派发）。

## round 0（初建）— 2026-09-16，builder

- 产物：`examples/fm_iq_receiver_rmo01a/FM_IQ_Receiver_RFIC2024.pptx`，19 页（封面页码 0，其余 "1 of 19"–"18 of 19"）。
- 管线：`build_deck.ps1`（PowerPoint COM 附着 GetActiveObject，只动本 Presentation，未 Quit）→ `build_eq.py`（raw-zip 注入 13 个原生 OMML 公式形状 + slide16 表格改 No Style No Grid）→ `export_slides.ps1` 渲染 19 张 PNG → `verify_deck.py`。
- 备份：`.bak-r0-skel`（首轮 COM 骨架）、`.bak-r0-fix1`（公式修复前状态）。
- verify 摘要（最终）：**0 FAIL / 0 WARN / 6 INFO**（INFO 全部为"检测到 OMML 数学区（可编辑公式）"，合规预期）。
  - 中途修复记录：①PageNo 默认 80pt 框被 "N of 19" 换行撑高越界（9 页 bounds FAIL）→ 加宽 140pt + WordWrap/AutoSize 关闭；②公式内 ①②（U+2460–24FF）在数学区缺 `<a:ea typeface="微软雅黑">` 声明（font_rules FAIL）→ build_eq.py decorate() 按 verify 的 EA 区间补声明并强制正体；③slide3 标题 12.04 dB 后移除空格避免双行估算溢出；④FreqAxis/Tick 装饰形状 8pt→16pt（档位表内）；⑤Note9 上移避免页脚候选误报（run "4" 被当页码，INFO 级）；⑥mini-LaTeX 词元合并 bug（`2=I`、`2+Q` 无空格并词）导致 E4a/E4b/E9a/E9b/E13a/E13b 项缺失或下标吞等号 → tex 全部加空格重建。
- WARN 裁决：无遗留 WARN。已裁决并消除的过程 WARN：溢出启发式对 PageNo/CoverTitle/Bullets7 的误报（AutoSize 钉死后消除）、FreqAxis 8pt 档位、Note9 页脚候选。
- 每页原型落位（SKILL.md §七）：
  | 页 | 内容 | 原型 | 备注 |
  |---|---|---|---|
  | 1 | 封面 | §三封面规范 | kicker 32pt 青绿 + 全题 44pt 两行 + 作者 24pt + 日期 20pt，页码 0 |
  | 2 | Outline | G | 5 条 32pt，青绿 bullet，关键数字红/蓝 |
  | 3 | 痛点 | F | 中央红字命题 + s(t)/s_i(t) 对照 OMML + 1000/600/200 Hz 频率轴 |
  | 4 | FM 预备 | J | ①② 步骤号，s(t) 相位积分式 + β + Carson 500 Hz |
  | 5 | 发射双谱 | B | cap_tx + F_tx_spectrum 顶边对齐，各自小标题 |
  | 6 | 全图四防线 | B | cap_root + cap_rx，①–④ 彩色防线章（蓝/绿/橙/紫，与 p7/9/11/13 呼应）+ LO 数字框 |
  | 7 | 防线① | A | 左式右图，z₁=LPF[r·2e^{−jω₁t}]，1000→+400 / 200→−400 |
  | 8 | z1 证据 | B | 双边谱 + 星座环带 ±52.3% |
  | 9 | 防线② | A | z₂=z₁e^{−jψ} + I/Q 展开两行 + cap_rx_stage2 |
  | 10 | z2 证据 | D | 大图 + 白底数值框（−11.9 dBc / 理论 −12.04 dB）+ 底部 takeaway |
  | 11 | 防线③ | A | H(s) 分式（ω₀ 橙色）+ −3dB=241 Hz + F_bb_iq_time |
  | 12 | LPF 对照 | B | 开/关 2-up + 数值框压图（−44.8/−54.7 dBc）+ 净压制 32.9 dB |
  | 13 | 防线④ | A | ω̂ 叉乘分式（紫）+ ε/G + cap_rx_disc |
  | 14 | 鲁棒性 | B | IQ 圆 + 包络 ±27.4%，\|H(600)\|≈0.88 vs \|H(200)\|≈1.0 |
  | 15 | 结果 | D | F_recovered 大图 + corr/滞后/频偏三数值框 + 闭环 takeaway |
  | 16 | 参数表 | H | 学术三线表（表头上下 2.25pt、底 1.5pt、无竖线），数值列蓝粗体，脚注 getVariable 实测 |
  | 17 | 结论 | K | 3 条 32pt + 一页收束条 |
  | 18 | Acknowledgments | K | Thank you + 待补充占位 |
  | 19 | References | L | 待补充占位（IEEE 格式 [1] 起） |
- 数值纪律：全部数值取自 `data_provenance.md` 登记表；LPF 全片口径"四极点级联（两节二阶 ζ=0.707），−3dB=562/241 Hz"，未出现 "Butterworth"；未使用旧口径 corr=0.9988 / Δ47.4dB / ±8.5%。身份元素（logo/会话号）未带；页脚 = FooterBand 渐变带 + PageNo。
- 遗留问题清单：
  1. p18 致谢正文、p19 References 条目：素材不存在，留占位待讲者补充（大纲注明"不得编造"）。
  2. p12 第三张素材 F_mirror_compare.png 未上图（版面已由 2-up + 结论条覆盖，数字已引用）——如需三图版可回炉。
  3. p6 cap_rx 缩至 440pt 宽后块内文字不可读（全景图定位，可接受）；p6/p17 底部有中等留白，构图审查（consolidator）如认定死区可加密。
  4. 公式为 Cambria Math 原生 OMML，但数学斜体/正体粒度沿用 omml_tex 引擎（希腊字母正体），与语料"变量斜体"细节略有差异，judge 如苛求可后续 raw-zip 调 `m:sty`。
  5. 待 ppt-judge 对全部 19 页（本轮为初建轮，等于全部为"改动页"）做视觉验收；FAIL 页回 builder 修复。
