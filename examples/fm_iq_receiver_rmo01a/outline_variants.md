# FM_IQ_Receiver_Basic 讲解 deck — 大纲三变体（ppt-architect 输出，2026-09-16）

- 预算：16–19 页/变体；三变体均 19 页，均全覆盖 C01–C21（映射见各行"素材出处"列）。
- 通用约定：
  - "页码"列为大纲序号；落版页脚页码按封面=0 计（SKILL.md §一），"N of M"由 builder 生成。
  - 身份元素（会议 logo/竖标/会话号）一律不带（§一豁免）；页脚 = 纯渐变色带 + 页码。
  - 本片无 Die Photo/测量 setup（§八对应位空缺合法）；Comparison 位由全链参数表 C19 承接（H 型）。
  - LPF 一律写"四极点级联（两节二阶 ζ=0.707），−3dB=562/241 Hz"，禁写"Butterworth"（data_provenance 规则 5）。
  - 禁用旧口径：corr=0.9988 / Δ47.4dB / ±8.5%（provenance 规则 4）。
  - 待人类补充项在三变体中相同：封面作者/单位、Acknowledgments 正文、References 条目（素材中不存在，不得编造）。
  - 公式页（J 型）公式一律原生 OMML/Cambria Math（§五），步骤编号 ①②③。

---

## 变体一 · 信号旅程顺序型（19 页）

叙事线一句话：跟着信号走完全程——发射机造出"有用+镜像"两个 FM → 接收链四环节（一次变频→二次旋转→基带 LPF→鉴频）逐站改写信号 → 恢复消息收口；实现系列页标题带 (n/4)。

