#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_user_scope.py — 把插件内的技能/法典同步到用户作用域（单一真源 = 本插件目录）。
目标: ZCode(~/.zcode/skills)、Codex(~/.codex/skills/ppt-team)、
      Trae Work(~/.trae-cn/skills/ppt-team + ppt-conference-style)。
用法: python scripts/sync_user_scope.py [--check]
"""
import filecmp
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.abspath(os.path.join(HERE, '..'))
USER_SKILL = os.path.join(os.path.expanduser('~'), '.zcode', 'skills', 'ppt-conference-style')
CODEX_SKILL = os.path.join(os.path.expanduser('~'), '.codex', 'skills', 'ppt-team')
TRAE_STYLE_SKILL = os.path.join(os.path.expanduser('~'), '.trae-cn', 'skills', 'ppt-conference-style')
TRAE_TEAM_SKILL = os.path.join(os.path.expanduser('~'), '.trae-cn', 'skills', 'ppt-team')
PLUGIN_HOME = PLUGIN
FILES = [
    (os.path.join(PLUGIN, 'skills', 'ppt-conference-style', 'SKILL.md'), 'SKILL.md'),
]


def _replace_all(s, pairs):
    for a, b in pairs:
        s = s.replace(a, b)
    return s


def build_trae_skill():
    """由仓库适配 SKILL.md 生成 Trae Work 安装副本（frontmatter 后插入主目录声明）。"""
    src = os.path.join(PLUGIN, 'skills', 'ppt-team', 'SKILL.md')
    with open(src, encoding='utf-8') as f:
        s = f.read()
    s = _replace_all(s, [
        ('# PPT Team for Codex', '# PPT Team for Trae Work'),
        ('Apply the architect, builder, consolidator, and judge roles in Codex while using',
         'Apply the architect, builder, consolidator, and judge roles while using'),
        ('This skill is the Codex adapter for the local multi-agent PPT Team. The original\n'
         '`.zcode-plugin` remains the ZCode source package. Codex loads this skill and the\n'
         'project\'s `ppt-conference-style` skill through `.codex-plugin/plugin.json`.',
         'This is the Trae Work adapter for the local multi-agent PPT Team. The original\n'
         '`.zcode-plugin` remains the ZCode source package. Trae Work auto-discovers this skill\n'
         'from `~/.trae-cn/skills/ppt-team/SKILL.md` together with the companion\n'
         '`ppt-conference-style` style codex.'),
        ('Codex does not treat the ZCode `agents/` and `commands/` manifest fields as\n'
         'native plugin components. Therefore the main Codex agent coordinates these roles\n'
         'sequentially, or uses available delegated workers only for read-only extraction,\n'
         'review, rendering, and validation. Never allow two workers to write the same\n'
         'PPTX at the same time.',
         'Trae Work has no first-class `agents/` team object, so this skill coordinates the\n'
         'four roles by dispatching workers that first read the role files in `agents/`.\n'
         'Each phase can fan out readers (extraction, review, rendering, validation), but the\n'
         'PPTX write path is strictly single-writer: never allow two workers to write the\n'
         'same PPTX at the same time.'),
        ('officecli MCP is configured in Codex (`config.toml` → `mcp_servers.officecli`) and\nis an approved',
         'officecli MCP is an approved'),
    ])
    fence = chr(45) * 3            # '---' frontmatter 围栏
    nl = chr(10)                   # 换行
    parts = s.split(fence + nl, 2)
    body = parts[2] if len(parts) == 3 else s
    home_block = ('# 插件主目录（下文所有相对路径解析到这里）' + nl + nl +
                  'PLUGIN_HOME = `' + PLUGIN_HOME + '`' + nl + nl +
                  '本技能可从任意工作目录触发。凡 `agents/...`、`scripts/...`、`templates/...`、' + nl +
                  '`skills/ppt-conference-style/SKILL.md` 等相对路径，一律读作'
                  ' `PLUGIN_HOME' + chr(92) + '<相对路径>`。' + nl + nl)
    return (fence + nl + (parts[1] if len(parts) == 3 else '') + fence + nl + nl +
            home_block + body.lstrip(nl))


def _write_new(dst, content, dirty, check_only, label):
    cur = open(dst, encoding='utf-8').read() if os.path.exists(dst) else ''
    if cur == content:
        print('ok: %s' % label)
        return dirty
    if check_only:
        print('DRIFT: %s' % label)
        return True
    if cur:
        open(dst + '.bak-autosync', 'w', encoding='utf-8', newline=chr(10)).write(cur)
    open(dst, 'w', encoding='utf-8', newline=chr(10)).write(content)
    print('synced %s -> %s' % (label, dst))
    return True


def build_codex_skill():
    """由仓库适配 SKILL.md 生成 Codex 安装副本（frontmatter 后插入主目录声明）。"""
    src = os.path.join(PLUGIN, 'skills', 'ppt-team', 'SKILL.md')
    with open(src, encoding='utf-8') as f:
        s = f.read()
    s = s.replace('technical PPT/PPTX in this project.',
                  'technical PPT/PPTX in any working directory.')
    fence = chr(45) * 3            # '---' frontmatter 围栏
    nl = chr(10)                   # 换行
    parts = s.split(fence + nl, 2)
    body = parts[2] if len(parts) == 3 else s
    home_block = ('# 插件主目录（下文所有相对路径解析到这里）' + nl + nl +
                  'PLUGIN_HOME = `' + PLUGIN_HOME + '`' + nl + nl +
                  '本技能可从任意工作目录触发。凡 `agents/...`、`scripts/...`、`templates/...`、' + nl +
                  '`skills/ppt-conference-style/SKILL.md` 等相对路径，一律读作'
                  ' `PLUGIN_HOME' + chr(92) + '<相对路径>`。' + nl + nl)
    return (fence + nl + (parts[1] if len(parts) == 3 else '') + fence + nl + nl +
            home_block + body.lstrip(nl))


def main():
    check_only = '--check' in sys.argv
    os.makedirs(USER_SKILL, exist_ok=True)
    dirty = False
    for src, name in FILES:
        dst = os.path.join(USER_SKILL, name)
        if not os.path.exists(dst) or not filecmp.cmp(src, dst, shallow=False):
            dirty = True
            if check_only:
                print('DRIFT: %s' % name)
            else:
                if os.path.exists(dst):
                    shutil.copy2(dst, dst + '.bak-autosync')
                shutil.copy2(src, dst)
                print('synced %s -> %s' % (src, dst))
        else:
            print('ok: %s' % name)
    # Codex 目标
    os.makedirs(CODEX_SKILL, exist_ok=True)
    dirty = _write_new(os.path.join(CODEX_SKILL, 'SKILL.md'), build_codex_skill(),
                       dirty, check_only, 'codex ppt-team SKILL.md')
    # Trae Work 目标：风格法典原样复制 + 团队适配器生成
    os.makedirs(TRAE_STYLE_SKILL, exist_ok=True)
    tsrc = os.path.join(PLUGIN, 'skills', 'ppt-conference-style', 'SKILL.md')
    if not os.path.exists(os.path.join(TRAE_STYLE_SKILL, 'SKILL.md')) or \
       not filecmp.cmp(tsrc, os.path.join(TRAE_STYLE_SKILL, 'SKILL.md'), shallow=False):
        if check_only:
            print('DRIFT: trae ppt-conference-style SKILL.md')
            dirty = True
        else:
            shutil.copy2(tsrc, os.path.join(TRAE_STYLE_SKILL, 'SKILL.md'))
            print('synced %s -> %s' % (tsrc, os.path.join(TRAE_STYLE_SKILL, 'SKILL.md')))
    else:
        print('ok: trae ppt-conference-style SKILL.md')
    os.makedirs(TRAE_TEAM_SKILL, exist_ok=True)
    dirty = _write_new(os.path.join(TRAE_TEAM_SKILL, 'SKILL.md'), build_trae_skill(),
                       dirty, check_only, 'trae ppt-team SKILL.md')
    if check_only and dirty:
        sys.exit(1)
    print('user scope %s' % ('in sync' if not dirty else 'updated'))


if __name__ == '__main__':
    main()
