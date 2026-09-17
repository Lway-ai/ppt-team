# -*- coding: utf-8 -*-
"""Per-deck style profiler over the RFIC2024 corpus (87 decks, 1 PDF = 1 talk).

For EVERY deck, measures the 8 style dimensions the ppt-team needs:
  1 fonts        : family histogram + bold/italic variant share + Latin-font verdict
  2 line spacing : baseline-delta/size per size level (median), tight<1.32 / loose>=1.32
  3 sizes        : title / cover(session,title,author,affil) / L1-L3 bullets / lead-in
  4 hierarchy    : bullet indent clusters -> per-level size+glyph color
  5 drawing      : stroke-width histogram, thick(>=2pt) share, dash usage,
                   top stroke/fill colors, min fig-annotation size
  6 formulas     : Cambria-Math span n / sizes / colors / circled-numbers
  7 tables       : This-work pages, horizontal-rule widths, fill colors
  8 layout       : left margin, img coverage, footer band, top-left logo

Read-only on the PDFs. Output:
  perdeck_profiles.json            (machine readable, 87 entries)
  RFIC2024_perdeck_profiles.md     (human readable, one block per deck)
Reuses the exact conventions of analyze_corpus.py / deep_measure.py.
"""
import json
import os
import re
import statistics
import sys
from collections import Counter

import fitz

SRC = r"D:\wanglei\project\TDA7707_GNSS\E_project\RFIC2024\2024_07_02_RMo01A_1"
HERE = os.path.dirname(os.path.abspath(__file__))

SUBSET_RE = re.compile(r"^[A-Z]{6}\+")
BULLETS = set("•●◦·▪◾–—‒□■○◊➢")
CIRCLED = [(0x2460, 0x2473), (0x2776, 0x277F), (0x24EB, 0x24F4)]


def chex(c):
    return "#{:06X}".format(c)


def c2d(counter, n=None):
    items = counter.most_common(n) if n else counter.most_common()
    return {str(k): v for k, v in items}


def median(xs):
    return round(statistics.median(xs), 2) if xs else None