| 页码 | 标题(≤22字) | 本页唯一要点 | 元素清单 | 素材出处 | 原型 |
|---|---|---|---|---|---|
| 1 | （封面）FM I/Q 接收机 Simulink 模型讲解 | 报告主题与讲者信息 | 全题（2 行内）+ 作者 + 单位；作者/单位**待人类补充**；无会话号/logo | content_manifest 主题行 | 封面规范(§三) |
| 2 | Outline | 五段议程预告 | 5 条 32pt bullets：背景与镜像问题 / 发射信号 / 接收四环节 / 基带特性与解调结果 / 参数与结论 | 全清单结构归纳 | G |
| 3 | 全链 60 块：发射 18、接收 42 | 模型=FM_Transmitter(18 块)→Weaver_FM_Receiver(42 块) | cap_root.png 大图 + 底部 takeaway 一条（蓝粗体） | C20 / cap_root.png | D |
| 4 | 相位积分合成 FM：β=4、B=500Hz | FM 由相位积分+载波相位合成 | 左 bullets+OMML：s(t)=A·cos(ω_c t+2πΔf·∫m dτ)、β=Δf/f_m=4、B=2(Δf+f_m)=500Hz；右 cap_tx.png（message→积分→+ω_c t→cos） | C01 C02 C04 / cap_tx.png | A |
| 5 | 镜像=同消息 FM，幅度仅 1/4 | 镜像与有用同消息同 β，仅载频/幅度不同 | 左 OMML：s_i(t)=γA·cos(ω_i t+β·sin ω_m t)，γ=0.25、−20lgγ=12.04dB；右 F_tx_spectrum_bisided（1kHz 有用+0.2kHz 镜像双边线谱） | C03 C05 / F_tx_spectrum_bisided_20260915.png | A |
| 6 | 接收四环节：变频→旋转→滤波→鉴频 | 接收链路图=后续 4 页路线图 | cap_rx.png 满版 + 色块标注环节①–④（与后续页同色呼应） | C21 / cap_rx.png | C |
| 7 | 一次变频(1/4)：复谱正负分离 | 复混频把有用/镜像搬到 ±400 两侧 | 左 OMML：z1=LPF{r·2e^(−jω₁t)}、LO1=600Hz、1000→+400 / 200→−400；右 cap_rx_stage1.png（标注混频→IF LPF 700Hz 口径四极点级联 −3dB=562Hz） | C06 C07 / cap_rx_stage1.png | A |
| 8 | z1 频谱：+400/−400 分居两半轴 | 复谱正负分离的仿真证据 | 2-up：F_z1_spectrum_r14 + F_z1_constellation_r15（环带 A(1±γ)、起伏 ±52.3%，含 LPF 倾斜），各带小标题 | C08 / F_z1_spectrum_r14.png + F_z1_constellation_r15.png | B |
| 9 | 二次旋转(2/4)：有用转向 DC | z2=z1·e^(−jψ) 旋平相位 | 左 OMML：I2=I1cosψ+Q1sinψ、Q2=−I1sinψ+Q1cosψ（ψ=ω_IF·t）；右 cap_rx_stage2.png（4 乘法器+2 合路+2 LPF，符号 [++]/[−+] 标色） | C09 C10 / cap_rx_stage2.png | A |
| 10 | z2 频谱：有用归 DC、镜像 −11.9dBc | 旋转后镜像被推到 −800Hz | F_z2_spectrum_r14 大图 + 底部 takeaway：−11.9dBc ≈ 理论 −20lgγ=−12.04dB（红/蓝粗体） | C11 / F_z2_spectrum_r14.png | D |
| 11 | 基带 LPF(3/4)：−3dB=241Hz 收口 | 300Hz 四极点级联滤镜像、保消息 | 左 bullets+OMML：(s²+√2ω₀s+ω₀²)²、DC 增益 1、−3dB=241Hz、脚注 f₃dB=0.803ω₀；右 F_bb_iq_time（输出 50Hz 调幅正交对） | C12 C17 / F_bb_iq_time.png | A |
| 12 | 开/关对照：净压制镜像 32.9dB | LPF 开/关镜像残差对比 | 2-up：F_bb_on_r14 + F_bb_off_r14，数字框 −44.8dBc(开)/−54.7dBc(关)、净 32.9dB（白底黑字数值框画法 §四） | C13 / F_bb_on_r14.png + F_bb_off_r14.png + F_mirror_compare.png | B |
| 13 | 零中频鉴频(4/4)：归一化检波 | 叉乘微分式直接恢复瞬时频偏 | 左 OMML：ω̂=(I·ΔQ−Q·ΔI)/(I²+Q²+ε)、ε=1e-6、G=1/(2πΔf)=7.958e-4；右 cap_rx_disc.png（Δ 支路+乘加+I²+Q² 标色） | C14 C15 / cap_rx_disc.png | A |
| 14 | IQ 近圆：±27.4% 纹波被归一化抵消 | 包络纹波成因与鉴频自抵消 | 2-up：F_iq_circle（近圆轨迹）+ F_envelope（±27.4%@50Hz）；要点：|H(600)|≈0.88 vs |H(200)|≈1.0，I²+Q² 归一化抵消 | C18 / F_iq_circle.png + F_envelope.png | B |
| 15 | 恢复 corr=0.9613、滞后 2.20ms | 解调质量定量收口 | F_recovered_r17 大图 + 数字框：corr=0.9613、时延 2.20ms（微分链群延迟口径）、频偏峰值 214Hz | C16 / F_recovered_r17.png | D |
| 16 | 全链参数表：47 变量实测一致 | 一页查全所有登记参数 | H 型三线表：fc/f_m/Δf/β/LO1/LO2/mixerGain/两 LPF(ω₀ 与 −3dB)/γ/ε/G/仿真时长 0.08s；脚注 2026-09-16 getVariable 实测 | C19 / data_provenance 表 | H |
| 17 | 结论：两级变频+LPF 抑制镜像 | 三条可带走结论 | 3–4 条 32pt bullets：复混频正负分离 / 旋转+LPF 净压制 32.9dB / 归一化鉴频 corr=0.9613 | C13 C16 C19 汇总 | K |
| 18 | Acknowledgments | 致谢 | 居中 "Thank you for your attention." + 致谢正文**待人类补充** | ——（人类补充） | K |
| 19 | References | 文献 | [n] 编号 IEEE 格式；条目**待人类补充**（素材无文献） | ——（人类补充） | L |

