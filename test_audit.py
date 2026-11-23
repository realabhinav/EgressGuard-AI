import json
import unittest
from pathlib import Path
from audit import audit, evidence

class AuditTests(unittest.TestCase):
    def setUp(self):
        data = json.loads(Path(__file__).with_name("demo.json").read_text())
        self.rows = audit(data["records"], data["pages"])
        self.pages = data["pages"]

    def test_count(self):
        self.assertEqual(len(self.rows), 5)

    def test_mapping(self):
        expected = ["demo-network/p1"]*2 + ["demo-network/p2"] + ["demo-ownership/p1"]*2
        self.assertEqual([r["source"] for r in self.rows], expected)

    def test_absent_evidence(self):
        self.assertIsNone(evidence("xyz", self.pages))

    def test_missing_observation(self):
        self.assertEqual(audit([{"id":"x","type":"proxy"}], self.pages), [])
