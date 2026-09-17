#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_deck.py — PPT 确定性检查器（多代理 PPT 系统的 'Lean' 层）。

纯标准库（zipfile + ElementTree + struct），不依赖 python-pptx，绝不写回 pptx。
检查项：形状越界 / 图片拉伸 / 字号越档 / 越版色 / 文本溢出(启发式) / 禁用文本 / 页码一致性
        / 形状相交(白名单豁免, 递归进组合形状) / 页脚色带越界 / 字体规则(中西文白名单 + 别名归一
        + 数学区 EA 文字显式声明) / 包完整性(断链 rels=FAIL, 孤立 media=WARN)
        / 公式可编辑性(OMML 数学区统计=INFO, 公式图片=WARN)。
相交规则：文本×文本 或 容器盖住子元素(容器 z 在上层) = FAIL；图片参与的交叠 = WARN
        （图片常含留白，需目检）；装饰/背景件（FooterBand/TitleHairline/RowPanel/HLbar 等）豁免。
        组合形状(grpSp)会按 chOff/chExt 映射到绝对坐标后一并参与检测。
形状命名契约（builder 必须遵守，详见 SKILL.md 第十一节）：
  FooterBand/PageNo/RowPanel*/KeyBox* 等名字参与豁免与容器判定——新建形状必须按契约命名。
页码规则：页码候选 = 形状名匹配 footer_whitelist_regex 或 底边伸入页脚色带(y+h > band_top-6)。
  "N of M" 总数错 = FAIL；纯数字页码与"封面计 0"约定不符 = INFO。
用法:
  python verify_deck.py deck.pptx --style style.json [--slides 1-13] [--json report.json] [--no-style]
