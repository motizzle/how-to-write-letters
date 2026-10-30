import json
import math
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "data")
COUNTS = {"print": 54, "cursive": 52, "hebrew": 27}


def load(name):
    with open(os.path.join(DATA, name + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def triangle(a, arrow, scale=1.0):
    s = min(a["s"] * scale, a["smax"])
    bx, by = a["x"] - a["dx"] * s * arrow["back"], a["y"] - a["dy"] * s * arrow["back"]
    nx, ny = -a["dy"], a["dx"]
    w = s * arrow["wing"]
    return [(a["x"] + a["dx"] * s, a["y"] + a["dy"] * s),
            (bx + nx * w, by + ny * w), (bx - nx * w, by - ny * w)]


class Documents(unittest.TestCase):
    def test_every_alphabet(self):
        for name, count in COUNTS.items():
            with self.subTest(alphabet=name):
                self.check(load(name), name, count)

    def check(self, doc, name, count):
        self.assertEqual(doc["format"], "how-to-write-letters/1")
        self.assertEqual(doc["alphabet"], name)
        self.assertEqual(len(doc["letters"]), count)
        ys = [r["y"] for r in doc["rules"]]
        self.assertEqual(ys, sorted(ys))
        self.assertTrue(all(0 < y < 1 for y in ys))
        self.assertIn("base", [r["kind"] for r in doc["rules"]])
        for k in ("back", "wing", "pulse"):
            self.assertGreater(doc["arrow"][k], 0)
        w = doc["walk"]
        self.assertGreater(w["speed"], 0)
        self.assertLessEqual(w["minMs"], w["maxMs"])
        self.assertGreaterEqual(w["holdMs"], 0)
        self.assertGreater(doc["strokeHalf"], 0)

        for ch, L in doc["letters"].items():
            where = f"{name}/{ch}"
            self.assertEqual(len(ch), 1, where)
            self.assertGreater(L["aspect"], 0, where)
            ops = re.findall(r"[MLQZ][^MLQZ]*", L["outline"])
            self.assertEqual("".join(ops), L["outline"], where)
            self.assertEqual(ops[0][0], "M", where)
            for op in ops:
                n = len(op[1:].split())
                self.assertEqual(n, {"M": 2, "L": 2, "Q": 4, "Z": 0}[op[0]], f"{where}: {op}")
            self.assertGreaterEqual(len(L["strokes"]), 1, where)
            self.assertTrue(L["strokes"][0]["lift"], f"{where}: the pencil starts down")
            arrows = 0
            for i, s in enumerate(L["strokes"]):
                at = f"{where} stroke {i + 1}"
                pts = s["points"]
                self.assertGreaterEqual(len(pts), 2 if not s["press"] else 1, at)
                for x, y in pts:
                    self.assertTrue(0 <= x <= L["aspect"], f"{at}: x {x} outside the cell")
                    self.assertTrue(0 <= y <= 1, f"{at}: y {y} outside the cell")
                if s["press"]:
                    self.assertEqual(s["arrows"], [], f"{at}: a press has no direction")
                    self.assertTrue(s["lift"], f"{at}: a press lifts the pencil")
                us = [a["u"] for a in s["arrows"]]
                self.assertEqual(us, sorted(us), f"{at}: arrows out of order")
                for a in s["arrows"]:
                    self.assertTrue(0 <= a["u"] <= 1, at)
                    self.assertAlmostEqual(math.hypot(a["dx"], a["dy"]), 1, delta=1e-3, msg=at)
                    self.assertGreater(a["s"], 0, at)
                    self.assertGreaterEqual(a["smax"] + 1e-4, a["s"], at)
                    for x, y in triangle(a, doc["arrow"]):
                        self.assertTrue(-1e-3 <= x <= L["aspect"] + 1e-3 and 0 <= y <= 1, at)
                arrows += len(s["arrows"])
            self.assertGreater(arrows, 0, f"{where}: no arrow anywhere")


class TeachingFacts(unittest.TestCase):

    def test_print(self):
        L = load("print")["letters"]
        self.assertEqual([s["press"] for s in L["i"]["strokes"]], [False, True])
        self.assertEqual(len(L["E"]["strokes"]), 4)
        self.assertEqual(len(L["O"]["strokes"]), 1)
        self.assertTrue(all(s["lift"] for L1 in L.values() for s in L1["strokes"]))

    def test_cursive(self):
        L = load("cursive")["letters"]
        i = L["i"]["strokes"]
        self.assertTrue(i[-1]["press"])
        self.assertEqual([s["lift"] for s in L["m"]["strokes"]], [True, False, False])
        self.assertEqual(len(L["G"]["strokes"]), 1)

    def test_hebrew(self):
        L = load("hebrew")["letters"]
        self.assertEqual(list(L)[0], "א")
        self.assertEqual(len(L["ו"]["strokes"]), 1)


if __name__ == "__main__":
    unittest.main()
