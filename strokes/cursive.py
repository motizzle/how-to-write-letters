#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import engine
import traced_lines as tl

FONT = tl.FONT
CELL = tl.CELL
RULES_CURSIVE = tl.RULES_CURSIVE

INK_HALF = 0.0187 * CELL

CAP_SIDES = 24

CAP_TURN = math.radians(20)

OVERLAP = 0.25

MEDIAN_STEP = 0.012 * CELL

INK_DECIMATE = 0.0016 * CELL

CUT_TURN = 60.0
CUT_CLOSE = 1.6
CUT_RUN = 2.5
CUT_CLOSE_END = 0.80

WHOLE = {"G"}

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

MANIFEST: dict[str, list[dict]] = {}


def _cw(points):
    pts = list(points)
    if engine._area(pts) > 0:
        pts.reverse()
    return [(pts[i], None, pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def _cap(centre, r, sides=CAP_SIDES):
    rr = r / math.cos(math.pi / sides)
    return [(centre[0] + rr * math.cos(2 * math.pi * i / sides + math.pi / sides),
             centre[1] + rr * math.sin(2 * math.pi * i / sides + math.pi / sides))
            for i in range(sides)]


def stroke_ink(medians, half=INK_HALF):
    contours = []
    for raw in medians:
        pts = engine.simplify(raw, INK_DECIMATE) if len(raw) > 2 else list(raw)
        segs = []
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            n = math.hypot(dx, dy)
            if n < 1e-9:
                segs.append(None)
                continue
            ux, uy = dx / n, dy / n
            nx, ny = -uy * half, ux * half
            ex, ey = ux * half * OVERLAP, uy * half * OVERLAP
            a = (a[0] - ex, a[1] - ey)
            b = (b[0] + ex, b[1] + ey)
            segs.append(math.atan2(dy, dx))
            contours.append(_cw([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                                 (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]))
        for i, p in enumerate(pts):
            before = segs[i - 1] if i else None
            after = segs[i] if i < len(segs) else None
            if before is not None and after is not None and abs(
                    (after - before + math.pi) % (2 * math.pi)
                    - math.pi) < CAP_TURN:
                continue
            contours.append(_cw(_cap(p, half)))
    return contours


MEDIAN_TOL = 3.0


def _resample(pts, step=MEDIAN_STEP):
    if len(pts) < 3:
        return list(pts)
    cum = engine.seg_cum(pts)
    n = max(2, int(round(cum[-1] / step)))
    return engine.simplify(engine.resample(pts, n + 1), MEDIAN_TOL)


def _turnarounds(pts):
    cum = engine.seg_cum(pts)
    close, run, step = CUT_CLOSE * INK_HALF, CUT_RUN * INK_HALF, INK_HALF * 0.25
    hits = []
    for i in range(2, len(pts) - 2):
        a = math.atan2(pts[i][1] - pts[i-1][1], pts[i][0] - pts[i-1][0])
        b = math.atan2(pts[i+1][1] - pts[i][1], pts[i+1][0] - pts[i][0])
        turn = abs((b - a + math.pi) % (2 * math.pi) - math.pi)
        if math.degrees(turn) < CUT_TURN:
            continue
        d = 0.0
        while True:
            lo, hi = cum[i] - d - step, cum[i] + d + step
            if lo < 0 or hi > cum[-1]:
                break
            pa, _ = engine.seg_along(pts, cum, lo / cum[-1])
            pb, _ = engine.seg_along(pts, cum, hi / cum[-1])
            if math.dist(pa, pb) > close:
                break
            d += step
        if d >= run:
            hits.append((i, d))
    keep = []
    for i, d in hits:
        if keep and cum[i] - cum[keep[-1][0]] < INK_HALF * 2:
            if d > keep[-1][1]:
                keep[-1] = (i, d)
            continue
        keep.append((i, d))
    return [i for i, _d in keep]


def _closure(beat):
    cum = engine.seg_cum(beat)
    L = cum[-1]
    if L <= 0:
        return None
    best = None
    for j in range(len(beat)):
        if cum[j] / L < CUT_CLOSE_END:
            continue
        for i in range(j):
            if cum[j] - cum[i] < 0.25 * L:
                break
            if math.dist(beat[i], beat[j]) < CUT_CLOSE * INK_HALF:
                best = j if best is None else min(best, j)
                break
    return best if best is not None and 0 < best < len(beat) - 1 else None


def _beats(char, pts):
    if char in WHOLE:
        return [pts]
    out, prev = [], 0
    for c in _turnarounds(pts) + [len(pts) - 1]:
        if c - prev >= 1:
            out.append(pts[prev:c + 1])
            prev = c
    if not out:
        return [pts]
    for k in range(len(out) - 1):
        j = _closure(out[k])
        if j is None:
            continue
        out[k + 1] = out[k][j:] + out[k + 1][1:]
        out[k] = out[k][:j + 1]
    return out


_FORMS: dict[str, tuple] | None = None
TRACED = tl.DATA


def form(char, doc=None):
    base = tl._rules()[1] * CELL
    strokes = tl.centre_lines(char, doc)
    med, press, lift = [], [], []
    for s in strokes:
        pts = [(x, base - y) for x, y in s["pts"]]
        if s["press"]:
            d = INK_HALF * 0.1
            med.append([(pts[0][0] - d, pts[0][1]), (pts[0][0] + d, pts[0][1])])
            press.append(True)
            lift.append(True)
            continue
        cut = _resample(pts)
        for bi, beat in enumerate(_beats(char, cut)):
            med.append(beat)
            press.append(False)
            lift.append(bool(s.get("lift")) if bi == 0 else False)
    lift[0] = True
    ink = stroke_ink(med)
    x0, y0, x1, y1 = engine.bbox(engine.flatten(ink))
    specs = []
    for pts, is_press, is_lift in zip(med, press, lift):
        spec = {"pts": [[round((x - x0) / (x1 - x0), 5),
                         round((y1 - y) / (y1 - y0), 5)]
                        for x, y in pts], "curve": True}
        if is_press:
            spec["press"] = True
        specs.append(spec)
    return ink, specs, lift


def forms():
    global _FORMS
    if _FORMS is None:
        doc = tl.load(TRACED)
        out = {}
        for ch in LETTERS:
            if not any(s.get("pts") for s in (doc.get(ch) or {}).get("strokes", [])):
                continue
            ink, specs, lift = form(ch, doc)
            out[ch] = (ink, specs, lift)
            MANIFEST[ch] = specs
        _FORMS = out
    return _FORMS


def _unmap(polys, pts_frac, push_target):
    x0, y0, x1, y1 = engine.bbox(polys)
    return [(x0 + fx * (x1 - x0), y1 - fy * (y1 - y0)) for fx, fy in pts_frac]


def _own_sha():
    h = hashlib.sha256()
    for path in (os.path.join(HERE, "cursive.py"),
                 os.path.join(HERE, "traced_lines.py"), TRACED):
        with open(path, "rb") as fh:
            h.update(fh.read())
    h.update(f"{INK_HALF}|{CAP_SIDES}|{CAP_TURN}|{OVERLAP}|"
             f"{MEDIAN_STEP}|{MEDIAN_TOL}|{INK_DECIMATE}|"
             f"{CUT_TURN}|{CUT_CLOSE}|{CUT_RUN}|{CUT_CLOSE_END}|"
             f"{sorted(WHOLE)}".encode())
    return h.hexdigest()[:8]


def build_synth():
    synth = {}
    tag = _own_sha()
    for ch, (ink, _specs, _lift) in forms().items():
        name = f"_cursive_ink_{ord(ch):x}_{tag}"
        setattr(engine, name, lambda _font, _metrics, _ink=ink: _ink)
        synth[ch] = name
    return synth


def deck():
    got = forms()
    return {
        "font": FONT,
        "letters": {ch: ch for ch in got},
        "x_ref": tl.X_REF,
        "rules": RULES_CURSIVE,
        "synth": build_synth(),
    }


def main():
    global TRACED
    argv = sys.argv[1:]
    if "--traced" in argv:
        TRACED = os.path.abspath(argv[argv.index("--traced") + 1])
    d = deck()
    if not d["letters"]:
        raise SystemExit("no letters traced yet — run tracer/trace_server.py")
    engine.MANIFEST = MANIFEST
    engine.DECKS = {"cursive": d}
    engine.derive_stroke = _unmap
    engine.CACHE_DIR = os.path.join(engine.ROOT, ".cache", "cursive")

    if "--fingerprint" in argv:
        json.dump({
            "algorithm": engine._algorithm_sha(),
            "cursive": _own_sha(),
            "decks": {"cursive": {ch: engine.form_fingerprint("cursive", d, ch)
                                  for ch in d["letters"]}},
        }, sys.stdout, sort_keys=True)
        return 0

    built = engine.build_deck("cursive", d)
    if built is None:
        raise SystemExit(
            f"TRACE_ONLY={os.environ.get('TRACE_ONLY')!r} matched no cursive letter")
    letters, meta = built
    lift = {ch: got[2] for ch, got in forms().items()}
    doc = engine.document("cursive", letters, meta, lift)
    if os.environ.get("TRACE_ONLY"):
        json.dump(doc, sys.stdout, ensure_ascii=False)
        return 0
    path = engine.write_document(doc)
    print(f"wrote {os.path.relpath(path)}  letters={len(letters)}  "
          f"strokeHalf={meta['strokeHalf']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
