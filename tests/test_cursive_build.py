import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CursiveBuild(unittest.TestCase):
    def test_built_letters_match_the_document(self):
        env = {**os.environ, "TRACE_ONLY": "i,m"}
        out = subprocess.run([sys.executable, os.path.join(ROOT, "strokes", "cursive.py")],
                             env=env, capture_output=True, text=True, check=True).stdout
        built = json.loads(out)["letters"]
        with open(os.path.join(ROOT, "docs", "data", "cursive.json"), encoding="utf-8") as fh:
            shipped = json.load(fh)["letters"]
        self.assertEqual(sorted(built), ["i", "m"])
        for ch in built:
            self.assertEqual(built[ch], shipped[ch], ch)

    def test_a_letter_emptied_in_the_tracer_is_left_out(self):
        import tempfile
        with open(os.path.join(ROOT, "data", "traced.json"), encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["i"]["strokes"] = [{"pts": []}]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "traced.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(doc, fh)
            env = {**os.environ, "TRACE_ONLY": "m"}
            run = subprocess.run([sys.executable, os.path.join(ROOT, "strokes", "cursive.py"), "--traced", path],
                                 env=env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr[-500:])
        self.assertEqual(sorted(json.loads(run.stdout)["letters"]), ["m"])


if __name__ == "__main__":
    unittest.main()