def profile_deck(path):
    doc = fitz.open(path)
    P = {
        "file": os.path.basename(path),
        "pages": doc.page_count,
        "pw": round(doc[0].rect.width, 1),
        "ph": round(doc[0].rect.height, 1),
    }
    fonts = Counter()          # family -> chars
    variants = Counter()       # Bold/Italic/BoldItalic -> chars
    math_font = Counter()      # math font names -> chars
    title_votes = Counter()    # (size,font,color) on pages>0
    title_centered = [0, 0]
    cover_sizes = []           # (size, bold, y, text, centered)
    leadin = Counter()
    bullet_lines = []          # (x0, glyph, glyph_size, glyph_color, text_size, text_font)
    spacing = {}               # size-level -> [ratios]
    ratio_hist = Counter()
    math_sizes, math_colors = Counter(), Counter()
    math_n = 0
    circled_n = 0
    circled_sizes = Counter()
    stroke_w = Counter()
    stroke_colors = Counter()
    fill_colors = Counter()
    dash_n = 0
    vec_total = 0
    fig_ann_min = Counter()    # min annotation size per fig-heavy page
    fig_ann_font = Counter()
    tw_pages = 0
    tw_hline = Counter()
    tw_fills = Counter()
    left_m, cont_b, img_cov = [], [], []
    footer_pages = 0
    logo_pages = 0
    pw, ph = P["pw"], P["ph"]

    for pno in range(doc.page_count):
        page = doc[pno]
        try:
            d = page.get_text("dict")
        except Exception:
            continue
        # image coverage + raster footer band + top-left logo (RFIC logo bleeds off-page)
        p_img = 0.0
        page_logo = False
        page_footer_img = False
        try:
            for img in page.get_images(full=True):
                for r in page.get_image_rects(img[0]):
                    p_img += r.width * r.height
                    if r.x0 < 80 and r.y0 < 40 and r.height > 50:
                        page_logo = True
                    if r.width > pw * 0.8 and r.y0 > ph - 60 and 15 < r.height < 80:
                        page_footer_img = True
        except Exception:
            pass
        if page_logo:
            logo_pages += 1
        img_cov.append(round(min(p_img / (pw * ph), 1.5), 3))

        blocks = []
        for blk in d.get("blocks", []):
            if blk.get("type") != 0:
                continue
            lines = []
            for line in blk.get("lines", []):
                spans = []
                for sp in line.get("spans", []):
                    t = sp.get("text", "")
                    if not t.strip():
                        continue
                    fname = SUBSET_RE.sub("", sp.get("font", "?"))
                    spans.append({
                        "t": t, "f": fname, "s": round(sp["size"] * 2) / 2.0,
                        "c": chex(sp["color"]), "fl": sp["flags"], "bb": sp["bbox"],
                    })
                    fonts[fname] += len(t)
                    if "math" in fname.lower().replace(" ", ""):
                        math_font[fname] += len(t)
                        math_n += 1
                        math_sizes[spans[-1]["s"]] += 1
                        math_colors[spans[-1]["c"]] += 1
                    elif fname.endswith("BoldItalic"):
                        variants["BoldItalic"] += len(t)
                    elif fname.endswith("Bold"):
                        variants["Bold"] += len(t)
                    elif fname.endswith("Italic"):
                        variants["Italic"] += len(t)
                    else:
                        variants["Regular"] += len(t)
                    for lo, hi in CIRCLED:
                        if any(lo <= ord(ch) <= hi for ch in t):
                            circled_n += 1
                            circled_sizes[spans[-1]["s"]] += 1
                if spans:
                    lines.append(spans)
            if lines:
                blocks.append(lines)

        # flat lines for margins / titles / cover
        flat = [ln for blk in blocks for ln in blk]
        xs0 = [ln[0]["bb"][0] for ln in flat if ln[0]["bb"][1] < ph - 45]
        ys1 = [ln[-1]["bb"][3] for ln in flat if ln[-1]["bb"][3] < ph - 45]
        if xs0:
            left_m.append(round(min(xs0), 1))
        if ys1:
            cont_b.append(round(max(ys1), 1))
        if flat and pno > 0:
            big = max((sp for ln in flat for sp in ln), key=lambda s: s["s"])
            if big["s"] >= 30:
                cx = (big["bb"][0] + big["bb"][2]) / 2.0
                title_votes[(big["s"], big["f"], big["c"])] += 1
                title_centered[1] += 1
                if abs(cx - pw / 2) < pw * 0.12:
                    title_centered[0] += 1
        if pno == 0 and flat:
            for sp in (sp for ln in flat for sp in ln):
                cx = (sp["bb"][0] + sp["bb"][2]) / 2.0
                cover_sizes.append((sp["s"], bool(sp["fl"] & 16), round(sp["bb"][1]),
                                    sp["t"].strip()[:40], abs(cx - pw / 2) < pw * 0.15))

        # lead-in: first line of page, bold+italic, 22-42pt (deep_measure convention)
        if flat:
            for sp in flat[0][:2]:
                if (sp["fl"] & 2) and (sp["fl"] & 16) and 22 <= sp["s"] <= 42:
                    leadin[sp["s"]] += 1
                    break

        # bullet hierarchy: glyph-line -> (indent, glyph info, text size/font)
        for blk in blocks:
            for li, ln in enumerate(blk):
                first = ln[0]
                st = first["t"].strip()
                if st and st[0] in BULLETS and len(st) <= 2:
                    nxt = ln[1] if len(ln) > 1 else (
                        blk[li + 1][0] if li + 1 < len(blk) else None)
                    bullet_lines.append((round(first["bb"][0]), st[0], first["s"],
                                         first["c"], nxt["s"] if nxt else None,
                                         nxt["f"] if nxt else None))

        # line spacing: consecutive lines within a block, same level, non-superscript
        for blk in blocks:
            for a, b in zip(blk, blk[1:]):
                sa = [sp for sp in a if not (sp["fl"] & 1)]
                sb = [sp for sp in b if not (sp["fl"] & 1)]
                if not sa or not sb:
                    continue
                s1, s2 = sa[0]["s"], sb[0]["s"]
                if abs(s1 - s2) > max(1.0, 0.15 * max(s1, s2)):
                    continue
                size = max(s1, s2)
                if size < 13:
                    continue
                delta = sb[0]["bb"][3] - sa[0]["bb"][3]
                if not (0.5 * size <= delta <= 2.5 * size) or delta <= 0:
                    continue
                r = round(delta / size, 2)
                spacing.setdefault(size, []).append(r)
                ratio_hist[round(r * 20) / 20.0] += 1

        # drawings: stroke widths / colors / fills / dash
        try:
            draws = page.get_drawings()
        except Exception:
            draws = []
        vec_total += len(draws)
        footer = False
        tfills = Counter()
        for dr in draws:
            r = dr["rect"]
            if dr.get("fill"):
                fc = chex((int(dr["fill"][0] * 255) << 16) + (int(dr["fill"][1] * 255) << 8)
                          + int(dr["fill"][2] * 255))
                fill_colors[fc] += 1
                tfills[fc] += 1
                if r.width > pw * 0.85 and r.y0 > ph - 48 and r.height > 18:
                    footer = True
            w = dr.get("width")
            if w:
                stroke_w[round(w * 4) / 4] += 1
            col = dr.get("color")
            if col:
                stroke_colors[chex((int(col[0] * 255) << 16) + (int(col[1] * 255) << 8)
                                   + int(col[2] * 255))] += 1
            if dr.get("dashes") and dr["dashes"] not in ("[] 0", ""):
                dash_n += 1
        if footer or page_footer_img:
            footer_pages += 1

        # This-work table pages: horizontal rule widths
        txt = " ".join(sp["t"] for ln in flat for sp in ln)
        if "This work" in txt or "This Work" in txt:
            tw_pages += 1
            for dr in draws:
                for item in dr.get("items", []):
                    if item[0] == "l" and abs(item[1].y - item[2].y) < 0.8 \
                            and abs(item[1].x - item[2].x) > 8:
                        tw_hline[round((dr.get("width") or 0) * 4) / 4] += 1
            for c, n in tfills.most_common(4):
                tw_fills[c] += n

        # fig annotation floor: min body-text size on fig-heavy pages
        n_draw_here = len(draws)
        if (n_draw_here >= 60 or img_cov[-1] >= 0.4) and flat:
            sizes = [sp["s"] for ln in flat for sp in ln if sp["s"] < 26]
            if sizes:
                m = min(sizes)
                fig_ann_min[m] += 1
                fsp = min((sp for ln in flat for sp in ln if sp["s"] == m),
                          key=lambda s: s["s"])
                fig_ann_font[fsp["f"]] += 1

    doc.close()

    # ---- hierarchy: cluster bullet indents ----
    levels = {}
    if bullet_lines:
        xs = sorted({b[0] for b in bullet_lines})
        clusters = [[xs[0], xs[0]]]
        for x in xs[1:]:
            if x - clusters[-1][1] <= 15:
                clusters[-1][1] = x
            else:
                clusters.append([x, x])
        order = []
        for lo, hi in clusters:
            cnt = sum(1 for b in bullet_lines if lo <= b[0] <= hi)
            if cnt >= max(3, 0.05 * len(bullet_lines)):
                order.append((lo, hi, cnt))
        order.sort()
        for i, (lo, hi, cnt) in enumerate(order[:3]):
            grp = [b for b in bullet_lines if lo <= b[0] <= hi]
            szs = Counter(b[4] for b in grp if b[4])
            gcols = Counter(b[3] for b in grp)
            gszs = Counter(b[2] for b in grp)
            glyphs = Counter(b[1] for b in grp)
            levels["L{}".format(i + 1)] = {
                "n": cnt,
                "text_size": szs.most_common(1)[0][0] if szs else None,
                "text_size_alt": [k for k, _ in szs.most_common(3)],
                "glyph": glyphs.most_common(1)[0][0] if glyphs else None,
                "glyph_color": gcols.most_common(1)[0][0] if gcols else None,
                "glyph_size": gszs.most_common(1)[0][0] if gszs else None,
            }

    # ---- line spacing per size level ----
    sp_lvl = {}
    for size in sorted(spacing, reverse=True):
        rs = spacing[size]
        if len(rs) >= 5:
            sp_lvl[size] = {"median": round(statistics.median(rs), 2), "n": len(rs)}

    # ---- stroke verdict ----
    sw_total = sum(stroke_w.values())
    main_w = None
    if sw_total:
        cand = {w: n for w, n in stroke_w.items() if 0.75 <= w <= 3.0}
        if cand:
            main_w = max(cand.items(), key=lambda kv: kv[1])[0]
    thick = sum(n for w, n in stroke_w.items() if w >= 2.0)
    thin = sum(n for w, n in stroke_w.items() if 0 < w < 0.75)

    title = None
    if title_votes:
        (ts, tf, tc), votes = title_votes.most_common(1)[0]
        title = {"size": ts, "font": tf, "color": tc, "n": votes,
                 "centered": round(title_centered[0] / max(title_centered[1], 1), 2)}

    cover = {}
    if cover_sizes:
        mx = max(s for s, b, y, t, c in cover_sizes)
        cover["title_size"] = mx
        sess = [s for s, b, y, t, c in cover_sizes if y < 95 and 26 <= s <= 40 and c]
        if sess:
            cover["session_size"] = Counter(sess).most_common(1)[0][0]
        auth = [s for s, b, y, t, c in cover_sizes if s < mx and 22 <= s <= 34 and b]
        if auth:
            cover["author_size"] = Counter(auth).most_common(1)[0][0]
        aff = [s for s, b, y, t, c in cover_sizes if s < mx and 16 <= s <= 24]
        if aff:
            cover["affil_size"] = Counter(aff).most_common(1)[0][0]

    total_chars = sum(fonts.values()) or 1
    fam = Counter()
    for f, n in fonts.items():
        fam[re.sub(r"-(Bold|Italic|BoldItalic|Regular|MT|BoldMT|Oblique)$", "", f)] += n
    P.update({
        "fonts": c2d(fam, 5),
        "font_raw": c2d(fonts, 8),
        "variants": c2d(variants, 4),
        "latin_main": fam.most_common(1)[0][0] if fam else None,
        "math_font": c2d(math_font, 3),
        "title": title,
        "cover": cover,
        "leadin_sizes": c2d(leadin, 3),
        "levels": levels,
        "spacing_by_size": {str(k): v for k, v in sp_lvl.items()},
        "ratio_hist_top": c2d(ratio_hist, 4),
        "math": {"n_spans": math_n, "sizes": c2d(math_sizes, 4),
                 "colors": c2d(math_colors, 3)},
        "circled": {"n": circled_n, "sizes": c2d(circled_sizes, 2)},
        "stroke": {"total": sw_total, "vec_ops": vec_total,
                   "main_w": main_w, "hist": c2d(stroke_w, 6),
                   "thick_ge2": thick, "thin_lt0.75": thin,
                   "dash_ops": dash_n,
                   "colors": c2d(stroke_colors, 5), "fills": c2d(fill_colors, 5)},
        "fig_ann": {"min_size": fig_ann_min.most_common(1)[0][0] if fig_ann_min else None,
                    "fonts": c2d(fig_ann_font, 2)},
        "table": {"tw_pages": tw_pages, "hline_w": c2d(tw_hline, 4),
                  "fills": c2d(tw_fills, 4)},
        "layout": {"left_margin": median(left_m), "content_bottom": median(cont_b),
                   "img_cov_median": median(img_cov),
                   "footer_band": round(footer_pages / P["pages"], 2),
                   "logo_topleft": round(logo_pages / P["pages"], 2)},
    })
    return P


