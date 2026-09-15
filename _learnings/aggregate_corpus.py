# -*- coding: utf-8 -*-
"""Aggregate corpus_stats.json into corpus-wide style statistics."""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "corpus_stats.json"), encoding="utf-8") as f:
    data = json.load(f)

decks = data["decks"]
for d in decks:
    if "error" in d: continue
    d["sizes"] = {float(k): v for k, v in d["sizes"].items()}
    d["titles"] = [{**t, "size": float(t["size"])} for t in d.get("titles", [])]
fonts = Counter()
sizes = Counter()
colors = Counter()
title_size = Counter()
title_color = Counter()
title_font = Counter()
title_centered = Counter()
page_sizes = Counter()
img_cov = []
margins = []
content_bottoms = []
footer_ok = 0
logo_ok = 0
total_pages = 0
table_decks = 0
per_deck = []

for d in decks:
    if "error" in d:
        per_deck.append((d["file"], "ERROR " + d["error"]))
        continue
    total_pages += d["pages"]
    page_sizes["{}x{}".format(d["page_w"], d["page_h"])] += 1
    for k, v in d["fonts"].items():
        fonts[k] += v
    for k, v in d["sizes"].items():
        sizes[k] += v
    for k, v in d["colors"].items():
        colors[k] += v
    img_cov.extend(min(c, 1.0) for c in d["img_cov"])
    margins.extend(d["left_margin"])
    content_bottoms.extend(d["content_bottom"])
    if d["footer_band_pages"] >= d["pages"] * 0.8:
        footer_ok += 1
    if d["top_left_logo_pages"] >= d["pages"] * 0.8:
        logo_ok += 1
    if d["table_pages"] > 0:
        table_decks += 1
    # content-page titles (skip cover)
    ts = d["titles"]
    for t in ts:
        title_size[t["size"]] += 1
        title_color[t["color"]] += 1
        title_font[t["font"]] += 1
        title_centered[t["centered"]] += 1
    dom_font = max(d["fonts"], key=d["fonts"].get) if d["fonts"] else "?"
    tmode_size = ts[0]["size"] if ts else 0
    tmode_col = Counter(t["color"] for t in ts).most_common(1)[0][0] if ts else "?"
    mcov = sum(min(c, 1.0) for c in d["img_cov"]) / max(len(d["img_cov"]), 1)
    per_deck.append((d["file"], "p{} dom={} title={}pt/{} imgcov={:.2f} footer={}/{} logo={}/{} tbl={} lm={} cb={}".format(
        d["pages"], dom_font, tmode_size, tmode_col, mcov,
        d["footer_band_pages"], d["pages"], d["top_left_logo_pages"], d["pages"],
        d["table_pages"],
        min(d["left_margin"]) if d["left_margin"] else -1,
        max(d["content_bottom"]) if d["content_bottom"] else -1)))

out = []
out.append("=== page sizes ===\n" + "\n".join("  {}: {}".format(k, v) for k, v in page_sizes.most_common()))
out.append("=== total pages: {} over {} decks ===".format(total_pages, len(decks)))
out.append("=== fonts (chars) top 20 ===\n" + "\n".join("  {:34s} {:9d}".format(k, v) for k, v in fonts.most_common(20)))
out.append("=== sizes (chars) top 24 ===\n" + "\n".join("  {:5.1f}pt {:9d}".format(k, v) for k, v in sizes.most_common(24)))
out.append("=== colors (chars) top 24 ===\n" + "\n".join("  {} {:9d}".format(k, v) for k, v in colors.most_common(24)))
out.append("=== title size dist ===\n" + "\n".join("  {:5.1f}pt x{}".format(k, v) for k, v in title_size.most_common(10)))
out.append("=== title color dist ===\n" + "\n".join("  {} x{}".format(k, v) for k, v in title_color.most_common(10)))
out.append("=== title font dist ===\n" + "\n".join("  {:34s} x{}".format(k, v) for k, v in title_font.most_common(10)))
out.append("=== title centered: {} T / {} F ===".format(title_centered.get(True, 0), title_centered.get(False, 0)))
img_cov.sort()
n = len(img_cov)
out.append("=== image coverage/page: mean={:.2f} med={:.2f} p10={:.2f} p90={:.2f} (n={}) ===".format(
    sum(img_cov) / n, img_cov[n // 2], img_cov[n // 10], img_cov[9 * n // 10], n))
margins.sort()
out.append("=== text left margin: min={} p10={:.0f} med={:.0f} max={:.0f} ===".format(
    margins[0], margins[n // 10], margins[len(margins) // 2], margins[-1]))
cb = sorted(content_bottoms)
out.append("=== content bottom: med={:.0f} p90={:.0f} max={:.0f} ===".format(cb[len(cb) // 2], cb[9 * len(cb) // 10], cb[-1]))
out.append("=== decks with footer band >=80% pages: {}/{} ; top-left logo >=80%: {}/{} ; decks containing tables: {}/{} ===".format(
    footer_ok, len(decks), logo_ok, len(decks), table_decks, len(decks)))
out.append("=== per deck ===\n" + "\n".join("  {:18s} {}".format(a, b) for a, b in per_deck))

report = "\n".join(out)
with open(os.path.join(HERE, "corpus_report.txt"), "w", encoding="utf-8") as f:
    f.write(report)
print(report[:6000])
print("...full report in corpus_report.txt")
