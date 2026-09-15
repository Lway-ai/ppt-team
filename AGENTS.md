# 本工作区全局守则（所有代理必读）

## 硬性禁令
1. 禁止用 python-pptx **保存** PPTX（重存会破坏兼容性）；编辑一律走 PowerPoint COM（PowerShell），文件级修改走 raw-zip 拼接。
2. OMML 公式形状（Aeq/Beq/RotA/RotB/AM* 等，特征是 TextRange.Runs().Count == 0 或文本显示为 ??）**永远不要用 .Text 赋值**——公式只能改 XML。
3. 向 PowerShell 传中文/非 ASCII 文本必须经 UTF-8 文件 + `Get-Content -Encoding UTF8`，不要内联在 .ps1 里。
4. 任何批量修改前必须先备份原文件（`*.bak-<标签>`）。

## 流程纪律
5. 每轮修改：改 → 导出渲染图 → `scripts/verify_deck.py` 检查 → 记录 changelog。
6. **验证双门禁（硬性）**：
   a. `verify_deck.py` 全片 0 FAIL（含形状相交检测——文本×文本重叠/容器盖子元素 = FAIL，图片参与的交叠 = WARN 需目检）；
   b. **judge 视觉验收只审本轮改动的页面**（改哪几页审哪几页，不必全片重审）——FAIL 页自动回 builder 修复，直到该页通过。做到"改动即验收"，不再靠事后抽查。
7. 修复轮上限 5 轮，超出升级给人。verify 不绿不许叫 judge。
8. 风格约束以 `skills/ppt-conference-style/SKILL.md` 为准，改规范必须先改 SKILL.md 再改代码。

## 已知盲区（写给所有代理，避免重犯）
- **并行写同一 .pptx 禁止**：COM/raw-zip 都是独占写，同一时刻只允许一个 builder 持有句柄；并行仅限提取/评审/渲染/验证。
- **形状命名契约**（SKILL.md 第十二节）：FooterBand/PageNo/KeyBox* 等名字参与 verify 的豁免与判定，新建形状必须按契约命名，否则误报成灾。
- **verify 查不了的事**：技术数值真实性（查 templates/data_provenance.md）、图表拓扑正确性、公式内容正确性——Gate C 人工终审必查。
- 几何碰撞已由相交检测覆盖（递归含组合形状）；但**"密度/构图失衡"（大片死区、图占比不足）检测器管不了**——依赖 ppt-consolidator 的构图审查（它是流水线里负责此项的唯一角色，不得跳过）。
- 图片内含留白，图片×文本的 bbox 交叠可能是假阳性——按 WARN 目检裁决，别机械当 FAIL。
- 页面合并/删除后：页码（"N of M"）与"第 N 页"交叉引用必须同步重映射（改前 grep 全片引用，降序替换）。
