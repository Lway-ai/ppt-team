#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inject_omml.py — 向已有 PPTX 的指定页注入原生 OMML 公式形状（raw-zip 拼接，不经 COM）。

背景（SKILL.md 第十节 2/8）: 公式必须原生 OMML/Cambria Math; COM 对数学区字体静默无效,
含东亚文字的 m:r 必须携带 <a:rPr i="0"><a:ea typeface="微软雅黑"/></a:rPr>（片段库已内置）。

用法:
  python inject_omml.py deck.pptx --slide 5 --omml ../scripts/omml/eq_frac.xml \
      --name "Equation 5" --x 120 --y 200 --w 500 --h 70 [--backup]

片段格式: omml/*.xml 的根元素为 <m:oMathPara>（内部声明 xmlns:m / xmlns:a）。
"""
import argparse
import re
import shutil
import sys
import zipfile

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
# PPTX 方言: 数学段落必须包在 a14:m 里(命名空间是 drawing/2010, 不是 powerpoint/2010),
# 否则文件能打开但公式不渲染（实测踩坑）
A14 = 'http://schemas.microsoft.com/office/drawing/2010/main'


def wrap_a14(fragment):
    fragment = fragment.strip()
    if fragment.startswith('<a14:m'):
        return fragment
    inner = re.sub(r'^<m:oMathPara[^>]*>|</m:oMathPara>$', '', fragment)
    return ('<a14:m xmlns:a14="%s"><m:oMathPara xmlns:m="%s">%s</m:oMathPara></a14:m>'
            % (A14, M, inner))


def shape_xml(name, x, y, w, h, fragment, unused_ids):
    E = 12700
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        '<p:txBody><a:bodyPr/><a:lstStyle/><a:p>%s</a:p></p:txBody></p:sp>'
        % (unused_ids, name, int(x * E), int(y * E), int(w * E), int(h * E), fragment))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('--slide', type=int, required=True)
    ap.add_argument('--omml', required=True, help='片段文件(根元素 m:oMathPara)')
    ap.add_argument('--name', default='Equation')
    ap.add_argument('--x', type=float, default=100)
    ap.add_argument('--y', type=float, default=200)
    ap.add_argument('--w', type=float, default=500)
    ap.add_argument('--h', type=float, default=70)
    ap.add_argument('--backup', action='store_true')
    a = ap.parse_args()

    with open(a.omml, encoding='utf-8') as f:
        fragment = wrap_a14(f.read())

    zin = zipfile.ZipFile(a.pptx)
    slide_path = 'ppt/slides/slide%d.xml' % a.slide
    xml = zin.read(slide_path).decode('utf-8')

    ids = [int(m) for m in re.findall(r'\bid="(\d+)"', xml)]
    new_id = (max(ids) + 1) if ids else 2
    sp = shape_xml(a.name, a.x, a.y, a.w, a.h, fragment, new_id)
    if '</p:spTree>' not in xml:
        sys.exit('FATAL: slide XML 里找不到 </p:spTree>')
    xml_new = xml.replace('</p:spTree>', sp + '</p:spTree>', 1)

    if a.backup:
        shutil.copy2(a.pptx, a.pptx + '.bak-omml')
    tmp = a.pptx + '.tmp-omml'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == slide_path:
                data = xml_new.encode('utf-8')
            zout.writestr(item, data)
    zin.close()
    shutil.move(tmp, a.pptx)
    print('injected %s -> slide %d of %s (shape id=%d)' % (a.omml, a.slide, a.pptx, new_id))


if __name__ == '__main__':
    main()
