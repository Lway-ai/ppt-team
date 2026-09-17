# PPT Team 项目记忆

- 真源是仓库内的 `agents/`、`skills/`、`scripts/` 与 `adapters/workbuddy/agents/`；用户级副本只通过 `scripts/sync_user_scope.py` 部署。
- 修改 PPTX 只能使用 PowerPoint COM、raw-zip OMML 或 OfficeCLI；修改后必须保存/关闭，再渲染并运行 `verify_deck.py`。
- 当前会议风格普通西文统一 Times New Roman，中文为微软雅黑，公式为原生 OMML/Cambria Math；Zou profile 保留其版式参数。
- WorkBuddy 未继承环境变量时，同步脚本优先探测已有的 `C:\Users\wanglei\.workbuddy`。
- OfficeCLI 对 raw-zip 注入的 `a14:m` 可能报告已知 schema 兼容错误；发布仍需 PowerPoint 可打开/渲染、`verify_deck` 通过和 judge 视觉验收。
