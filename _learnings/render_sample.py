# -*- coding: utf-8 -*-
"""Render stratified sample pages from the RFIC2024 corpus to PNG for visual review."""
import os
import sys
import fitz

SRC = r"D:\wanglei\project\TDA7707_GNSS\E_project\RFIC2024\2024_07_02_RMo01A_1"
OUT = r"D:\wanglei\project\TDA7707_GNSS\E_project\multi_agent_PPT_zcode\_learnings\renders_rmo01a"

# (deck, [page indices]) — filled after stats; below: one representative per session
PLAN = {}


def render(plan):
    os.makedirs(OUT, exist_ok=True)
    for deck, pages in plan.items():
        path = os.path.join(SRC, deck)
        doc = fitz.open(path)
        n = doc.page_count
        for p in pages:
            if p >= n:
                continue
            pix = doc[p].get_pixmap(dpi=96)
            name = "{}_p{:02d}.png".format(os.path.splitext(deck)[0], p + 1)
            pix.save(os.path.join(OUT, name))
            print(name, flush=True)
        doc.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import json
    plan_file = os.path.join(os.path.dirname(__file__), "render_plan.json")
    with open(plan_file, encoding="utf-8") as f:
        plan = json.load(f)
    render(plan)