选择建议（≤100字）：最贴"模型讲解"本体，听众按信号流顺序零认知跳跃；实现系列 (n/4) 节奏感强，适合教学式报告与不熟悉 Weaver 架构的听众；代价是冲突感弱、开题吸引力平平。

---

## 变体二 · 问题驱动型（镜像抑制主线，19 页）

叙事线一句话：先立"镜像只低 12dB 且与有用不可区分"的问题，再把接收链讲成四道防线，每页回答"镜像此刻去哪了"，以净压制 32.9dB 与 corr=0.9613 收束。

| 页码 | 标题(≤22字) | 本页唯一要点 | 元素清单 | 素材出处 | 原型 |
|---|---|---|---|---|---|
| 1 | （封面）FM I/Q 接收机 Simulink 模型讲解 | 报告主题与讲者信息 | 同变体一 p1；作者/单位**待人类补充** | content_manifest 主题行 | 封面规范(§三) |
| 2 | Outline | 五段议程预告 | 5 条：镜像问题 / FM 预备 / 四道防线 / 鲁棒性与结果 / 参数与结论 | 全清单结构归纳 | G |
| 3 | 痛点：镜像同消息同 β，仅低 12.04dB | 镜像无法从消息域区分、强度不可忽略 | F 型中央命题（红字）：γ=0.25 → −20lgγ=12.04dB；周围小 OMML：s_i(t) 与 s(t) 对照；频率轴示意（1000/600/200Hz） | C03（频点数值取 C06/provenance#5） | F |
| 4 | FM 预备：β=4、Carson 500Hz | 听众对齐 FM 基础口径 | J 型：s(t)=A·cos(ω_c t+2πΔf·∫m dτ)、m(t)=sin(2πf_m t)、β=4、B=500Hz；步骤编号①② | C01 C02 | J |
| 5 | 发射机产出双 FM 载波谱 | 镜像在发射机内与有用同源生成 | 2-up：cap_tx.png（镜像支路共享 fm_phase_integrator，标色）+ F_tx_spectrum_bisided（1k/0.2k 双谱） | C04 C05 C03 / cap_tx.png + F_tx_spectrum_bisided_20260915.png | B |
| 6 | 全图四道防线全景 | 方案全景=四防线地图 | C 型满版：cap_rx 全宽 hero + ①–④ 彩色 chip + KeyBox 叠图右上 + 底行 cap_root/bullets/takeaway（r1 由 B 改 C） | C20 C21（LO 数值 provenance#5）/ cap_root.png + cap_rx.png | C |
| 7 | 防线①(1/4)：复混频分离正负谱 | 复数混频使镜像落到 −400 | 左 OMML：z1=LPF{r·2e^(−jω₁t)}、1000→+400 / 200→−400；右 cap_rx_stage1.png（IF LPF 700Hz 口径 −3dB=562Hz） | C06 C07 / cap_rx_stage1.png | A |
| 8 | z1 证据：±400 分居、环带 ±52.3% | 分离已被仿真证实 | 2-up：F_z1_spectrum_r14 + F_z1_constellation_r15（A(1±γ) 环带 ±52.3%） | C08 / F_z1_spectrum_r14.png + F_z1_constellation_r15.png | B |
| 9 | 防线②(2/4)：旋转推镜像至 −800Hz | 二次旋转把有用旋到 DC | 左 OMML：z2=z1·e^(−jψ) 展开式；右 cap_rx_stage2.png（符号 [++]/[−+] 高亮） | C09 C10 / cap_rx_stage2.png | A |
| 10 | z2 证据：有用归 DC、镜像 −11.9dBc | 旋转后镜像残差定标 | F_z2_spectrum_r14 大图 + takeaway：−11.9dBc ≈ −20lgγ（理论 −12.04dB） | C11 / F_z2_spectrum_r14.png | D |
| 11 | 防线③(3/4)：LPF −3dB=241Hz | 基带 LPF 是压制主力 | 左 OMML：(s²+√2ω₀s+ω₀²)²、DC 增益 1、脚注 f₃dB=0.803ω₀；右 F_bb_iq_time（LPF 输出正交对） | C12 C17 / F_bb_iq_time.png | A |
| 12 | LPF 前后对照：净压制 32.9dB | 开/关对照实验定证压制量 | 2-up：F_bb_on_r14 + F_bb_off_r14，数字框 −44.8/−54.7dBc、净 32.9dB（F_mirror_compare 结论引用） | C13 / F_bb_on_r14.png + F_bb_off_r14.png + F_mirror_compare.png | B |
| 13 | 防线④(4/4)：归一化鉴频检波 | 鉴频对残余纹波归一化 | 左 OMML：ω̂=(I·ΔQ−Q·ΔI)/(I²+Q²+ε)、G=7.958e-4；右 cap_rx_disc.png | C14 C15 / cap_rx_disc.png | A |
| 14 | 鲁棒性：±27.4% 纹波被抵消 | IF LPF 倾斜代价已被归一化化解 | 2-up：F_iq_circle + F_envelope；要点：|H(600)|≈0.88 vs |H(200)|≈1.0 → I²+Q² 抵消 | C18 / F_iq_circle.png + F_envelope.png | B |
| 15 | 结果：corr=0.9613 恢复 50Hz 消息 | 问题→方案闭环定量收口 | F_recovered_r17 大图 + 数字框：corr=0.9613、滞后 2.20ms、峰值 214Hz | C16 / F_recovered_r17.png | D |
| 16 | 全链参数表：47 变量实测一致 | 一页查全参数 | 同变体一 p16（H 型三线表） | C19 | H |
| 17 | 结论：四道防线净压镜像 32.9dB | 三条可带走结论 | bullets：复分离/旋转+LPF 32.9dB/鉴频 corr=0.9613 | C13 C16 C19 汇总 | K |
| 18 | Acknowledgments | 致谢 | 同变体一 p18；正文**待人类补充** | ——（人类补充） | K |
| 19 | References | 文献 | 条目**待人类补充** | ——（人类补充） | L |

