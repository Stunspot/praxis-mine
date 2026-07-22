from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "praxis_mine.py"
SUBSTRATE_ROOT = Path(__file__).resolve().parents[3] / "cd-data-substrate-v0.1.0"


class PraxisMineIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp.name)
        self.data_home = self.temp_path / "data"
        self.environment = os.environ.copy()
        self.environment["CD_DATA_SUBSTRATE_ROOT"] = str(SUBSTRATE_ROOT)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_mine(self, *arguments: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--data-home", str(self.data_home), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=self.environment,
        )
        if completed.returncode != 0:
            self.fail(f"miner failed: {completed.stderr}\n{completed.stdout}")
        return json.loads(completed.stdout)

    def test_seed_ingestion_evaluation_and_report_are_idempotent(self) -> None:
        health = self.run_mine("init")
        self.assertTrue(health["healthy"])
        manifest = SKILL_ROOT / "assets" / "seed-manifest.json"
        first = self.run_mine("ingest-manifest", str(manifest))
        self.assertEqual(10, first["counts"]["candidates_created"])
        second = self.run_mine("ingest-manifest", str(manifest))
        self.assertEqual(10, second["counts"]["candidates_unchanged"])

        evaluation = SKILL_ROOT / "assets" / "seed-evaluations" / "microsoft_waza.json"
        assessed = self.run_mine("evaluate", "microsoft_waza", str(evaluation))
        self.assertEqual("pilot", assessed["disposition"])
        repeated = self.run_mine("evaluate", "microsoft_waza", str(evaluation))
        self.assertEqual("unchanged", repeated["action"])

        report_path = self.temp_path / "report.md"
        output = self.run_mine("report", "--output", str(report_path))
        self.assertEqual(64, len(output["sha256"]))
        report = report_path.read_text(encoding="utf-8")
        self.assertIn("Microsoft Waza", report)
        self.assertIn("**pilot**", report)
        status = self.run_mine("status")
        self.assertEqual(10, status["candidates"])
        self.assertEqual(1, status["evaluations"])
        self.assertTrue(status["health"]["healthy"])

    def test_local_scan_hashes_discovered_skill(self) -> None:
        collection = self.temp_path / "collection"
        candidate = collection / "useful-skill"
        candidate.mkdir(parents=True)
        (candidate / "SKILL.md").write_text(
            "---\nname: useful-skill\ndescription: Performs a bounded useful operation.\n---\n\n# Useful\n",
            encoding="utf-8",
        )
        result = self.run_mine("scan-local", str(collection), "--source-key", "fixture_collection")
        self.assertEqual(1, result["counts"]["created"])
        repeated = self.run_mine("scan-local", str(collection), "--source-key", "fixture_collection")
        self.assertEqual(1, repeated["counts"]["unchanged"])
        status = self.run_mine("status")
        self.assertEqual(1, status["candidates"])


if __name__ == "__main__":
    unittest.main()
