# -*- coding: utf-8 -*-
"""RFIC2024 corpus batch analyzer.
Measures every PDF deck: fonts, sizes, colors, margins, image coverage,
footer band, title style. Outputs corpus_stats.json + per-deck one-liners.
Read-only: never touches the PDFs.
"""
import json
import os
import re
import sys
from collections import Counter

import fitz  # PyMuPDF

SRC = r"D:\wanglei\project\TDA7707_GNSS\E_project\RFIC2024\2024_07_02_RMo01A_1"
OUT_DIR = r"D:\wanglei\project\TDA7707_GNSS\E_project\multi_agent_PPT_zcode\_learnings"

SUBSET_RE = re.compile(r"^[A-Z]{6}\+")


def chex(c):
    return "#{:06X}".format(c)


def analyze_deck(path):
    doc = fitz.open(path)
    deck = {
        "file": os.path.basename(path),
        "pages": doc.page_count,
        "page_w": round(doc[0].rect.width, 1),
        "page_h": round(doc[0].rect.height, 1),
        "fonts": Counter(),
        "sizes": Counter(),
        "colors": Counter(),
        "img_cov": [],          # per-page image-area / page-area
        "vec_ops": [],          # per-page vector drawing op count
        "left_margin": [],
        "content_bottom": [],
        "footer_band_pages": 0,
        "top_left_logo_pages": 0,
        "titles": [],           # (page, size, font, color, text, x, y, align_center)
        "cover_spans": [],      # page-0 span list (size desc)
        "table_pages": 0,
        "table_styles": Counter(),
        "n_draw_decks_flag": 0,
    }
    for pno in range(doc.page_count):
        page = doc[pno]
        pw, ph = page.rect.width, page.rect.height
        try:
            d = page.get_text("dict")
        except Exception:
            continue
        page_img_area = 0.0
        try:
            for img in page.get_images(full=True):
                try:
                    for r in page.get_image_rects(img[0]):
                        page_img_area += r.width * r.height
                except Exception:
                    pass
        except Exception:
            pass
        deck["img_cov"].append(round(min(page_img_area / (pw * ph), 1.5), 3))

        spans = []
        for blk in d.get("blocks", []):
            if blk.get("type") != 0:
                continue
            for line in blk.get("lines", []):
                for sp in line.get("spans", []):
                    txt = sp.get("text", "")
                    if not txt.strip():
                        continue
                    fname = SUBSET_RE.sub("", sp.get("font", "?"))
                    size = round(sp["size"] * 2) / 2.0
                    col = chex(sp["color"])
                    spans.append((fname, size, col, txt, sp["bbox"]))
                    deck["fonts"][fname] += len(txt)
                    deck["sizes"][size] += len(txt)
                    deck["colors"][col] += len(txt)
        if not spans:
            continue
        # left margin & content bottom (above footer band zone y>495)
        xs0 = [s[4][0] for s in spans if s[4][1] < ph - 45]
        ys1 = [s[4][3] for s in spans if s[4][3] < ph - 45]
        if xs0:
            deck["left_margin"].append(round(min(xs0), 1))
        if ys1:
            deck["content_bottom"].append(round(max(ys1), 1))
        # title = biggest span on page
        big = max(spans, key=lambda s: s[1])
        if pno > 0 and big[1] >= 30:
            cx = (big[4][0] + big[4][2]) / 2.0
            deck["titles"].append({
                "p": pno, "size": big[1], "font": big[0], "color": big[2],
                "text": big[3][:60], "x": round(big[4][0], 1), "y": round(big[4][1], 1),
                "centered": abs(cx - pw / 2) < pw * 0.12,
            })
        # footer band: wide filled rect near bottom via drawings
        try:
            draws = page.get_drawings()
            deck["vec_ops"].append(len(draws))
            fills = Counter()
            footer = False
            for dr in draws:
                if dr.get("fill"):
                    r = dr["rect"]
                    if r.width > pw * 0.85 and r.y0 > ph - 48 and r.height > 18:
                        footer = True
                    if r.width > pw * 0.5 or (r.width * r.height) > 0.02 * pw * ph:
                        f = dr["fill"]
                        fills[chex((int(f[0] * 255) << 16) + (int(f[1] * 255) << 8) + int(f[2] * 255))] += 1
            if footer:
                deck["footer_band_pages"] += 1
            # table detection: many small grid-like rects clustered
            small = [dr for dr in draws if dr.get("fill") is not None or dr.get("color") is not None]
            hlines = sum(1 for dr in draws for item in dr.get("items", []) if item[0] == "l" and abs(item[1].y - item[2].y) < 0.7)
            vlines = sum(1 for dr in draws for item in dr.get("items", []) if item[0] == "l" and abs(item[1].x - item[2].x) < 0.7)
            if hlines >= 6 and vlines >= 3:
                deck["table_pages"] += 1
                for c, n in fills.most_common(4):
                    deck["table_styles"][c] += n
        except Exception:
            pass
        # top-left logo image on page
        try:
            for img in page.get_images(full=True):
                for r in page.get_image_rects(img[0]):
                    if r.x0 < 80 and r.y0 < 40 and r.width < 110 and r.height > 60:
                        deck["top_left_logo_pages"] += 1
                        break
        except Exception:
            pass
        if pno == 0:
            deck["cover_spans"] = sorted(
                [{"size": s[1], "font": s[0], "color": s[2], "text": s[3][:48]}
                 for s in spans], key=lambda s: -s["size"])[:14]
    doc.close()
    return deck


def main():
    decks = []
    files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".pdf"))
    for i, fn in enumerate(files):
        path = os.path.join(SRC, fn)
        try:
            dk = analyze_deck(path)
        except Exception as e:
            dk = {"file": fn, "error": str(e)}
        decks.append(dk)
        print("[{}/{}] {}".format(i + 1, len(files), fn), flush=True)
    out = {
        "source": SRC,
        "n_decks": len(decks),
        "decks": decks,
    }
    with open(os.path.join(OUT_DIR, "corpus_stats.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved corpus_stats.json", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
