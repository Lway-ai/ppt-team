# 技术数据来源表 — FM_IQ_Receiver_Basic 模型讲解 deck（RFIC2024 风格版，2026-09-16）

> 全部数值来自对 `FM\FM_IQ_Receiver_Basic.slx` 的直接读取与仿真。
> 参数复核：2026-09-16 MATLAB `getVariable` 实测模型工作区 47 个变量（本表全部命中）。
> 仿真口径：sim 0–0.08s，ode45；频谱窗 20–80ms 去暂态；重采样 10kHz；复信号双边谱，矩形窗；
> 离散线谱、k×50Hz bin、全局归一化保留镜像 −12dB 相对幅度（2026-09-15 round16 口径）。
> 机器可读备份：`assets/measurements.txt`；中间数据 `FM\_ppt_run\assets\simdata_r15.mat`、`proc_data.mat`。

| # | 数值/参数 | 出现页(拟) | 来源 | 备注 |
|---|---|---|---|---|
| 1 | fc=1000 Hz, A=1 | 参数表/封面 | 模型工作区 fc, carrierAmplitude | 2026-09-16 实测 |
| 2 | f_m=50 Hz, 幅度 1 | 全片 | fmMsg, messageAmplitude | 实测 |
| 3 | Δf=200 Hz, β=4 | 全片 | freqDev；β=Δf/f_m 推导 | 实测 |
| 4 | 镜像 200 Hz, γ=0.25 | 镜像页 | mirrorFreq, mirrorAmplitude | 同消息同 β（共享 fm_phase_integrator，拓扑验证） |
| 5 | LO1=600, LO2=400, f_LIF=400 | 参数表/环节②③ | stage1LoFreq, stage2LoFreq, fLowIF | LO1+LO2=fc |
| 6 | mixerGain=2（两级 LO 幅度 2） | 环节②③ | mixerGain | 补偿混频 ½ 损耗 |
| 7 | IF LPF=700Hz、基带 LPF=300Hz（ω₀），均四极点级联（两节二阶 ζ=0.707），−3dB=562/241 Hz，DC 增益 1 | 环节②③ | ifLpfCutoff/lpfCutoff+ifLpf/ basebandLpf 分子分母系数 | round18 修正口径：**禁写"4 阶 Butterworth"** |
| 8 | ε=1e-6；G=1/(2πΔf)=7.958e-4 | 鉴频页 | discEpsilon, receiverOutputGain | 实测 |
| 9 | 发射频谱形态（1kHz/0.2kHz 双 FM，Carson 500Hz，双边线谱） | 环节① | 仿真 F_tx_spectrum_bisided | sim. |
| 10 | z1 频谱：有用 +400 / 镜像 −400 | 环节② | 仿真 F_z1_spectrum_r14 | sim. 复谱正负分离 |
| 11 | z1 星座：A(1±γ) 环带，半径起伏 ±52.3%（含 LPF 倾斜） | 环节② | 仿真 F_z1_constellation_r15 | sim.；±8.5% 为旧口径作废 |
| 12 | z2 频谱：0 / −800；镜像 −11.9 dBc | 环节③ | 仿真 F_z2_spectrum_r14 | sim.；−20lg0.25 理论 −12.04dB |
| 13 | LPF 后镜像 −44.8 dBc(开) / −54.7 dBc(关)；净压制 32.9 dB | 环节③ | 仿真 F_bb_on/off_r14、F_mirror_compare | sim. |
| 14 | 包络纹波 ±27.4% @50Hz；|H(600)|≈0.88 vs |H(200)|≈1.0 | 基带特性页 | 仿真 F_iq_circle/F_envelope；|H| 由 ifLpf 系数计算 | sim. |
| 15 | corr=0.9613；时延 2.20ms（恢复滞后参考）；频偏峰值 214Hz | 解调页 | 仿真 F_recovered_r17、measurements.txt | sim.；时延口径=恢复滞后参考 |
| 16 | 仿真时长 0.08s | 参数表 | simStopTime | 实测 |
| 17 | f₃dB=0.803×ω₀（1/(1+u⁴) 特性导出） | 环节②③脚注 | 理论 | 与 #7 一致 |

## 规则确认

1. builder 只准使用本表登记值；不得从风格/惯例推断数值。
2. 同一参数全片一致（以本表为准）。
3. 全部曲线为 **sim.**（无数值竞争对比表，无实测硬件数据；Comparison 位用全链参数表 C19 承接）。
4. 旧口径 corr=0.9988 / 镜像 Δ47.4dB / 纹波 ±8.5% 为 2026-09-14 旧数据，**禁用**。
5. LPF 描述一律"四极点级联 / 4-pole cascade"，−3dB 值写 562/241 Hz；ω₀=700/300 Hz 可并写。
