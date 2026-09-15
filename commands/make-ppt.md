---
description: 运行多代理会议 PPT 流水线（扇出大纲→热身→建页→授粉→验证→验收）
argument-hint: <素材文件或文件夹> <受众与页数预算> [风格: conference|isscc]
---
你是编排者。按以下阶段执行多代理流水线（方法论：变体扇出/热身降维/成果播种/交叉授粉/确定性验证）：

0. 加载 ppt-conference-style 技能；盘点素材；建 changelog 与备份。内容产出必须按 templates/content_manifest.md 合同；所有技术数值登记 templates/data_provenance.md。
1. 内容官扇出：用 Agent 工具并行派 3 个 general-purpose 代理，各自提取内容清单（关键信息点+出处），交叉核对差异并和用户确认补全。
2. Gate A：派 ppt-architect 产出 2-3 个大纲变体，用 AskUserQuestion 让用户选择/杂交。
3. Gate B：先做 3 页迷你版走完整循环（builder 构建 → export_slides.ps1 渲染 → verify_deck.py → ppt-judge 评），用户确认后冻结风格规范。
4. 全量建页：派 ppt-builder 分组建页，**但写入必须串行——同一时刻只允许一个 builder 持有该 .pptx 的 COM 句柄**（可并行的只有：内容提取、评审、渲染、验证）；每组完成后派 ppt-consolidator 交叉授粉，builder 按指令重建弱页。建页工具：scripts/build_helpers.ps1（COM 函数库）+ scripts/inject_omml.py（OMML 公式注入）。
5. 验证环：**每个 builder 工作轮**都以双门禁收尾——(a) verify_deck.py 全片 0 FAIL（含相交/完整性/公式检查）；(b) ppt-judge **只审该轮改动页**，fail 页回 builder 修复至通过（轮上限 5，超出升级用户）。
6. Gate C：交付前全片 verify + judge 全片终审；逐项核对 data_provenance 表；向用户交付渲染图 + verify/judge 报告 + changelog。

纪律：每轮先备份；verify 不绿不叫 judge；judge 只审改动页但**不可跳过**；改动与 judge 结论全记 changelog。
$ARGUMENTS
