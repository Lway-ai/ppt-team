# 把 PPT TEAM 五个角色导入 WorkBuddy（自定义子代理通道）

> 背景：`trae_custom_agents_ppt_team.md` 走的是 Trae 的「自定义智能体」面板（手工填提示词）。
> WorkBuddy 这边有**磁盘文件通道**——角色直接落成 `.md` 文件，不需要在 UI 里粘贴提示词，
> 新增/修改角色即改文件，且支持在 frontmatter 里做**工具白名单**（这是 Trae 面板给不了的硬约束）。
>
> 本文件记录安装位置与用法；角色本体的唯一来源仍是仓库里的 `agents/*.md`。

## 一、WorkBuddy 的子代理发现规则（已从 CLI 包体实测确认）

从 `resources/app.asar.unpacked/cli/dist/codebuddy.js` 提取到的路径常量：

```js
getHomeDir()          = process.env.CODEBUDDY_CONFIG_DIR || ~/.codebuddy
getHomeAgentsDir()    = <HomeDir>/agents
getProjectHomeDir()   = <WorkDir>/.codebuddy
getProjectAgentsDir() = <WorkDir>/.codebuddy/agents
```

本机 `CODEBUDDY_CONFIG_DIR = C:\Users\wanglei\.workbuddy`，因此：

