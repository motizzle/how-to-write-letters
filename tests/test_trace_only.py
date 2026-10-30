import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TraceOnly(unittest.TestCase):
    def test_prints_only_the_letters_asked_for(self):
        env = {**os.environ, "TRACE_ONLY": "b,c"}
        out = subprocess.run([sys.executable, os.path.join(ROOT, "strokes", "engine.py")],
                             env=env, capture_output=True, text=True, check=True).stdout
        self.assertEqual(sorted(json.loads(out)["letters"]), ["b", "c"])


if __name__ == "__main__":
    unittest.main()
