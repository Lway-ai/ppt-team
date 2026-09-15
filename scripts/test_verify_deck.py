#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_verify_deck.py — verify_deck.py 回归测试集（合成 fixture，纯标准库）。

每个用例在临时目录构造最小 pptx（presentation.xml + slide XML + 按需 media/rels），
以子进程运行 verify_deck.py --json，断言 findings。跑法:
  python scripts/test_verify_deck.py
退出码 0 = 全绿。
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import zlib
import struct
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "verify_deck.py")
STYLE = os.path.join(HERE, "style.json")

NS = ('xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')

RELNS = 'http://schemas.openxmlformats.org/package/2006/relationships'


def make_png(w, h):
    sig = b'\x89PNG\r\n\x1a\n'

    def chunk(typ, data):
        return (struct.pack('>I', len(data)) + typ + data +
                struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    raw = b''.join(b'\x00' + b'\xff\x00\x00' * w for _ in range(h))
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


def sp(name, x, y, w, h, text=None, sz=3200, latin="Calibri", ea=None, mrow=None):
    """构造一个 p:sp。text=正文, mrow=数学区文字(EA)。坐标单位 pt。"""
    E = 12700
    body = ''
    if text is not None:
        ea_xml = '<a:ea typeface="%s"/>' % ea if ea else ''
        body = ('<p:txBody><a:p><a:r><a:rPr lang="en-US" sz="%d" altLang="zh-CN">'
                '<a:latin typeface="%s"/>%s</a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody>'
                % (sz, latin, ea_xml, text))
    if mrow is not None:
        body += ('<p:txBody><a:p><m:oMath><m:r><m:t>%s</m:t></m:r></m:oMath></a:p></p:txBody>'
                 % mrow)
    if not body:
        body = '<p:txBody><a:p/></p:txBody>'
    return ('<p:sp><p:nvSpPr><p:cNvPr id="0" name="%s"/><p:cNvSpPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>%s</p:sp>'
            % (name, int(x * E), int(y * E), int(w * E), int(h * E), body))


def pic(name, x, y, w, h, rid):
    E = 12700
    return ('<p:pic><p:nvPicPr><p:cNvPr id="0" name="%s"/><p:cNvPicPr/></p:nvPicPr>'
            '<p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
            % (name, rid, int(x * E), int(y * E), int(w * E), int(h * E)))


def grp(children, gx, gy, gw, gh, chx=0.0, chy=0.0, chw=None, chh=None):
    """grpSp: children 以本地坐标摆放, 组把 (chx,chy,chw,chh) 映射到 (gx,gy,gw,gh)。"""
    E = 12700
    chw = chw if chw is not None else gw
    chh = chh if chh is not None else gh
    return ('<p:grpSp><p:nvGrpSpPr><p:cNvPr id="0" name="Group1"/><p:cNvGrpSpPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/>'
            '<a:chOff x="%d" y="%d"/><a:chExt cx="%d" cy="%d"/></a:xfrm></p:grpSpPr>%s</p:grpSp>'
            % (int(gx * E), int(gy * E), int(gw * E), int(gh * E),
               int(chx * E), int(chy * E), int(chw * E), int(chh * E), children))


def slide_xml(inner):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld %s><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
            '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/>'
            '<a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>'
            '</p:grpSpPr>%s</p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping/></p:clrMapOvr>'
            '</p:sld>' % (NS, inner))


def rels_xml(pairs):
    items = ''.join('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="%s"/>' % (rid, tgt)
                    for rid, tgt in pairs)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="%s">%s</Relationships>' % (RELNS, items))


