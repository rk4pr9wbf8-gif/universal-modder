"""Draw every picture The Veiled Hollows needs, procedurally, with Pillow.

    python make_art.py            # writes into mod/gfx/

Everything here is original art: no game files are read. Textures are written as uncompressed 32-bit DDS
(what HoI4 reads for interface sprites) and flags as 32-bit TGA. Sizes follow the vanilla sprites:
focus icons 95x85, national spirits 64x64, decisions 32x32, event pictures 210x176, leader portraits 156x210,
advisor portraits 65x67, flags 82x52 / 41x26 / 10x7.

The look: bone-white sigils on blood-dark and bruise-purple grounds, fog-choked ridgelines, red eyes.
"""

from __future__ import annotations

import math
import random
import struct
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
GFX = HERE / "mod" / "gfx"
SS = 4  # supersampling factor; every shape is drawn big and shrunk for clean edges

BONE = (226, 216, 190, 255)
BONE_DIM = (160, 150, 128, 255)
BLOOD = (150, 18, 22, 255)
EMBER = (230, 60, 30, 255)
EYE = (255, 40, 30, 255)
VOID = (10, 8, 12, 255)
GROUNDS = {
    "blood": ((70, 6, 10), (12, 3, 5)),
    "bruise": ((52, 22, 66), (10, 5, 16)),
    "moss": ((22, 46, 30), (5, 12, 8)),
    "ash": ((54, 52, 50), (12, 12, 12)),
    "coal": ((40, 30, 22), (8, 6, 5)),
}


# ---------------------------------------------------------------- writers

def save_dds(img: Image.Image, path: Path) -> None:
    """Uncompressed A8R8G8B8 DDS. HoI4 (and every DDS reader) accepts it."""
    img = img.convert("RGBA")
    w, h = img.size
    r, g, b, a = img.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()  # stored as BGRA
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x8  # CAPS|HEIGHT|WIDTH|PIXELFORMAT|PITCH
    header = struct.pack(
        "<4sIIIIIII44sIIIIIIII4sIIII",
        b"DDS ", 124, flags, h, w, w * 4, 0, 1, b"\0" * 44,
        32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000,  # DDPF_RGB|ALPHAPIXELS
        b"\x00\x10\x00\x00", 0, 0, 0, 0,  # DDSCAPS_TEXTURE
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + data)