def render_md(P):
    L = ["### {} — {}页 {}×{}".format(P["file"], P["pages"], P["pw"], P["ph"])]
    var = P["variants"]
    tot = sum(var.values()) or 1
    L.append("- 字体: 西文主字体 **{}**（{}%）; 变体 Bold {}% / Italic {}% / BoldItalic {}%".format(
        P["latin_main"], round(100 * sum(v for k, v in P["fonts"].items()
                                         if k == P["latin_main"]) / tot, 1),
        round(100 * var.get("Bold", 0) / tot), round(100 * var.get("Italic", 0) / tot),
        round(100 * var.get("BoldItalic", 0) / tot)))
    t = P["title"]
    L.append("- 标题: {}pt {} {} 居中{}%".format(
        t["size"], t["font"], t["color"], round(100 * t["centered"]) if t else "-"))
    c = P["cover"]
    L.append("- 封面: 题{} / 会话号{} / 作者{} / 单位{}".format(
        c.get("title_size", "?"), c.get("session_size", "?"),
        c.get("author_size", "?"), c.get("affil_size", "?")))
    lv = P["levels"]
    parts = []
    for k in ("L1", "L2", "L3"):
        if k in lv:
            e = lv[k]
            parts.append("{} {}pt {}{}".format(
                k, e["text_size"], e["glyph"] or "", e["glyph_color"] or ""))
    li = P["leadin_sizes"]
    if li:
        parts.append("Lead-in {}pt".format("/".join(li.keys())))
    L.append("- 层级: " + ("; ".join(parts) if parts else "（无 bullet 正文页）"))
    sp = P["spacing_by_size"]
    L.append("- 行距: " + (" ".join("{}→{}×(n={})".format(k, v["median"], v["n"])
                                   for k, v in sorted(sp.items(), key=lambda kv: -float(kv[0])))
                            if sp else "n/a")
             + "; 全deck直方 " + " ".join("{}×{}%".format(k, round(100 * v / max(sum(P["ratio_hist_top"].values()), 1)))
                                          for k, v in P["ratio_hist_top"].items()))
    m = P["math"]
    if m["n_spans"]:
        L.append("- 公式: 原生 {} spans, 字号Top {}, 色Top {}{}".format(
            m["n_spans"],
            "/".join("{}pt".format(k) for k in list(m["sizes"])[:3]),
            "/".join(list(m["colors"])[:3]),
            "; 圈号n={}".format(P["circled"]["n"]) if P["circled"]["n"] else ""))
    else:
        L.append("- 公式: 无原生数学字体（公式在图内或无公式）" +
                 ("; 圈号n={}".format(P["circled"]["n"]) if P["circled"]["n"] else ""))
    s = P["stroke"]
    if s["total"] >= 20:
        L.append("- 图线: 主体 {}; ≥2pt强调 {}%; <0.75pt细线 {}%; dashed {} op{}".format(
            "{}pt".format(s["main_w"]) if s["main_w"] else "无0.75–3pt描边",
            round(100 * s["thick_ge2"] / s["total"]),
            round(100 * s["thin_lt0.75"] / s["total"]), s["dash_ops"],
            "; 描边Top " + ",".join(list(s["colors"])[:3]) if s["colors"] else ""))
    else:
        L.append("- 图线: 矢量元素少({} op)——图多为位图，线宽不可测（按语料惯例 1.5pt）".format(s["vec_ops"]))
    fa = P["fig_ann"]
    if fa["min_size"]:
        L.append("- 图注: 最小 {}pt（{}）".format(fa["min_size"],
                                               ",".join(list(fa["fonts"])[:2])))
    tb = P["table"]
    L.append("- 表: This-work页 {}; 横线 {}; 填充Top {}".format(
        tb["tw_pages"],
        " ".join("{}pt×{}".format(k, v) for k, v in list(tb["hline_w"].items())[:3]) or "-",
        ",".join(list(tb["fills"])[:3]) or "-"))
    lay = P["layout"]
    L.append("- 版式: 左边距{}pt; 图覆盖中位{}%; 页脚带{}%; 左上logo{}%".format(
        lay["left_margin"], round(100 * (lay["img_cov_median"] or 0)),
        round(100 * lay["footer_band"]), round(100 * lay["logo_topleft"])))
    return "\n".join(L)


