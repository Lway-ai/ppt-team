# 内容清单 — FM_IQ_Receiver_Basic 模型讲解（RFIC2024 风格 · RMo01A 对照目标）

> Deck 目标: examples/fm_iq_receiver_rmo01a/ · 风格 profile: scripts/style.json（RFIC2024 官方模板多数派）
> 美观对照: RFIC2024/2024_07_02_RMo01A_1（87 deck 语料；无会议身份元素，遵守 SKILL.md §一豁免）
> 素材: 本目录 assets/（7 截图 + 10 仿真图 + measurements.txt，全部源自对
> D:\wanglei\project\TDA7707_GNSS\E_project\FM\FM_IQ_Receiver_Basic.slx 的直接截图/仿真，2026-09-15 生成并经 18 轮核查）
> 参数复核: 2026-09-16 MATLAB getVariable 实测 47 个模型工作区变量，与本清单一致

## 模型拓扑（find_system 验证 + 2026-09-16 复载）

- 根：FM_Transmitter（18 块）→ Weaver_FM_Receiver（42 块，内部平铺）
- 发射链：message_m(50Hz 正弦) → freq_dev_gain → fm_phase_integrator → instantaneous_phase(+ωc·t)
  → FM_carrier_cos；镜像支路：同一 fm_phase_integrator → Mirror_FM_Carrier(200Hz) → Mirror_Amplitude_0p25
  → RF_Desired_Plus_Mirror 合路。**镜像与有用同消息同 β，仅载频/幅度不同**
- 接收链：Stage1 I/Q 混频(LO1=600Hz, 2cos/−2sin) → Stage1_I/Q_LPF(700Hz 四极点) →
  Stage2 I/Q 旋转(LO2=400Hz)：I2=I1cosψ+Q1sinψ, Q2=−I1sinψ+Q1cosψ（z2=z1·e^(−jψ)）→
  Stage2_I/Q_Baseband_LPF(300Hz 四极点) → 鉴频器 (I·ΔQ−Q·ΔI)/(I²+Q²+ε) → ×1/(2πΔf) → m̂
- 精确 LPF 口径（round18 R1 修正）：两节二阶级联 ζ=0.707，(s²+√2ω₀s+ω₀²)²，−3dB=562/241 Hz，
  **不是"四阶 Butterworth"**（ω₀ 处 −6dB）；DC 增益=1

## 清单

ID | 类别 | 信息点 | 数值/公式 | 出处 | 原型 | 置信度
C01 | theory | FM 调制公式 | s(t)=A·cos(ω_c t + 2πΔf·∫m dτ)，m(t)=sin(2πf_m t) | 模型 workspace+FM_Transmitter 拓扑 | J | 高
C02 | theory | 调制指数与 Carson 带宽 | β=Δf/f_m=200/50=4；B=2(Δf+f_m)=500Hz | 参数 fc/freqDev/fmMsg | J | 高
C03 | motivation | 镜像定义：同消息 FM @200Hz，γ=0.25 | s_i(t)=γA·cos(ω_i t+β sin ω_m t)；−20lgγ=12.04dB | Mirror_* 块+mirrorFreq/mirrorAmplitude | F/B | 高
C04 | circuit | 发射机模型截图 | cap_tx.png | Simulink 截图 | A | 高
C05 | measurement | 发射频谱：1kHz 有用 + 0.2kHz 镜像（双边离散线谱） | F_tx_spectrum_bisided_20260915.png | 仿真 | D | 高
C06 | theory | 一次变频=复数混频 z1 = LPF{r·2e^(−jω1 t)} | 有用 1000−600=+400；镜像 200−600=−400（复谱正负分离） | Stage1_* 拓扑 | J | 高
C07 | circuit | Stage1 放大截图（RF_In→I/Q 混频→LPF） | cap_rx_stage1.png | 截图裁剪 | A | 高
C08 | measurement | z1 频谱：±400 分居；z1 星座：A(1±γ) 环带 ±52.3% | F_z1_spectrum_r14.png + F_z1_constellation_r15.png | 仿真 | B/D | 高
C09 | theory | 二次旋转 z2 = z1·e^(−jψ)，ψ=ω_IF·t | I2=I1cosψ+Q1sinψ；Q2=−I1sinψ+Q1cosψ | Stage2_Combine 符号 [++]/[−+] | J | 高
C10 | circuit | Stage2 放大截图（4 乘法器+2 合路+2 LPF） | cap_rx_stage2.png | 截图裁剪 | A | 高
C11 | measurement | z2 频谱：有用归 DC、镜像 −800Hz(−11.9dBc≈−20lgγ) | F_z2_spectrum_r14.png | 仿真 | D | 高
C12 | theory | 基带 LPF 300Hz 四极点级联，DC 增益 1，−3dB=241Hz | 分子=分母常数项 | lpfCutoff+系数 | A/J | 高
C13 | measurement | LPF 后：有用 DC±50；镜像 −44.8dBc(开)/−54.7(关)，净压制 32.9dB | F_bb_on_r14.png + F_bb_off_r14.png + F_mirror_compare.png | 仿真 | B | 高
C14 | theory | 零中频鉴频：ω̂=(I·ΔQ−Q·ΔI)/(I²+Q²+ε)，m̂=ω̂/(2πΔf) | ε=1e-6 防零除；G=1/(2π·200)=7.958e-4 | FM_Disc_* 拓扑+参数 | J | 高
C15 | circuit | 鉴频器放大截图（Δ 导数+乘加+I²+Q²+ε） | cap_rx_disc.png | 截图裁剪 | A | 高
C16 | measurement | 恢复消息 corr=0.9613、时延 2.20ms（微分链群延迟）、频偏峰值 214Hz | F_recovered_r17.png | 仿真 | D | 高
C17 | measurement | 基带 I/Q 时域（50Hz 调幅正交对） | F_bb_iq_time.png | 仿真 | B | 高
C18 | measurement | IQ 轨迹近圆 + 包络纹波 ±27.4%@50Hz（IF LPF 带内倾斜 |H(600)|≈0.88 vs |H(200)|≈1.0；鉴频 I²+Q² 归一化抵消） | F_iq_circle.png + F_envelope.png | 仿真 | B | 高
C19 | comparison | 全链参数表：fc/fm/Δf/β/LO1/LO2/两 LPF/γ/ε/G/仿真时长 | 参数表 | 模型 workspace（2026-09-16 实测） | H | 高
C20 | other | 根模型总览截图 | cap_root.png | 截图 | C | 高
C21 | other | 接收机全图截图 | cap_rx.png | 截图 | C | 高

## 待人类补充

（无——全部数值/图像均从模型与仿真直接获得）
