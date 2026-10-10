"""A small numpy renderer for The Veiled Hollows' art: noise, skies, moons, ridgelines, fog, relit motifs,
ray-marched busts and a film finish. No game files, no network, no third-party images: only numpy and Pillow.

Images are float32 arrays, H x W x 3 (or 4 with alpha), in linear-ish 0..1.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

# ---------------------------------------------------------------- conversions


def to_pil(a: np.ndarray) -> Image.Image:
    a = np.clip(a, 0, 1)
    mode = "RGBA" if a.shape[2] == 4 else "RGB"
    return Image.fromarray((a * 255 + .5).astype(np.uint8), mode).convert("RGBA")


def from_pil(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert("RGBA"), dtype=np.float32) / 255


def resize(a: np.ndarray, size) -> np.ndarray:
    """Lanczos resize of a float image (any channel count), size = (w, h)."""
    chans = [Image.fromarray(a[..., c].astype(np.float32), "F").resize(size, Image.LANCZOS) for c in range(a.shape[2])]
    return np.stack([np.asarray(c, dtype=np.float32) for c in chans], -1)


def blur(a: np.ndarray, r: float) -> np.ndarray:
    """Gaussian blur of a 2D (or HxWxC) float array."""
    if r <= 0:
        return a
    # three box blurs approximate a Gaussian of radius (sigma) r; box half-width from the standard formula
    k = max(1, int(round((math.sqrt(12 * r * r / 3 + 1) - 1) / 2)))
    out = a.astype(np.float32)
    for axis in (0, 1):
        for _ in range(3):
            out = _box(out, k, axis)
    return out


def _box(a, k, axis):
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (k + 1, k)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    hi = np.take(c, np.arange(2 * k + 1, 2 * k + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * k + 1)).astype(np.float32)


def rgb(c) -> np.ndarray:
    return np.array(c[:3], dtype=np.float32) / 255


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- noise


def value_noise(h, w, cell, rng, aspect=1.0):
    """Smooth noise with features about `cell` px across (stretched horizontally by `aspect`)."""
    gh, gw = max(2, int(h / cell) + 3), max(2, int(w / (cell * aspect)) + 3)
    grid = rng.random((gh, gw)).astype(np.float32)
    im = Image.fromarray(grid, "F").resize((int(gw * cell * aspect) + 1, int(gh * cell) + 1), Image.BICUBIC)
    a = np.asarray(im, dtype=np.float32)
    oy, ox = int(rng.integers(0, max(1, a.shape[0] - h))), int(rng.integers(0, max(1, a.shape[1] - w)))
    return a[oy:oy + h, ox:ox + w]


def fbm(h, w, cell, seed, octaves=5, aspect=1.0, gain=.5):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for _ in range(octaves):
        if cell < 1.5:
            break
        out += amp * value_noise(h, w, cell, rng, aspect)
        tot += amp
        amp *= gain
        cell /= 2
    return out / tot


def fbm1d(n, cell, seed, octaves=6):
    return fbm(1, n, cell, seed, octaves)[0]


# ---------------------------------------------------------------- scene pieces


def sky(h, w, top, bottom, seed, clouds=.5, cloud_light=(1, 1, 1)):
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    img = lerp(rgb(top), rgb(bottom), t ** .8) * np.ones((1, w, 1), np.float32)
    if clouds:
        n = fbm(h, w, h * .5, seed, 6, aspect=2.4)
        c = smoothstep(.45, .8, n) * clouds
        shade = fbm(h, w, h * .25, seed + 1, 4, aspect=2) * .6 + .4
        img = lerp(img, img * .45 + rgb(top) * .3 * np.array(cloud_light, np.float32) * shade[..., None], c[..., None])
    return img


def moon(img, cx, cy, r, color=(236, 222, 196), glow=(150, 40, 36), glow_strength=.9, seed=0):
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    halo = np.exp(-np.maximum(d - r, 0) / (r * 1.6)) * glow_strength
    img = img + rgb(glow)[None, None] * halo[..., None] * .6
    disk = smoothstep(r + .8, r - .8, d)
    nx, ny = (xx - cx) / r, (yy - cy) / r
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    maria = fbm(h, w, r * .7, seed, 4)
    craters = fbm(h, w, r * .18, seed + 7, 3)
    shade = (.62 + .38 * nz ** .5) * (1 - .32 * smoothstep(.48, .7, maria)) * (.9 + .2 * craters)
    surface = rgb(color)[None, None] * shade[..., None]
    return lerp(img, surface, disk[..., None])


def ridge_mask(h, w, base, amp, seed, cell=None, sharp=0.0):
    """Mask (1 below the ridge) for a mountain line at height `base` (px) with jaggedness `amp`."""
    line = fbm1d(w, cell or w * .45, seed)
    line = (line - line.mean()) * 2
    if sharp:
        line = line + sharp * (np.abs(fbm1d(w, w * .12, seed + 3) - .5) * -2)
    y = base - line * amp
    yy = np.arange(h, dtype=np.float32)[:, None]
    return smoothstep(y[None] - .8, y[None] + .8, yy)


def pine_mask(h, w, ground, seed, n=40, hmin=.1, hmax=.3, ss=3):
    """Ragged pine silhouettes standing on y = ground (fraction of h)."""
    rng = np.random.default_rng(seed)
    im = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x = rng.uniform(-.05, 1.05) * w * ss
        th = rng.uniform(hmin, hmax) * h * ss
        base = (ground + rng.uniform(-.03, .05)) * h * ss
        tw = th * rng.uniform(.22, .32)
        tiers = int(rng.integers(6, 11))
        for i in range(tiers):
            f = i / tiers
            y0 = base - th * (1 - f) - th * .02
            ww = tw * (.25 + .75 * f) * rng.uniform(.8, 1.15)
            y1 = y0 + th / tiers * 2.2
            jag = [(x, y0)]
            for k in range(5):
                jag.append((x + ww * (k + 1) / 5 * (1 if k % 2 == 0 else .7), y0 + (y1 - y0) * (k + 1) / 5))
            jag += [(x - p[0] + x, p[1]) for p in reversed(jag[1:])]
            d.polygon(jag, fill=255)
        d.rectangle([x - tw * .06, base - th * .1, x + tw * .06, base + th * .1], fill=255)
    im = im.resize((w, h), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32) / 255


def fog_layer(h, w, y0, y1, seed, density=.7, cell=None):
    """Fog density field: thickest between y0 and y1 (px), drifting in horizontal banks."""
    n = fbm(h, w, cell or h * .35, seed, 5, aspect=3)
    yy = np.arange(h, dtype=np.float32)[:, None]
    band = smoothstep(y0 - (y1 - y0) * .6, y0, yy) * (1 - smoothstep(y1, y1 + (y1 - y0) * 1.2, yy))
    return np.clip(band * (n * 1.6 - .25), 0, 1) * density


def add_fog(img, density, color):
    return lerp(img, rgb(color)[None, None] * np.ones_like(img), density[..., None])


def god_rays(img, cx, cy, strength=.35, color=(220, 200, 190), steps=24):
    """Cheap radial blur of the bright parts, added back: shafts of light through fog and branches."""
    h, w, _ = img.shape
    lum = img.mean(-1)
    bright = np.clip((lum - .35) * 2, 0, 1)
    pil = Image.fromarray(bright.astype(np.float32), "F")
    acc = np.zeros((h, w), np.float32)
    for i in range(steps):
        s = 1 + i * .03
        sw, sh = int(w * s), int(h * s)
        big = pil.resize((sw, sh), Image.BILINEAR)
        ox, oy = int(cx * (s - 1)), int(cy * (s - 1))
        acc += np.asarray(big, dtype=np.float32)[oy:oy + h, ox:ox + w] * (1 - i / steps)
    acc /= steps
    return img + rgb(color)[None, None] * acc[..., None] * strength


def eyes(img, emis, pts, r, color=(255, 40, 30)):
    """Pairs of glowing eyes at pts; adds to `emis` (emissive buffer) so the finish blooms them."""
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for (x, y) in pts:
        for dx in (-r * 2.2, r * 2.2):
            d = np.sqrt(((xx - x - dx) / 1.3) ** 2 + (yy - y) ** 2)
            core = smoothstep(r, r * .4, d)
            emis += rgb(color)[None, None] * core[..., None] * 1.6
    return img


# ---------------------------------------------------------------- relit motifs


def motif_layers(draw_fn, size, ss=4):
    """Draw a make_art motif at ss x size. Returns (mask, emissive_mask) as float arrays at ss x size."""
    w, h = size
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(im), ss)
    a = from_pil(im)
    red = np.clip((a[..., 0] - a[..., 1] * 1.4) * 2, 0, 1) * a[..., 3]
    # dark fills inside a motif (eye sockets, a crescent's shadow, teeth gaps) are holes, not surface
    lum = a[..., :3].mean(-1)
    alpha = a[..., 3] * np.maximum(smoothstep(.12, .35, lum), red)
    return alpha, red


def relight(mask, albedo, light=(-.55, -.7, .55), rough=.5, bump=1.0, seed=0, metal=False, rim=(150, 30, 26),
            depth=None):
    """Turn a flat mask into a sculpted, lit object: height from layered blurs of the mask, normals from its
    gradient, a key light, a soft specular, a red rim from below and surface grain. Returns RGBA (premultiplied
    over nothing) at mask's size."""
    h, w = mask.shape
    s = depth or max(h, w) / 60
    height = (blur(mask, s * .35) * .55 + blur(mask, s * 1.2) * .3 + blur(mask, s * 3.5) * .25)
    tex = fbm(h, w, max(4, s * 3), seed, 4)
    height = height + (tex - .5) * .08 * bump
    gy, gx = np.gradient(height * s * 4 * bump)
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    L = np.array(light, np.float32)
    L /= np.linalg.norm(L)
    ndl = np.clip((n * L).sum(-1), 0, 1)
    H = L + np.array([0, 0, 1], np.float32)
    H /= np.linalg.norm(H)
    spec = np.clip((n * H).sum(-1), 0, 1) ** (8 + 60 * (1 - rough))
    rimv = np.clip(n[..., 1], 0, 1) ** 2  # faces pointing down catch the red light from below
    ao = np.clip(.45 + .55 * blur(mask, s * 2.5), 0, 1)
    alb = rgb(albedo)[None, None] * (.75 + .5 * tex[..., None])
    if metal:
        col = alb * (.12 + .9 * ndl[..., None]) + alb * spec[..., None] * 1.6
    else:
        col = alb * (.06 + 1.05 * ndl[..., None] ** 1.2) + spec[..., None] * (.5 * (1 - rough))
    col = col * ao[..., None] + rgb(rim)[None, None] * rimv[..., None] * .55
    return np.concatenate([col, mask[..., None]], -1)


