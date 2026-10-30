import contextlib
import io
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "strokes"))
os.environ["STROKES_NO_CACHE"] = "1"

import engine


def one_letter(char):
    return {"font": engine.FONT, "letters": {char: char}, "x_ref": "x",
            "rules": engine.RULES_LATIN}


class Refusal(unittest.TestCase):
    def setUp(self):
        self.saved = dict(engine.MANIFEST)

    def tearDown(self):
        engine.MANIFEST.clear()
        engine.MANIFEST.update(self.saved)

    def build(self, char, strokes):
        engine.MANIFEST[char] = strokes
        with contextlib.redirect_stderr(io.StringIO()):
            return engine.build_deck("test", one_letter(char))

    def test_a_good_sketch_builds(self):
        letters, meta = self.build("l", [{"pts": [[0.5, 0.03], [0.5, 0.97]]}])
        self.assertEqual(len(letters["l"]["medians"]), 1)
        self.assertGreater(len(letters["l"]["arrows"][0]), 0)

    def test_a_stroke_across_a_hole_is_refused(self):
        with self.assertRaises(SystemExit) as got:
            self.build("o", [{"pts": [[0.0, 0.5], [1.0, 0.5]]}])
        self.assertRegex(str(got.exception), r"^o stroke 0: ")

    def test_a_letter_with_no_sketch_is_named(self):
        engine.MANIFEST.pop("l", None)
        with self.assertRaises(SystemExit) as got:
            engine.build_deck("test", one_letter("l"))
        self.assertIn("no MANIFEST entry for 'l'", str(got.exception))


if __name__ == "__main__":
    unittest.main()
