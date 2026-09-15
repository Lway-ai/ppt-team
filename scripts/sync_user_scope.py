#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_user_scope.py — 把插件内的技能/法典同步到用户作用域（单一真源 = 本插件目录）。
目标: ZCode(~/.zcode/skills) 与 Codex(~/.codex/skills/ppt-team)。
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
PLUGIN_HOME = PLUGIN
FILES = [
    (os.path.join(PLUGIN, 'skills', 'ppt-conference-style', 'SKILL.md'), 'SKILL.md'),
]


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
    cdst = os.path.join(CODEX_SKILL, 'SKILL.md')
    content = build_codex_skill()
    cur = open(cdst, encoding='utf-8').read() if os.path.exists(cdst) else ''
    if cur != content:
        dirty = True
        if check_only:
            print('DRIFT: codex ppt-team SKILL.md')
        else:
            if cur:
                open(cdst + '.bak-autosync', 'w', encoding='utf-8', newline=chr(10)).write(cur)
            open(cdst, 'w', encoding='utf-8', newline=chr(10)).write(content)
            print('synced codex %s' % cdst)
    else:
        print('ok: codex ppt-team SKILL.md')
    if check_only and dirty:
        sys.exit(1)
    print('user scope %s' % ('in sync' if not dirty else 'updated'))


if __name__ == '__main__':
    main()
