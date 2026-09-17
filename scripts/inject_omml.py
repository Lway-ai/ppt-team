#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inject_omml.py — 向已有 PPTX 的指定页注入原生 OMML 公式形状（raw-zip 拼接，不经 COM）。

背景（SKILL.md 第十节 2/8）: 公式必须原生 OMML/Cambria Math; COM 对数学区字体静默无效,
含东亚文字的 m:r 必须携带 <a:rPr i="0"><a:ea typeface="微软雅黑"/></a:rPr>。

两种输入（二选一）:
  --omml 片段文件   根元素 <m:oMathPara>（scripts/omml/eq_*.xml）
  --tex  "LaTeX"    mini-LaTeX 子串（omml_tex.py 引擎: 分式/上下标/根号/希腊/矩阵/多行/\\text 中文）

关键方言（实测踩坑）: 数学段落必须包 <a14:m xmlns:a14="...office/drawing/2010/main">，
裸 m:oMathPara 或命名空间写错 = 文件能打开但公式不渲染。

用法:
  python inject_omml.py deck.pptx --slide 5 --tex "F = \\frac{S_i}{S_{o}}" \
      --name "Equation 5" --x 120 --y 200 --w 500 --h 70 [--backup]
"""
import argparse
import os
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omml_tex import tex_paragraphs  # noqa: E402

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
A14 = 'http://schemas.microsoft.com/office/drawing/2010/main'


def wrap_a14(fragment):
    fragment = fragment.strip()
    if fragment.startswith('<a14:m'):
        return fragment
    inner = re.sub(r'^<m:oMathPara[^>]*>|</m:oMathPara>$', '', fragment)
    return ('<a14:m xmlns:a14="%s"><m:oMathPara xmlns:m="%s">%s</m:oMathPara></a14:m>'
            % (A14, M, inner))


def shape_xml(name, x, y, w, h, paragraphs, new_id):
    """paragraphs: 已包 a14:m 的段落 XML 列表（每段一个 <a:p>）。"""
    E = 12700
    body = ''.join('<a:p>%s</a:p>' % p for p in paragraphs)
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        '<p:txBody><a:bodyPr/><a:lstStyle/>%s</p:txBody></p:sp>'
        % (new_id, name, int(x * E), int(y * E), int(w * E), int(h * E), body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('--slide', type=int, required=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--omml', help='片段文件(根元素 m:oMathPara)')
    src.add_argument('--tex', help='mini-LaTeX 公式串')
    ap.add_argument('--name', default='Equation')
    ap.add_argument('--x', type=float, default=100)
    ap.add_argument('--y', type=float, default=200)
    ap.add_argument('--w', type=float, default=500)
    ap.add_argument('--h', type=float, default=70)
    ap.add_argument('--size', type=int, default=24, help='公式字号 pt(写入 bodyPr 每段默认字号)')
    ap.add_argument('--backup', action='store_true')
    a = ap.parse_args()

    if a.tex is not None:
        paras = [wrap_a14(p) for p in tex_paragraphs(a.tex)]
        if not paras:
            sys.exit('FATAL: --tex 未产出任何公式段落')
        src_desc = 'tex:%s' % a.tex[:40]
    else:
        with open(a.omml, encoding='utf-8') as f:
            paras = [wrap_a14(f.read())]
        src_desc = a.omml

    sz = '<a:bodyPr/>'
    zin = zipfile.ZipFile(a.pptx)
    slide_path = 'ppt/slides/slide%d.xml' % a.slide
    xml = zin.read(slide_path).decode('utf-8')

    ids = [int(m) for m in re.findall(r'\bid="(\d+)"', xml)]
    new_id = (max(ids) + 1) if ids else 2
    # 公式字号: 在所有 a:rPr 上补 sz（omml_tex 产出的 run 均带 i="0/1" 特征）
    sz_hundred = int(a.size * 100)
    paras = [re.sub(r'(<a:rPr lang="en-US" i="[01]")>', r'\1 sz="%d">' % sz_hundred, p)
             for p in paras]
    sp = shape_xml(a.name, a.x, a.y, a.w, a.h, paras, new_id)
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
    print('injected %s -> slide %d of %s (shape id=%d, %d paragraph(s))'
          % (src_desc, a.slide, a.pptx, new_id, len(paras)))


if __name__ == '__main__':
    main()