| 类型 | 路径 | 范围 | 优先级 |
| :--- | :--- | :--- | :--- |
| 用户级子代理 | `C:\Users\wanglei\.workbuddy\agents\` | 所有项目可用 | 较低 |
| 项目级子代理 | `<工作目录>\.codebuddy\agents\` | 仅该项目 | 最高（同名覆盖用户级） |
| 插件代理 | `<插件目录>\agents\`（清单 `agents` 字段声明） | 插件启用期间 | — |

插件清单目录有三个合法名字：`.codebuddy-plugin` / `.workbuddy-plugin` / `.claude-plugin`，
清单文件固定为 `plugin.json`。本仓库目前只有 `.zcode-plugin` + `.codex-plugin`，**尚未**提供 CodeBuddy 清单。

## 二、本次安装内容（用户级 = 全项目可用）

**真源 = 仓库 `adapters/workbuddy/agents/`**（5 个文件，随仓库版本化）；
安装副本在用户作用域，由同步脚本单向部署：

```bash
python scripts/sync_user_scope.py --only workbuddy     # 部署/更新
python scripts/sync_user_scope.py --check --only workbuddy   # 漂移检测
```

安装位置：`C:\Users\wanglei\.workbuddy\agents\`（脚本优先取 `CODEBUDDY_CONFIG_DIR`；未设置时自动探测已有的
`.workbuddy`，最后才回落 `~/.codebuddy`）。
脚本沿用既有约定：内容一致打印 `ok`，不一致时打印 `synced`/`DRIFT:` 并先备份 `.bak-autosync`。

| 文件 | 角色 | 工具白名单 | 写权限 |
| :--- | :--- | :--- | :--- |
| `ppt-team.md` | 总指挥（conductor） | Read, Write, Edit, Glob, Grep, Bash, PowerShell, Agent, Skill, AskUserQuestion, TaskCreate/Get/Update/List | 可写（changelog、报告） |
| `ppt-architect.md` | 大纲架构师 | Read, Write, Glob, Grep | 仅写大纲 md，禁碰 pptx |
| `ppt-builder.md` | 构建代理 | Read, Write, Edit, Glob, Grep, Bash, PowerShell | **pptx 唯一写者** |
| `ppt-consolidator.md` | 交叉授粉代理 | Read, Glob, Grep | 只读 |
| `ppt-judge.md` | 视觉验收裁判 | Read, Glob | 只读 |

设计要点：

1. **薄适配层**：每个文件只装「身份 + 公共声明 + 职责摘要 + 边界」，正文要求角色动手前完整读取
   `PLUGIN_HOME/agents/<角色>.md` 与 `skills/ppt-conference-style/SKILL.md`。
   角色定义的唯一真源仍在仓库 `agents/`，改仓库即全量生效，不会出现两份提示词漂移。
2. **工具白名单即纪律**：judge/consolidator 物理上拿不到写工具，「只看渲染图、不为自己辩护」「不自己动手改文件」
   从口头约束升级为能力约束。
3. **PLUGIN_HOME 写死绝对路径**：子代理看不到主会话上下文，因此在文件里显式声明
   `PLUGIN_HOME = D:\wanglei\project\TDA7707_GNSS\E_project\multi_agent_PPT_zcode`，
   任何工作目录下都能解析团队资产。

## 三、用法

1. **加载时机**：手工放入磁盘的子代理在**下次启动会话**时加载（本次安装已通过一次实跑验证：
   `ppt-judge` 可被 Agent 工具直接调度，且工具白名单生效）。
2. **自动调度**：主代理按各角色 `description` 里的「何时调用」自动派发；`ppt-team` 的
   description 里带了 `PROACTIVELY`，命中「做一份会议风格 PPT」类需求会优先起团队。
3. **显式调用**：在对话里点名，例如「用 ppt-builder 改 P12」「让 ppt-judge 只审 P8/P12」。
4. **接口**：本机 WorkBuddy 的 `/agents` 面板可查看/编辑/删除这五个角色；
   Trae 侧的四个自定义智能体与它们**互不影响**（两套宿主、同一份 `agents/*.md` 真源）。
5. **回归验证方法**（改完角色文件后自检）：
   先 `python scripts/sync_user_scope.py --only workbuddy` 重新部署，再派一个只读角色做一次最小读取，
   确认「能发现 + 工具白名单正确」。本次用 `ppt-judge` 验证通过（返回角色名、工具清单 = Read/Glob、PLUGIN_HOME）。
6. **漂移检查**：应在同步脚本解析出的实际 WorkBuddy home 上执行；当前仓库版本会优先探测已有的
   `C:\Users\wanglei\.workbuddy`，避免普通 PowerShell 未继承 `CODEBUDDY_CONFIG_DIR` 时误查 `~/.codebuddy`。
   如发现 `DRIFT`，执行 `python scripts/sync_user_scope.py`（不加 `--only`）全量同步，会先备份 `.bak-autosync`。

## 四、可选第二条通道：把整个仓库打成 WorkBuddy 插件

如果希望以「插件」形态安装（可上架市场、可版本化分发），需要补一份 CodeBuddy 清单：

```json
{
  "name": "ppt-team",
  "version": "0.3.0",
  "description": "Multi-agent conference PPT team: outline fan-out, COM/raw-zip builders, cross-pollination consolidator, deterministic verifier, visual judge",
  "author": { "name": "Wanglei PPT Team" },
  "license": "UNLICENSED",
  "agents": [
    "./agents/ppt-team.md",
    "./agents/ppt-architect.md",
    "./agents/ppt-builder.md",
    "./agents/ppt-consolidator.md",
    "./agents/ppt-judge.md"
  ],
  "skills": "./skills",
  "commands": "./commands"
}
```

存放路径：`<仓库根>\.codebuddy-plugin\plugin.json`（与 `.zcode-plugin` 平级）。

**注意**：该通道与用户级安装**会形成同名重复代理**（`/agents` 面板会把重复项标出来并要求二选一），
因此除非确实要走插件分发，否则不要两条通道同时开——当前采用的是用户级通道。

## 五、与其它宿主的对应关系

| 宿主 | 接入方式 | 位置 |
| :--- | :--- | :--- |
| ZCode | 插件原生支持 agents/skills/commands | `.zcode-plugin/plugin.json` |
| Codex | 技能适配层，由主代理顺序调度角色 | `.codex-plugin/plugin.json` + `skills/ppt-team/SKILL.md` |
| Trae Work | 自定义智能体面板（需手工粘贴提示词） | `trae_custom_agents_ppt_team.md` |
| **WorkBuddy** | **自定义子代理磁盘文件 + 工具白名单** | `~\.workbuddy\agents\*.md` |
