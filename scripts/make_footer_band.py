# -*- coding: utf-8 -*-
"""make_footer_band.py — 生成 RFIC 风格页脚渐变色带 PNG（纯标准库）。
按语料测量: y502-540 全宽, 青绿→绿渐变 + 顶部黄绿细条。输出 1920x76 (2x 抗糊)。
用法: python make_footer_band.py [输出路径]
"""
import os
import struct
import sys
import zlib

W, H = 1920, 76          # 960x38pt @2x
STRIP = 6                # 顶部黄绿细条 ~3pt
LEFT = (0x19, 0x70, 0x84)   # #197084 青绿
RIGHT = (0x2E, 0x8B, 0x3C)  # 深绿(收尾, 偏语料绿系)
MID = (0x1F, 0x9E, 0x8A)    # 中段青绿过渡
STRIP_C = (0xC5, 0xD4, 0x33)  # 黄绿细条


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def build_png(path):
    rows = []
    for y in range(H):
        row = bytearray()
        row.append(0)  # filter none
        for x in range(W):
            t = x / (W - 1)
            c = lerp(lerp(LEFT, MID, t * 2) if t < 0.5 else lerp(MID, RIGHT, (t - 0.5) * 2),
                     RIGHT, 0.0)
            # 轻微斜向亮度变化, 模拟语料色带的折纸质感
            k = 0.9 + 0.1 * ((x + y * 3) % 160) / 160.0
            c = tuple(min(255, int(v * k)) for v in c)
            if y < STRIP:
                c = STRIP_C
            row += bytes(c)
        rows.append(bytes(row))
    raw = b''.join(rows)

    def chunk(typ, data):
        return (struct.pack('>I', len(data)) + typ + data +
                struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff))
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    png = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    print('wrote %s (%d bytes)' % (path, len(png)))


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'footer_band.png')
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    build_png(out)