选择建议（≤100字）：冲突—解决弧线最抓人，每页自带"镜像去哪了"钩子，最贴 §八 Motivation→方案 语料节奏；适合主张"架构思想"的会议报告；对只想看模型实现的听众铺垫稍多。

---

## 变体三 · 理论→实现分层型（19 页）

叙事线一句话：先把三条理论（FM 调制/两级复变频/归一化鉴频）一次讲完，再逐块映射到 Simulink 实现（系列 n/4），最后五张仿真图逐条验证理论——三层结构，理论页与证据页一一对应。

| 页码 | 标题(≤22字) | 本页唯一要点 | 元素清单 | 素材出处 | 原型 |
|---|---|---|---|---|---|
| 1 | （封面）FM I/Q 接收机 Simulink 模型讲解 | 报告主题与讲者信息 | 同变体一 p1；作者/单位**待人类补充** | content_manifest 主题行 | 封面规范(§三) |
| 2 | Outline | 四段议程预告 | 4 条：理论 / Simulink 实现 / 仿真验证 / 参数与结论（可进度式灰化） | 全清单结构归纳 | G |
| 3 | 理论① FM 调制：β=4、B=500Hz | FM=相位积分调制 | J 型：s(t)=A·cos(ω_c t+2πΔf·∫m dτ)、β=Δf/f_m=4、B=2(Δf+f_m)=500Hz | C01 C02 | J |
| 4 | 理论② 复混频+旋转：两级变频 | 两级复数变频=先分离再归 DC | J 型双式：z1=LPF{r·2e^(−jω₁t)}（1000→+400/200→−400）；z2=z1·e^(−jψ) 展开 I2/Q2；步骤①② | C06 C09 | J |
| 5 | 理论③ 鉴频：叉乘归一化、ε 防零除 | 鉴频方程与增益一级定义 | J 型：ω̂=(I·ΔQ−Q·ΔI)/(I²+Q²+ε)、ε=1e-6、m̂=ω̂/(2πΔf)、G=7.958e-4 | C14 | J |
| 6 | 实现① 全景：根图与接收 42 块 | 模型分层=发射 18 块+接收 42 块 | 2-up：cap_root.png + cap_rx.png（标注即将展开的实现块编号） | C20 C21 / cap_root.png + cap_rx.png | B |
| 7 | 实现② 发射机：镜像共享积分器 | 镜像与有用同源同 β（γ=0.25） | 左 bullets：镜像支路接同一 fm_phase_integrator、γ=0.25、−20lgγ=12.04dB；右 cap_tx.png | C03 C04 / cap_tx.png | A |
| 8 | 实现③ Stage1+2：4 乘法器 2 合路 | 两级混频/旋转的块级落地 | 2-up：cap_rx_stage1.png + cap_rx_stage2.png（叠加理论②公式编号标注、LPF 口径 −3dB=562/241Hz） | C07 C10（LPF 数值 C12 口径）/ cap_rx_stage1.png + cap_rx_stage2.png | B |
| 9 | 实现④ LPF：两节二阶 ζ=0.707 | LPF 传递函数与输出形态 | 左 OMML：(s²+√2ω₀s+ω₀²)²、DC 增益 1、−3dB=562/241Hz、脚注 0.803ω₀；右 F_bb_iq_time | C12 C17 / F_bb_iq_time.png | A |
| 10 | 实现⑤ 鉴频器：Δ 叉乘+I²+Q² | 鉴频器块级落地 | cap_rx_disc.png 为主图 + 标注对应理论③各项（同色呼应） | C15 / cap_rx_disc.png | D |
| 11 | 验证① 发射双边谱 1k/0.2k | 理论①的谱证据 | F_tx_spectrum_bisided 大图 + takeaway：Carson 500Hz 包络 | C05 / F_tx_spectrum_bisided_20260915.png | D |
| 12 | 验证② z1 ±400 分离、环带 ±52.3% | 理论②前半的谱+星座证据 | 2-up：F_z1_spectrum_r14 + F_z1_constellation_r15 | C08 / F_z1_spectrum_r14.png + F_z1_constellation_r15.png | B |
| 13 | 验证③ 净压制 32.9dB（旋转+滤波） | 理论②后半+LPF 合并定量验证 | 2-up：F_z2_spectrum_r14（−11.9dBc/−800Hz）+ F_bb_on_r14；数字框：−44.8/−54.7dBc（关，F_bb_off）、净 32.9dB | C11 C13 / F_z2_spectrum_r14.png + F_bb_on_r14.png + F_bb_off_r14.png + F_mirror_compare.png | B |
| 14 | 验证④ IQ 近圆、纹波 ±27.4% | 包络纹波成因与抵消机制 | 2-up：F_iq_circle + F_envelope；要点：|H(600)|≈0.88 vs |H(200)|≈1.0 | C18 / F_iq_circle.png + F_envelope.png | B |
| 15 | 验证⑤ corr=0.9613 恢复消息 | 理论③的端到端证据 | F_recovered_r17 大图 + 数字框：corr=0.9613、滞后 2.20ms、峰值 214Hz | C16 / F_recovered_r17.png | D |
| 16 | 全链参数表：47 变量实测一致 | 一页查全参数 | 同变体一 p16（H 型三线表） | C19 | H |
| 17 | 结论：理论—实现—验证闭环 | 三条可带走结论 | bullets：三式理论定架构 / 42 块实现全对齐 / 32.9dB+corr=0.9613 收口 | C13 C16 C19 汇总 | K |
| 18 | Acknowledgments | 致谢 | 同变体一 p18；正文**待人类补充** | ——（人类补充） | K |
| 19 | References | 文献 | 条目**待人类补充** | ——（人类补充） | L |

选择建议（≤100字）：理论集中在前 3 页、证据压在后段，信息密度分层清晰，适合熟稔复信号处理的资深 RF 听众或 20 分钟以上报告；前段公式较重，短时段或混合听众略显陡峭。
