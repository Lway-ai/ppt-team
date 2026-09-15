# 风格抽样记录
- 随机种子: 20260913, 从 IMS2024(141 份)+RFIC2024(1 份)共 142 份 PDF 中抽取 3 份
- 样本: IMS2024/2024_07_02_IF01_1/IF01_32.pdf(1页,信息量有限) | IMS2024/2024_07_02_IF01_1/Th01C_2.pdf(20页) | RFIC2024/2024_07_02_RMo01A_1/RMo01B_2.pdf(25页)
- 全部 960×540pt(16:9)
- 学习方式: 2 个并行子代理, PyMuPDF 逐 span 测量字体/字号/颜色/位置
- 约束已合并进 skills/ppt-conference-style/SKILL.md 与 scripts/style.json

## 2026-09-14 全语料轮（v0.3）
- RFIC2024/2024_07_02_RMo01A_1 全量 87 deck / 2536 页扫描（analyze_corpus.py + deep_measure.py + 版式分类）
- 50 页分层渲染目检（renders_rmo01a/，覆盖 19 分会）
- 产出: RFIC2024_corpus_constraints.md（逐元素测量+87 deck 一览）；SKILL.md 重写为语料多数派默认
  （Calibri-Bold 48pt 青绿标题 / 青绿 bullet / 32-28-24 三级 / 公式 Cambria Math / 表格三流派 / 图线语义 / 版式原型 A–L）
- style.json: 档位补 17.5/28/34-46，色板补 19 个语料实测色，字体白名单补 Arial Narrow
- 子代理 prompt: architect/builder/consolidator/judge 均接入新法典条目
- 备份: 全部被改文件 *.bak-corpus2024（含用户作用域 SKILL.md）
- 修正旧结论: 默认参照 Zou→官方模板多数派；"零表格"→对比表是标准收尾；bullet 黑→青绿；无备份页→Appendix 合法
