#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_user_scope.py — 把插件内的风格技能/法典同步到用户作用域（单一真源 = 本插件目录）。
用法: python scripts/sync_user_scope.py [--check]
"""
import filecmp
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.abspath(os.path.join(HERE, '..'))
USER_SKILL = os.path.join(os.path.expanduser('~'), '.zcode', 'skills', 'ppt-conference-style')
FILES = [
    (os.path.join(PLUGIN, 'skills', 'ppt-conference-style', 'SKILL.md'), 'SKILL.md'),
]


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
    if check_only and dirty:
        sys.exit(1)
    print('user scope %s' % ('in sync' if not dirty else 'updated'))


if __name__ == '__main__':
    main()
