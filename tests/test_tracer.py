import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tracer"))

import trace_server

A = {"A": {"strokes": [{"pts": [[0.1, 0.2], [0.5, 0.9]]}]}}
AB = {**A, "B": {"strokes": [{"pts": [[0.2, 0.1], [0.2, 1.0]], "lift": True}]}}


class Server(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        trace_server.DATA = os.path.join(self.dir, "mine.json")
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), trace_server.H)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_address[1]}"

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        shutil.rmtree(self.dir)

    def call(self, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(self.url + path, data)) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            with e:
                return e.code, e.read()

    def test_the_page_and_its_frame(self):
        status, page = self.call("/")
        self.assertEqual(status, 200)
        self.assertIn(b"Trace the path", page)
        status, meta = self.call("/meta")
        meta = json.loads(meta)
        self.assertEqual(len(meta), 52)
        m = meta["a"]
        self.assertEqual(m["key"], "low_a")
        self.assertEqual(m["base"] - m["top"], m["unit"])
        self.assertTrue(m["top"] < m["mid"] < m["base"])
        self.assertFalse(m["backdrop"])
        self.assertEqual(self.call("/traced.json"), (200, b"{}"))

    def test_saves_and_refuses_to_lose_letters(self):
        self.assertEqual(self.call("/traced.json", AB)[0], 200)
        with open(trace_server.DATA, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), AB)
        status, body = self.call("/traced.json", A)
        self.assertEqual(status, 409)
        self.assertEqual(json.loads(body)["onDisk"], 2)
        with open(trace_server.DATA, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), AB)
        self.assertEqual(self.call("/traced.json?shrink=1", A)[0], 200)
        with open(trace_server.DATA, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), A)
        backups = os.listdir(os.path.join(self.dir, "backups"))
        self.assertEqual(len(backups), 1)


if __name__ == "__main__":
    unittest.main()
