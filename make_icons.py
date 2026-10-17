"""產生 PWA 用的 PNG 圖示（與 icons/icon.svg 同一個圖形），不需要第三方套件。

用法：python3 make_icons.py
"""
import math
import struct
import zlib
from pathlib import Path

BG = (0x2F, 0x6B, 0x5A)
CREAM = (0xF6, 0xF3, 0xEC)
WARM = (0xE7, 0x98, 0x68)
# 以 512 為基準的座標；PNG 一律滿版方形，圓角交給系統處理
NODES = [((256, 170), 52, CREAM), ((160, 340), 44, CREAM), ((352, 340), 44, WARM)]
LINES = [((160, 340), (256, 170)), ((256, 170), (352, 340)), ((160, 340), (352, 340))]
STROKE = 11  # 半寬


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def mix(c1, c2, a):
    return tuple(round(c1[i] * (1 - a) + c2[i] * a) for i in range(3))


def render(size, pad=0.0):
    """pad：maskable 圖示的安全邊距比例（圖形縮小置中）。"""
    scale = 512 / (size * (1 - 2 * pad))
    off = 512 * pad / (1 - 2 * pad)
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            px = (x + 0.5) * scale - off
            py = (y + 0.5) * scale - off
            color = BG
            d = min(seg_dist(px, py, a, b) for a, b in LINES)
            color = mix(color, CREAM, max(0.0, min(1.0, (STROKE - d) / scale + 0.5)))
            for (cx, cy), r, c in NODES:
                dd = math.hypot(px - cx, py - cy)
                color = mix(color, c, max(0.0, min(1.0, (r - dd) / scale + 0.5)))
            row += bytes(color)
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


if __name__ == "__main__":
    out = Path(__file__).parent / "icons"
    for name, size, pad in [("icon-192.png", 192, 0.08), ("icon-512.png", 512, 0.08), ("apple-touch-icon.png", 180, 0.0)]:
        (out / name).write_bytes(render(size, pad))
        print("wrote", name)