退出码: 0 = 无 FAIL; 2 = 存在 FAIL; 1 = 用法/IO 错误。
"""
import argparse
import json
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'


def q(ns, tag):
    return '{%s}%s' % (ns, tag)


def is_ea_char(c):
    """东亚码点：带圈数字/汉字/日文/全角形式（据 SKILL.md 第三节字体规则）。"""
    o = ord(c)
    return (0x2460 <= o <= 0x24FF or 0x2E80 <= o <= 0x9FFF or
            0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF)


EMU = 12700.0

# --- 字体族名别名：同一字体的中英文族名归一化（COM 常写英文名，法典用中文名） ---
FONT_ALIASES = {
    'microsoft yahei': '微软雅黑',
    'msyh': '微软雅黑',
    'simhei': '黑体',
    'simsun': '宋体',
    'franklin gothic book': 'Franklin Gothic Book',
    'calibri': 'Calibri',
    'arial': 'Arial',
    'arial mt': 'ArialMT',
    'arialnarrow': 'Arial Narrow',
    'arial narrow': 'Arial Narrow',
}


def norm_font(name):
    if not name:
        return name
    key = name.strip().lower()
    return FONT_ALIASES.get(key, name.strip())


def is_ea_family(name):
    return norm_font(name) in ('微软雅黑', '黑体', '宋体', '仿宋', '楷体')


# --- overlap detection defaults (overridable via style.json "overlap") ---
DEFAULT_BG_RE = r'^(FooterBand|TitleHairline|FooterRule|CoverRule|CoverRuleHL|CoverFootRule|RowPanel[0-9]*|HLbar|CoverBG)$'
DEFAULT_CONTAINERS = ('KeyBox', 'KeyBox2', 'CoverKey', 'Capsule', 'NoteBox', 'TakeawayStrip', 'Takeaway4')
DEFAULT_FOOTER_OK_RE = r'^(Footer|PageNo|SessionId|CoverFoot|CoverPage|CoverC|FooterRule|FooterBand)'
DEFAULT_FOOTER_TEXT_RE = r'^(?:page\s*)?[0-9]+(?:\s*(?:of|/)\s*[0-9]+)?$'
FORMULA_PIC_RE = re.compile(r'(equation|formula|^eq[ _\-0-9])', re.I)


def png_size(d):
    if len(d) > 24 and d[:8] == b'\x89PNG\r\n\x1a\n':
        w, h = struct.unpack('>II', d[16:24])
        return w, h
    return None


def jpg_size(d):
    if len(d) < 4 or d[:2] != b'\xff\xd8':
        return None
    i, n = 2, len(d)
    while i < n - 9:
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if m == 0xD9:
            break
        ln = struct.unpack('>H', d[i + 2:i + 4])[0]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack('>HH', d[i + 5:i + 9])
            return w, h
        i += 2 + ln
    return None


def est_overflow(shape, box_w_emu, latchar, line_h):
    """启发式：按 em 宽度估行数，估算文本总高与形状高度比较。仅 WARN 级。"""
    tx = shape.find(q(P, 'txBody'))
    if tx is None or box_w_emu <= 0:
        return None
    paras = tx.findall(q(A, 'p'))
    if not paras:
        return None
    spPr = shape.find(q(P, 'spPr'))
    ext = spPr.find(q(A, 'xfrm') + '/' + q(A, 'ext')) if spPr is not None else None
    if ext is None:
        return None
    hpt = int(ext.get('cy')) / EMU
    total = 0.0
    has_text = False
    for pa in paras:
        txt = ''.join((t.text or '') for t in pa.iter(q(A, 't')))
        if not txt.strip():
            total += 6.0
            continue
        has_text = True
        szs = [int(el.get('sz')) / 100.0 for el in pa.iter()
               if el.tag in (q(A, 'rPr'), q(A, 'defRPr')) and el.get('sz')]
        sz = max(szs) if szs else 18.0
        wpt = sum((1.0 if ord(c) > 0x2E80 else latchar) * sz for c in txt)
        avail = max(box_w_emu / EMU - 16.0, 20.0)
        lines = max(1, int(wpt / avail + 0.999))
        total += lines * sz * line_h
    if not has_text:
        return None
    if total > hpt * 1.02 + 2:
        return 'est %.0fpt > box %.0fpt' % (total, hpt)
    return None


def slide_numbers(z):
    out = []
    for name in z.namelist():
        m = re.match(r'ppt/slides/slide(\d+)\.xml$', name)
        if m:
            out.append((int(m.group(1)), name))
    return sorted(out)


def parse_slides_arg(s):
    sel = set()
    for part in s.split(','):
        if '-' in part:
            lo, hi = part.split('-')
            sel.update(range(int(lo), int(hi) + 1))
        else:
            sel.add(int(part))
    return sel


def shape_xfrm(el):
    """返回 (off, ext) Element 或 (None, None)。sp/pic 取 spPr/xfrm，graphicFrame 取顶层 xfrm。"""
    tag = el.tag
    if tag in (q(P, 'sp'), q(P, 'pic')):
        spPr = el.find(q(P, 'spPr'))
        xf = spPr.find(q(A, 'xfrm')) if spPr is not None else None
    elif tag == q(P, 'graphicFrame'):
        xf = el.find(q(P, 'xfrm'))
    else:
        xf = None
    if xf is None:
        return None, None
    return xf.find(q(A, 'off')), xf.find(q(A, 'ext'))


def collect_shapes(tree_el, base_x=0.0, base_y=0.0, sx=1.0, sy=1.0, out=None, counter=None):
    """递归收集 sp/pic/graphicFrame 的绝对坐标矩形（pt）。
    组合形状 grpSp：子坐标经 chOff/chExt 映射回绝对坐标后继续下钻。
    返回 [{name, tag, x, y, w, h, z, pic, cont}]，z 为文档顺序（用于上下层判定）。"""
    if out is None:
        out = []
    if counter is None:
        counter = [0]
    for el in list(tree_el):
        tag = el.tag
        if tag == q(P, 'grpSp'):
            off, ext = shape_xfrm(el)
            xfrm = el.find(q(P, 'grpSpPr') + '/' + q(A, 'xfrm')) if off is not None else None
            _collect_group(el, off, ext, xfrm, base_x, base_y, sx, sy, out, counter)
            continue
        if tag not in (q(P, 'sp'), q(P, 'pic'), q(P, 'graphicFrame')):
            continue
        nm_el = el.find('.//' + q(P, 'cNvPr'))
        nm = nm_el.get('name') if nm_el is not None else '?'
        off, ext = shape_xfrm(el)
        if off is None or ext is None:
            continue
        lx, ly = int(off.get('x')) / EMU, int(off.get('y')) / EMU
        lw, lh = int(ext.get('cx')) / EMU, int(ext.get('cy')) / EMU
        counter[0] += 1
        out.append({'name': nm, 'tag': tag,
                    'x': base_x + lx * sx, 'y': base_y + ly * sy,
                    'w': lw * sx, 'h': lh * sy,
                    'z': counter[0], 'pic': tag == q(P, 'pic'),
                    'cont': nm in CONTAINERS_SET})
    return out


def _collect_group(el, off, ext, xfrm, base_x, base_y, sx, sy, out, counter):
    """grpSp 下钻：子绝对 = 组原点(绝对) + (子本地 - chOff) * (ext/chExt) * 外层scale。"""
    if off is None or ext is None or xfrm is None:
        collect_shapes(el, base_x, base_y, sx, sy, out, counter)
        return
    x = int(off.get('x')) / EMU
    y = int(off.get('y')) / EMU
    w = int(ext.get('cx')) / EMU
    h = int(ext.get('cy')) / EMU
    ch_off = xfrm.find(q(A, 'chOff'))
    ch_ext = xfrm.find(q(A, 'chExt'))
    if ch_off is not None and ch_ext is not None and int(ch_ext.get('cx')) and int(ch_ext.get('cy')):
        gx, gy = int(ch_off.get('x')) / EMU, int(ch_off.get('y')) / EMU
        gsx = (w / (int(ch_ext.get('cx')) / EMU)) * sx
        gsy = (h / (int(ch_ext.get('cy')) / EMU)) * sy
        nbx = base_x + x * sx - gx * gsx
        nby = base_y + y * sy - gy * gsy
        collect_shapes(el, nbx, nby, gsx, gsy, out, counter)
    else:
        collect_shapes(el, base_x + x * sx, base_y + y * sy, sx, sy, out, counter)


CONTAINERS_SET = set()


def main():
    global CONTAINERS_SET
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('--style', default=None)
    ap.add_argument('--slides', default=None, help='例如 1-13 或 3,7')
    ap.add_argument('--json', dest='json_out', default=None)
    ap.add_argument('--no-style', action='store_true', help='跳过字号档位/色板检查')
    a = ap.parse_args()

    style = {}
    if a.style and not a.no_style:
        with open(a.style, encoding='utf-8') as f:
            style = json.load(f)
    tiers = [round(t, 1) for t in style.get('font_size_tiers_pt', [])]
    palette = style.get('palette', {})
    margins = style.get('margins_pt', {})
    footer_re = re.compile(style.get('footer_regex', DEFAULT_FOOTER_TEXT_RE), re.I)
    banned = [re.compile(p) for p in style.get('banned_text_patterns', [])]
    latchar = float(style.get('overflow_latchar_em', 0.55))
    line_h = float(style.get('overflow_line_height', 1.35))
    rtol = float(style.get('ratio_tolerance', 0.05))
    ol_cfg = style.get('overlap', {})
    min_ov = float(ol_cfg.get('min_overlap_pt', 5))
    min_area = float(ol_cfg.get('min_area_pt2', 100))
    bg_re = re.compile(ol_cfg.get('background_regex', DEFAULT_BG_RE))
    CONTAINERS_SET = set(ol_cfg.get('container_names', DEFAULT_CONTAINERS))
    band_top = float(ol_cfg.get('footer_band_top_pt', 502))
    footer_ok_re = re.compile(ol_cfg.get('footer_whitelist_regex', DEFAULT_FOOTER_OK_RE))
    fr_cfg = style.get('font_rules', {})
    aliases = dict(FONT_ALIASES)
    aliases.update({k.strip().lower(): v for k, v in fr_cfg.get('font_aliases', {}).items()})
    ea_allowed = set(fr_cfg.get('allowed_ea', ['微软雅黑'])) | {aliases.get(x, x) for x in fr_cfg.get('allowed_ea', ['微软雅黑'])}
    latin_allowed = set(fr_cfg.get('allowed_latin_plain',
                        ['Arial', 'ArialMT', 'Arial-BoldMT', 'Arial-BoldItalicMT',
                         'Franklin Gothic Book', 'FranklinGothic', 'Calibri']))
    latin_allowed = {norm_font(x) for x in latin_allowed}
    ea_allowed = {norm_font(x) for x in ea_allowed}
    math_ea_required = norm_font(fr_cfg.get('math_ea_required', '微软雅黑'))
    missing_font_sev = fr_cfg.get('missing_font_severity', 'INFO')

    sel = parse_slides_arg(a.slides) if a.slides else None

    z = zipfile.ZipFile(a.pptx)
    proot = ET.fromstring(z.read('ppt/presentation.xml'))
    szel = proot.find(q(P, 'sldSz'))
    SW = int(szel.get('cx')) if szel is not None else 12192000
    SH = int(szel.get('cy')) if szel is not None else 6858000
    all_slides = slide_numbers(z)

    findings = []
    plain_latin_seen = set()

    def add(sl, check, sev, msg):
        findings.append((sl, check, sev, msg))

    # ---- 包完整性：rels 目标存在性 + 孤立 media ----
    names = set(z.namelist())
    referenced = set()
    for name in names:
        if not name.endswith('.rels'):
            continue
        try:
            rroot = ET.fromstring(z.read(name))
        except ParseError:
            continue
        base = '' if name == '_rels/.rels' else name.rsplit('/_rels/', 1)[0]
        for rel in rroot:
            tgt = rel.get('Target') or ''
            if rel.get('TargetMode') == 'External':
                continue
            if tgt.startswith('../'):
                part = tgt.replace('../', 'ppt/')
            elif tgt.startswith('/'):
                part = tgt.lstrip('/')
            elif base:
                part = base + '/' + tgt
            else:
                part = tgt          # 包根 _rels/.rels:target 即包内路径
            while '/./' in part:
                part = part.replace('/./', '/')
            referenced.add(part)
            if part not in names:
                add(0, 'integrity', 'FAIL', '断链引用: %s -> %s 不在包内' % (name, tgt))
    orphans = sorted(n for n in names if n.startswith('ppt/media/') and n not in referenced)
    for n in orphans:
        add(0, 'integrity', 'WARN', '孤立媒体(未被任何 rels 引用): %s' % n)

    for idx, path in all_slides:
        if sel and idx not in sel:
            continue
        rels = {}
        try:
            rroot = ET.fromstring(z.read('ppt/slides/_rels/slide%d.xml.rels' % idx))
            for rel in rroot:
                rels[rel.get('Id')] = rel.get('Target').replace('../', 'ppt/')
        except (KeyError, ParseError):
            pass
        try:
            root = ET.fromstring(z.read(path))
        except ParseError as e:
            add(idx, 'parse', 'FAIL', 'slide XML 解析失败: %s' % e)
            continue
        tree = root.find(q(P, 'cSld') + '/' + q(P, 'spTree'))
        if tree is None:
            continue

        footer_cands = []   # (name, text, y_bottom_pt)
        math_zones = 0
        for sh in tree.iter():
            tag = sh.tag
            if tag == q(M, 'oMath'):
                math_zones += 1
            if tag not in (q(P, 'sp'), q(P, 'pic'), q(P, 'graphicFrame')):
                continue
            name_el = sh.find('.//' + q(P, 'cNvPr'))
            name = name_el.get('name') if name_el is not None else '?'

            xf = None
            if tag in (q(P, 'sp'), q(P, 'pic')):
                spPr = sh.find(q(P, 'spPr'))
                xf = spPr.find(q(A, 'xfrm')) if spPr is not None else None
            elif tag == q(P, 'graphicFrame'):
                xf = sh.find(q(P, 'xfrm'))

            box_w_emu = 0
            yb_pt = -1.0
            if xf is not None:
                off, ext = xf.find(q(A, 'off')), xf.find(q(A, 'ext'))
                if off is not None and ext is not None:
                    x, y = int(off.get('x')), int(off.get('y'))
                    w, h = int(ext.get('cx')), int(ext.get('cy'))
                    box_w_emu = w
                    yb_pt = (y + h) / EMU
                    if x < -1000 or y < -1000 or x + w > SW + 1000 or y + h > SH + 1000:
                        add(idx, 'bounds', 'FAIL',
                            '形状[%s]越界: pos(%d,%d) size(%d,%d) EMU, 画布(%d,%d)' % (name, x, y, w, h, SW, SH))
                    if margins and w < SW * 0.9:
                        mx = x / EMU
                        if mx < margins.get('left', 0) - 2:
                            add(idx, 'margins', 'INFO',
                                '形状[%s] 左边缘 %.0fpt 小于版心 %.0fpt' % (name, mx, margins['left']))

            if tag == q(P, 'pic'):
                if FORMULA_PIC_RE.search(name or ''):
                    add(idx, 'formula_editable', 'WARN',
                        '图片[%s] 命名疑似公式 — 若为公式截图则不可编辑，应为 OMML 数学区' % name)
                blip = sh.find('.//' + q(A, 'blip'))
                ext = xf.find(q(A, 'ext')) if xf is not None else None
                if blip is not None and ext is not None:
                    rid = blip.get(q(R, 'embed'))
                    dims = None
                    if rid not in rels:
                        add(idx, 'integrity', 'FAIL',
                            '图片[%s] r:embed=%s 无对应 rels 条目，渲染必断' % (name, rid))
                    else:
                        try:
                            blob = z.read(rels[rid])
                        except KeyError:
                            add(idx, 'integrity', 'FAIL',
                                '图片[%s] 引用 %s 不在包内' % (name, rels[rid]))
                            blob = b''
                        dims = png_size(blob) or jpg_size(blob)
                    if dims and dims[0] > 0 and int(ext.get('cy')) > 0:
                        nat = dims[0] / dims[1]
                        placed = int(ext.get('cx')) / int(ext.get('cy'))
                        if abs(nat - placed) / nat > rtol:
                            add(idx, 'image_ratio', 'FAIL',
                                '图片[%s]拉伸: 原始比 %.3f vs 摆放比 %.3f' % (name, nat, placed))

            for t in sh.iter(q(A, 't')):
                if not t.text:
                    continue
                for b in banned:
                    if b.search(t.text):
                        add(idx, 'banned_text', 'FAIL',
                            '文本含禁用模式 %r: "%s"' % (b.pattern, t.text[:40]))
                if footer_re.search(t.text.strip()):
                    footer_cands.append((name, t.text, yb_pt))

            # 字号档位 / 色板（逐形状去重）
            sz_seen, clr_seen = set(), set()
            for el in sh.iter():
                if el.tag in (q(A, 'rPr'), q(A, 'defRPr'), q(A, 'endParaRPr')) and el.get('sz'):
                    pt = round(int(el.get('sz')) / 100.0, 1)
                    if pt not in sz_seen:
                        sz_seen.add(pt)
                        if tiers and pt not in tiers:
                            add(idx, 'font_tier', 'WARN',
                                '形状[%s] 字号 %.1fpt 不在档位表' % (name, pt))
                if el.tag == q(A, 'srgbClr'):
                    v = (el.get('val') or '').upper()
                    if v and palette and v not in palette and v not in clr_seen:
                        clr_seen.add(v)
                        add(idx, 'palette', 'WARN', '形状[%s] 色值 #%s 不在色板' % (name, v))

            # ---- 中西文字体规则（SKILL.md 第三节）----
            # 数学区 m:r：含东亚文字时必须显式声明 ea 字体且非斜体，否则数学引擎
            # 强制 Cambria Math 并回退衬线，造成同页字体不一致
            for mr in sh.iter(q(M, 'r')):
                mtxt = ''.join((t.text or '') for t in mr.findall(q(M, 't')))
                if not mtxt or not any(is_ea_char(c) for c in mtxt):
                    continue
                rpr = mr.find(q(A, 'rPr'))
                ea_el = rpr.find(q(A, 'ea')) if rpr is not None else None
                ea_tf = norm_font(ea_el.get('typeface') if ea_el is not None else None)
                if ea_tf != math_ea_required:
                    add(idx, 'font_rules', 'FAIL',
                        '形状[%s] 数学区东亚文字 %r ea=%r≠%r，回退衬线与全片不一致'
                        % (name, mtxt[:12], ea_tf, math_ea_required))
                elif rpr is not None and rpr.get('i') == '1':
                    add(idx, 'font_rules', 'FAIL',
                        '形状[%s] 数学区东亚文字 %r 为斜体(i="1")，EA 文字须正体'
                        % (name, mtxt[:12]))
            # 正文 a:r：latin/ea 白名单（族名先别名归一化）
            for r_el in sh.iter(q(A, 'r')):
                txt = ''.join((t.text or '') for t in r_el.findall(q(A, 't')))
                if not txt.strip():
                    continue
                rpr = r_el.find(q(A, 'rPr'))
                if rpr is None:
                    continue
                lat = rpr.find(q(A, 'latin'))
                ea = rpr.find(q(A, 'ea'))
                lat_tf = norm_font((lat.get('typeface') or '') if lat is not None else '')
                ea_tf = norm_font((ea.get('typeface') or '') if ea is not None else '')
                # latin 槽位允许：西文白名单 或 EA 白名单（混排运行常整段用中文字体）
                if lat_tf and lat_tf not in latin_allowed and lat_tf not in ea_allowed:
                    add(idx, 'font_rules', 'FAIL',
                        '形状[%s] 正文西文 %r 用了 %r，不在白名单 %s'
                        % (name, txt[:16], lat_tf, sorted(latin_allowed)))
                if lat_tf and lat_tf not in ea_allowed:
                    plain_latin_seen.add(lat_tf)
                if ea_tf and ea_tf not in ea_allowed:
                    add(idx, 'font_rules', 'FAIL',
                        '形状[%s] 正文东亚文字 %r 用了 %r，不在白名单 %s'
                        % (name, txt[:16], ea_tf, sorted(ea_allowed)))
                if not lat_tf and not ea_tf and missing_font_sev != 'NONE':
                    add(idx, 'font_rules', missing_font_sev,
                        '形状[%s] 文本 %r 未声明字体，将继承主题默认'
                        % (name, txt[:16]))

            if tag == q(P, 'sp') and xf is not None and box_w_emu > 0:
                ov = est_overflow(sh, box_w_emu, latchar, line_h)
                if ov:
                    add(idx, 'overflow', 'WARN', '形状[%s]疑似文本溢出: %s' % (name, ov))

        if math_zones:
            add(idx, 'formula_editable', 'INFO', '检测到 %d 个 OMML 数学区(可编辑公式)' % math_zones)

        # ---- 形状相交检测（递归含组合形状，白名单豁免）----
        recs = [r for r in collect_shapes(tree)
                if not bg_re.match(r['name'])]
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                Ra, Rb = recs[i], recs[j]
                ox = min(Ra['x'] + Ra['w'], Rb['x'] + Rb['w']) - max(Ra['x'], Rb['x'])
                oy = min(Ra['y'] + Ra['h'], Rb['y'] + Rb['h']) - max(Ra['y'], Rb['y'])
                if ox < min_ov or oy < min_ov or ox * oy < min_area:
                    continue
                a_in_b = (Rb['x'] <= Ra['x'] + 1 and Rb['y'] <= Ra['y'] + 1 and
                          Rb['x'] + Rb['w'] >= Ra['x'] + Ra['w'] - 1 and
                          Rb['y'] + Rb['h'] >= Ra['y'] + Ra['h'] - 1)
                b_in_a = (Ra['x'] <= Rb['x'] + 1 and Ra['y'] <= Rb['y'] + 1 and
                          Ra['x'] + Ra['w'] >= Rb['x'] + Rb['w'] - 1 and
                          Ra['y'] + Ra['h'] >= Rb['y'] + Rb['h'] - 1)
                if a_in_b or b_in_a:
                    outer, inner = (Rb, Ra) if a_in_b else (Ra, Rb)
                    if outer['cont'] and outer['z'] > inner['z']:
                        add(idx, 'overlap', 'FAIL',
                            '容器[%s]盖住[%s] (交叠 %.0fx%.0fpt, 容器画在上层)' % (
                                outer['name'], inner['name'], ox, oy))
                    continue
                if Ra['pic'] or Rb['pic']:
                    if ox >= 10 and oy >= 10:
                        add(idx, 'overlap', 'WARN',
                            '图片与形状区域交叠[%s]x[%s] %.0fx%.0fpt(图片含留白, 目检裁决)' % (
                                Ra['name'], Rb['name'], ox, oy))
                    continue
                add(idx, 'overlap', 'FAIL',
                    '形状重叠[%s]x[%s] 交叠 %.0fx%.0fpt' % (Ra['name'], Rb['name'], ox, oy))
        # ---- 页脚色带越界 ----
        for rr in recs:
            if footer_ok_re.match(rr['name']):
                continue
            if rr['y'] + rr['h'] > band_top + 2:
                add(idx, 'footer_zone', 'WARN',
                    '形状[%s]底边 %.0fpt 越过页脚色带上沿 %.0fpt' % (
                        rr['name'], rr['y'] + rr['h'], band_top))

        # ---- 页码一致性：只在"页脚候选"上判定（名字命中 or 底边伸入色带）----
        pageish = [(nm, ft) for nm, ft, yb in footer_cands
                   if footer_ok_re.match(nm) or yb > band_top - 6]
        if not pageish:
            add(idx, 'footer', 'WARN', '未找到页脚候选（页码形状需按命名契约命名或位于色带内）')
        seen_pn = set()
        for nm, ft in pageish:
            key = (nm, ft)
            if key in seen_pn:
                continue
            seen_pn.add(key)
            m = re.match(r'\s*(\d+)\s*(?:of|/)\s*(\d+)\s*$', ft)
            if m:
                nn, mm = int(m.group(1)), int(m.group(2))
                if mm != len(all_slides):
                    add(idx, 'page_number', 'FAIL',
                        '页码总页数错误: "%s" 但实际 %d 页' % (ft.strip(), len(all_slides)))
                continue
            m2 = re.match(r'\s*(\d+)\s*$', ft)
            if m2 and int(m2.group(1)) != idx - 1:
                add(idx, 'page_number', 'INFO',
                    '纯数字页码 "%s" 与"封面计 0"约定(本页应为 %d)不符 — 如为序号页请人工确认'
                    % (ft.strip(), idx - 1))

    if len(plain_latin_seen) > 1:
        add(0, 'font_rules', 'WARN',
            '全片正文西文字体多于一种: %s — 违反"全片正文西文只能一种"(SKILL.md 第三节)'
            % sorted(plain_latin_seen))

    fails = [f for f in findings if f[2] == 'FAIL']
    warns = [f for f in findings if f[2] == 'WARN']
    infos = [f for f in findings if f[2] == 'INFO']
    for sl, check, sev, msg in findings:
        print('[%s] slide %2d %-16s %s' % (sev, sl, check, msg))
    print('\n== 汇总: %d FAIL, %d WARN, %d INFO, 共 %d 页 ==' % (
        len(fails), len(warns), len(infos), len(all_slides)))
    if a.json_out:
        with open(a.json_out, 'w', encoding='utf-8') as f:
            json.dump([{'slide': s, 'check': c, 'severity': v, 'msg': m}
                       for s, c, v, m in findings], f, ensure_ascii=False, indent=1)
    sys.exit(2 if fails else 0)


if __name__ == '__main__':
    main()
