# MVP 交付记录 — Zou 风格 3 页演示 deck

日期: 2026-09-15 | profile: `scripts/style.zou.json` | 用时: 单会话内

## 这是第一份"完整流水线 + 全套交付物"的可复现案例

| 交付物 | 文件 | 状态 |
|---|---|---|
| 内容清单实例 | `content_manifest.md` | 6 条, 1 条待人类补充 |
| 数据来源表实例 | `data_provenance.md` | slide 上数值全部可溯源 |
| 大纲/agenda | `agenda.md` | 3 页 |
| 构建脚本 | `build.ps1` | builder 读取 Zou profile 建页 |
| 交付 deck | `mvp_zou.pptx` | 3 页, 原生可编辑 |
| 渲染图 | `render/slide0*.png` | export_slides.ps1 导出 |
| verify 报告 | `verify_report.json` | **0 FAIL**, 6 WARN(已逐条裁决), 4 INFO |
| judge 报告 | `judge_report.json` | **3 pass** (第 1 轮 slide2 乱码 FAIL → 回炉修复 → 复审 pass) |

## 流水线轨迹（双门禁真实运转的一次记录）

1. `build.ps1`（builder=COM+Zou profile）建 3 页
2. `inject_omml.py --tex` 注入公式（omml_tex 引擎）
3. `export_slides.ps1` 渲染
4. `verify_deck.py --style style.zou.json` → 0 FAIL（WARN 列表进 judge 裁决）
5. judge 目检: 第 1 轮 slide2 bullet 乱码（FAIL：构建脚本内联非 ASCII 违反安全管线 3）
   → 回炉改为 UTF-8 文件传入 → 第 2 轮复审 pass
6. 本 README + 数据来源表核对 → 交付

## 复现方式

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File examples\mvp_zou\build.ps1
python scripts\inject_omml.py examples\mvp_zou\mvp_zou.pptx --slide 3 --tex "F = \frac{S_i}{S_o} = \frac{1}{G_t}, \quad \mathrm{NF} = 10\log_{10} F" --name "Equation 1" --x 200 --y 370 --w 560 --h 80 --size 24
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_slides.ps1 -Pptx <绝对路径>\examples\mvp_zou\mvp_zou.pptx -OutDir <绝对路径>\examples\mvp_zou\render
python scripts\verify_deck.py examples\mvp_zou\mvp_zou.pptx --style scripts\style.zou.json --json examples\mvp_zou\verify_report.json
```
