#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""omml_tex.py — mini LaTeX → OMML 生成器（inject_omml.py 的公式引擎）。

支持子集（RFIC 推导常用面）:
  变量/数字自动正斜体;  x_i  x^2  x_i^2  a_{ij}
  \\frac{a}{b}   \\sqrt{x}   \\sqrt[n]{x}
  希腊字母(\\alpha..\\Omega)与常用符号(\\times \\cdot \\pm \\leq \\geq \\neq \\approx
    \\infty \\rightarrow \\Rightarrow \\partial \\nabla \\propto ...)
  \\text{...} / \\mathrm{...} 正体（含中文自动挂 EA 字体正体 i="0" —— 事故修复样式）
  \\log \\ln \\sin ... 函数名正体
  \\left( ... \\right) 自适应定界符;  ( ) [ ] 直接量
  \\begin{matrix|pmatrix|bmatrix} a & b \\\\ c & d \\end{...} 矩阵
  顶层 \\\\ 分行 → 多段落

输出: tex_paragraphs(latex) -> [m:oMathPara XML, ...]（不含 a14:m 包装, inject_omml 负责）。
"""
import re
import xml.sax.saxutils as sx

M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

SYMBOLS = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε',
    'varepsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'vartheta': 'ϑ',
    'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ',
    'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
    'phi': 'φ', 'varphi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
    'Gamma': 'Γ', 'Delta': 'Δ', 'Theta': 'Θ', 'Lambda': 'Λ', 'Xi': 'Ξ',
    'Pi': 'Π', 'Sigma': 'Σ', 'Phi': 'Φ', 'Psi': 'Ψ', 'Omega': 'Ω',
    'times': '×', 'cdot': '·', 'div': '÷', 'pm': '±', 'mp': '∓',
    'leq': '≤', 'geq': '≥', 'neq': '≠', 'approx': '≈', 'equiv': '≡',
    'infty': '∞', 'rightarrow': '→', 'to': '→', 'Rightarrow': '⇒',
    'leftarrow': '←', 'Leftarrow': '⇐', 'mapsto': '↦',
    'propto': '∝', 'partial': '∂', 'nabla': '∇', 'hbar': 'ℏ',
    'circ': '∘', 'ldots': '…', 'cdots': '⋯', 'dots': '…',
    'in': '∈', 'notin': '∉', 'cup': '∪', 'cap': '∩',
    'subset': '⊂', 'supset': '⊃', 'perp': '⊥', 'parallel': '∥',
    'degree': '°', 'angle': '∠', 'quad': '  ', 'qquad': '    ',
    ',': ' ', ';': ' ', ':': ' ', ' ': ' ',
}
FUNCNAMES = {'log', 'ln', 'exp', 'sin', 'cos', 'tan', 'max', 'min', 'det', 'tr', 'Re', 'Im'}
GREEK_RE = re.compile(r'^[α-ωΑ-Ω]$')


def esc(t):
    return sx.escape(t)


def run(text, italic=True, ea_font='微软雅黑'):
    """m:r 运行。含 EA 码点 → 挂 a:ea 且正体（事故修复样式）；数字/符号正体；字母斜体。"""
    has_ea = any(ord(c) > 0x2E80 for c in text)
    is_letter = any(c.isalpha() and c.isascii() for c in text)
    up = (not italic) or (not is_letter)
    i = '0' if (up or has_ea) else '1'
    eaf = '<a:ea typeface="%s"/>' % ea_font if has_ea else ''
    return ('<m:r><a:rPr lang="en-US" i="%s">'
            '<a:latin typeface="Cambria Math"/>%s</a:rPr><m:t>%s</m:t></m:r>'
            % (i, eaf, esc(text)))


TOKEN_RE = re.compile(r"""
    \\\\ |
    \\[A-Za-z]+ | \\[,;:! ] |
    [_^] | [{}\[\]&()] |
    [^\s_^{}\\&()\[\]]+ |
    \s+
