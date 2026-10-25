"""Checks leakage, thresholds, metrics and data integrity, not prose authorship."""
import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import detector_lab as lab


class DetectorLabTests(unittest.TestCase):
    def test_group_assignment_stable(self):
        self.assertEqual(lab.split_group("same question"), lab.split_group("same question"))
        self.assertEqual(lab.canonical("A  Question\n"), lab.canonical("a question"))

    def test_group_leakage_rejected(self):
        rows = [lab.Record("first", 0, "finance", "q", "train"),
                lab.Record("second", 1, "finance", "q", "test")]
        with self.assertRaisesRegex(ValueError, "Question group"):
            lab.assert_disjoint(rows)

    def test_duplicate_text_leakage_rejected(self):
        rows = [lab.Record("Same TEXT", 0, "finance", "q1", "train"),
                lab.Record("same   text", 1, "finance", "q2", "test")]
        with self.assertRaisesRegex(ValueError, "normalized text"):
            lab.assert_disjoint(rows)

    def test_threshold_respects_ties_and_fpr(self):
        values = [0.1] * 99 + [0.9]
        threshold = lab.choose_threshold(values)
        self.assertLessEqual(np.mean(np.asarray(values) >= threshold), 0.01)
        self.assertGreater(threshold, 0.1)

    def test_tiny_calibration_cannot_claim_low_fpr(self):
        threshold = lab.choose_threshold([0.2, 0.3])
        self.assertGreater(threshold, 0.3)
        self.assertGreater(lab.wilson(0, 2)[1], 0.5)

    def test_bad_calibration_rejected(self):
        for values in ([], [float("nan")], [float("inf")]):
            with self.assertRaises(ValueError):
                lab.choose_threshold(values)

    def test_known_confusion_matrix(self):
        result = lab.metrics([0, 0, 1, 1], [0.1, 0.8, 0.7, 0.9], 0.75)
        self.assertEqual(result["false_positives"], 1)
        self.assertEqual(result["true_positives"], 1)
        self.assertEqual(result["fpr"], 0.5)
        self.assertEqual(result["tpr"], 0.5)
        self.assertAlmostEqual(result["auroc"], 0.75)

    def test_empty_and_one_class(self):
        self.assertIsNone(lab.metrics([], [], 0.5)["fpr"])
        self.assertIsNone(lab.metrics([0], [0.2], 0.5)["auroc"])

    def test_invalid_labels_rejected(self):
        with self.assertRaises(ValueError):
            lab.metrics([2], [0.5], 0.5)

    def test_surface_empty_is_finite(self):
        self.assertTrue(np.isfinite(lab.SurfaceFeatures().transform(["", "...", "Words."])).all())

    def test_length_evaluation_keeps_complete_pairs(self):
        rows = [lab.Record("word " * 60, 0, "finance", "q1", "test"),
                lab.Record("word " * 45, 1, "finance", "q1", "test"),
                lab.Record("word " * 60, 0, "finance", "q2", "test"),
                lab.Record("word " * 70, 1, "finance", "q2", "test")]
        class FakeModel:
            def predict_proba(self, texts):
                self.lengths = [len(t.split()) for t in texts]
                return np.array([[0.9, 0.1], [0.1, 0.9]])
        model = FakeModel()
        result = lab.evaluate(model, rows, 0.5, words=50)
        self.assertEqual(result["human"], 1)
        self.assertEqual(result["ai"], 1)
        self.assertEqual(model.lengths, [50, 50])

    def test_tampered_dataset_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, "finance.jsonl").write_text("altered")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                lab.load_records(Path(temp), 10)

    def test_download_checks_hash_before_replacing(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp, "finance.jsonl")
            destination.write_bytes(b"old content")
            with patch.dict(lab.FILES, {"finance": lab.digest(b"expected")}, clear=True):
                with patch.object(lab.urllib.request, "urlopen", return_value=io.BytesIO(b"wrong")):
                    with self.assertRaisesRegex(ValueError, "size/hash mismatch"):
                        lab.fetch(Path(temp))
            self.assertEqual(destination.read_bytes(), b"old content")

    def test_verified_download_and_cached_fetch(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(lab.FILES, {"finance": lab.digest(b"expected")}, clear=True):
                with patch.object(lab.urllib.request, "urlopen", return_value=io.BytesIO(b"expected")):
                    lab.fetch(Path(temp))
                self.assertEqual(Path(temp, "finance.jsonl").read_bytes(), b"expected")
                with patch.object(lab.urllib.request, "urlopen", side_effect=AssertionError("cache should be used")):
                    lab.fetch(Path(temp))

    def test_loader_keeps_answer_pairs_together(self):
        rows = []
        for i in range(20):
            rows.append({"question": f"Question {i}", "human_answers": [(f"human{i} " * 45).strip()],
                         "chatgpt_answers": [(f"ai{i} " * 45).strip()]})
        raw = "\n".join(json.dumps(r) for r in rows).encode()
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, "finance.jsonl").write_bytes(raw)
            with patch.dict(lab.FILES, {"finance": lab.digest(raw)}, clear=True):
                records, audit = lab.load_records(Path(temp), 10)
        self.assertEqual(len(records), 20)
        self.assertEqual(audit["finance"]["question_pairs"], 10)
        for group in {r.group for r in records}:
            pair = [r for r in records if r.group == group]
            self.assertEqual({r.label for r in pair}, {0, 1})
            self.assertEqual(len({r.split for r in pair}), 1)

    def test_rewrite_fixtures_preserve_required_text(self):
        cases = json.loads(Path(__file__).with_name("rewrite_cases.json").read_text())
        self.assertEqual(len({c["id"] for c in cases}), len(cases))
        for case in cases:
            self.assertIn("assistant-generated", case["provenance"])
            for invariant in case["must_preserve"]:
                self.assertIn(invariant, case["after"], (case["id"], invariant))


if __name__ == "__main__":
    unittest.main()
