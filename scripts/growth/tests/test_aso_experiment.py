from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.growth.check_aso_experiment import validate_aso_experiment


ROOT = Path(__file__).resolve().parents[3]


class AsoExperimentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.experiment = json.loads(
            (ROOT / "growth/experiments/growth-2026-09-uz-query-headline.json").read_text(
                encoding="utf-8"
            )
        )
        self.metadata = json.loads(
            (ROOT / "store/metadata.json").read_text(encoding="utf-8")
        )
        self.gates = json.loads(
            (ROOT / "growth/quality/gates.json").read_text(encoding="utf-8")
        )

    def failures(self, experiment=None, metadata=None, gates=None):
        return validate_aso_experiment(
            experiment or self.experiment,
            metadata or self.metadata,
            gates or self.gates,
            ROOT,
        )

    def test_repository_draft_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_second_variable_is_rejected(self) -> None:
        experiment = copy.deepcopy(self.experiment)
        experiment["surfaces"][0]["field"] = "subtitle"
        self.assertIn(
            "surfaces[0] changes a field outside the single variable",
            self.failures(experiment=experiment),
        )

    def test_activation_cannot_be_inferred_from_blocked_gates(self) -> None:
        experiment = copy.deepcopy(self.experiment)
        experiment["activation"]["activation_ready"] = True
        self.assertIn(
            "a repository draft cannot infer activation readiness",
            self.failures(experiment=experiment),
        )

    def test_unapproved_query_token_is_rejected(self) -> None:
        experiment = copy.deepcopy(self.experiment)
        experiment["surfaces"][0]["variant"] = "Nimbo: AI Toshkent Ob-havo"
        experiment["surfaces"][0]["variant_characters"] = len(
            experiment["surfaces"][0]["variant"]
        )
        self.assertIn(
            "surfaces[0] variant uses an unapproved title token",
            self.failures(experiment=experiment),
        )

    def test_non_title_control_drift_is_rejected(self) -> None:
        metadata = copy.deepcopy(self.metadata)
        metadata["localizations"]["en-GB"]["subtitle"] = "Changed"
        self.assertIn(
            "surfaces[0] non-title control fields drifted",
            self.failures(metadata=metadata),
        )

    def test_every_publication_gate_is_required(self) -> None:
        experiment = copy.deepcopy(self.experiment)
        del experiment["activation"]["required_gate_statuses"]["ios_crash_gate"]
        self.assertIn(
            "activation must require every publication-blocking gate",
            self.failures(experiment=experiment),
        )


if __name__ == "__main__":
    unittest.main()
