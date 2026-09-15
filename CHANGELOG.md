# Changelog

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