def main():
    files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".pdf"))
    profiles, mds = [], []
    for i, fn in enumerate(files):
        try:
            p = profile_deck(os.path.join(SRC, fn))
        except Exception as e:
            p = {"file": fn, "error": str(e)}
        profiles.append(p)
        mds.append(render_md(p) if "error" not in p else "### {} — ERROR {}".format(fn, p["error"]))
        print("[{}/{}] {}".format(i + 1, len(files), fn), flush=True)
    with open(os.path.join(HERE, "perdeck_profiles.json"), "w", encoding="utf-8") as f:
        json.dump({"source": SRC, "n_decks": len(profiles), "decks": profiles},
                  f, ensure_ascii=False, indent=1)
    head = """# RFIC2024 逐 deck 风格档案（87 份，一份一档）

- 逐 PDF 剖析 8 维度：字体族与粗斜变体、标题/封面/层级字号、行距（按字号档中位倍率）、
  图线粗细（描边直方、≥2pt 强调占比、dashed）、公式（Cambria Math 字号/颜色/圈号）、
  图注下限、表格线与填充、版式（边距/图覆盖/页脚带/logo）。
- 方法：PyMuPDF 逐 span + get_drawings 全量扫描（`perdeck_profile.py`），
  口径与 `analyze_corpus.py` / `deep_measure.py` 一致；机读数据 `perdeck_profiles.json`。
- 行距读法：`32→1.44×(n=...)` = 32pt 段内基线倍率中位；n<5 的档不报。
  图线读法：`主体 1.5pt` = 0.75–3pt 描边直方众数（位图 MATLAB 图测不到，按语料惯例 1.5pt）。
- 聚合法典见 `RFIC2024_corpus_constraints.md`；单页深测样例见 `RFIC_RMo01B_constraints.md`。

"""
    with open(os.path.join(HERE, "RFIC2024_perdeck_profiles.md"), "w", encoding="utf-8") as f:
        f.write(head + "\n\n".join(mds) + "\n")
    print("saved perdeck_profiles.json + RFIC2024_perdeck_profiles.md", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
