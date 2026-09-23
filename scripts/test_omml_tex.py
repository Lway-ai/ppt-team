#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_omml_tex.py — omml_tex 生成器的结构化回归测试（纯标准库）。跑法: python scripts/test_omml_tex.py"""
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from omml_tex import tex_paragraphs  # noqa: E402

M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
FAILS = []


def case(name, cond, detail=''):
    print(('  PASS ' if cond else '  FAIL ') + name + ('' if cond else '  ' + str(detail)[:220]))
    if not cond:
        FAILS.append(name)


def wellformed(paras):
    for p in paras:
        ET.fromstring('<a:p xmlns:m="%s" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">%s</a:p>'
                      % (M, p))


def flat(paras):
    return ''.join(paras)


def main():
    # 1 分式 + 逗号
    x = tex_paragraphs(r"F = \frac{S_i}{S_{out}}, \quad \mathrm{NF} = 10\log_{10} F")
    wellformed(x)
    case('frac structure', '<m:f><m:num>' in flat(x) and '<m:den>' in flat(x), x)
    case('subscript sSub', '<m:sSub>' in flat(x), x)
    case('mathrm upright NF', 'NF' in flat(x), x)
    case('log present', 'log' in flat(x), x)

    # 2 上下标组合
    x = tex_paragraphs(r"v_m^2 = \omega_0^2 L C")
    wellformed(x)
    case('sSubSup pair', '<m:sSubSup>' in flat(x), x)

    # 3 根号(带次数)
    x = tex_paragraphs(r"c = \sqrt{a^2 + b^2} + \sqrt[3]{x}")
    wellformed(x)
    case('sqrt rad', '<m:rad>' in flat(x) and 'degHide' in flat(x), x)
    case('cubic root degree', '<m:deg>3</m:deg>' in flat(x) or '<m:deg><m:r>' in flat(x), x)

    # 4 希腊字母 + 符号
    x = tex_paragraphs(r"\phi = \omega t + \Delta\phi, \; Z \propto \omega L")
    wellformed(x)
    case('greek phi', 'φ' in flat(x) and 'Δ' in flat(x) and 'ω' in flat(x), x)
    case('propto symbol', '∝' in flat(x), x)

    # 5 中文正体 + EA 字体（事故修复样式）
    x = tex_paragraphs(r"F = \frac{S_i}{S_o}\text{（噪声系数定义，中文须正体）}")
    wellformed(x)
    case('EA font declared', '微软雅黑' in flat(x), x)
    case('EA run upright i=0', '<a:rPr lang="en-US" i="0"><a:latin typeface="Cambria Math"/><a:ea' in flat(x), x)

    # 6 矩阵 pmatrix 2x3
    x = tex_paragraphs(r"M = \begin{pmatrix} g_m & C_{gs} & r_o \\ 0 & g_{ds} & L_1 \end{pmatrix}")
    wellformed(x)
    case('matrix 2 rows', flat(x).count('<m:mr>') == 2, x)
    case('matrix 3 cols', 'm:val="3"' in flat(x), x)
    case('pmatrix parens', 'begChr m:val="("' in flat(x) and 'endChr m:val=")"' in flat(x), x)

    # 7 自适应定界符
    x = tex_paragraphs(r"\left[ \frac{a}{b} \right] + (c)")
    wellformed(x)
    case('left/right bracket delim', 'begChr m:val="["' in flat(x), x)

    # 8 多行 → 多段落
    x = tex_paragraphs(r"A = B \\ C = D")
    case('line break two paragraphs', len(x) == 2, len(x))

    # 9 XML 转义
    x = tex_paragraphs(r"a < b")
    wellformed(x)
    case('escape lt', '&lt;' in flat(x), x)

    # 10 chr 类定界符（2026-09-17 修：\left| 曾静默丢竖线且不报错）
    x = tex_paragraphs(r"S = \left| \frac{L}{1+L} \right|^{2} S_{ref}")
    wellformed(x)
    case('left/right pipe delim', 'begChr m:val="|"' in flat(x)
         and 'endChr m:val="|"' in flat(x), x)
    case('pipe delim keeps superscript', '<m:sSup>' in flat(x), x)

    # 11 重音宏 → m:acc
    x = tex_paragraphs(r"g_{n} = \frac{f_{REF}}{\hat{K}_{DCO}}")
    wellformed(x)
    case('hat accent m:acc', '<m:acc>' in flat(x)
         and '<m:chr m:val="\u0302"/>' in flat(x), x)
    x = tex_paragraphs(r"\tilde{c}_{0} = 1 - \frac{\tau}{T}")
    wellformed(x)
    case('tilde accent m:acc', '<m:chr m:val="\u0303"/>' in flat(x), x)
    case('accent no literal macro', 'hat' not in flat(x)
         and 'tilde' not in flat(x), x)

    # 12 长箭头符号（2026-09-17 修：曾字面化成 Longleftrightarrow）
    x = tex_paragraphs(r"a \Longleftrightarrow b")
    wellformed(x)
    case('Longleftrightarrow glyph', '\u27fa' in flat(x)
         and 'Longleftrightarrow' not in flat(x), x)

    print('\n== %d cases failed ==' % len(FAILS))
    for f in FAILS:
        print('  -', f)
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
