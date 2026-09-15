# -*- coding: utf-8 -*-
"""Deep per-element measurements over the RFIC2024 corpus.
1) formulas   : CambriaMath span size/color/italic; circled numbers; fake-math italic serif
2) hierarchy  : bullet glyph (size,color,font) + adjacent text size; lead-in bold-italic lines
3) tables     : on 'This work' pages — stroke widths, fills, cell text size/font/color
4) fig lines  : on vector-heavy pages — stroke width + stroke color histograms
Read-only. Output: deep_stats.json + printed summary.
"""
import os
import sys
import json
from collections import Counter

import fitz

SRC = r"D:\wanglei\project\TDA7707_GNSS\E_project\RFIC2024\2024_07_02_RMo01A_1"
HERE = os.path.dirname(os.path.abspath(__file__))

import re
SUBSET_RE = re.compile(r"^[A-Z]{6}\+")
BULLETS = set("•●◦·▪◾◦–—‒□■○◊➢")
CIRCLED = [(0x2460, 0x2473), (0x2776, 0x277F), (0x24EB, 0x24F4)]


def inch(c):
    return "#{:06X}".format(c)


def main():
    S = {
        "math": {"sizes": Counter(), "colors": Counter(), "fonts": Counter(), "n_spans": 0},
        "circled": {"sizes": Counter(), "colors": Counter(), "chars": Counter(), "n": 0},
        "fakemath": {"fonts": Counter(), "sizes": Counter(), "n": 0},
        "bullets": {"glyphs": Counter(), "pair": Counter(), "glyph_colors": Counter()},
        "leadin": {"sizes": Counter(), "n": 0},
        "table": {"stroke_w": Counter(), "fills": Counter(), "text_sizes": Counter(),
                  "text_colors": Counter(), "n_pages": 0},
        "fig": {"stroke_w": Counter(), "stroke_colors": Counter(), "dash": Counter(),
                "fill_colors": Counter()},
        "fig_text_min": Counter(),   # per heavy-fig page min annotation size bucket
    }
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".pdf"))
    for fn in files:
        doc = fitz.open(os.path.join(SRC, fn))
        pages_spans = []
        for pno in range(doc.page_count):
            page = doc[pno]
            try:
                d = page.get_text("dict")
            except Exception:
                pages_spans.append(None)
                continue
            spans = []
            for blk in d.get("blocks", []):
                if blk.get("type") != 0:
                    continue
                for line in blk.get("lines", []):
                    lsps = []
                    for sp in line.get("spans", []):
                        t = sp.get("text", "")
                        if not t.strip():
                            continue
                        lsps.append({
                            "t": t, "f": SUBSET_RE.sub("", sp.get("font", "?")),
                            "s": round(sp["size"] * 2) / 2.0, "c": inch(sp["color"]),
                            "fl": sp["flags"], "bb": sp["bbox"],
                        })
                    if lsps:
                        spans.append(lsps)
            pages_spans.append(spans)

        # ---- 1) formulas / circled ----
        for spans in pages_spans:
            if not spans:
                continue
            for line in spans:
                for sp in line:
                    fname = sp["f"].lower()
                    if "cambriamath" in fname.replace(" ", "") or "math" in fname:
                        S["math"]["n_spans"] += 1
                        S["math"]["sizes"][sp["s"]] += 1
                        S["math"]["colors"][sp["c"]] += 1
                        S["math"]["fonts"][sp["f"]] += 1
                    for lo, hi in CIRCLED:
                        if any(lo <= ord(ch) <= hi for ch in sp["t"]):
                            S["circled"]["n"] += 1
                            S["circled"]["sizes"][sp["s"]] += 1
                            S["circled"]["colors"][sp["c"]] += 1
                            for ch in sp["t"]:
                                if any(lo <= ord(ch) <= hi for lo, hi in CIRCLED):
                                    S["circled"]["chars"][ch] += 1
                    # fake math: italic serif times/cambria non-math with letters+digits
                    it = sp["fl"] & 2
                    if it and ("times" in fname or "cambria" in fname) and "math" not in fname:
                        if any(ch.isalpha() for ch in sp["t"]) and any(ch.isdigit() or ch in "=±×∙·" for ch in sp["t"]):
                            S["fakemath"]["n"] += 1
                            S["fakemath"]["fonts"][sp["f"]] += 1
                            S["fakemath"]["sizes"][sp["s"]] += 1

        # ---- 2) hierarchy: bullets + lead-in ----
        for spans in pages_spans:
            if not spans:
                continue
            for li, line in enumerate(spans):
                first = line[0]
                stripped = first["t"].strip()
                if stripped and stripped[0] in BULLETS and len(first["t"].strip()) <= 2:
                    nxt = None
                    if len(line) > 1:
                        nxt = line[1]
                    elif li + 1 < len(spans):
                        cand = spans[li + 1][0]
                        nxt = cand
                    S["bullets"]["glyphs"][stripped[0]] += 1
                    S["bullets"]["glyph_colors"][first["c"]] += 1
                    if nxt is not None:
                        S["bullets"]["pair"]["{}glyph {}pt -> text {}pt {}".format(
                            stripped[0], first["s"], nxt["s"], nxt["f"])] += 1
            # lead-in: bold+italic line, 24-40pt, above all bullets, ends with ':' mostly
            if spans:
                flat_first = spans[0]
                for sp in flat_first[:2]:
                    if (sp["fl"] & 2) and (sp["fl"] & 16) and 22 <= sp["s"] <= 42:
                        S["leadin"]["n"] += 1
                        S["leadin"]["sizes"][sp["s"]] += 1

        # ---- 3) tables on 'This work' pages ----
        for pno, spans in enumerate(pages_spans):
            if not spans:
                continue
            txt = " ".join(sp["t"] for line in spans for sp in line)
            if "This work" not in txt and "This Work" not in txt:
                continue
            S["table"]["n_pages"] += 1
            if S["table"]["n_pages"] > 60:
                continue
            try:
                draws = page.get_drawings() if False else doc[pno].get_drawings()
            except Exception:
                continue
            hw, vw = Counter(), Counter()
            fills = Counter()
            tbox = None
            for dr in draws:
                r = dr["rect"]
                for item in dr.get("items", []):
                    if item[0] == "l":
                        p1, p2 = item[1], item[2]
                        w = dr.get("width") or 0
                        if abs(p1.y - p2.y) < 0.8 and abs(p1.x - p2.x) > 8:
                            hw[round(w * 4) / 4] += 1
                            if tbox is None:
                                tbox = [r.x0, r.y0, r.x1, r.y1]
                        elif abs(p1.x - p2.x) < 0.8 and abs(p1.y - p2.y) > 4:
                            vw[round(w * 4) / 4] += 1
                    elif item[0] == "re" and dr.get("fill"):
                        f = dr["fill"]
                        fills[inch((int(f[0] * 255) << 16) + (int(f[1] * 255) << 8) + int(f[2] * 255))] += 1
            for w, n in hw.most_common(6):
                S["table"]["stroke_w"]["h:{}pt x{}".format(w, n)] += 1
            for w, n in vw.most_common(4):
                S["table"]["stroke_w"]["v:{}pt x{}".format(w, n)] += 1
            for c, n in fills.most_common(8):
                S["table"]["fills"][c] += n
            if tbox:
                for line in spans:
                    for sp in line:
                        bb = sp["bb"]
                        if bb[0] >= tbox[0] - 2 and bb[2] <= tbox[2] + 2 and bb[1] >= tbox[1] - 2 and bb[3] <= tbox[3] + 2:
                            S["table"]["text_sizes"][sp["s"]] += 1
                            S["table"]["text_colors"][sp["c"]] += 1

        # ---- 4) fig line weights on vector-heavy pages ----
        heavy = []
        for pno in range(doc.page_count):
            try:
                nd = len(doc[pno].get_drawings())
            except Exception:
                nd = 0
            heavy.append((nd, pno))
        heavy.sort(reverse=True)
        for nd, pno in heavy[:4]:
            if nd < 120:
                break
            try:
                draws = doc[pno].get_drawings()
            except Exception:
                continue
            mins = 99
            for dr in draws:
                w = dr.get("width")
                col = dr.get("color")
                if dr.get("dashes") and dr["dashes"] not in ("[] 0", ""):
                    S["fig"]["dash"][str(dr["dashes"])[:24]] += 1
                if w:
                    S["fig"]["stroke_w"][round(w * 4) / 4] += 1
                if col:
                    c = inch((int(col[0] * 255) << 16) + (int(col[1] * 255) << 8) + int(col[2] * 255))
                    S["fig"]["stroke_colors"][c] += 1
                if dr.get("fill"):
                    f = dr["fill"]
                    S["fig"]["fill_colors"][inch((int(f[0] * 255) << 16) + (int(f[1] * 255) << 8) + int(f[2] * 255))] += 1
            spans = pages_spans[pno]
            if spans:
                sizes = [sp["s"] for line in spans for sp in line if sp["s"] < 26]
                if sizes:
                    S["fig_text_min"][round(min(sizes))] += 1
        doc.close()
        print("done", fn, flush=True)

    out = {}
    for k, v in S.items():
        out[k] = {str(kk): vv for kk, vv in v.items()}
    with open(os.path.join(HERE, "deep_stats.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    def show(name, counter, top=14):
        print("== {} ==".format(name))
        for kk, vv in counter.most_common(top):
            print("   {}: {}".format(kk, vv))

    show("MATH sizes", S["math"]["sizes"])
    show("MATH colors", S["math"]["colors"], 8)
    show("MATH fonts", S["math"]["fonts"], 6)
    print("   n_spans:", S["math"]["n_spans"])
    show("CIRCLED sizes", S["circled"]["sizes"], 8)
    show("CIRCLED colors", S["circled"]["colors"], 8)
    show("CIRCLED chars", S["circled"]["chars"], 10)
    print("   n:", S["circled"]["n"])
    show("FAKEMATH fonts", S["fakemath"]["fonts"], 8)
    show("FAKEMATH sizes", S["fakemath"]["sizes"], 10)
    show("BULLET glyphs", S["bullets"]["glyphs"], 12)
    show("BULLET glyph colors", S["bullets"]["glyph_colors"], 6)
    show("BULLET glyph->text pairs", S["bullets"]["pair"], 18)
    show("LEADIN sizes(bold+italic)", S["leadin"]["sizes"], 8)
    print("   n:", S["leadin"]["n"])
    print("== TABLE (n_pages={}) ==".format(S["table"]["n_pages"]))
    show("  stroke_w", S["table"]["stroke_w"], 12)
    show("  fills", S["table"]["fills"], 10)
    show("  text_sizes", S["table"]["text_sizes"], 12)
    show("  text_colors", S["table"]["text_colors"], 8)
    show("FIG stroke widths", S["fig"]["stroke_w"], 12)
    show("FIG stroke colors", S["fig"]["stroke_colors"], 14)
    show("FIG fill colors", S["fig"]["fill_colors"], 12)
    show("FIG dash patterns", S["fig"]["dash"], 6)
    show("FIG min text size", S["fig_text_min"], 10)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