def over(dst, src):
    """Composite RGBA src (straight alpha) over RGB dst."""
    a = src[..., 3:4]
    return dst * (1 - a) + src[..., :3] * a


def drop_shadow(dst, mask, dx, dy, r, strength=.75):
    sh = blur(np.roll(np.roll(mask, int(dy), 0), int(dx), 1), r)
    return dst * (1 - sh[..., None] * strength)


def glow(dst, mask, r, color, strength=1.0):
    g = blur(mask, r)
    return dst + rgb(color)[None, None] * g[..., None] * strength


# ---------------------------------------------------------------- ray-marched busts


def bust(size, seed, hood=False, hat=None, eye_color=(255, 40, 30), coat=(22, 18, 20), skin=(150, 128, 112),
         key=(-.95, -.25, .45), key_color=(255, 214, 170), rim_color=(170, 50, 40), glasses=False, beard=False, hair=False, hair_color=(40, 32, 28), shirt=None,
         tie_color=(60, 14, 16),
         helmet=False, collar=False, gaunt=0.0, age=0.0, steps=72):
    """A head-and-shoulders figure, ray-marched from signed distance fields and lit like a night photograph:
    one hard key light from the side, a coloured rim from behind, glowing eyes. Returns (rgb, alpha, emissive)
    at `size` (w, h)."""
    w, h = size
    aspect = w / h
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xs / w - .5) * 2 * aspect
    v = -(ys / h - .5) * 2
    ro = np.array([0, .08, 4.2], np.float32)
    rd = np.stack([u * .36, v * .36 - .02, -np.ones_like(u)], -1)
    rd /= np.linalg.norm(rd, axis=-1, keepdims=True)
    rng = np.random.default_rng(seed)
    jx = rng.uniform(-.04, .04)

    def smin(a, b, k):
        hh = np.clip(.5 + .5 * (b - a) / k, 0, 1)
        return lerp(b, a, hh) - k * hh * (1 - hh)

    def ellipsoid(p, c, r):
        q = (p - np.array(c, np.float32)) / np.array(r, np.float32)
        k0 = np.linalg.norm(q, axis=-1)
        k1 = np.linalg.norm(q / np.array(r, np.float32), axis=-1)
        return k0 * (k0 - 1) / np.maximum(k1, 1e-4)

    def capsule(p, a, b, r):
        a, b = np.array(a, np.float32), np.array(b, np.float32)
        pa, ba = p - a, b - a
        t = np.clip((pa * ba).sum(-1) / (ba * ba).sum(), 0, 1)
        return np.linalg.norm(pa - ba * t[..., None], axis=-1) - r

    def cyl(p, c, r, hh):
        q = p - np.array(c, np.float32)
        d = np.stack([np.sqrt(q[..., 0] ** 2 + q[..., 2] ** 2) - r, np.abs(q[..., 1]) - hh], -1)
        return np.minimum(np.maximum(d[..., 0], d[..., 1]), 0) + np.linalg.norm(np.maximum(d, 0), axis=-1)

    def scene(p):
        """Returns (distance, material id): 0 skin, 1 cloth, 2 hat/helmet/hood."""
        hx = jx
        head = ellipsoid(p, (hx, .56, -.02), (.37 - gaunt * .04, .47, .41))
        jaw = ellipsoid(p, (hx, .32, .06), (.29 - gaunt * .06, .22, .31))
        headd = smin(head, jaw, .14)
        for sx in (-.19, .19):  # cheekbones
            headd = smin(headd, ellipsoid(p, (hx + sx, .47, .22), (.10, .07, .1)), .06)
        nose = capsule(p, (hx, .56, .36), (hx, .45, .42), .045)
        headd = smin(headd, nose, .06)
        for sx in (-.37, .37):  # ears
            headd = smin(headd, ellipsoid(p, (hx + sx, .53, -.02), (.04, .09, .06)), .03)
        brow = capsule(p, (hx - .17, .66, .30), (hx + .17, .66, .30), .06 + age * .01)
        headd = smin(headd, brow, .06)
        for sx in (-.14, .14):  # eye sockets
            headd = np.maximum(headd, -ellipsoid(p, (hx + sx, .58, .36), (.085, .05, .06)))
        if gaunt:
            for sx in (-.25, .25):  # hollow cheeks
                headd = np.maximum(headd, -ellipsoid(p, (hx + sx, .40, .30), (.08, .10, .08)) - .01)
        neck = capsule(p, (hx * .5, -.05, -.02), (hx, .30, -.02), .19)
        body = ellipsoid(p, (0, -1.05, -.05), (1.0, .8, .42))
        body = smin(body, capsule(p, (-.62, -.42, -.06), (.62, -.42, -.06), .2), .25)  # shoulders
        body = smin(body, ellipsoid(p, (0, -.24, -.04), (.30, .16, .24)), .18)
        if collar:
            body = smin(body, capsule(p, (-.2, -.05, .12), (.2, -.05, .12), .07), .05)
        skin_d = smin(headd, neck, .08)
        cloth_d = body
        top = np.full(skin_d.shape, 9.0, np.float32)
        if hat == "stovepipe":
            top = np.minimum(cyl(p, (hx, 1.13, -.02), .30, .26), cyl(p, (hx, .88, -.02), .52, .015) - .01)
        elif hat == "brim":
            top = np.minimum(ellipsoid(p, (hx, .93, -.02), (.36, .17, .38)), cyl(p, (hx, .86, 0), .60, .01) - .01)
        elif hat == "cap":
            top = np.minimum(ellipsoid(p, (hx, .88, -.02), (.39, .2, .41)), ellipsoid(p, (hx, .82, .32), (.22, .03, .16)))
        if helmet:
            top = np.minimum(ellipsoid(p, (hx, .90, -.02), (.42, .26, .44)), cyl(p, (hx, .98, .40), .07, .05))
        if hood:
            outer = ellipsoid(p, (hx, .58, -.06), (.52, .66, .56))
            inner = ellipsoid(p, (hx, .52, .12), (.40, .55, .52))
            hd = np.maximum(outer, -inner)
            hd = np.maximum(hd, -(p[..., 2] - .38) * -1 - .0)  # open at the front
            hd = smin(hd, body + .02, .2)
            top = np.minimum(top, hd)
        hair_d = np.full(skin_d.shape, 9.0, np.float32)
        if beard:
            hair_d = ellipsoid(p, (hx, .25, .17), (.31, .25, .24))
            hair_d = np.maximum(hair_d, -ellipsoid(p, (hx, .36, .40), (.10, .035, .06)))  # mouth gap
        if hair:
            hair_d = np.minimum(hair_d, ellipsoid(p, (hx, .70, -.06), (.40, .40, .40)))
            hair_d = np.minimum(hair_d, ellipsoid(p, (hx, .78, -.40), (.18, .16, .16)))  # bun
            hair_d = np.maximum(hair_d, -(ellipsoid(p, (hx, .48, .3), (.34, .32, .3))))  # keep the face clear
        d = np.minimum(np.minimum(np.minimum(skin_d, cloth_d), top), hair_d)
        mat = np.where(d == skin_d, 0, np.where(d == cloth_d, 1, np.where(d == hair_d, 3, 2)))
        return d, mat

    t = np.full((h, w), 2.4, np.float32)
    hit = np.zeros((h, w), bool)
    for _ in range(steps):
        p = ro + rd * t[..., None]
        d, _ = scene(p)
        hit |= d < .002
        t = np.where(hit, t, np.minimum(t + d * .9, 8.0))
        if (t > 6.5).all():
            break
    p = ro + rd * t[..., None]
    d, mat = scene(p)
    hit = d < .01
    e = .004
    n = np.stack([scene(p + np.array(o, np.float32))[0] - scene(p - np.array(o, np.float32))[0]
                  for o in ((e, 0, 0), (0, e, 0), (0, 0, e))], -1)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    L = np.array(key, np.float32)
    L /= np.linalg.norm(L)
    ndl = np.clip((n * L).sum(-1), 0, 1)
    # hard shadow toward the key light
    sh = np.ones((h, w), np.float32)
    ts = np.full((h, w), .02, np.float32)
    for _ in range(24):
        q = p + L * ts[..., None]
        dq, _ = scene(q)
        sh = np.minimum(sh, np.clip(8 * dq / ts, 0, 1))
        ts += np.clip(dq, .02, .2)
    ao = np.clip(scene(p + n * .08)[0] / .08, 0, 1) * .6 + .4
    view = -rd
    fres = np.clip(1 - (n * view).sum(-1), 0, 1) ** 3
    back = np.clip(-n[..., 0] * np.sign(L[0]) * .6 + n[..., 1] * .4, 0, 1)
    tex = fbm(h, w, max(3, w / 30), seed + 3, 4)
    strands = fbm(h, w, max(2, w / 80), seed + 5, 3, aspect=.25)
    alb = np.where(mat[..., None] == 0, rgb(skin)[None, None] * (.85 + .3 * tex[..., None]),
                   np.where(mat[..., None] == 1, rgb(coat)[None, None] * (.8 + .4 * tex[..., None]),
                            np.where(mat[..., None] == 3, rgb(hair_color)[None, None] * (.6 + .8 * strands[..., None]),
                                     rgb(coat)[None, None] * .7 * (.8 + .4 * tex[..., None]))))
    if shirt:  # a white shirt and a dark tie in the V of the coat
        px_, py_, pz_ = p[..., 0] - jx * .3, p[..., 1], p[..., 2]
        v = (mat == 1) & (pz_ > 0) & (py_ < -.12) & (np.abs(px_) < (py_ + .8) * .36)
        tie = v & (np.abs(px_) < .035 + (-.12 - py_) * .04) & (py_ > -.75)
        alb = np.where(v[..., None], rgb(shirt)[None, None] * (.85 + .2 * tex[..., None]), alb)
        alb = np.where(tie[..., None], rgb(tie_color)[None, None], alb)
    H = L + view
    H /= np.linalg.norm(H, axis=-1, keepdims=True)
    spec = np.clip((n * H).sum(-1), 0, 1) ** np.where(mat == 0, 24, 10) * np.where(mat == 0, .25, .12)
    col = alb * (rgb(key_color)[None, None] * (ndl * sh)[..., None] * 1.1 + .05 * ao[..., None])
    col += spec[..., None] * sh[..., None] * rgb(key_color)[None, None]
    col += rgb(rim_color)[None, None] * (fres * back)[..., None] * .9
    col *= ao[..., None]
    alpha = blur(hit.astype(np.float32), .5)
    emis = np.zeros((h, w, 3), np.float32)
    # eyes: project the two eye points and paint glowing irises (hidden inside a hood they glow in the dark)
    for sx in (-.14, .14):
        ex, ey, ez = jx + sx, .575, .36
        pu = (ex - ro[0]) / (ro[2] - ez) / .36
        pv = ((ey - ro[1]) / (ro[2] - ez) + .02) / .36
        cx = (pu / (2 * aspect) + .5) * w
        cy = (-pv / 2 + .5) * h
        dd = np.sqrt((xs - cx) ** 2 + ((ys - cy) * 1.5) ** 2)
        r = w * .018
        emis += rgb(eye_color)[None, None] * smoothstep(r, r * .3, dd)[..., None] * 1.4
        col = col * (1 - smoothstep(r * 1.6, r, dd)[..., None] * .8)
        if glasses:
            ring = np.abs(np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) - r * 2.4)
            col = lerp(col, np.full_like(col, .65), smoothstep(w * .006, 0, ring)[..., None])
    return col, alpha, emis


