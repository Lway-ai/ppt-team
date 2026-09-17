# FM_IQ_Receiver_RMo01A — 交付记录

**Deck**: [FM_IQ_Receiver_RFIC2024.pptx](FM_IQ_Receiver_RFIC2024.pptx) · 19 页 · RFIC2024 官方模板多数派风格（scripts/style.json）· 无会议身份元素
**源模型**: `D:\wanglei\project\TDA7707_GNSS\E_project\FM\FM_IQ_Receiver_Basic.slx`（Weaver 镜像抑制 FM 接收 + FM 发射，根 2 子系统 60 块）
**美观对照**: `RFIC2024/2024_07_02_RMo01A_1/`（87 deck 语料；复现档 `_learnings/perdeck_renders/`）
**日期**: 2026-09-16 · 制作：ppt-team 四角色流水线（architect → builder → consolidator ↔ judge）

## 叙事线

问题驱动型（镜像抑制主线）：封面 → Outline → 痛点（镜像同消息同 β 仅低 12.04 dB）→ FM 预备 → 发射双谱 → 四道防线全景 → 防线①复混频 → z1 证据 → 防线②旋转 → z2 证据 → 防线③基带 LPF → 开/关对照 32.9 dB → 防线④鉴频 → 鲁棒性 → corr=0.9613 恢复 → 全链参数表 → 结论 → 致谢/文献。
大纲三变体全文见 [outline_variants.md](outline_variants.md)。

## 质量门禁（全部通过）

| 门禁 | 结果 |
|---|---|
| verify_deck.py（--style scripts/style.json） | 0 FAIL / 0 WARN / 7 INFO（6 OMML + 1 已裁决版心 INFO） |
| judge 视觉验收 | r1 18/19 → r2/r3/r4 全 pass（改动页制）；Gate C 全新实例全片终审 19/19 pass |
| 数值抽查（Gate C） | 24 项登记值全命中；禁用旧口径（corr=0.9988 / Δ47.4dB / ±8.5% / "4阶Butterworth"）零出现；算术自洽 |
| 参数一致性 | 47 个模型工作区变量 MATLAB getVariable 当日实测全命中（[data_provenance.md](data_provenance.md)） |

评审链证据：[review_log.md](review_log.md)（round 0–4）· [consolidator_r1.md](consolidator_r1.md)/[consolidator_r2.md](consolidator_r2.md) · [judge_report_r1.json](judge_report_r1.json)…[judge_report_final.json](judge_report_final.json)/[judge_report_r4.json](judge_report_r4.json)

## 循环打磨记录（用户要求：对比参考→review→修改，循环至同美观）

1. **循环 1**：judge r1 抓 p3 红蓝语义反色；consolidator r1 对照 RMo01A 语料开 36 条指令（含 judge 漏报的 p7 同根反色；否决 judge 对 p11 的语义冲突建议）→ builder 全落地 → 全 pass。
2. **循环 2**：consolidator r2 换 5 份新语料拼图提基准，开 G01–G09 → 全落地 → 全 pass。
3. **Gate C 终审**（全新 judge 实例+数值抽查）：可交付；余 3 个图内轻症。
4. **循环 3**：MATLAB regen_c3.m 重生成 4 张图（z1 底影对齐簇色 / z2 收紧空轴 / 图内字号提档 / iq_circle 术语"四极点级联"）+ builder 换图与 p6 盒内块数 → judge r4 全 pass，收敛。

## 复现

```powershell
# 构建源（builder 会话内执行序）：build_deck.ps1（COM 建页）→ build_eq.py（OMML 注入+三线表）→ 渲染验证
powershell -File ../../scripts/export_slides.ps1 -Pptx FM_IQ_Receiver_RFIC2024.pptx -OutDir render
C:/Python314/python.exe ../../scripts/verify_deck.py FM_IQ_Receiver_RFIC2024.pptx --style ../../scripts/style.json
# 仿真图重生成（需 MATLAB，数据源 FM/_ppt_run/assets/simdata_r15.mat，不重跑仿真）
matlab -batch run('figs/regen_c3.m')
```

## 待讲者补充（有意占位）

- p18 致谢正文、p19 References 条目（素材中不存在，按"不编造"纪律留框架）
- 封面未写单位行（讲者自行补充；其余封面要素已按语料惯例就位）

## 目录

`assets/` 截图+仿真图（旧图 `*.png.bak-c3`）· `figs/regen_c3.m` 图重生成脚本 · `render/` 19 页渲染图 · deck 备份 `*.bak-r0…r4` · 构建源 `deck_content.json` / `deck_emph.json` / `table16.json` / `build_deck.ps1` / `build_eq.py`
