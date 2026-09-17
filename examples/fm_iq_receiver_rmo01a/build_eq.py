#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_eq.py — round 0 OMML injection for FM_IQ_Receiver_RFIC2024.pptx.

Reuses scripts/omml_tex.tex_paragraphs (mini-LaTeX -> OMML), then:
  * injects sz on every run (display size 24/26pt, tier-safe);
  * applies per-run term coloring rules (palette names only);
  * wraps paragraphs in a14:m (mandatory namespace, SKILL.md §十一);
  * fixes slide16 table to "No Style, No Grid" (COM banding off) -> three-line look.
Raw-zip splice only; never touches COM. Backup written as *.bak-r0-com first.
"""
import os
import re
import shutil
import sys
import zipfile

ROOT = r'D:\wanglei\project\TDA7707_GNSS\E_project\multi_agent_PPT_zcode'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from omml_tex import tex_paragraphs  # noqa: E402

M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
A14 = 'http://schemas.microsoft.com/office/drawing/2010/main'
EMU = 12700.0
NO_STYLE_GUIDE = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'

DECK = os.path.join(ROOT, r'examples\fm_iq_receiver_rmo01a\FM_IQ_Receiver_RFIC2024.pptx')

EQS = [
    dict(slide=3, name='Equation3a', x=80, y=118, w=400, h=52, size=24,
         tex=r's(t)=A\cos(\omega_c t+\beta\sin\omega_m t)',
         rules=[('c', '0070C0')]),
    dict(slide=3, name='Equation3b', x=480, y=118, w=400, h=52, size=24,
         tex=r's_i(t) = \gamma A\cos(\omega_i t+\beta\sin\omega_m t)',
         rules=[('γ', 'FF0000'), ('i', 'FF0000')]),
    dict(slide=3, name='Equation3c', x=280, y=434, w=400, h=48, size=24,
         tex=r'−20\lg\gamma = −20\lg 0.25 = 12.04\ \mathrm{dB}',
         rules=[('γ', 'FF0000'), ('12.04', 'FF0000')]),
    dict(slide=4, name='Equation4a', x=140, y=160, w=680, h=58, size=24,
         tex=r'①\ \ s(t)=A\cos(\omega_c t + 2πΔf∫ m(τ)dτ)',
         rules=[('c', '0070C0'), ('2πΔf∫', 'FF0000')]),
    dict(slide=4, name='Equation4b', x=140, y=240, w=680, h=58, size=24,
         tex=r'②\ \ m(t)=\sin(2\pi f_m t)\,,\quad\beta = \Delta f / f_m = 4',
         rules=[('β', 'FF0000'), ('4', 'FF0000')]),
    dict(slide=4, name='Equation4c', x=140, y=311, w=680, h=58, size=24,
         tex=r'B=2(\Delta f+f_m)=2\times(200+50)=500\ \mathrm{Hz}\ \text{（Carson 带宽）}',
         rules=[('500', 'FF0000')]),
    dict(slide=7, name='Equation7a', x=40, y=174, w=440, h=54, size=26,
         tex=r'z_1=\mathrm{LPF}[\,r\cdot 2e^{−j\omega_1 t}\,]',
         rules=[('2', 'FF0000'), ('e', 'FF0000'), ('−j', 'FF0000')]),
    dict(slide=7, name='Equation7b', x=40, y=236, w=440, h=48, size=24,
         tex=r'1000\ \mathrm{Hz}\to+400\,,\ \ 200\ \mathrm{Hz}\to−400',
         rules=[('1000', 'FF0000'), ('+400', 'FF0000'), ('200', '0070C0'), ('−400', '0070C0')]),
    dict(slide=9, name='Equation9a', x=72, y=220, w=416, h=48, size=26,
         tex=r'z_2 = z_1 e^{−j\psi}\,,\quad\psi = \omega_{IF} t',
         rules=[('e', '00B050'), ('−j', '00B050')]),
    dict(slide=9, name='Equation9b', x=72, y=272, w=416, h=84, size=24,
         tex=r'I_2 = I_1\cos\psi + Q_1\sin\psi \\ Q_2 = −I_1\sin\psi + Q_1\cos\psi',
         rules=[]),
    dict(slide=11, name='Equation11a', x=40, y=208, w=440, h=88, size=26,
         tex=r'H(s)=\frac{\omega_0^4}{(s^2+\sqrt{2}\,\omega_0 s+\omega_0^2)^2}',
         rules=[('ω', 'DF6C0E')]),
    dict(slide=13, name='Equation13a', x=40, y=176, w=440, h=96, size=26,
         tex=r'ω̂=\frac{I\cdot ΔQ − Q\cdot ΔI}{I^2 + Q^2 + \varepsilon}',
         rules=[('ω̂', '7030A0'), ('ε', '7030A0')]),
    dict(slide=13, name='Equation13b', x=40, y=288, w=440, h=96, size=24,
         tex=r'\varepsilon = 1\times 10^{−6} \\ G = 1/(2\pi\Delta f) = 7.958\times 10^{−4}',
         rules=[('7.958', '7030A0')]),
]

RUN_RE = re.compile(r'<m:r><a:rPr lang="en-US" i="([01])">(.*?)</a:rPr><m:t>(.*?)</m:t></m:r>', re.S)


def wrap_a14(fragment):
    fragment = fragment.strip()
    if fragment.startswith('<a14:m'):
        return fragment
    inner = re.sub(r'^<m:oMathPara[^>]*>|</m:oMathPara>$', '', fragment)
    return ('<a14:m xmlns:a14="%s"><m:oMathPara xmlns:m="%s">%s</m:oMathPara></a14:m>'
            % (A14, M, inner))


def is_ea(t):
    """Mirror verify_deck.is_ea_char: circled digits + CJK ranges count as EA."""
    return any(0x2460 <= ord(c) <= 0x24FF or 0x2E80 <= ord(c) <= 0x9FFF or
               0xF900 <= ord(c) <= 0xFAFF or 0xFF00 <= ord(c) <= 0xFFEF for c in t)


def decorate(par, size_pt, rules):
    def repl(m):
        i, inner, t = m.group(1), m.group(2), m.group(3)
        fill = ''
        for key, col in rules:
            if t == key or (len(key) > 1 and key in t):
                fill = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % col
                break
        if is_ea(t):
            # math zone EA text must declare ea=微软雅黑 and stay upright (font_rules FAIL otherwise;
            # omml_tex only covers ord>0x2E80, misses circled digits U+2460-24FF)
            if '<a:ea' not in inner:
                inner = inner + '<a:ea typeface="微软雅黑"/>'
            i = '0'
        return '<m:r><a:rPr lang="en-US" i="%s">%s%s</a:rPr><m:t>%s</m:t></m:r>' % (i, fill, inner, t)

    par = RUN_RE.sub(repl, par)
    sz100 = int(size_pt * 100)
    par = re.sub(r'(<a:rPr lang="en-US" i="[01]")>', r'\1 sz="%d">' % sz100, par)
    return par


def shape_xml(name, x, y, w, h, paragraphs, new_id):
    E = 12700
    body = ''.join('<a:p>%s</a:p>' % p for p in paragraphs)
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        '<p:txBody><a:bodyPr/><a:lstStyle/>%s</p:txBody></p:sp>'
        % (new_id, name, int(x * E), int(y * E), int(w * E), int(h * E), body))


def fix_table_style(xml):
    xml = xml.replace('firstRow="1"', 'firstRow="0"').replace('bandRow="1"', 'bandRow="0"')
    xml = re.sub(r'<a:tableStyleId>[^<]*</a:tableStyleId>',
                 '<a:tableStyleId>%s</a:tableStyleId>' % NO_STYLE_GUIDE, xml)
    return xml


def main():
    if not os.path.exists(DECK):
        sys.exit('FATAL: deck not found: ' + DECK)
    bak = DECK + '.bak-r0-com'
    if not os.path.exists(bak):
        shutil.copy2(DECK, bak)
        print('backup -> ' + bak)

    zin = zipfile.ZipFile(DECK)
    data = {item.filename: zin.read(item.filename) for item in zin.infolist()}
    infos = [(item.filename, item) for item in zin.infolist()]
    zin.close()

    patched = {}
    for eq in EQS:
        spath = 'ppt/slides/slide%d.xml' % eq['slide']
        xml = patched.get(spath) or data[spath].decode('utf-8')
        paras = tex_paragraphs(eq['tex'])
        if not paras:
            sys.exit('FATAL: tex produced nothing for ' + eq['name'])
        paras = [wrap_a14(decorate(p, eq['size'], eq['rules'])) for p in paras]
        ids = [int(v) for v in re.findall(r'\bid="(\d+)"', xml)]
        new_id = (max(ids) + 1) if ids else 2
        sp = shape_xml(eq['name'], eq['x'], eq['y'], eq['w'], eq['h'], paras, new_id)
        if '</p:spTree>' not in xml:
            sys.exit('FATAL: no spTree in ' + spath)
        xml = xml.replace('</p:spTree>', sp + '</p:spTree>', 1)
        patched[spath] = xml
        print('injected %s -> slide %d (id=%d, %d para)' % (eq['name'], eq['slide'], new_id, len(paras)))

    s16 = 'ppt/slides/slide16.xml'
    xml16 = patched.get(s16) or data[s16].decode('utf-8')
    xml16 = fix_table_style(xml16)
    patched[s16] = xml16
    print('table style -> No Style No Grid (slide16)')

    tmp = DECK + '.tmp-eq'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, info in infos:
            zout.writestr(info, patched.get(name, data[name]).encode('utf-8')
                          if name in patched else data[name])
    shutil.move(tmp, DECK)
    print('OK: ' + DECK)


if __name__ == '__main__':
    main()
