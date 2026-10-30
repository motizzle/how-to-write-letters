#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PORT = int(os.environ.get("TRACE_PORT", "8781"))
DATA = os.path.join(ROOT, "data", "traced.json")
BACKDROPS = os.path.join(HERE, "backdrops")
ORDER = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz")

FRAME_LEFT, FRAME_W = 0.25, 2.0
FRAME_TOP, FRAME_H = 0.35, 2.1
PX = 100


def _mid_rule():
    sys.path.insert(0, os.path.join(ROOT, "strokes"))
    from traced_lines import RULES_CURSIVE
    y = {r["kind"]: r["y"] for r in RULES_CURSIVE}
    return (y["mid"] - y["ascender"]) / (y["base"] - y["ascender"])


def form_key(ch):
    return ("cap_" if ch.isupper() else "low_") + ch.lower()


def meta():
    mid = _mid_rule()
    out = {}
    for ch in ORDER:
        key = form_key(ch)
        out[ch] = {
            "key": key,
            "w": FRAME_W * PX, "h": FRAME_H * PX,
            "top": FRAME_TOP * PX, "mid": (FRAME_TOP + mid) * PX,
            "base": (FRAME_TOP + 1) * PX,
            "left": FRAME_LEFT * PX, "unit": PX,
            "backdrop": os.path.exists(os.path.join(BACKDROPS, key + ".png")),
        }
    return out


def _count(doc):
    return sum(1 for v in (doc or {}).values()
               if any(s.get("pts") for s in v.get("strokes", [])))


def _read():
    if not os.path.exists(DATA):
        return {}
    try:
        with open(DATA, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _backup(keep=40):
    cur = _read()
    if not _count(cur):
        return
    backups = os.path.join(os.path.dirname(DATA), "backups")
    os.makedirs(backups, exist_ok=True)
    name = time.strftime("traced-%Y%m%d-%H%M%S.json")
    path = os.path.join(backups, name)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_render(cur))
    old = sorted(f for f in os.listdir(backups) if f.endswith(".json"))
    for f in old[:-keep]:
        os.remove(os.path.join(backups, f))


def _render(body):
    letters = []
    for ch in sorted(body, key=lambda c: (c.islower(), c)):
        rows = []
        for st in body[ch].get("strokes", []):
            pts = ", ".join("[%g, %g]" % (p[0], p[1]) for p in st.get("pts", []))
            flags = "".join(
                ', "%s": true' % k for k in ("press", "lift") if st.get(k))
            rows.append('   {"pts": [%s]%s}' % (pts, flags))
        letters.append('  "%s": {"strokes": []}' % ch if not rows else
                       '  "%s": {"strokes": [\n%s\n  ]}'
                       % (ch, ",\n".join(rows)))
    return "{\n" + ",\n".join(letters) + "\n}\n"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            with open(os.path.join(HERE, "trace.html"), "rb") as fh:
                return self._send(200, fh.read(), "text/html; charset=utf-8")
        if p == "/meta":
            return self._send(200, json.dumps(meta()))
        if p == "/traced.json":
            if os.path.exists(DATA):
                with open(DATA, "rb") as fh:
                    return self._send(200, fh.read())
            return self._send(200, "{}")
        if p.startswith("/backdrops/") and p.endswith(".png"):
            f = os.path.join(BACKDROPS, os.path.basename(p))
            if os.path.exists(f):
                with open(f, "rb") as fh:
                    return self._send(200, fh.read(), "image/png")
        return self._send(404, '{"error":"no"}')

    def do_POST(self):
        if self.path.split("?")[0] != "/traced.json":
            return self._send(404, '{"error":"no"}')
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        try:
            body = json.loads(raw)
        except Exception as exc:
            return self._send(400, json.dumps({"error": str(exc)}))
        before = _count(_read())
        after = _count(body)
        allow_shrink = "shrink=1" in (self.path.split("?", 1) + [""])[1]
        if after < before and not allow_shrink:
            return self._send(409, json.dumps({
                "error": "refused", "onDisk": before, "posted": after,
                "hint": "this page has fewer letters than the file — reload "
                        "before clicking, nothing was overwritten"}))
        _backup()
        tmp = DATA + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(_render(body))
        os.replace(tmp, DATA)
        return self._send(200, json.dumps({"ok": True, "letters": after}))


def main():
    global DATA
    if len(sys.argv) > 1:
        DATA = os.path.abspath(sys.argv[1])
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"tracing tool  ->  http://127.0.0.1:{PORT}/")
    print(f"saving to        {DATA}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
