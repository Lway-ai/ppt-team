#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recrop_r1.py — locate cap_rx_stage1/stage2/disc windows inside F_receiver_full_r17.png,
re-crop with margins so edge-cut labels are fully included, overwrite assets (bak-r1 made)."""
import os
import numpy as np
from PIL import Image

ROOT = r'D:\wanglei\project\TDA7707_GNSS\E_project'
SRC = os.path.join(ROOT, r'FM\_ppt_run\assets\F_receiver_full_r17.png')
ASSETS = os.path.join(ROOT, r'multi_agent_PPT_zcode\examples\fm_iq_receiver_rmo01a\assets')

S_RGB = Image.open(SRC).convert('RGB')
S = np.asarray(S_RGB.convert('L'), dtype=np.float64)
SH, SW = S.shape
D = 4  # downscale factor for coarse pass


def fft_corr(S, C):
    """Return SSD map of sliding window C over S (same mode) via FFT. Shapes: S (H,W), C (h,w)."""
    H, W = S.shape
    h, w = C.shape
    fs = np.fft.rfft2(S)
    fc = np.fft.rfft2(np.flipud(np.fliplr(C)), s=(H, W))
    corr = np.fft.irfft2(fs * fc, s=(H, W))
    # sum of S^2 over window
    fs2 = np.fft.rfft2(S ** 2)
    fones = np.fft.rfft2(np.flipud(np.fliplr(np.ones((h, w)))), s=(H, W))
    s2sum = np.fft.irfft2(fs2 * fones, s=(H, W))
    ssd = s2sum - 2 * corr + (C ** 2).sum()
    valid = ssd[h - 1:H, w - 1:W]
    return valid


def locate(name):
    C_img = Image.open(os.path.join(ASSETS, name + '.png')).convert('RGB')
    C = np.asarray(C_img.convert('L'), dtype=np.float64)
    ch, cw = C.shape
    # coarse on downscaled
    Sd = S[::D, ::D]
    Cd = C[::D, ::D]
    if Cd.shape[0] < 4 or Cd.shape[1] < 4:
        raise SystemExit('crop too small to downscale: ' + name)
    v = fft_corr(Sd, Cd)
    y0, x0 = np.unravel_index(np.argmin(v), v.shape)
    # refine full-res around coarse hit
    best = (None, 1e18)
    for dy in range(-3 * D, 3 * D + 1):
        for dx in range(-3 * D, 3 * D + 1):
            y, x = y0 * D + dy, x0 * D + dx
            if y < 0 or x < 0 or y + ch > SH or x + cw > SW:
                continue
            win = S[y:y + ch, x:x + cw]
            ssd = ((win - C) ** 2).mean()
            if ssd < best[1]:
                best = ((x, y), ssd)
    (x, y), ssd = best
    print('%s: window x=%d y=%d w=%d h=%d  rms=%.3f' % (name, x, y, cw, ch, ssd ** 0.5))
    return x, y, cw, ch


def recrop(name, x, y, w, h, mx=120, my=60):
    nx = max(0, x - mx)
    ny = max(0, y - my)
    nx2 = min(SW, x + w + mx)
    ny2 = min(SH, y + h + my)
    out = S_RGB.crop((nx, ny, nx2, ny2))
    dst = os.path.join(ASSETS, name + '.png')
    out.save(dst)
    print('%s: new crop (%d,%d)-(%d,%d) size %dx%d ratio %.4f -> %s'
          % (name, nx, ny, nx2, ny2, out.size[0], out.size[1], out.size[0] / out.size[1], dst))
    return out.size


if __name__ == '__main__':
    wins = {}
    for n in ('cap_rx_stage1', 'cap_rx_stage2', 'cap_rx_disc'):
        wins[n] = locate(n)
    for n, (x, y, w, h) in wins.items():
        recrop(n, x, y, w, h)