# ---------------------------------------------------------------- finish


def finish(img, emis=None, seed=0, grain=.035, vignette=.55, bloom=.6, warm=(1.0, .96, .92), contrast=1.08):
    """Film look: bloom of bright and emissive light, a filmic tone curve, a vignette, slight colour fringe and
    grain. Returns an RGB array."""
    h, w, _ = img.shape
    if emis is not None:
        img = img + emis
    bright = np.clip(img - .7, 0, None) + (emis if emis is not None else 0)
    img = img + (blur(bright, max(1.5, w / 90)) * .9 + blur(bright, max(3, w / 30)) * .6) * bloom
    img = img * np.array(warm, np.float32)
    img = img / (1 + img * .35)  # soft shoulder
    img = np.clip((img - .5) * contrast + .5 + (contrast - 1) * .1, 0, None)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx / w - .5) * 2) ** 2 + ((yy / h - .5) * 2) ** 2) / math.sqrt(2)
    img = img * (1 - vignette * smoothstep(.35, 1.05, r))[..., None]
    if w >= 100:  # a whisper of chromatic aberration on the bigger pictures
        img[..., 0] = np.roll(img[..., 0], 1, 1) * .5 + img[..., 0] * .5
    rng = np.random.default_rng(seed + 991)
    g = rng.normal(0, 1, (h, w)).astype(np.float32)
    g = blur(g, .45)
    img = img + g[..., None] * grain * (.4 + .6 * (1 - np.clip(img.mean(-1, keepdims=True), 0, 1)))
    return np.clip(img, 0, 1)