def save_tga(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGBA").save(path, format="TGA", compression=None)


# ---------------------------------------------------------------- canvases

def gradient(size, top, bottom):
    w, h = size
    im = Image.new("RGBA", size)
    px = im.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(w):
            px[x, y] = c
    return im


def radial(size, inner, outer, center=(0.5, 0.42)):
    w, h = size
    im = Image.new("RGBA", size)
    px = im.load()
    cx, cy = center[0] * w, center[1] * h
    rmax = math.hypot(max(cx, w - cx), max(cy, h - cy))
    for y in range(h):
        for x in range(w):
            t = min(1.0, math.hypot(x - cx, y - cy) / rmax) ** 0.8
            px[x, y] = tuple(int(inner[i] + (outer[i] - inner[i]) * t) for i in range(3)) + (255,)
    return im


def grain(im, amount=14, seed=0):
    rnd = random.Random(seed)
    noise = Image.new("L", im.size)
    noise.putdata([rnd.randint(0, 255) for _ in range(im.size[0] * im.size[1])])
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    dark = Image.new("RGBA", im.size, (0, 0, 0, 255))
    mask = noise.point(lambda v: int(amount * v / 255))
    return Image.composite(dark, im, mask)


def fog(size, seed, density=0.55, color=(200, 200, 205)):
    """Soft drifting fog as an RGBA layer."""
    rnd = random.Random(seed)
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(int(40 * density)):
        x = rnd.uniform(-0.2, 1.2) * w
        y = rnd.uniform(0.35, 1.0) * h
        rw, rh = rnd.uniform(0.15, 0.45) * w, rnd.uniform(0.04, 0.10) * h
        d.ellipse([x - rw, y - rh, x + rw, y + rh], fill=color + (rnd.randint(18, 45),))
    return layer.filter(ImageFilter.GaussianBlur(w / 40))


# ---------------------------------------------------------------- motifs
# Each motif draws into ImageDraw `d` on a square box (x0, y0, size) with colour `c`.

def m_eye(d, x, y, s, c, pupil=EYE):
    d.ellipse([x + s * .08, y + s * .30, x + s * .92, y + s * .70], outline=c, width=int(s * .06))
    d.ellipse([x + s * .36, y + s * .34, x + s * .64, y + s * .66], fill=c)
    d.ellipse([x + s * .44, y + s * .38, x + s * .56, y + s * .62], fill=pupil)


def m_moth(d, x, y, s, c):
    cx = x + s / 2
    for side in (-1, 1):
        d.polygon([(cx, y + s * .38), (cx + side * s * .48, y + s * .12), (cx + side * s * .44, y + s * .52)], fill=c)
        d.polygon([(cx, y + s * .48), (cx + side * s * .36, y + s * .58), (cx + side * s * .18, y + s * .86)], fill=c)
        d.line([(cx, y + s * .30), (cx + side * s * .18, y + s * .08)], fill=c, width=int(s * .03))
    d.ellipse([cx - s * .06, y + s * .28, cx + s * .06, y + s * .82], fill=c)
    for side in (-1, 1):
        d.ellipse([cx + side * s * .24 - s * .05, y + s * .26, cx + side * s * .24 + s * .05, y + s * .36], fill=EYE)


def m_mountain(d, x, y, s, c, fill=None):
    pts = [(x, y + s * .9), (x + s * .28, y + s * .38), (x + s * .42, y + s * .55), (x + s * .62, y + s * .22),
           (x + s, y + s * .9)]
    d.polygon(pts, fill=fill or c)


def m_dome(d, x, y, s, c):
    w = int(s * .05)
    d.arc([x + s * .06, y + s * .14, x + s * .94, y + s * 1.6], 180, 360, fill=c, width=w)
    d.arc([x + s * .2, y + s * .32, x + s * .8, y + s * 1.4], 180, 360, fill=c, width=max(1, w // 2))
    d.line([(x + s * .04, y + s * .87), (x + s * .96, y + s * .87)], fill=c, width=w)
    for i in range(7):
        a = math.pi * (1 + (i + .5) / 7)
        px, py = x + s * .5 + math.cos(a) * s * .44, y + s * .87 + math.sin(a) * s * .73
        d.ellipse([px - s * .025, py - s * .025, px + s * .025, py + s * .025], fill=c)


def m_skull(d, x, y, s, c, eyes=VOID):
    d.ellipse([x + s * .2, y + s * .12, x + s * .8, y + s * .7], fill=c)
    d.rectangle([x + s * .32, y + s * .6, x + s * .68, y + s * .84], fill=c)
    d.ellipse([x + s * .3, y + s * .36, x + s * .46, y + s * .54], fill=eyes)
    d.ellipse([x + s * .54, y + s * .36, x + s * .70, y + s * .54], fill=eyes)
    d.polygon([(x + s * .5, y + s * .56), (x + s * .45, y + s * .66), (x + s * .55, y + s * .66)], fill=VOID)
    for i in range(4):
        tx = x + s * (.36 + i * .085)
        d.line([(tx, y + s * .72), (tx, y + s * .84)], fill=VOID, width=max(1, int(s * .02)))


def m_horned_skull(d, x, y, s, c):
    m_skull(d, x + s * .1, y + s * .18, s * .8, c, eyes=EYE)
    for side in (-1, 1):
        cx = x + s / 2 + side * s * .3
        d.arc([cx - s * .22, y + s * .05, cx + s * .22, y + s * .55], 200 if side < 0 else -20, 340 if side < 0 else 160,
              fill=c, width=int(s * .07))


def m_moon(d, x, y, s, c, bg=VOID):
    d.ellipse([x + s * .15, y + s * .15, x + s * .85, y + s * .85], fill=c)
    d.ellipse([x + s * .32, y + s * .08, x + s * .98, y + s * .74], fill=bg)


def m_full_moon(d, x, y, s, c):
    d.ellipse([x + s * .2, y + s * .1, x + s * .8, y + s * .7], fill=c)


def m_hand(d, x, y, s, c):
    d.rounded_rectangle([x + s * .3, y + s * .45, x + s * .72, y + s * .92], radius=int(s * .08), fill=c)
    for i, (fx, top) in enumerate([(.3, .2), (.41, .1), (.52, .12), (.63, .22)]):
        d.rounded_rectangle([x + s * fx, y + s * top, x + s * (fx + .085), y + s * .55], radius=int(s * .04), fill=c)
    d.polygon([(x + s * .3, y + s * .6), (x + s * .12, y + s * .42), (x + s * .18, y + s * .38), (x + s * .34, y + s * .52)], fill=c)
    m_eye(d, x + s * .36, y + s * .52, s * .3, VOID, pupil=EYE)


def m_footprint(d, x, y, s, c):
    d.ellipse([x + s * .3, y + s * .3, x + s * .7, y + s * .95], fill=c)
    for i, (tx, ty, r) in enumerate([(.28, .2, .07), (.4, .12, .075), (.53, .1, .075), (.65, .15, .065), (.74, .25, .055)]):
        d.ellipse([x + s * (tx - r), y + s * (ty - r), x + s * (tx + r), y + s * (ty + r)], fill=c)


def m_charm(d, x, y, s, c):
    d.line([(x + s * .5, y + s * .02), (x + s * .5, y + s * .2)], fill=c, width=int(s * .03))
    d.polygon([(x + s * .5, y + s * .18), (x + s * .82, y + s * .5), (x + s * .5, y + s * .92), (x + s * .18, y + s * .5)],
              outline=c, width=int(s * .05))
    m_eye(d, x + s * .27, y + s * .3, s * .46, c)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(x + s * .5 + math.cos(r) * s * .45, y + s * .55 + math.sin(r) * s * .45),
                (x + s * .5 + math.cos(r) * s * .48, y + s * .55 + math.sin(r) * s * .48)], fill=c, width=int(s * .03))


def m_flatwoods(d, x, y, s, c):
    # the Flatwoods visitor: spade-shaped hood, glowing face, skirt-like body
    d.polygon([(x + s * .5, y + s * .02), (x + s * .82, y + s * .3), (x + s * .5, y + s * .52), (x + s * .18, y + s * .3)], fill=c)
    d.ellipse([x + s * .36, y + s * .22, x + s * .64, y + s * .44], fill=VOID)
    d.ellipse([x + s * .41, y + s * .28, x + s * .47, y + s * .34], fill=EYE)
    d.ellipse([x + s * .53, y + s * .28, x + s * .59, y + s * .34], fill=EYE)
    d.polygon([(x + s * .36, y + s * .48), (x + s * .64, y + s * .48), (x + s * .8, y + s * .96), (x + s * .2, y + s * .96)], fill=c)
    for side in (-1, 1):
        d.line([(x + s * .5 + side * s * .14, y + s * .58), (x + s * .5 + side * s * .3, y + s * .72)], fill=VOID, width=int(s * .04))


def m_antlers(d, x, y, s, c):
    w = int(s * .05)
    cx = x + s / 2
    for side in (-1, 1):
        base = (cx + side * s * .08, y + s * .62)
        tip = (cx + side * s * .42, y + s * .08)
        d.line([base, tip], fill=c, width=w)
        for t in (.3, .55, .8):
            px, py = base[0] + (tip[0] - base[0]) * t, base[1] + (tip[1] - base[1]) * t
            d.line([(px, py), (px - side * s * .1, py - s * .18)], fill=c, width=w)
    m_skull(d, x + s * .28, y + s * .5, s * .44, c, eyes=EYE)


def m_candles(d, x, y, s, c):
    d.ellipse([x + s * .08, y + s * .55, x + s * .92, y + s * .9], outline=c, width=int(s * .03))
    for i in range(5):
        a = math.radians(90 + i * 72)
        cx, cy = x + s * .5 + math.cos(a) * s * .36, y + s * .72 + math.sin(a) * s * .14
        d.rectangle([cx - s * .03, cy - s * .2, cx + s * .03, cy], fill=c)
        d.ellipse([cx - s * .025, cy - s * .3, cx + s * .025, cy - s * .2], fill=EMBER)


def m_bell(d, x, y, s, c):
    d.polygon([(x + s * .5, y + s * .12), (x + s * .68, y + s * .25), (x + s * .74, y + s * .62), (x + s * .88, y + s * .78),
               (x + s * .12, y + s * .78), (x + s * .26, y + s * .62), (x + s * .32, y + s * .25)], fill=c)
    d.ellipse([x + s * .44, y + s * .78, x + s * .56, y + s * .9], fill=c)
    d.ellipse([x + s * .38, y + s * .36, x + s * .48, y + s * .46], fill=EYE)
    d.ellipse([x + s * .52, y + s * .36, x + s * .62, y + s * .46], fill=EYE)
    for side in (-1, 1):
        d.arc([x + s * (.5 + side * .45) - s * .12, y + s * .3, x + s * (.5 + side * .45) + s * .12, y + s * .7],
              90 if side > 0 else 270, 270 if side > 0 else 450, fill=c, width=int(s * .025))


def m_book(d, x, y, s, c):
    d.polygon([(x + s * .1, y + s * .25), (x + s * .5, y + s * .32), (x + s * .5, y + s * .88), (x + s * .1, y + s * .8)], fill=c)
    d.polygon([(x + s * .9, y + s * .25), (x + s * .5, y + s * .32), (x + s * .5, y + s * .88), (x + s * .9, y + s * .8)], fill=BONE_DIM)
    m_sigil_small(d, x + s * .55, y + s * .4, s * .3, BLOOD)
    d.rectangle([x + s * .2, y + s * .42, x + s * .42, y + s * .45], fill=VOID)
    d.rectangle([x + s * .2, y + s * .52, x + s * .42, y + s * .55], fill=VOID)
    d.rectangle([x + s * .2, y + s * .62, x + s * .38, y + s * .65], fill=VOID)


def m_sigil_small(d, x, y, s, c):
    d.ellipse([x, y, x + s, y + s], outline=c, width=max(1, int(s * .08)))
    pts = [(x + s / 2 + math.cos(math.radians(-90 + i * 144)) * s * .45,
            y + s / 2 + math.sin(math.radians(-90 + i * 144)) * s * .45) for i in range(6)]
    d.line(pts, fill=c, width=max(1, int(s * .06)))


def m_sigil(d, x, y, s, c):
    d.ellipse([x + s * .05, y + s * .05, x + s * .95, y + s * .95], outline=c, width=int(s * .04))
    d.ellipse([x + s * .14, y + s * .14, x + s * .86, y + s * .86], outline=c, width=int(s * .02))
    # seven-pointed star of the hollows
    pts = [(x + s / 2 + math.cos(math.radians(-90 + i * 360 * 3 / 7)) * s * .36,
            y + s / 2 + math.sin(math.radians(-90 + i * 360 * 3 / 7)) * s * .36) for i in range(8)]
    d.line(pts, fill=c, width=int(s * .035))
    rnd = random.Random(int(s))
    for i in range(14):
        a = math.radians(i * 360 / 14)
        r1 = s * .405
        px, py = x + s / 2 + math.cos(a) * r1, y + s / 2 + math.sin(a) * r1
        k = rnd.choice(["|", "v", "o"])
        if k == "|":
            d.line([(px, py - s * .02), (px, py + s * .02)], fill=c, width=max(1, int(s * .015)))
        elif k == "v":
            d.line([(px - s * .015, py - s * .015), (px, py + s * .015), (px + s * .015, py - s * .015)], fill=c, width=max(1, int(s * .012)))
        else:
            d.ellipse([px - s * .012, py - s * .012, px + s * .012, py + s * .012], outline=c)
    d.ellipse([x + s * .45, y + s * .45, x + s * .55, y + s * .55], fill=EYE)


def m_veiled(d, x, y, s, c):
    d.polygon([(x + s * .5, y + s * .05), (x + s * .78, y + s * .3), (x + s * .92, y + s * .95), (x + s * .08, y + s * .95),
               (x + s * .22, y + s * .3)], fill=c)
    d.ellipse([x + s * .34, y + s * .2, x + s * .66, y + s * .5], fill=VOID)
    d.ellipse([x + s * .40, y + s * .32, x + s * .46, y + s * .37], fill=EYE)
    d.ellipse([x + s * .54, y + s * .32, x + s * .60, y + s * .37], fill=EYE)
    for i in range(5):
        lx = x + s * (.2 + i * .15)
        d.line([(lx, y + s * .55), (lx + s * .02, y + s * .95)], fill=BONE_DIM, width=max(1, int(s * .015)))


def m_horns(d, x, y, s, c):
    for side in (-1, 1):
        cx = x + s / 2 + side * s * .18
        pts = []
        for i in range(12):
            t = i / 11
            pts.append((cx + side * math.sin(t * 2.2) * s * .28, y + s * (.75 - t * .68)))
        for i in range(len(pts) - 1):
            d.line([pts[i], pts[i + 1]], fill=c, width=max(1, int(s * (.12 - i * .009))))
    d.ellipse([x + s * .28, y + s * .55, x + s * .72, y + s * .98], fill=c)
    d.polygon([(x + s * .36, y + s * .68), (x + s * .46, y + s * .74), (x + s * .36, y + s * .76)], fill=EYE)
    d.polygon([(x + s * .64, y + s * .68), (x + s * .54, y + s * .74), (x + s * .64, y + s * .76)], fill=EYE)


def m_crown(d, x, y, s, c):
    pts = [(x + s * .12, y + s * .75), (x + s * .12, y + s * .35), (x + s * .3, y + s * .55), (x + s * .5, y + s * .2),
           (x + s * .7, y + s * .55), (x + s * .88, y + s * .35), (x + s * .88, y + s * .75)]
    d.polygon(pts, fill=c)
    for i in range(9):
        tx = x + s * (.1 + i * .1)
        d.polygon([(tx, y + s * .78), (tx + s * .05, y + s * .92), (tx + s * .1, y + s * .78)], fill=BONE_DIM)
    d.ellipse([x + s * .45, y + s * .5, x + s * .55, y + s * .6], fill=EYE)


def m_pickaxe(d, x, y, s, c):
    d.line([(x + s * .25, y + s * .85), (x + s * .7, y + s * .3)], fill=c, width=int(s * .07))
    d.arc([x + s * .4, y + s * .05, x + s * 1.0, y + s * .6], 200, 330, fill=c, width=int(s * .08))
    d.line([(x + s * .15, y + s * .3), (x + s * .5, y + s * .85)], fill=BONE_DIM, width=int(s * .06))
    d.ellipse([x + s * .08, y + s * .22, x + s * .22, y + s * .38], fill=BONE_DIM)
    d.ellipse([x + s * .44, y + s * .8, x + s * .58, y + s * .94], fill=BONE_DIM)


def m_jug(d, x, y, s, c):
    d.ellipse([x + s * .18, y + s * .32, x + s * .82, y + s * .95], fill=c)
    d.rectangle([x + s * .4, y + s * .12, x + s * .6, y + s * .4], fill=c)
    d.arc([x + s * .52, y + s * .2, x + s * .86, y + s * .55], 270, 90, fill=c, width=int(s * .06))
    d.text((x + s * .38, y + s * .5), "XXX", fill=VOID)
    m_skull(d, x + s * .34, y + s * .48, s * .32, VOID, eyes=EYE)


def m_shaft(d, x, y, s, c):
    d.polygon([(x + s * .15, y + s * .95), (x + s * .15, y + s * .35), (x + s * .5, y + s * .12), (x + s * .85, y + s * .35),
               (x + s * .85, y + s * .95)], fill=c)
    d.rectangle([x + s * .3, y + s * .45, x + s * .7, y + s * .95], fill=VOID)
    for ex in (.42, .58):
        d.ellipse([x + s * (ex - .03), y + s * .62, x + s * (ex + .03), y + s * .68], fill=EYE)


def m_chimney(d, x, y, s, c):
    d.rectangle([x + s * .1, y + s * .55, x + s * .9, y + s * .95], fill=c)
    for cx in (.22, .45, .68):
        d.rectangle([x + s * cx, y + s * .18, x + s * (cx + .1), y + s * .6], fill=c)
    for cx in (.27, .5, .73):
        for k in range(3):
            r = s * (.05 + k * .03)
            d.ellipse([x + s * cx - r, y + s * (.12 - k * .05) - r, x + s * cx + r, y + s * (.12 - k * .05) + r],
                      fill=(90, 80, 80, 200))
    m_skull(d, x + s * .36, y + s * .58, s * .3, VOID, eyes=EMBER)


def m_dam(d, x, y, s, c):
    d.polygon([(x + s * .05, y + s * .3), (x + s * .95, y + s * .3), (x + s * .8, y + s * .9), (x + s * .2, y + s * .9)], fill=c)
    for i in range(4):
        gx = x + s * (.28 + i * .14)
        d.rectangle([gx, y + s * .45, gx + s * .07, y + s * .88], fill=VOID)
    d.rectangle([x + s * .05, y + s * .2, x + s * .95, y + s * .3], fill=BLOOD)


def m_flask(d, x, y, s, c):
    d.polygon([(x + s * .4, y + s * .1), (x + s * .6, y + s * .1), (x + s * .6, y + s * .4), (x + s * .88, y + s * .92),
               (x + s * .12, y + s * .92), (x + s * .4, y + s * .4)], outline=c, width=int(s * .05))
    d.polygon([(x + s * .3, y + s * .6), (x + s * .7, y + s * .6), (x + s * .84, y + s * .89), (x + s * .16, y + s * .89)], fill=BLOOD)
    m_eye(d, x + s * .32, y + s * .6, s * .36, c)


def m_flame(d, x, y, s, c):
    pts = []
    for i in range(40):
        t = i / 39 * 2 * math.pi
        r = .3 + .08 * math.sin(t * 5)
        px = x + s * .5 + math.sin(t) * s * r
        py = y + s * .62 - math.cos(t) * s * r * 1.4 * (1 if math.cos(t) > 0 else .7)
        pts.append((px, py))
    d.polygon(pts, fill=EMBER)
    d.polygon([(x + s * .5, y + s * .15), (x + s * .68, y + s * .6), (x + s * .5, y + s * .9), (x + s * .32, y + s * .6)], fill=c)
    m_skull(d, x + s * .37, y + s * .52, s * .26, VOID, eyes=EMBER)


def m_stones(d, x, y, s, c):
    for i, (sx, h) in enumerate([(.08, .5), (.3, .7), (.54, .62), (.76, .48)]):
        d.polygon([(x + s * sx, y + s * .9), (x + s * (sx + .02), y + s * (.9 - h)), (x + s * (sx + .16), y + s * (.88 - h)),
                   (x + s * (sx + .18), y + s * .9)], fill=c)
        m_sigil_small(d, x + s * (sx + .04), y + s * (.94 - h * .7), s * .1, BLOOD)
    d.line([(x, y + s * .92), (x + s, y + s * .92)], fill=c, width=int(s * .04))


def m_drop(d, x, y, s, c):
    d.polygon([(x + s * .5, y + s * .06), (x + s * .74, y + s * .52), (x + s * .26, y + s * .52)], fill=c)
    d.ellipse([x + s * .25, y + s * .36, x + s * .75, y + s * .9], fill=c)


def m_lock(d, x, y, s, c):
    d.arc([x + s * .28, y + s * .08, x + s * .72, y + s * .6], 180, 360, fill=c, width=int(s * .09))
    d.line([(x + s * .3, y + s * .34), (x + s * .3, y + s * .5)], fill=c, width=int(s * .09))
    d.line([(x + s * .7, y + s * .34), (x + s * .7, y + s * .5)], fill=c, width=int(s * .09))
    d.rounded_rectangle([x + s * .18, y + s * .45, x + s * .82, y + s * .92], radius=int(s * .06), fill=c)
    m_eye(d, x + s * .3, y + s * .54, s * .4, VOID, pupil=EYE)


def m_mouth(d, x, y, s, c):
    d.chord([x + s * .1, y + s * .25, x + s * .9, y + s * .8], 0, 180, fill=c)
    d.chord([x + s * .1, y + s * .2, x + s * .9, y + s * .65], 180, 360, fill=c)
    d.ellipse([x + s * .2, y + s * .38, x + s * .8, y + s * .62], fill=VOID)
    for i in range(7):
        tx = x + s * (.24 + i * .08)
        d.polygon([(tx, y + s * .4), (tx + s * .04, y + s * .5), (tx + s * .08, y + s * .4)], fill=BONE)
        d.polygon([(tx, y + s * .6), (tx + s * .04, y + s * .5), (tx + s * .08, y + s * .6)], fill=BONE)


def m_torn(d, x, y, s, c):
    m_dome(d, x, y, s, c)
    d.polygon([(x + s * .42, y + s * .1), (x + s * .58, y + s * .1), (x + s * .52, y + s * .4), (x + s * .62, y + s * .55),
               (x + s * .48, y + s * .9), (x + s * .5, y + s * .55), (x + s * .4, y + s * .42)], fill=VOID)
    m_hand(d, x + s * .3, y + s * .3, s * .4, c)


def m_arrow(d, x, y, s, c):
    d.line([(x + s * .1, y + s * .9), (x + s * .85, y + s * .15)], fill=EMBER, width=int(s * .07))
    d.polygon([(x + s * .95, y + s * .05), (x + s * .62, y + s * .14), (x + s * .86, y + s * .38)], fill=EMBER)


def m_wolf(d, x, y, s, c):
    # a shaggy grassman / woodbooger head
    d.ellipse([x + s * .18, y + s * .18, x + s * .82, y + s * .9], fill=c)
    for i in range(9):
        a = math.radians(200 + i * 17.5)
        d.polygon([(x + s * .5 + math.cos(a) * s * .28, y + s * .5 + math.sin(a) * s * .3),
                   (x + s * .5 + math.cos(a + .1) * s * .44, y + s * .5 + math.sin(a + .1) * s * .44),
                   (x + s * .5 + math.cos(a + .2) * s * .28, y + s * .5 + math.sin(a + .2) * s * .3)], fill=c)
    d.rectangle([x + s * .3, y + s * .4, x + s * .7, y + s * .48], fill=VOID)
    d.ellipse([x + s * .34, y + s * .41, x + s * .42, y + s * .47], fill=EYE)
    d.ellipse([x + s * .58, y + s * .41, x + s * .66, y + s * .47], fill=EYE)
    d.ellipse([x + s * .36, y + s * .6, x + s * .64, y + s * .8], fill=VOID)
    for i in range(5):  # fangs
        tx = x + s * (.39 + i * .046)
        d.polygon([(tx, y + s * .6), (tx + s * .023, y + s * .7), (tx + s * .046, y + s * .6)], fill=c)


def m_bones(d, x, y, s, c):
    for a, b in (((.15, .15), (.85, .85)), ((.85, .15), (.15, .85))):
        d.line([(x + s * a[0], y + s * a[1]), (x + s * b[0], y + s * b[1])], fill=c, width=int(s * .1))
        for p in (a, b):
            for off in (-.05, .05):
                d.ellipse([x + s * (p[0] + off) - s * .06, y + s * (p[1] - off) - s * .06,
                           x + s * (p[0] + off) + s * .06, y + s * (p[1] - off) + s * .06], fill=c)
    m_skull(d, x + s * .3, y + s * .26, s * .4, c, eyes=EYE)


MOTIFS = {k[2:]: v for k, v in globals().items() if k.startswith("m_")}


def draw_motif(img, name, box, color=BONE, glow=True):
    """Draw motif `name` into img at box=(x, y, size) with a faint red glow behind it."""
    x, y, s = box
    big = Image.new("RGBA", (img.size[0] * SS, img.size[1] * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    MOTIFS[name](d, x * SS, y * SS, s * SS, color)
    layer = big.resize(img.size, Image.LANCZOS)
    if glow:
        alpha = layer.split()[3].filter(ImageFilter.GaussianBlur(max(1.5, s / 18)))
        halo = Image.new("RGBA", img.size, (190, 20, 20, 0))
        halo.putalpha(alpha.point(lambda v: int(v * .7)))
        img.alpha_composite(halo)
    img.alpha_composite(layer)
    return img


# ---------------------------------------------------------------- composed pictures

def shield_mask(size):
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    W, H = w * SS, h * SS
    d.polygon([(W * .14, H * .06), (W * .86, H * .06), (W * .9, H * .55), (W * .5, H * .97), (W * .1, H * .55)], fill=255)
    return m.resize(size, Image.LANCZOS)


def focus_icon(motifs, ground, seed):
    size = (95, 85)
    top, bottom = GROUNDS[ground]
    bg = grain(radial(size, top, bottom), 20, seed)
    bg.alpha_composite(fog(size, seed, .4, (150, 150, 160)))
    for i, (name, box) in enumerate(motifs):
        draw_motif(bg, name, box)
    mask = shield_mask(size)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    # bone rim
    rim = Image.new("RGBA", (size[0] * SS, size[1] * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(rim)
    W, H = size[0] * SS, size[1] * SS
    d.polygon([(W * .14, H * .06), (W * .86, H * .06), (W * .9, H * .55), (W * .5, H * .97), (W * .1, H * .55)],
              outline=BONE_DIM, width=int(SS * 1.6))
    out.alpha_composite(rim.resize(size, Image.LANCZOS))
    return out


def square_icon(size, motif, ground, seed, round_frame=True):
    top, bottom = GROUNDS[ground]
    bg = grain(radial(size, top, bottom), 18, seed)
    s = min(size) * .8
    draw_motif(bg, motif, ((size[0] - s) / 2, (size[1] - s) / 2, s))
    mask = Image.new("L", (size[0] * SS, size[1] * SS), 0)
    d = ImageDraw.Draw(mask)
    if round_frame:
        d.rounded_rectangle([SS * 2, SS * 2, size[0] * SS - SS * 2, size[1] * SS - SS * 2], radius=SS * 6, fill=255)
    else:
        d.rectangle([0, 0, size[0] * SS, size[1] * SS], fill=255)
    mask = mask.resize(size, Image.LANCZOS)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    return out


def ridge_line(d, w, h, base, amp, seed, color):
    rnd = random.Random(seed)
    pts = [(0, h)]
    y = base
    for x in range(0, w + 8, 8):
        y += rnd.uniform(-amp, amp)
        y = min(max(y, base - amp * 4), base + amp * 3)
        pts.append((x, y))
    pts.append((w, h))
    d.polygon(pts, fill=color)


def pines(d, w, base, seed, color, n=40, hmax=60):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(0, w)
        hh = rnd.uniform(.4, 1) * hmax
        d.polygon([(x, base - hh), (x - hh * .22, base), (x + hh * .22, base)], fill=color)


def landscape(size, seed, sky=((40, 8, 14), (6, 4, 8)), moon=True, eyes=0, figure=None):
    """Fog-drowned Appalachian ridges at night. figure = motif drawn as a silhouette in the middle."""
    w, h = size
    S = SS
    img = gradient((w * S, h * S), sky[0], sky[1])
    d = ImageDraw.Draw(img)
    if moon:
        mx, my, mr = w * S * .76, h * S * .2, w * S * .07
        d.ellipse([mx - mr * 2.4, my - mr * 2.4, mx + mr * 2.4, my + mr * 2.4], fill=(120, 30, 30, 255))
        img = img.filter(ImageFilter.GaussianBlur(S * 6))
        d = ImageDraw.Draw(img)
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(232, 205, 180, 255))
    for i, (base, col) in enumerate([(.5, (34, 20, 30)), (.6, (22, 12, 20)), (.72, (12, 6, 10))]):
        ridge_line(d, w * S, h * S, h * S * base, h * S * .025, seed + i, col + (255,))
        img.alpha_composite(fog((w * S, h * S), seed + 10 + i, .5, (170, 160, 170)))
        d = ImageDraw.Draw(img)
    pines(d, w * S, h * S * .9, seed, (4, 3, 4, 255), n=60, hmax=h * S * .3)
    if figure:
        fs = h * S * .55
        MOTIFS[figure](d, w * S * .5 - fs / 2, h * S * .3, fs, (6, 4, 6, 255))
    rnd = random.Random(seed)
    for _ in range(eyes):
        ex, ey = rnd.uniform(.08, .92) * w * S, rnd.uniform(.7, .92) * h * S
        r = S * rnd.uniform(.8, 1.3)
        d.ellipse([ex - r * 2.2 - r, ey - r, ex - r * 2.2 + r, ey + r], fill=EYE)
        d.ellipse([ex + r * 2.2 - r, ey - r, ex + r * 2.2 + r, ey + r], fill=EYE)
    img.alpha_composite(fog((w * S, h * S), seed + 99, .7, (190, 185, 195)))
    out = img.resize(size, Image.LANCZOS)
    # vignette
    vig = radial(size, (0, 0, 0), (0, 0, 0))
    mask = Image.new("L", size, 0)
    px = mask.load()
    for y in range(size[1]):
        for x in range(size[0]):
            dx, dy = (x / size[0] - .5) * 2, (y / size[1] - .5) * 2
            px[x, y] = int(min(255, max(0, (dx * dx + dy * dy - .45) * 200)))
    out = Image.composite(vig, out, mask)
    return grain(out, 22, seed)


def portrait(seed, hood=True, eye_color=EYE, ground=((40, 16, 30), (6, 4, 8)), size=(156, 210), extra=None):
    w, h = size
    S = SS
    img = gradient((w * S, h * S), *ground)
    img.alpha_composite(fog((w * S, h * S), seed, .6, (150, 140, 150)))
    d = ImageDraw.Draw(img)
    W, H = w * S, h * S
    # shoulders and coat
    d.polygon([(W * .02, H), (W * .12, H * .72), (W * .35, H * .62), (W * .65, H * .62), (W * .88, H * .72), (W * .98, H)],
              fill=(14, 10, 12, 255))
    if hood:
        d.polygon([(W * .5, H * .1), (W * .8, H * .3), (W * .82, H * .7), (W * .18, H * .7), (W * .2, H * .3)], fill=(20, 14, 18, 255))
        d.ellipse([W * .3, H * .26, W * .7, H * .62], fill=(4, 3, 4, 255))
        face_y = H * .42
    else:
        d.ellipse([W * .32, H * .2, W * .68, H * .6], fill=(30, 24, 26, 255))
        d.rectangle([W * .28, H * .16, W * .72, H * .24], fill=(16, 12, 14, 255))  # hat brim
        d.rectangle([W * .36, H * .04, W * .64, H * .18], fill=(16, 12, 14, 255))  # stovepipe hat
        face_y = H * .38
    for ex in (.42, .58):
        r = W * .022
        d.ellipse([W * ex - r * 3, face_y - r * 3, W * ex + r * 3, face_y + r * 3], fill=eye_color[:3] + (60,))
        d.ellipse([W * ex - r, face_y - r, W * ex + r, face_y + r], fill=eye_color)
    if extra:
        MOTIFS[extra](d, W * .36, H * .74, W * .28, BONE_DIM)
    img = img.resize(size, Image.LANCZOS)
    img.alpha_composite(fog(size, seed + 5, .35, (160, 150, 160)))
    return grain(img, 22, seed)


def flag(size):
    w, h = size
    S = 8
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (34, 16, 40, 255))
    d = ImageDraw.Draw(img)
    # three bands: night, a blood stripe, coal black
    d.rectangle([0, H * .78, W, H], fill=(14, 10, 12, 255))
    d.rectangle([0, H * .72, W, H * .78], fill=BLOOD)
    # ridgeline
    d.polygon([(0, H * .72), (W * .18, H * .46), (W * .3, H * .58), (W * .5, H * .36), (W * .7, H * .58), (W * .82, H * .48),
               (W, H * .72)], fill=(14, 10, 12, 255))
    # the veil: a pale ring over the mountains with the moth inside
    d.ellipse([W * .5 - H * .34, H * .06, W * .5 + H * .34, H * .74], outline=BONE, width=int(S * 2.2 * w / 82))
    MOTIFS["moth"](d, W * .5 - H * .24, H * .14, H * .48, BONE)
    return img.resize(size, Image.LANCZOS)


# ---------------------------------------------------------------- the catalogue

FOCUS = {
    # id suffix: (ground, [(motif, (x, y, size)), ...])
    "the_severance": ("bruise", [("dome", (17, 6, 61)), ("eye", (35, 36, 26))]),
    "feed_the_veil": ("blood", [("dome", (17, 4, 61)), ("drop", (36, 34, 24))]),
    "wardstones": ("bruise", [("stones", (16, 12, 63))]),
    "hollow_mist": ("ash", [("eye", (20, 12, 55))]),
    "seal_the_passes": ("bruise", [("mountain", (15, 22, 65)), ("lock", (34, 28, 28))]),
    "whispers_in_the_fog": ("ash", [("mouth", (18, 12, 59))]),
    "eternal_veil": ("bruise", [("dome", (12, 2, 71)), ("sigil", (32, 32, 31))]),
    "part_the_veil": ("blood", [("torn", (14, 4, 67))]),
    "beyond_the_ridges": ("moss", [("mountain", (12, 18, 66)), ("arrow", (40, 8, 38))]),
    "the_night_march": ("blood", [("moon", (46, 6, 26)), ("skull", (18, 18, 50))]),
    "the_mountains_remember": ("moss", [("mountain", (12, 20, 70)), ("eye", (30, 34, 34))]),
    "a_shadow_over_america": ("blood", [("eye", (14, 8, 66)), ("moth", (31, 40, 32))]),
    "call_of_the_hollows": ("moss", [("hand", (18, 8, 58))]),
    "the_mothman_compact": ("bruise", [("moth", (14, 8, 66))]),
    "wake_the_woodboogers": ("moss", [("wolf", (16, 8, 62))]),
    "binding_charm_forges": ("coal", [("charm", (18, 6, 58))]),
    "sheepsquatch_herds": ("ash", [("horned_skull", (16, 6, 62))]),
    "the_flatwoods_visitors": ("moss", [("flatwoods", (20, 8, 56))]),
    "children_of_the_night": ("bruise", [("moon", (28, 4, 40)), ("eye", (18, 34, 58))]),
    "the_wild_hunt": ("blood", [("antlers", (14, 4, 66))]),
    "convene_the_coven": ("bruise", [("candles", (16, 10, 62))]),
    "granny_witch_healers": ("moss", [("veiled", (20, 8, 56))]),
    "the_bell_witch": ("ash", [("bell", (18, 8, 58))]),
    "the_dark_sermons": ("blood", [("book", (18, 8, 58))]),
    "rites_of_the_black_mountain": ("blood", [("sigil", (18, 6, 59))]),
    "the_matriarch": ("bruise", [("veiled", (20, 6, 56))]),
    "bargain_with_old_scratch": ("blood", [("horns", (18, 6, 58))]),
    "the_hollow_crown": ("bruise", [("crown", (18, 10, 58))]),
    "coal_and_bone": ("coal", [("pickaxe", (18, 10, 58))]),
    "moonshine_economy": ("coal", [("jug", (20, 10, 54))]),
    "the_deep_mines": ("coal", [("shaft", (18, 8, 58))]),
    "bone_foundries": ("coal", [("chimney", (16, 8, 62))]),
    "valley_of_dams": ("moss", [("dam", (16, 12, 62))]),
    "the_hollow_laboratories": ("bruise", [("flask", (20, 8, 56))]),
    "the_black_furnace": ("coal", [("flame", (18, 6, 58))]),
    # spreading the Veil
    "the_creeping_fog": ("ash", [("dome", (17, 4, 61)), ("arrow", (44, 30, 28))]),
    "the_fog_rolls_east": ("bruise", [("mountain", (12, 24, 66)), ("dome", (25, 2, 44))]),
    "fog_without_end": ("ash", [("dome", (10, 0, 75)), ("eye", (30, 34, 35))]),
    # the Midnight Pact
    "the_midnight_pact": ("bruise", [("candles", (16, 26, 62)), ("full_moon", (34, 4, 28))]),
    "la_llorona": ("moss", [("veiled", (20, 8, 56))]),
    "the_banshee_wails": ("ash", [("mouth", (18, 12, 59))]),
    "strigoi": ("blood", [("skull", (18, 8, 58)), ("moon", (52, 6, 22))]),
    "the_draugr_wake": ("ash", [("skull", (18, 8, 58))]),
    "the_migoi_descend": ("ash", [("footprint", (20, 8, 56))]),
    "the_mapinguari_stirs": ("moss", [("wolf", (16, 8, 62))]),
    "a_world_of_nightmares": ("blood", [("sigil", (18, 6, 59))]),
    "the_veil_shelters_the_pact": ("bruise", [("dome", (12, 2, 71)), ("candles", (24, 34, 46))]),
}

IDEAS = {
    "the_veil": ("dome", "bruise"),
    "blood_price": ("drop", "blood"),
    "blood_price_eased": ("drop", "moss"),
    "hollow_folk": ("eye", "ash"),
    "hollow_mist_spirit": ("eye", "ash"),
    "children_of_the_night_spirit": ("moon", "bruise"),
    "the_wild_hunt_spirit": ("antlers", "blood"),
    "moonshine_economy_spirit": ("jug", "coal"),
    "old_scratch_bargain": ("horns", "blood"),
    "the_black_furnace_spirit": ("flame", "coal"),
    "the_eternal_veil": ("sigil", "bruise"),
    "veil_parted": ("torn", "blood"),
    "blood_moon": ("full_moon", "blood"),
    "mist_rite": ("eye", "ash"),
    "black_mountain_curse": ("skull", "blood"),
    "fog_madness": ("mouth", "ash"),
    "bell_witch_torment": ("bell", "ash"),
    "veil_shattered": ("torn", "ash"),
    "the_matriarch_spirit": ("veiled", "moss"),
    "awakened_folklore": ("book", "bruise"),
    "black_library": ("book", "blood"),
    "cheat_god": ("crown", "blood"),
}

DECISIONS = {
    "blood_tithe": ("drop", "blood"),
    "bury_the_bones": ("bones", "coal"),
    "blood_moon": ("full_moon", "blood"),
    "hollow_mist": ("eye", "ash"),
    "curse": ("skull", "blood"),
    "raise_the_dead": ("hand", "moss"),
    "lantern": ("eye", "ash"),
    "creeping_fog": ("dome", "ash"),
    "council": ("candles", "bruise"),
    "treasury": ("jug", "coal"),
    "charms": ("charm", "coal"),
    "library": ("book", "bruise"),
    "cold_war": ("eye", "blood"),
    "cheat": ("crown", "ash"),
}
DECISION_CATEGORY_IMAGE = "sigil"

UNITS = {
    "hollow_revenants": "skull",
    "mothman_flock": "moth",
    "woodbooger_brutes": "wolf",
    "sheepsquatch_packs": "horned_skull",
    "flatwoods_sentinels": "flatwoods",
    "granny_witches": "veiled",
}

EVENTS = {
    "fog": dict(seed=3, eyes=6),
    "severance": dict(seed=11, figure="dome", eyes=4),
    "mothman": dict(seed=21, figure="moth"),
    "mine": dict(seed=31, figure="shaft", sky=((18, 14, 12), (4, 3, 3)), moon=False),
    "not_deer": dict(seed=41, figure="antlers", eyes=2),
    "witch": dict(seed=51, figure="veiled", sky=((20, 34, 24), (4, 6, 5))),
    "ritual": dict(seed=61, figure="sigil", sky=((60, 6, 10), (8, 2, 4))),
    "veil_falls": dict(seed=71, figure="torn", sky=((30, 30, 40), (6, 6, 8)), eyes=10),
    "flatwoods": dict(seed=81, figure="flatwoods", eyes=0),
    "tailypo": dict(seed=91, figure="wolf", eyes=3),
}


def main() -> None:
    goals = GFX / "interface" / "goals"
    for i, (key, (ground, motifs)) in enumerate(FOCUS.items()):
        save_dds(focus_icon(motifs, ground, i), goals / f"APL_{key}.dds")
    for i, (key, (motif, ground)) in enumerate(IDEAS.items()):
        save_dds(square_icon((64, 64), motif, ground, 100 + i), GFX / "interface" / "ideas" / f"APL_{key}.dds")
    for i, (key, (motif, ground)) in enumerate(DECISIONS.items()):
        save_dds(square_icon((32, 32), motif, ground, 200 + i), GFX / "interface" / "decisions" / f"APL_{key}.dds")
    cat = landscape((545, 102), 7, figure=None, eyes=8)
    draw_motif(cat, DECISION_CATEGORY_IMAGE, (230, 8, 86))
    save_dds(cat, GFX / "interface" / "decisions" / "APL_rites_category.dds")
    lantern = landscape((545, 102), 8, sky=((30, 30, 40), (6, 6, 8)), eyes=0)
    draw_motif(lantern, "dome", (220, 4, 100))
    save_dds(lantern, GFX / "interface" / "decisions" / "APL_lantern_category.dds")
    council = landscape((545, 102), 9, sky=((40, 16, 50), (6, 4, 8)), eyes=6)
    draw_motif(council, "candles", (220, 6, 96))
    save_dds(council, GFX / "interface" / "decisions" / "APL_council_category.dds")
    cheats = landscape((545, 102), 10, sky=((70, 50, 10), (8, 6, 2)), eyes=0)
    draw_motif(cheats, "crown", (225, 6, 92))
    save_dds(cheats, GFX / "interface" / "decisions" / "APL_cheats_category.dds")
    # balance-of-power side emblems
    save_dds(square_icon((80, 80), "sigil", "blood", 500), GFX / "interface" / "bop" / "APL_coven_side.dds")
    save_dds(square_icon((80, 80), "pickaxe", "coal", 501), GFX / "interface" / "bop" / "APL_assembly_side.dds")
    for i, (key, motif) in enumerate(UNITS.items()):
        save_dds(square_icon((40, 40), motif, "ash", 300 + i, round_frame=False), GFX / "interface" / "units" / f"APL_{key}.dds")
    for key in ("binding_charms", "binding_charms_1", "binding_charms_2"):
        big = square_icon((120, 64), "charm", "coal", 400, round_frame=True)
        save_dds(big, GFX / "interface" / "equipment" / f"APL_{key}_medium.dds")
        save_dds(square_icon((32, 32), "charm", "coal", 401), GFX / "interface" / "equipment" / f"APL_{key}_small.dds")
    for key, kw in EVENTS.items():
        save_dds(landscape((210, 176), **kw), GFX / "event_pictures" / f"APL_{key}.dds")
    leaders = GFX / "leaders" / "APL"
    save_dds(portrait(1, hood=False, extra="moth"), leaders / "APL_silas_blackwood.dds")
    save_dds(portrait(2, hood=True, eye_color=(170, 230, 160, 255), ground=((20, 34, 24), (4, 6, 5)), extra="candles"),
             leaders / "APL_maw_hettie_crane.dds")
    save_dds(portrait(2, hood=True, eye_color=(170, 230, 160, 255), ground=((20, 34, 24), (4, 6, 5)), size=(65, 67)),
             leaders / "APL_maw_hettie_crane_small.dds")
    save_dds(portrait(3, hood=False, ground=((44, 30, 20), (6, 4, 3))), leaders / "APL_jeremiah_coalbrook.dds")
    save_dds(portrait(4, hood=True, eye_color=(220, 220, 255, 255), ground=((30, 30, 40), (6, 6, 8)), extra="skull"),
             leaders / "APL_the_pale_lieutenant.dds")
    for key, kw in {
        "APL_big_john_kessler": dict(seed=5, hood=False, ground=((50, 36, 20), (8, 6, 3)), extra="pickaxe"),
        "APL_reverend_ezra_pike": dict(seed=6, hood=False, ground=((40, 10, 14), (6, 2, 3)), extra="book"),
        "APL_dr_lucille_varner": dict(seed=7, hood=True, eye_color=(140, 255, 120, 255),
                                      ground=((20, 30, 40), (3, 5, 7)), extra="flask"),
    }.items():
        save_dds(portrait(**kw), leaders / f"{key}.dds")
        small = {k: v for k, v in kw.items() if k != "extra"}
        save_dds(portrait(size=(65, 67), **small), leaders / f"{key}_small.dds")
    for path, size in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
        save_tga(flag(size), GFX / "flags" / f"{path}APL.tga")
    # previews for the README / Steam Workshop thumbnail (not loaded by the game)
    thumb = landscape((512, 512), 5, figure="moth", eyes=12)
    thumb.convert("RGB").save(HERE / "mod" / "thumbnail.png")
    write_gfx()
    print("art written to", GFX)


def write_gfx() -> None:
    """interface/APL.gfx and APL_goals_shine.gfx: one spriteType per texture written above."""
    mod = HERE / "mod"

    def sprite(name, tex, extra=""):
        return f'\tspriteType = {{\n\t\tname = "{name}"\n\t\ttexturefile = "{tex}"\n{extra}\t}}\n'

    def anim(tex, rot):
        return (f'\t\tanimation = {{\n\t\t\tanimationmaskfile = "{tex}"\n'
                '\t\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.dds"\n'
                f'\t\t\tanimationrotation = {rot}\n\t\t\tanimationlooping = no\n\t\t\tanimationtime = 0.75\n'
                '\t\t\tanimationdelay = 0\n\t\t\tanimationblendmode = "add"\n\t\t\tanimationtype = "scrolling"\n'
                '\t\t\tanimationrotationoffset = { x = 0.0 y = 0.0 }\n'
                '\t\t\tanimationtexturescale = { x = 1.0 y = 1.0 }\n\t\t}\n')

    rel = lambda q: q.relative_to(mod).as_posix()
    out, shine = ["spriteTypes = {\n"], ["spriteTypes = {\n"]
    for q in sorted((mod / "gfx/interface/goals").glob("APL_*.dds")):
        out.append(sprite(f"GFX_goal_{q.stem}", rel(q)))
        shine.append(sprite(f"GFX_goal_{q.stem}_shine", rel(q), '\t\teffectFile = "gfx/FX/buttonstate.lua"\n'
                            + anim(rel(q), "-90.0") + anim(rel(q), "90.0") + "\t\tlegacy_lazy_load = no\n"))
    for q in sorted((mod / "gfx/interface/ideas").glob("APL_*.dds")):
        out.append(sprite(f"GFX_idea_{q.stem}", rel(q)))
    for q in sorted((mod / "gfx/interface/decisions").glob("APL_*.dds")):
        if not q.stem.endswith("_category"):
            out.append(sprite(f"GFX_decision_{q.stem}", rel(q)))
    out.append(sprite("GFX_decision_cat_APL_rites", "gfx/interface/decisions/APL_rites_category.dds"))
    out.append(sprite("GFX_decision_cat_APL_lantern", "gfx/interface/decisions/APL_lantern_category.dds"))
    out.append(sprite("GFX_decision_cat_APL_council_cat", "gfx/interface/decisions/APL_council_category.dds"))
    out.append(sprite("GFX_decision_cat_APL_cheats", "gfx/interface/decisions/APL_cheats_category.dds"))
    for q in sorted((mod / "gfx/interface/bop").glob("APL_*.dds")):
        out.append(sprite(f"GFX_bop_{q.stem}", rel(q)))
    for q in sorted((mod / "gfx/event_pictures").glob("APL_*.dds")):
        out.append(sprite(f"GFX_report_event_{q.stem}", rel(q)))
    for q in sorted((mod / "gfx/interface/units").glob("APL_*.dds")):
        for suffix in ("_icon_medium", "_icon_small"):
            out.append(sprite(f"GFX_unit_{q.stem}{suffix}", rel(q)))
    for q in sorted((mod / "gfx/interface/equipment").glob("APL_*_medium.dds")):
        base = q.stem[:-len("_medium")]
        small = rel(q.with_name(base + "_small.dds"))
        out += [sprite(f"GFX_{base}_medium", rel(q)), sprite(f"GFX_{base}_icon_small", small), sprite(f"GFX_{base}_small", small)]
    (mod / "interface/APL.gfx").write_text("".join(out) + "}\n")
    (mod / "interface/APL_goals_shine.gfx").write_text("".join(shine) + "}\n")


if __name__ == "__main__":
    main()
