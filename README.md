# ppt-team — 多代理会议 PPT 制作系统

借鉴 OpenAI Navier–Stokes 项目的多代理方法论，落成 ZCode 插件：
变体扇出 → 热身降维 → 成果播种 → 交叉授粉 → 确定性验证兜底 → 人类三道门禁。

## 架构

```
素材 ─→ [内容官×3 扇出提取] ──────────── Gate A(人):选大纲变体
     ─→ [迷你版3页全流水线] ──────────── Gate B(人):定稿风格规范
     ─→ [ppt-builder 按章节分组构建]
     ─→ [ppt-consolidator 交叉授粉] ⇄ 弱页重建
     ─→ [verify_deck.py 确定性检查:全片0 FAIL]  ← "Lean"层,程序而非AI
     ─→ [ppt-judge 只审本轮改动页] ⇄ FAIL页回炉(≤5轮)  ← 双门禁
     ─→ 交付前全片 verify + judge 终审 ───── Gate C(人):终审
```

## 验证双门禁（v0.2 起硬性）

1. **`verify_deck.py` 全片 0 FAIL**——检查项：形状越界 / 图片拉伸 / 字号档位 / 色板 /
   文本溢出(启发式) / 禁用文本 / 页码一致性 / **形状相交** / 页脚色带越界。
   相交规则：文本×文本重叠、容器画在其子元素之上（横幅盖标签、徽章被切）= **FAIL**；
   图片参与的交叠（图片自带留白）= WARN 目检裁决；装饰/背景件白名单豁免。
   合成测试（横幅上移制造压标签）已验证可自动命中三类错误。
2. **ppt-judge 硬门禁，只审本轮改动页**——改了哪几页审哪几页，FAIL 页回 builder 修复至通过；
   交付前再做全片终审。改动即验收，不靠事后抽查。

## 组件
| 路径 | 作用 |
|---|---|
| `agents/ppt-team.md` | **团队总指挥（conductor）**——一次调用跑完整流水线，内部调度四名角色 |
| `agents/` | 4 个执行角色：architect(大纲变体)/builder(建页)/consolidator(授粉+构图审查)/judge(验收) |
| `skills/ppt-conference-style/` | 完整法典（**RFIC2024 官方语料 87 deck/2536 页全量测量** + 4 份历史深测）+ 安全管线手册 + 已知盲区清单 |
| `commands/make-ppt.md` | `/make-ppt` 斜杠命令，编排整条流水线（含双门禁、写入串行纪律） |
| `scripts/verify_deck.py` | 确定性检查器（纯标准库）：越界/拉伸/档位/色板/相交(递归)/色带/页码/字体别名/包完整性/公式可编辑性 |
| `scripts/test_verify_deck.py` | 验证器回归测试集（16 个合成用例，改 verify/style 前后必须跑） |
| `scripts/export_slides.ps1` | PowerPoint COM 渲染导出 |
| `scripts/build_helpers.ps1` | COM 建页函数库（New-Deck/Add-TextBox/Add-FooterBand/HexColor…，冒烟已通） |
| `scripts/inject_omml.py` | OMML 公式 raw-zip 注入（自动 a14:m 包装）+ `scripts/omml/eq_*.xml` 片段库 |
| `scripts/make_footer_band.py` | 生成 `assets/footer_band.png` 页脚渐变色带素材 |
| `scripts/sync_user_scope.py` | 用户作用域 SKILL.md 单向同步（真源 = 本插件目录） |
| `scripts/style.json` | 可调参数法典（字号档位/色板/相交白名单/字体别名）；`style.zou.json` = Zou 变体 profile |
| `templates/` | 内容清单合同 + 技术数据来源表（数据真实性在 Gate C 人工核对） |
| `_learnings/` | 风格学习原始记录：`RFIC2024_corpus_constraints.md`（87 deck 全量，主参照）+ Zou 28 页深测等 |
| `_backups/` | 历次批量修改的备份（按标签分目录） |
| `AGENTS.md` | 全体代理硬性禁令 + 流程纪律 + 已知盲区 |

## 团队的三层包装
1. **插件级**：安装 `ppt-team` 插件 = 装上整个团队（5 个代理 + 法典 + 命令 + 脚本）；
2. **指挥级**：把任务交给 `ppt-team` 代理 = 由总指挥调度四名角色（可派子代理则派，不可则亲自戴帽执行）；
3. **命令级**：`/make-ppt` = 从主会话直接触发整条流水线（等价入口）。

## 安装状态（2026-09-13 已注册）

- **插件本体**：已在 `~/.zcode/cli/config.json` 的 `plugins.dirs` 注册本目录
  （机制 = ZCode 的 `readUserPluginConfigState`→扫描 `plugins.dirs`→读 `.zcode-plugin/plugin.json`→默认启用），
  并在 `plugins.enabledPlugins` 写入 `"ppt-team": true`。**重启 ZCode / 新会话生效**，
  之后 4 个角色成为原生可调用子代理（Agent 工具的 subagent_type）。
- **用户作用域**（立即生效）：`~/.zcode/skills/ppt-conference-style/SKILL.md`、
  `~/.zcode/commands/make-ppt.md` 已部署——任何工作区都能加载风格法典、使用 `/make-ppt`。
- 回滚：`~/.zcode/cli/config.json.bak-before-ppt-team`。
- 若未来需要 GUI 管理：设置 → Plugin Management（注：Agent 模式下该入口可能提示 retired，
  本地注册走 `plugins.dirs` 字段即可，此为已验证路径）。

## 用法
在会话里输入 `/make-ppt <素材> <受众与页数>`，或直接描述需求并要求按本插件流水线执行。
单页修改时：builder 改 → verify（含相交检测）→ judge 只审该页 → 记录 changelog。