""", re.X)


class Tok:
    def __init__(self, kind, val):
        self.kind, self.val = kind, val


def tokenize(s):
    toks = []
    for m in TOKEN_RE.finditer(s):
        t = m.group(0)
        if t.isspace():
            continue
        if t == '\\\\':
            toks.append(Tok('rowbreak', t))
        elif t.startswith('\\'):
            toks.append(Tok('cmd', t[1:]))
        elif t in '_^{}&':
            toks.append(Tok(t, t))
        elif t in '[]()':
            toks.append(Tok('paren', t))
        else:
            toks.append(Tok('chr', t))
    return toks


class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def next(self):
        t = self.peek()
        self.i += 1
        return t

    def parse_seq(self, until_right=False, stop=None):
        items = []
        while True:
            t = self.peek()
            if t is None:
                break
            if stop and t.kind == stop:
                break
            if until_right and t.kind == 'cmd' and t.val == 'right':
                self.next()
                d = self.next()
                self._right_char = d.val if d and d.kind == 'paren' else (
                    SYMBOLS.get(d.val, '.') if d and d.kind == 'cmd' else '.')
                break
            items.append(self.parse_atom())
        return items

    def group(self):
        t = self.peek()
        if t and t.kind == '{':
            self.next()
            items = self.parse_seq(stop='}')
            if self.peek() and self.peek().kind == '}':
                self.next()
            return items
        a = self.parse_atom()
        return [a] if a is not None else []

    def parse_atom(self):
        t = self.next()
        if t is None:
            return None
        if t.kind == 'cmd':
            name = t.val
            if name in ('frac', 'dfrac', 'tfrac'):
                num, den = self.group(), self.group()
                return ('frac', num, den)
            if name == 'sqrt':
                nxt = self.peek()
                if nxt and nxt.kind == 'paren' and nxt.val == '[':
                    self.next()
                    deg = self.parse_seq()
                    t2 = self.peek()
                    if t2 and t2.kind == 'paren' and t2.val == ']':
                        self.next()
                    return ('sqrt', self.group(), deg)
                return ('sqrt', self.group(), None)
            if name in ('text', 'mathrm', 'operatorname', 'textrm'):
                return ('text', self._raw_group())
            if name in FUNCNAMES:
                return ('text', name)
            if name == 'begin':
                return self._matrix()
            if name == 'left':
                d = self.next()
                beg = d.val if d and d.kind == 'paren' else (
                    SYMBOLS.get(d.val, '.') if d and d.kind == 'cmd' else '.')
                self._right_char = ')'
                inner = self.parse_seq(until_right=True)
                return ('delim', beg, self._right_char, inner)
            if name == 'right':  # 无配对 \left, 直接产出字符
                d = self.next()
                return ('sym', d.val if d and d.kind == 'paren' else '.')
            if name in SYMBOLS:
                return ('sym', SYMBOLS[name])
            return ('text', name)   # 未知命令按正体字面
        if t.kind == '_':
            return self._script('sub')
        if t.kind == '^':
            return self._script('sup')
        if t.kind == '&':
            return None
        if t.kind in ('{', '}'):
            return None
        if t.kind == 'paren':
            return ('sym', t.val)
        return ('sym', t.val)

    def _raw_group(self):
        t = self.next()
        if t and t.kind == '{':
            buf = ''
            depth = 1
            while depth:
                t2 = self.next()
                if t2 is None:
                    break
                if t2.kind == '{':
                    depth += 1
                elif t2.kind == '}':
                    depth -= 1
                    if not depth:
                        break
                if t2.kind == 'chr':
                    buf += t2.val
                elif t2.kind == 'cmd':
                    buf += SYMBOLS.get(t2.val, t2.val)
                else:
                    buf += t2.val
            return buf
        if t and t.kind == 'chr':
            return t.val
        if t and t.kind == 'cmd':
            return SYMBOLS.get(t.val, t.val)
        return ''

    def _script(self, which):
        return ('script', which, self.group())

    def _matrix(self):
        self.next()               # 消耗 begin 后的 '{'
        env = self.next()         # 环境名
        envname = env.val if env else 'matrix'
        if self.peek() and self.peek().kind == '}':
            self.next()
        rows = [[[]]]          # 行 × 格 × items
        while True:
            t = self.peek()
            if t is None:
                break
            if t.kind == 'cmd' and t.val == 'end':
                self.next()
                while self.peek() and self.peek().kind != '}':
                    self.next()
                if self.peek():
                    self.next()
                break
            if t.kind == 'rowbreak':
                self.next()
                rows.append([[]])
                continue
            if t.kind == '&':
                self.next()
                rows[-1].append([])
                continue
            a = self.parse_atom()
            if a is not None:
                rows[-1][-1].append(a)
        return ('matrix', envname, rows)


def fold_scripts(items):
    """x_i^2 序列折叠: 前一元素 + 连续 script → ('scripted', base, sub, sup)。"""
    out = []
    k = 0
    while k < len(items):
        it = items[k]
        if isinstance(it, tuple) and it[0] == 'script' and out:
            base = out.pop()
            sub = it[2] if it[1] == 'sub' else None
            sup = it[2] if it[1] == 'sup' else None
            if k + 1 < len(items) and isinstance(items[k + 1], tuple) and items[k + 1][0] == 'script':
                it2 = items[k + 1]
                sub = it2[2] if it2[1] == 'sub' else sub
                sup = it2[2] if it2[1] == 'sup' else sup
                k += 1
            out.append(('scripted', base, sub, sup))
            k += 1
            continue
        if it is not None:
            out.append(it)
        k += 1
    return out


def to_xml(items):
    items = fold_scripts(items)
    out = []
    k = 0
    while k < len(items):
        it = items[k]
        kind = it[0] if it else None
        if kind == 'sym':
            out.append(run(it[1], italic=not (GREEK_RE.match(it[1]) or it[1].isdigit())))
        elif kind == 'text':
            out.append(run(it[1], italic=False))
        elif kind == 'frac':
            out.append('<m:f><m:num>%s</m:num><m:den>%s</m:den></m:f>'
                       % (to_xml(it[1]), to_xml(it[2])))
        elif kind == 'sqrt':
            deg = ('<m:deg>%s</m:deg>' % to_xml(it[2])) if it[2] else '<m:deg/>'
            hide = '' if it[2] else '<m:radPr><m:degHide m:val="1"/></m:radPr>'
            out.append('<m:rad>%s%s<m:e>%s</m:e></m:rad>' % (hide, deg, to_xml(it[1])))
        elif kind == 'scripted':
            base = to_xml([it[1]])
            sub = to_xml(it[2]) if it[2] else None
            sup = to_xml(it[3]) if it[3] else None
            if sub and sup:
                out.append('<m:sSubSup><m:e>%s</m:e><m:sub>%s</m:sub><m:sup>%s</m:sup></m:sSubSup>'
                           % (base, sub, sup))
            elif sub:
                out.append('<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>' % (base, sub))
            elif sup:
                out.append('<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>' % (base, sup))
        elif kind == 'delim':
            beg, end = it[1], it[2]
            dpr = ''
            if not (beg == '(' and end == ')'):
                dpr = ('<m:dPr><m:begChr m:val="%s"/><m:endChr m:val="%s"/></m:dPr>'
                       % (esc(beg), esc(end)))
            out.append('<m:d>%s<m:e>%s</m:e></m:d>' % (dpr, to_xml(it[3])))
        elif kind == 'matrix':
            out.append(_matrix_xml(it[1], it[2]))
        k += 1
    return ''.join(out)


def _matrix_xml(env, rows):
    ncol = max(len(r) for r in rows) if rows else 1
    mcs = ('<m:mcs><m:mc><m:mcPr><m:mcount m:val="%d"/><m:mcJc m:val="center"/></m:mcPr>'
           '</m:mc></m:mcs>' % ncol)
    mrs = ''.join('<m:mr>%s</m:mr>' % ''.join('<m:e>%s</m:e>' % to_xml(fold_scripts(cell)) for cell in row)
                  for row in rows)
    inner = '<m:m><m:mPr>%s</m:mPr>%s</m:m>' % (mcs, mrs)
    if env == 'pmatrix':
        return ('<m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>'
                '<m:e>%s</m:e></m:d>' % inner)
    if env == 'bmatrix':
        return ('<m:d><m:dPr><m:begChr m:val="["/><m:endChr m:val="]"/></m:dPr>'
                '<m:e>%s</m:e></m:d>' % inner)
    return inner


MATRIX_BLOCK_RE = re.compile(
    r'\\begin\{(matrix|pmatrix|bmatrix|vmatrix|Bmatrix|array)\}.*?\\end\{\1\}', re.S)


def tex_paragraphs(latex):
    """分段: 顶层 \\\\ 分行, 但矩阵环境内的 \\\\ 受保护(整块并入当前段落)。
    返回 [m:oMathPara XML, ...]（不含 a14:m 包装）。"""
    paras = []
    buf = []
    idx = 0

    def flush():
        body = ''.join(buf)
        buf.clear()
        items = fold_scripts(Parser(tokenize(body)).parse_seq())
        xml = to_xml(items)
        if xml.strip():
            paras.append('<m:oMathPara xmlns:m="%s"><m:oMath>%s</m:oMath></m:oMathPara>' % (M, xml))

    pieces = []
    for m in MATRIX_BLOCK_RE.finditer(latex):
        for j, pc in enumerate(latex[idx:m.start()].split('\\\\')):
            pieces.append((j > 0, pc))
        pieces.append((False, m.group(0)))
        idx = m.end()
    for j, pc in enumerate(latex[idx:].split('\\\\')):
        pieces.append((j > 0, pc))
    for is_break, pc in pieces:
        if is_break:
            flush()
        buf.append(pc)
    flush()
    return paras
