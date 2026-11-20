#!/usr/bin/env python3
"""THE WORLD TODAY - front page for Friday 20 November 2026.

Draws one dense broadsheet front page (1024x1024 PNG) summing up the
world news of Friday 20 November 2026. Python 3.13 standard library
only. All text and data are typed by hand in this file; the art is
procedural (shapes, figures, skylines); no network, no downloaded
files, no external fonts. The PNG is encoded by hand with zlib+struct
and the output is fully deterministic: two runs write identical bytes.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font --
# 5x7 bitmap font, hand defined. Each glyph is 7 rows of 5 bits.
# Characters covered: A-Z a-z 0-9 and common punctuation.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01101", "10011", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

# -------------------------------------------------------------- canvas --
PAPER = (248, 244, 234)
INK = (18, 18, 18)
RED = (166, 28, 28)
NAVY = (24, 44, 84)
GRAY = (112, 108, 98)
LIGHT = (232, 228, 218)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) ** 2) * (ry * ry) + ((yy - cy) ** 2) * (rx * rx) <= rx * rx * ry * ry:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if (yy - ay) * (yy - by) <= 0 and ay != by:
                    t = (yy - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)


def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g is None:
            cx += 6 * scale
            continue
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, lines, scale, color, leading=None):
    if leading is None:
        leading = 7 * scale + 2
    for ln in lines:
        draw_text(cv, x, y, ln, scale, color)
        y += leading
    return y


# ------------------------------------------------------------------ png --
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------- drawing helpers --
def lcg(seed):
    """Deterministic pseudo-random stream (no random module needed)."""
    state = [seed & 0x7FFFFFFF]

    def nxt(n):
        state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return state[0] % n

    return nxt


def person(cv, x, base_y, h, shirt, pants, skin=(214, 172, 138), hair=(40, 28, 18)):
    """Simple flat figure standing on base_y, total height h."""
    head_r = max(2, h // 9)
    leg_h = h // 3
    torso_h = h - head_r * 2 - leg_h
    cx = x
    # legs
    cv.rect(cx - head_r, base_y - leg_h, head_r, leg_h, pants)
    cv.rect(cx + 1, base_y - leg_h, head_r, leg_h, pants)
    # torso
    cv.rect(cx - head_r - 1, base_y - leg_h - torso_h, 2 * head_r + 2, torso_h, shirt)
    # arms
    cv.rect(cx - head_r - 3, base_y - leg_h - torso_h + 1, 3, torso_h - 2, shirt)
    cv.rect(cx + head_r + 1, base_y - leg_h - torso_h + 1, 3, torso_h - 2, shirt)
    # head + hair
    cv.circle(cx, base_y - leg_h - torso_h - head_r + 2, head_r, skin)
    cv.rect(cx - head_r, base_y - leg_h - torso_h - head_r * 2 + 2, 2 * head_r, head_r, hair)


def skyline(cv, x, base_y, w, max_h, color, seed, lit=(255, 210, 110)):
    rnd = lcg(seed)
    bx = x
    while bx < x + w - 8:
        bw = 14 + rnd(26)
        bh = max_h // 3 + rnd(max_h * 2 // 3)
        if bx + bw > x + w:
            bw = x + w - bx
        cv.rect(bx, base_y - bh, bw, bh, color)
        # lit windows
        for wy in range(base_y - bh + 4, base_y - 4, 7):
            for wx in range(bx + 3, bx + bw - 3, 7):
                if rnd(3) == 0:
                    cv.rect(wx, wy, 3, 4, lit)
        bx += bw + 2 + rnd(6)


def flag_pole(cv, x, base_y, h, stripes):
    """Small flag on a pole; stripes = list of colors top to bottom."""
    cv.vline(x, base_y - h, h, INK, 2)
    fw = 26
    fh = h // 2
    sh = max(1, fh // len(stripes))
    for i, col in enumerate(stripes):
        cv.rect(x + 2, base_y - h + i * sh, fw, sh, col)
    cv.hline(x + 2, base_y - h, fw, INK, 1)
    cv.hline(x + 2, base_y - h + fh - 1, fw, INK, 1)
    cv.vline(x + 2 + fw - 1, base_y - h, fh, INK, 1)


# ------------------------------------------------------------ hero art ---
def art_court(cv, x, y, w, h):
    """The Hague courtroom: wood wall, bench, robed judges, scales."""
    base = y + h
    cv.rect(x, y, w, h, (44, 58, 86))
    cv.rect(x, base - 30, w, 30, (96, 62, 38))          # wood panelling
    cv.rect(x, base - 30, w, 3, (70, 44, 26))
    # scales of justice, left
    sx = x + 52
    sy = y + 8
    cv.rect(sx - 2, sy, 4, 40, (212, 175, 90))
    cv.hline(sx - 26, sy + 6, 52, (212, 175, 90), 3)
    cv.line(sx - 26, sy + 8, sx - 38, sy + 26, (212, 175, 90), 2)
    cv.line(sx + 26, sy + 8, sx + 38, sy + 26, (212, 175, 90), 2)
    cv.triangle(sx - 46, sy + 26, sx - 30, sy + 26, sx - 38, sy + 38, (212, 175, 90))
    cv.triangle(sx + 30, sy + 26, sx + 46, sy + 26, sx + 38, sy + 38, (212, 175, 90))
    cv.circle(sx, sy - 2, 5, (212, 175, 90))
    # bench
    cv.rect(x + 8, base - 24, w - 16, 24, (120, 78, 46))
    cv.rect(x + 8, base - 24, w - 16, 3, (150, 100, 60))
    # three robed judges behind the bench
    for jx in (x + w - 210, x + w - 130, x + w - 50):
        cv.rect(jx - 20, base - 56, 40, 32, (22, 22, 26))
        cv.rect(jx - 6, base - 56, 12, 10, (240, 240, 240))  # collar
        cv.circle(jx, base - 62, 10, (214, 172, 138))
        cv.rect(jx - 10, base - 72, 20, 5, (200, 200, 200))  # wig
    # flags flanking the bench
    flag_pole(cv, x + 14, base - 24, 46, [(0, 128, 64), (255, 215, 0), (220, 40, 40)])
    flag_pole(cv, x + w - 46, base - 24, 46, [(30, 60, 160), (255, 255, 255), (220, 40, 40)])


def art_summit(cv, x, y, w, h):
    """Shenzhen summit: three leaders at a round table, three flags."""
    base = y + h
    cv.rect(x, y, w, h, (158, 196, 224))
    cv.rect(x, base - 14, w, 14, (120, 84, 50))          # floor
    # flags behind the leaders
    flag_pole(cv, x + 60, y + 44, 40, [(200, 30, 30), (255, 255, 255), (200, 30, 30),
                                       (255, 255, 255), (200, 30, 30), (255, 255, 255), (200, 30, 30)])
    flag_pole(cv, x + w // 2 - 14, y + 44, 40, [(210, 20, 20)])
    flag_pole(cv, x + w - 88, y + 44, 40, [(255, 255, 255), (40, 80, 200), (210, 20, 20)])
    # round table
    cv.ellipse(x + w // 2, base - 18, w // 2 - 30, 12, (96, 62, 38))
    cv.rect(x + w // 2 - 14, base - 12, 28, 12, (70, 44, 26))
    # three seated leaders
    person(cv, x + 110, base - 22, 44, (28, 32, 44), (28, 32, 44), hair=(200, 200, 200))
    person(cv, x + w // 2, base - 22, 44, (20, 24, 36), (20, 24, 36), hair=(20, 20, 20))
    person(cv, x + w - 110, base - 22, 44, (34, 36, 48), (34, 36, 48), hair=(220, 210, 190))
    # handshake above the table centre
    cv.circle(x + w // 2 - 7, base - 36, 5, (214, 172, 138))
    cv.circle(x + w // 2 + 7, base - 36, 5, (226, 190, 158))


def art_gta(cv, x, y, w, h):
    """Vice City sunset: orange sky, sun, skyline, palms, sports car."""
    base = y + h
    bands = [(255, 122, 46), (255, 92, 110), (196, 64, 140), (96, 44, 116)]
    bh = h // 4
    for i, col in enumerate(bands):
        hh = bh if i < 3 else h - 3 * bh
        cv.rect(x, y + i * bh, w, hh, col)
    cv.circle(x + w - 66, y + 18, 12, (255, 236, 160))    # low sun
    skyline(cv, x, base - 14, w, 22, (52, 26, 74), 42)
    # palm trees
    for px in (x + 26, x + 54, x + w - 44):
        cv.line(px, base - 14, px + 3, base - 38, (40, 22, 30), 3)
        for dx, dy in ((-12, -6), (-8, -10), (0, -12), (8, -10), (12, -6)):
            cv.line(px + 3, base - 38, px + 3 + dx, base - 38 + dy, (30, 90, 50), 2)
    # sports car on the road
    cy = base - 8
    cv.rect(x + w // 2 - 52, cy - 10, 104, 10, (220, 30, 60))
    cv.rect(x + w // 2 - 28, cy - 20, 52, 11, (220, 30, 60))
    cv.rect(x + w // 2 - 23, cy - 18, 42, 8, (180, 220, 240))
    cv.circle(x + w // 2 - 34, cy, 7, (16, 16, 16))
    cv.circle(x + w // 2 + 34, cy, 7, (16, 16, 16))
    cv.circle(x + w // 2 - 34, cy, 3, (200, 200, 200))
    cv.circle(x + w // 2 + 34, cy, 3, (200, 200, 200))


def art_riyadh(cv, x, y, w, h):
    """Riyadh at night: twisted PIF tower, missile streak, smoke."""
    cv.rect(x, y, w, h, (12, 18, 44))
    rnd = lcg(7)
    for _ in range(26):
        cv.set(x + rnd(w), y + rnd(h // 2), (255, 255, 255))
    # city base
    skyline(cv, x, y + h, w, h // 4, (26, 34, 66), 99)
    # PIF tower: stacked offset slabs, 8 slabs of 7px
    tx = x + w // 2 - 24
    for i in range(8):
        off = 7 if i % 2 == 0 else -2
        cv.rect(tx + off, y + 2 + i * 7, 48 - abs(off), 7, (70, 130, 190))
        for wx in range(tx + off + 4, tx + off + 42, 9):
            if (i + wx) % 3 == 0:
                cv.rect(wx, y + 4 + i * 7, 4, 4, (255, 220, 120))
    # missile streak and smoke
    cv.line(x + w - 24, y + 4, x + w // 2 + 26, y + 34, (255, 220, 120), 3)
    cv.line(x + w - 24, y + 4, x + w // 2 + 38, y + 42, (255, 120, 40), 2)
    cv.circle(x + w // 2 + 30, y + 38, 8, (255, 160, 60))
    cv.circle(x + w // 2 + 20, y + 24, 10, (120, 120, 128))
    cv.circle(x + w // 2 + 36, y + 18, 7, (150, 150, 158))
    cv.circle(x + w // 2 + 46, y + 28, 6, (120, 120, 128))


def art_markets(cv, x, y, w, h):
    """Falling market chart with candlesticks and a down arrow."""
    cv.rect(x, y, w, h, (255, 255, 255))
    # grid
    for gy in range(y + 8, y + h - 4, 12):
        cv.hline(x + 6, gy, w - 12, (228, 228, 228), 1)
    # candlesticks, descending, kept inside the art area
    rnd = lcg(21)
    n = 9
    cw = (w - 40) // n
    top = y + 8
    for i in range(n):
        cx = x + 20 + i * cw
        ch = 6 + rnd(8)
        col = (200, 40, 40) if i % 5 != 3 else (40, 160, 80)
        cv.rect(cx, top + i * 4, cw - 6, ch, col)
        cv.vline(cx + (cw - 6) // 2, top + i * 4 - 3, ch + 6, col, 1)
    # falling line
    pts = []
    for i in range(n + 1):
        pts.append((x + 16 + i * ((w - 32) // n), y + 12 + i * ((h - 24) // n) + (4 if i % 2 else -3)))
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], (166, 28, 28), 3)
    # big down arrow, bottom right, inside the art area
    ax = x + w - 52
    ay = y + h - 22
    cv.rect(ax - 6, ay - 26, 12, 26, (166, 28, 28))
    cv.triangle(ax - 18, ay, ax + 18, ay, ax, ay + 20, (166, 28, 28))
    # exchange bell, bottom left
    cv.ellipse(x + 34, y + h - 14, 16, 8, (212, 175, 90))
    cv.rect(x + 30, y + h - 24, 8, 6, (212, 175, 90))


def art_kyiv(cv, x, y, w, h):
    """Kyiv under fire: burning skyline, smoke, broken bridge over water."""
    cv.rect(x, y, w, h, (22, 22, 34))
    skyline(cv, x, y + h - 26, w, h // 2 + 8, (8, 8, 12), 55)
    # fires on rooftops
    for fx in (x + 40, x + 96, x + 150):
        cv.triangle(fx - 8, y + h - 34, fx + 8, y + h - 34, fx, y + h - 58, (255, 140, 30))
        cv.triangle(fx - 5, y + h - 34, fx + 5, y + h - 34, fx, y + h - 50, (255, 220, 90))
    # smoke
    cv.circle(x + 60, y + 18, 10, (110, 110, 118))
    cv.circle(x + 76, y + 10, 8, (140, 140, 148))
    cv.circle(x + 130, y + 22, 9, (110, 110, 118))
    # river + broken bridge
    cv.rect(x, y + h - 26, w, 26, (28, 52, 96))
    cv.line(x, y + h - 30, x + w // 2 - 22, y + h - 44, (200, 200, 210), 3)
    cv.line(x + w // 2 + 22, y + h - 44, x + w, y + h - 30, (200, 200, 210), 3)
    cv.line(x + w // 2 - 22, y + h - 44, x + w // 2 - 6, y + h - 26, (255, 140, 30), 3)

# --------------------------------------------------------------- layout --
def hero_panel(cv, x, y, w, h, art, kicker, headline, deck):
    """Hero panel: illustration on top, kicker, headline, deck below."""
    cv.rect(x, y, w, h, (255, 255, 255))
    art_h = h - 122
    art(cv, x + 2, y + 2, w - 4, art_h)
    ty = y + art_h + 8
    draw_text(cv, x + 10, ty, kicker, 1, RED)
    ty += 11
    hl = wrap(headline, w - 20, 3)
    ty = draw_block(cv, x + 10, ty, hl[:2], 3, INK, leading=23)
    ty += 3
    dl = wrap(deck, w - 20, 2)
    draw_block(cv, x + 10, ty, dl[:3], 2, (52, 52, 52), leading=16)
    # border
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)


def hero_panel_small(cv, x, y, w, h, art, kicker, headline, deck):
    """Smaller hero panel (row 2): headline scale 2, deck scale 1."""
    cv.rect(x, y, w, h, (255, 255, 255))
    art_h = h - 92
    art(cv, x + 2, y + 2, w - 4, art_h)
    ty = y + art_h + 7
    draw_text(cv, x + 10, ty, kicker, 1, RED)
    ty += 11
    hl = wrap(headline, w - 20, 2)
    ty = draw_block(cv, x + 10, ty, hl[:2], 2, INK, leading=16)
    ty += 2
    dl = wrap(deck, w - 20, 1)
    draw_block(cv, x + 10, ty, dl[:3], 1, (52, 52, 52), leading=10)
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)


def kyiv_strip(cv, x, y, w, h):
    art_w = 210
    cv.rect(x, y, w, h, (255, 255, 255))
    art_kyiv(cv, x + 2, y + 2, art_w - 4, h - 4)
    tx = x + art_w + 12
    tw = w - art_w - 22
    draw_text(cv, tx, y + 6, "KYIV - UKRAINE", 1, RED)
    hl = wrap("KYIV STRUCK; BRIDGE HIT AGAIN", tw, 3)
    draw_block(cv, tx, y + 16, hl[:1], 3, INK, leading=23)
    deck = ("Russian overnight strikes kill eight in Kyiv, 28 injured across "
            "nine regions; bridges targeted. Ukraine hits the Crimea Bridge "
            "a third time in four days; rail traffic halted.")
    dl = wrap(deck, tw, 2)
    draw_block(cv, tx, y + 40, dl[:3], 2, (52, 52, 52), leading=16)
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)


# ------------------------------------------------------------ story data --
# (headline, deck) for the featured story of each column, then briefs.
COLUMNS = [
    ("WAR & DIPLOMACY",
     ("IRAN WAR: TANKER BURNS AFTER MINE STRIKE",
      "Tanker burns in the Strait of Hormuz after a mine strike; US war "
      "cost $48.3bn. Senate rejects war-powers bid 51-48."),
     ["COP31 DRAFT DROPS FOSSIL-FUEL PHASE-OUT",
      "UK AND EU AGREE YOUTH MOBILITY SCHEME",
      "BUKELE REGISTERS FOR THIRD TERM IN EL SALVADOR",
      "HAITI FORCES KILL 34 SUSPECTED GANG MEMBERS",
      "US AND VENEZUELA SIGN MILITARY COOPERATION DEAL",
      "DENMARK RATIFIES GREENLAND SECURITY DEAL",
      "MONGOLIA'S PRESIDENT KHURELSUKH RESIGNS",
      "BRAZIL RECOGNISES CHIEF RAONI'S ANCESTRAL LAND"]),
    ("ECONOMY, TECH & SCIENCE",
     ("NVIDIA PROBED AS ITS CHIEF EXECUTIVE RESIGNS",
      "California subpoenas Nvidia; chief executive Jensen Huang resigned "
      "over an affair with an alleged spy; 879,000+ AI chips approved "
      "for China."),
     ["IMF WARNS PUBLIC DEBT NEAR 100% OF WORLD GDP",
      "US SENATE PASSES ENERGY PERMITTING OVERHAUL 62-33",
      "ITALY FINES META 805 MILLION EUROS",
      "VOYAGER 1 REACHES ONE LIGHT-DAY FROM EARTH",
      "KENYA DISCHARGES LAST EBOLA PATIENT",
      "CYCLONE AKVAN MAKES LANDFALL IN ODISHA",
      "FAA GROUND STOP STRANDS 1.5 MILLION TRAVELLERS",
      "GOLD -4.2%; BRENT $90.05; BRAZIL SELLS $1BN"]),
    ("SOCIETY, CULTURE & SPORT",
     ("EUROPE'S YOUTH STRIKE IN 25+ COUNTRIES",
      "Young Europeans walk out over living costs and militarisation, in "
      "the largest coordinated youth strike of the year, in 25+ countries."),
     ["MIGRANT BOAT CAPSIZES OFF SENEGAL; FOUR DEAD",
      "SUDAN DRONE STRIKE KILLS 10 AT GOLD MINE",
      "ISRAELI FORCES CROSS YELLOW LINE IN GAZA",
      "IAEA: N. KOREA EXPANDING URANIUM ENRICHMENT",
      "US SANCTIONS COMANCHEROS AND 'NDRANGHETA",
      "WHITE HOUSE FIRES CYBER DIRECTOR CAIRNCROSS",
      "EL NINO: FIJI, TONGA DECLARE DISASTERS",
      "ELLA LANGLEY SWEEPS THE CMA AWARDS"]),
]

TICKER = ("ALSO: Pete Rose pardoned - UN chief race stalls - S. Korea orders "
          "Han retrial - Sanchez admits mistakes - Zimbabwe's 250,000th mine "
          "destroyed")


def draw_column(cv, x, y, w, h, title, featured, briefs):
    draw_text(cv, x, y, title, 2, NAVY)
    cv.hline(x, y + 17, w, RED, 3)
    fy = y + 26
    head, deck = featured
    hl = wrap(head, w, 2)
    fy = draw_block(cv, x, fy, hl[:2], 2, INK, leading=16)
    fy += 3
    dl = wrap(deck, w, 1)
    fy = draw_block(cv, x, fy, dl[:3], 1, (52, 52, 52), leading=10)
    fy += 6
    cv.hline(x, fy, w, LIGHT, 2)
    fy += 8
    for b in briefs:
        cv.rect(x, fy + 3, 7, 7, RED)
        bl = wrap(b, w - 16, 2)
        fy = draw_block(cv, x + 16, fy, bl[:2], 2, INK, leading=16)
        fy += 4


# ----------------------------------------------------------------- main --
def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    draw_text_centered(cv, W // 2, 12, "THE WORLD TODAY", 7, INK)
    cv.hline(16, 70, W - 32, INK, 3)
    cv.rect(16, 78, W - 32, 24, NAVY)
    draw_text(cv, 28, 84, "VOL. I", 1, (255, 255, 255))
    draw_text_centered(cv, W // 2, 80, "FRIDAY 20 NOVEMBER 2026", 3, (255, 255, 255))
    draw_text(cv, W - 28 - text_w("PRICE: FREE", 1), 84, "PRICE: FREE", 1, (255, 255, 255))

    # ---- hero row 1: two large panels ----
    hero_panel(cv, 16, 108, 488, 200, art_court, "THE HAGUE",
               "WORLD COURT RULES MYANMAR COMMITTED GENOCIDE",
               "ICJ rules 9-6: Myanmar committed genocide against the "
               "Rohingya - the first time a state is held responsible.")
    hero_panel(cv, 520, 108, 488, 200, art_summit, "SHENZHEN - APEC",
               "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
               "First three-way summit: ~70 minutes, four points on "
               "nuclear risk, UN reform, energy and ICC jurisdiction.")

    # ---- hero row 2: three panels ----
    hero_panel_small(cv, 16, 316, 320, 150, art_gta, "ENTERTAINMENT",
                     "GTA VI: $2.36 BILLION IN A DAY",
                     "Sensor Tower estimates 24.58m copies sold on day one, "
                     "the biggest entertainment launch ever. Take-Two has "
                     "not released official figures.")
    hero_panel_small(cv, 352, 316, 320, 150, art_riyadh, "RIYADH",
                     "HOUTHI MISSILE HITS RIYADH TOWER",
                     "Missiles hit the financial district, damaging the "
                     "Public Investment Fund tower. No injuries reported; "
                     "another missile and five drones intercepted.")
    hero_panel_small(cv, 688, 316, 320, 150, art_markets, "MARKETS",
                     "MARKETS SLIDE; ANTHROPIC DEBUTS",
                     "S&P 500 falls ~2%, a fifth straight day of losses; "
                     "Nikkei down 4.8%. Anthropic closes ~$97 on its Nasdaq "
                     "debut, 17% above its $83 IPO price.")

    # ---- Kyiv strip ----
    kyiv_strip(cv, 16, 474, 992, 92)

    # ---- more from the day ----
    draw_text_centered(cv, W // 2, 572, "MORE FROM THE DAY", 2, INK)
    cv.hline(16, 590, W - 32, INK, 2)
    col_w = 320
    for i, (title, featured, briefs) in enumerate(COLUMNS):
        draw_column(cv, 16 + i * (col_w + 16), 598, col_w, 380,
                    title, featured, briefs)

    # ---- footer ticker ----
    cv.hline(16, 1000, W - 32, INK, 2)
    draw_text_centered(cv, W // 2, 1008, TICKER, 1, GRAY)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    build()
