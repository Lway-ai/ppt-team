# -*- coding: utf-8 -*-
"""Render one 2x3 contact sheet per deck (87 sheets) for visual style audit.

Page picker per deck (6 tiles):
  t1 = cover (p0), t2 = p1 (outline/first content),
  t3 = max image-coverage content page, t4 = math-heaviest page,
  t5 = This-work comparison page (if any, else 2nd-max img page),
  t6 = densest bullet page (most body-size spans).
Output: perdeck_renders/<deck>.png  (tiles 640x360, sheet 1280x1080)
Read-only on the PDFs.
"""
import os
import sys

import fitz

SRC = r"D:\wanglei\project\TDA7707_GNSS\E_project\RFIC2024\2024_07_02_RMo01A_1"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "perdeck_renders")
os.makedirs(OUT, exist_ok=True)

TILE_W, TILE_H = 640, 360


def pick_pages(doc):
    n = doc.page_count
    img_cov, math_n, dense, tw = {}, {}, {}, []
    for pno in range(n):
        page = doc[pno]
        try:
            d = page.get_text("dict")
        except Exception:
            continue
        p_img = 0.0
        try:
            for img in page.get_images(full=True):
                for r in page.get_image_rects(img[0]):
                    p_img += r.width * r.height
        except Exception:
            pass
        img_cov[pno] = p_img / (page.rect.width * page.rect.height)
        mn, body = 0, 0
        txt = []
        for blk in d.get("blocks", []):
            if blk.get("type") != 0:
                continue
            for line in blk.get("lines", []):
                for sp in line.get("spans", []):
                    t = sp.get("text", "")
                    if not t.strip():
                        continue
                    txt.append(t)
                    if "math" in sp.get("font", "").lower().replace(" ", ""):
                        mn += 1
                    elif 20 <= sp["size"] <= 34:
                        body += 1
        math_n[pno] = mn
        dense[pno] = body
        if "This work" in " ".join(txt) or "This Work" in " ".join(txt):
            tw.append(pno)
    content = [p for p in range(1, n)]
    t3 = max(content, key=lambda p: img_cov.get(p, 0)) if content else 0
    t4 = max(content, key=lambda p: math_n.get(p, 0)) if content else 0
    t6 = max(content, key=lambda p: dense.get(p, 0)) if content else 0
    t5 = tw[0] if tw else max(content, key=lambda p: img_cov.get(p, 0) if p != t3 else -1)
    return [0, 1 if n > 1 else 0, t3, t4, t5, t6]


def main():
    files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".pdf"))
    for i, fn in enumerate(files):
        path = os.path.join(SRC, fn)
        out = os.path.join(OUT, fn.replace(".pdf", ".png"))
        if os.path.exists(out):
            print("[{}/{}] skip {}".format(i + 1, len(files), fn), flush=True)
            continue
        try:
            doc = fitz.open(path)
            pages = pick_pages(doc)
            zoom = TILE_W / doc[0].rect.width
            mat = fitz.Matrix(zoom, zoom)
            from PIL import Image
            sheet = Image.new("RGB", (TILE_W * 2, TILE_H * 3), "white")
            for k, pno in enumerate(pages):
                pix = doc[pno].get_pixmap(matrix=mat, alpha=False)
                tile = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                sheet.paste(tile, ((k % 2) * TILE_W, (k // 2) * TILE_H))
            sheet.save(out)
            doc.close()
            print("[{}/{}] {} pages={}".format(i + 1, len(files), fn, pages), flush=True)
        except Exception as e:
            print("[{}/{}] {} ERROR {}".format(i + 1, len(files), fn, e), flush=True)
    print("done ->", OUT, flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
