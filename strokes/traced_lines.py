#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import engine
from fontTools.ttLib import TTFont

DATA = os.path.join(os.path.dirname(HERE), "data", "traced.json")

RULES_CURSIVE = [
    {"kind": "ascender", "y": 0.30},
    {"kind": "mid", "y": 0.506},
    {"kind": "base", "y": 0.72},
]

FONT = os.path.join(HERE, "fonts", "Roboto-Bold.ttf")
X_REF = "l"


def _rules():
    r = {d["kind"]: d["y"] for d in RULES_CURSIVE}
    return r["ascender"], r["base"]


def _cell():
    top, base = _rules()
    polys = engine.flatten(engine.glyph_segments(TTFont(FONT), X_REF))
    return engine.bbox(polys)[3] / (base - top)


CELL = _cell()
RESAMPLE = 0.00225 * CELL
FAIR = 30


def _second_derivatives(t, y):
    n = len(t)
    a, b, c, d = [0.0] * n, [1.0] * n, [0.0] * n, [0.0] * n
    h0, hn = t[1] - t[0], t[n-1] - t[n-2]
    s0, sn = (y[1] - y[0]) / h0, (y[n-1] - y[n-2]) / hn
    b[0], c[0], d[0] = 2 * h0, h0, 6 * (s0 - s0)
    a[n-1], b[n-1], d[n-1] = hn, 2 * hn, 6 * (sn - sn)
    for i in range(1, n - 1):
        h0, h1 = t[i] - t[i-1], t[i+1] - t[i]
        a[i], b[i], c[i] = h0, 2 * (h0 + h1), h1
        d[i] = 6 * ((y[i+1] - y[i]) / h1 - (y[i] - y[i-1]) / h0)
    for i in range(1, n):
        w = a[i] / b[i-1]
        b[i] -= w * c[i-1]
        d[i] -= w * d[i-1]
    m = [0.0] * n
    m[n-1] = d[n-1] / b[n-1]
    for i in range(n - 2, -1, -1):
        m[i] = (d[i] - c[i] * m[i+1]) / b[i]
    return m


CORNER = 90.0


def corners(pts, deg=CORNER):
    out = []
    for i in range(1, len(pts) - 1):
        u = (pts[i][0] - pts[i-1][0], pts[i][1] - pts[i-1][1])
        v = (pts[i+1][0] - pts[i][0], pts[i+1][1] - pts[i][1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        if lu < 1e-9 or lv < 1e-9:
            continue
        c = (u[0]*v[0] + u[1]*v[1]) / (lu * lv)
        if math.degrees(math.acos(max(-1.0, min(1.0, c)))) >= deg:
            out.append(i)
    return out


def _spline_piece(pts, step):
    if len(pts) < 3:
        return list(pts)
    t = [0.0]
    for i in range(1, len(pts)):
        t.append(t[-1] + max(math.dist(pts[i-1], pts[i]) ** 0.5, 1e-6))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    mx, my = _second_derivatives(t, xs), _second_derivatives(t, ys)
    out = []
    for i in range(len(pts) - 1):
        h = t[i+1] - t[i]
        n = max(2, int(math.dist(pts[i], pts[i+1]) / step) + 1)
        for k in range(n):
            tt = t[i] + h * k / n
            A = (t[i+1] - tt) / h
            B = (tt - t[i]) / h
            C = (A*A*A - A) * h * h / 6
            D = (B*B*B - B) * h * h / 6
            out.append((A*xs[i] + B*xs[i+1] + C*mx[i] + D*mx[i+1],
                        A*ys[i] + B*ys[i+1] + C*my[i] + D*my[i+1]))
    out.append(tuple(pts[-1]))
    return out


def smooth(pts, step=RESAMPLE):
    return _join(smooth_pieces(pts, step))


def smooth_pieces(pts, step=RESAMPLE):
    if len(pts) < 3:
        return [list(pts)]
    cuts = [0, *corners(pts), len(pts) - 1]
    return [_spline_piece(pts[a:b + 1], step) for a, b in zip(cuts, cuts[1:])]


def _join(pieces):
    out = []
    for k, piece in enumerate(pieces):
        out.extend(piece if k == 0 else piece[1:])
    return out


RELAX = 1


def relax(pts, n=RELAX, lam=0.5, mu=-0.53):
    if len(pts) < 3 or n == 0:
        return list(pts)
    pinned = set(corners(pts))
    p = [list(q) for q in pts]
    for _ in range(n):
        for w in (lam, mu):
            q = [list(x) for x in p]
            for i in range(1, len(p) - 1):
                if i in pinned:
                    continue
                for k in (0, 1):
                    q[i][k] = p[i][k] + w * (
                        (p[i-1][k] + p[i+1][k]) / 2.0 - p[i][k])
            p = q
    return [tuple(x) for x in p]


def fair(pts, n=FAIR, lam=0.5, mu=-0.53):
    if len(pts) < 3:
        return list(pts)
    p = [list(q) for q in pts]
    for _ in range(n):
        for w in (lam, mu):
            q = [list(x) for x in p]
            for i in range(1, len(p) - 1):
                for k in (0, 1):
                    q[i][k] = p[i][k] + w * (
                        (p[i-1][k] + p[i+1][k]) / 2.0 - p[i][k])
            p = q
    return [tuple(x) for x in p]


def load(path=None):
    with open(path or DATA, encoding="utf-8") as fh:
        return json.load(fh)


def centre_lines(ch, doc=None):
    doc = doc if doc is not None else load()
    top, base = _rules()
    unit = (base - top) * CELL
    out = []
    for st in (doc.get(ch) or {}).get("strokes", []):
        pts = [(x * unit, top * CELL + y * unit) for x, y in st.get("pts", [])]
        if not pts:
            continue
        press = bool(st.get("press")) or len(pts) == 1
        out.append({"pts": [pts[-1]] if press else _join(
                        [fair(piece) for piece in smooth_pieces(relax(pts))]),
                    "press": press,
                    "lift": bool(st.get("lift")) or press})
    if not out:
        return []
    xs = [p[0] for s in out for p in s["pts"]]
    shift = (CELL - (max(xs) - min(xs))) / 2 - min(xs)
    for s in out:
        s["pts"] = [(x + shift, y) for x, y in s["pts"]]
    return out


def main():
    doc = load()
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    for ch in (only or sorted(doc, key=lambda c: (c.islower(), c))):
        strokes = centre_lines(ch, doc)
        if not strokes:
            continue
        n = sum(len(s["pts"]) for s in strokes)
        pres = sum(1 for s in strokes if s["press"])
        xs = [q[0] for s in strokes for q in s["pts"]]
        ys = [q[1] for s in strokes for q in s["pts"]]
        print(f"{ch}: {len(strokes)} stroke(s), {pres} press, {n} points  "
              f"x {min(xs):.0f}..{max(xs):.0f}  y {min(ys):.0f}..{max(ys):.0f} "
              f"of {CELL:.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