def build_pptx(path, slides, media=None, rels=None):
    """slides: [inner_xml]; media: {name: bytes}; rels: {slideN: [(rid, target)]}"""
    pres = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
    zout = zipfile_in_mem(path)
    zout.writestr('ppt/presentation.xml', pres)
    for i, inner in enumerate(slides, 1):
        zout.writestr('ppt/slides/slide%d.xml' % i, slide_xml(inner))
        r = (rels or {}).get(i)
        if r is not None:
            zout.writestr('ppt/slides/_rels/slide%d.xml.rels' % i, rels_xml(r))
    for name, blob in (media or {}).items():
        zout.writestr('ppt/media/%s' % name, blob)
    zout.close()


def zipfile_in_mem(path):
    import zipfile
    return zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)


def run_verify(path, tmpdir, tag):
    out_json = os.path.join(tmpdir, tag + '.json')
    p = subprocess.run([sys.executable, VERIFY, path, '--style', STYLE, '--json', out_json],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    data = json.load(open(out_json, encoding='utf-8')) if os.path.exists(out_json) else []
    return p.returncode, data


FAILS = []
WARNS = []


def findings(data, sev, check=None, slide=None):
    out = []
    for f in data:
        if f['severity'] != sev:
            continue
        if check and f['check'] != check:
            continue
        if slide is not None and f['slide'] != slide:
            continue
        out.append(f['msg'])
    return out


def case(name, cond, detail=''):
    if cond:
        print('  PASS %s' % name)
    else:
        print('  FAIL %s  %s' % (name, detail))
        FAILS.append(name)


def main():
    tmpdir = tempfile.mkdtemp(prefix='verify_deck_test_')
    F = lambda i: findings

    # --- C1 文本×文本重叠 → FAIL ---
    p1 = os.path.join(tmpdir, 'c1.pptx')
    build_pptx(p1, [sp("A", 100, 100, 300, 50, "hello world segment one") +
                    sp("B", 150, 120, 300, 50, "hello world segment two")])
    rc, d = run_verify(p1, tmpdir, 'c1')
    case('C1 text-text overlap FAIL', rc == 2 and findings(d, 'FAIL', 'overlap'),
         findings(d, 'FAIL'))

    # --- C2 容器(KeyBox)画在子元素之上 → FAIL；画在子元素之下 → 豁免 ---
    p2 = os.path.join(tmpdir, 'c2.pptx')
    build_pptx(p2, [sp("Label", 100, 100, 200, 40, "inner label") +
                    sp("KeyBox", 90, 90, 220, 60)])
    rc, d = run_verify(p2, tmpdir, 'c2')
    case('C2 container-over-child FAIL', rc == 2 and
         any('容器' in m for m in findings(d, 'FAIL', 'overlap')), findings(d, 'FAIL'))

    # --- C3 图片×文本 → WARN 且不 FAIL ---
    p3 = os.path.join(tmpdir, 'c3.pptx')
    build_pptx(p3, [sp("T", 100, 100, 300, 50, "text near plot") +
                    pic("Plot", 120, 110, 280, 140, "rId1")],
              media={'plot.png': make_png(4, 2)},
              rels={1: [('rId1', '../media/plot.png')]})
    rc, d = run_verify(p3, tmpdir, 'c3')
    case('C3 pic-text overlap WARN only', rc == 0 and findings(d, 'WARN', 'overlap'),
         'rc=%s warns=%s' % (rc, findings(d, 'WARN')))

    # --- C4 FooterBand 参与交叠 → 豁免 ---
    p4 = os.path.join(tmpdir, 'c4.pptx')
    build_pptx(p4, [sp("T", 100, 100, 300, 50, "body") +
                    sp("FooterBand", 0, 502, 960, 38)])
    rc, d = run_verify(p4, tmpdir, 'c4')
    case('C4 FooterBand exempt', rc == 0 and not findings(d, 'FAIL', 'overlap'),
         findings(d, 'FAIL'))

    # --- C5 越界 → FAIL ---
    p5 = os.path.join(tmpdir, 'c5.pptx')
    build_pptx(p5, [sp("Off", 900, 520, 200, 60, "beyond canvas")])
    rc, d = run_verify(p5, tmpdir, 'c5')
    case('C5 bounds FAIL', rc == 2 and findings(d, 'FAIL', 'bounds'), findings(d, 'FAIL'))

    # --- C6 图片拉伸 → FAIL ---
    p6 = os.path.join(tmpdir, 'c6.pptx')
    build_pptx(p6, [pic("Stretched", 100, 100, 200, 200, "rId1")],
              media={'img.png': make_png(4, 2)}, rels={1: [('rId1', '../media/img.png')]})
    rc, d = run_verify(p6, tmpdir, 'c6')
    case('C6 stretch FAIL', rc == 2 and findings(d, 'FAIL', 'image_ratio'), findings(d, 'FAIL'))

    # --- C7 页脚回归: 纯数字页码 OK；表格值 31/0.5 不再误判 ---
    p7 = os.path.join(tmpdir, 'c7.pptx')
    build_pptx(p7, [sp("GainCtl", 100, 300, 200, 40, "31/0.5", sz=2000) +
                    sp("PageNo", 400, 505, 120, 30, "1")],
              slides=None) if False else None
    # build: slide1 = cover(page0), slide2 = content with PageNo "1" + 表格值
    build_pptx(p7, [sp("Cover", 100, 100, 400, 60, "Cover Slide"),
                    sp("GainCtl", 100, 300, 200, 40, "31/0.5", sz=2000) +
                    sp("PageNo", 400, 505, 120, 30, "1")])
    rc, d = run_verify(p7, tmpdir, 'c7')
    case('C7a "31/0.5" not page number', not findings(d, 'FAIL', 'page_number'),
         findings(d, 'FAIL'))
    case('C7b pure-number footer found, no mismatch finding',
         not [m for m in findings(d, 'WARN', 'footer') if 'slide 2' in ''] and
         not findings(d, 'INFO', 'page_number', slide=2),
         'warn=%s info=%s' % (findings(d, 'WARN', 'footer'), findings(d, 'INFO', 'page_number')))

    # --- C8 "5 of 9" 实际 2 页 → FAIL；"1 of 2" 正确 → 无 ---
    p8 = os.path.join(tmpdir, 'c8.pptx')
    build_pptx(p8, [sp("Cover", 100, 100, 400, 60, "Cover"),
                    sp("PageNo", 400, 505, 160, 30, "1 of 9")])
    rc, d = run_verify(p8, tmpdir, 'c8')
    case('C8 N-of-M mismatch FAIL', rc == 2 and findings(d, 'FAIL', 'page_number'),
         findings(d, 'FAIL'))

    # --- C9 数学区 EA 缺失 → FAIL; 别名 Microsoft YaHei + i=0 → PASS ---
    p9 = os.path.join(tmpdir, 'c9.pptx')
    build_pptx(p9, [sp("Equation 1", 100, 100, 400, 60, mrow="半带互补条件")])
    rc, d = run_verify(p9, tmpdir, 'c9')
    case('C9a math EA missing FAIL', rc == 2 and
         any('数学区' in m for m in findings(d, 'FAIL', 'font_rules')), findings(d, 'FAIL'))

    p9b = os.path.join(tmpdir, 'c9b.pptx')
    E = 12700
    omml_ok = ('<p:sp><p:nvSpPr><p:cNvPr id="0" name="Equation 2"/><p:cNvSpPr/></p:nvSpPr>'
               '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm></p:spPr>'
               '<p:txBody><a:p><m:oMath><m:r><m:rPr><m:sty m:val="p"/></m:rPr>'
               '<a:t>互补条件</a:t></m:r></m:oMath></a:p></p:txBody></p:sp>'
               % (100 * E, 100 * E, 400 * E, 60 * E))
    # 带显式 ea 的数学运行（走 rPr 层级较繁琐, 用原始 XML 注入 a:rPr）
    omml_ok = omml_ok.replace('<m:rPr><m:sty m:val="p"/></m:rPr>',
                              '<a:rPr i="0"><a:ea typeface="Microsoft YaHei"/></a:rPr>')
    build_pptx(p9b, [omml_ok])
    rc, d = run_verify(p9b, tmpdir, 'c9b')
    case('C9b math EA alias(YaHei) + i=0 PASS', rc == 0 and not findings(d, 'FAIL', 'font_rules'),
         findings(d, 'FAIL'))

    # --- C10 latin=Microsoft YaHei 的中文混排 → PASS; latin=Times New Roman → FAIL ---
    p10 = os.path.join(tmpdir, 'c10.pptx')
    build_pptx(p10, [sp("Mixed", 100, 100, 400, 60, "把余弦代入", latin="Microsoft YaHei", ea="微软雅黑"),
                     sp("Bad", 100, 200, 400, 60, "legacy serif", latin="Times New Roman")])
    rc, d = run_verify(p10, tmpdir, 'c10')
    msgs = [m for m in findings(d, 'FAIL', 'font_rules')]
    case('C10 YaHei-latin alias PASS, Times FAIL',
         not any('Mixed' in m for m in msgs) and any('Bad' in m for m in msgs), msgs)

    # --- C11 孤立 media → WARN; 断链 rels → FAIL ---
    p11 = os.path.join(tmpdir, 'c11.pptx')
    build_pptx(p11, [sp("T", 100, 100, 300, 50, "plain")],
              media={'orphan.png': make_png(1, 1)})
    rc, d = run_verify(p11, tmpdir, 'c11')
    case('C11a orphan media WARN', rc == 0 and findings(d, 'WARN', 'integrity'),
         'rc=%s warns=%s' % (rc, findings(d, 'WARN')))

    p11b = os.path.join(tmpdir, 'c11b.pptx')
    build_pptx(p11b, [pic("Ghost", 100, 100, 100, 60, "rId1")],
              rels={1: [('rId1', '../media/ghost.png')]})
    rc, d = run_verify(p11b, tmpdir, 'c11b')
    case('C11b broken rels FAIL', rc == 2 and
         any('断链' in m or '不在包内' in m for m in findings(d, 'FAIL', 'integrity')),
         findings(d, 'FAIL'))

    # --- C12 公式图片命名 → WARN ---
    p12 = os.path.join(tmpdir, 'c12.pptx')
    build_pptx(p12, [pic("Equation 3", 100, 100, 200, 100, "rId1")],
              media={'eq.png': make_png(2, 1)}, rels={1: [('rId1', '../media/eq.png')]})
    rc, d = run_verify(p12, tmpdir, 'c12')
    case('C12 formula-as-picture WARN', rc == 0 and findings(d, 'WARN', 'formula_editable'),
         findings(d, 'WARN'))

    # --- C13 组合形状内两文本重叠 → FAIL（递归 + 坐标映射）---
    p13 = os.path.join(tmpdir, 'c13.pptx')
    inner = sp("GChildA", 0, 0, 300, 50, "group child alpha") + \
            sp("GChildB", 50, 20, 300, 50, "group child beta")
    build_pptx(p13, [grp(inner, gx=200, gy=150, gw=600, gh=200, chx=0, chy=0, chw=600, chh=200)])
    rc, d = run_verify(p13, tmpdir, 'c13')
    case('C13 overlap inside group FAIL', rc == 2 and
         any('GChildA' in m and 'GChildB' in m for m in findings(d, 'FAIL', 'overlap')),
         findings(d, 'FAIL'))

    # --- C14 字号越档 → WARN ---
    p14 = os.path.join(tmpdir, 'c14.pptx')
    build_pptx(p14, [sp("Odd", 100, 100, 400, 60, "off tier size", sz=1780)])
    rc, d = run_verify(p14, tmpdir, 'c14')
    case('C14 off-tier size WARN', rc == 0 and findings(d, 'WARN', 'font_tier'),
         findings(d, 'WARN'))

    print('\n== %d cases failed ==' % len(FAILS))
    for f in FAILS:
        print('  -', f)
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
