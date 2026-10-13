import datetime as dt
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "token_ledger.py"
SPEC = importlib.util.spec_from_file_location("token_ledger", SCRIPT)
ledger = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ledger)
TODAY = dt.date(2026, 7, 12)
BENCHMARK_SHA256 = "1" * 64
INPUT_SHA256 = "2" * 64
RUBRIC_SHA256 = "3" * 64


def row(phase="baseline", task="a", call="call-1", model="model-a", quality=9.0):
    return {
        "schema_version": 1,
        "call_id": call,
        "phase": phase,
        "task_id": task,
        "declared_model": model,
        "actual_model": model,
        "input_tokens": 100,
        "output_tokens": 20,
        "cached_input_tokens": 0,
        "cost_usd": 1.0,
        "latency_ms": 100.0,
        "quality": quality,
        "success": True,
        "pricing_source": "provider-receipt",
        "pricing_as_of": "2026-07-12",
        "benchmark_sha256": BENCHMARK_SHA256,
        "input_sha256": INPUT_SHA256,
        "rubric_sha256": RUBRIC_SHA256,
    }


class TokenLedgerTests(unittest.TestCase):
    def test_paired_quality_constrained_savings(self):
        after = row("after", call="call-2", quality=8.95)
        after.update(input_tokens=50, output_tokens=10, cost_usd=0.5, latency_ms=80)
        report = ledger.summarize([row(), after], tolerance=0.1)
        self.assertTrue(report["optimization_pass"])
        self.assertEqual(report["savings"]["tokens_percent"], 50.0)
        self.assertEqual(report["savings"]["cost_percent"], 50.0)

    def test_quality_regression_fails_optimization(self):
        self.assertFalse(
            ledger.summarize(
                [row(), row("after", call="call-2", quality=8.0)], tolerance=0.1
            )["optimization_pass"]
        )

    def test_per_task_quality_regression_cannot_hide_in_aggregate_mean(self):
        baseline_a = row(task="a", call="baseline-a", quality=10.0)
        baseline_b = row(task="b", call="baseline-b", quality=0.0)
        after_a = row("after", task="a", call="after-a", quality=0.0)
        after_b = row("after", task="b", call="after-b", quality=10.0)
        after_a.update(input_tokens=50, output_tokens=10, cost_usd=0.5)
        after_b.update(input_tokens=50, output_tokens=10, cost_usd=0.5)

        report = ledger.summarize(
            [baseline_a, baseline_b, after_a, after_b], tolerance=0.1
        )

        self.assertEqual(report["quality_delta"], 0.0)
        self.assertFalse(report["quality_parity"])
        self.assertFalse(report["optimization_pass"])
        self.assertEqual(
            report["quality_regressions"],
            [{"task_id": "a", "baseline": 10.0, "after": 0.0, "delta": -10.0}],
        )
        self.assertIn("Regressed tasks: a (-10.0)", ledger.markdown(report))

    def test_summarize_rejects_duplicate_phase_task_rows(self):
        duplicate = row(call="baseline-a-duplicate", quality=0.0)
        after = row("after", call="after-a", quality=9.0)
        after.update(input_tokens=50, output_tokens=10, cost_usd=0.5)

        with self.assertRaisesRegex(ValueError, "duplicate phase/task: baseline/a"):
            ledger.summarize([row(call="baseline-a"), duplicate, after], tolerance=0.1)

    def test_summarize_rejects_duplicate_call_ids(self):
        after = row("after", call="shared-call", quality=9.0)
        after.update(input_tokens=50, output_tokens=10, cost_usd=0.5)

        with self.assertRaisesRegex(ValueError, "duplicate call_id: shared-call"):
            ledger.summarize(
                [row(call="shared-call"), after],
                tolerance=0.1,
            )

    def test_quality_tolerance_exact_boundary_passes(self):
        for baseline_quality, after_quality in ((9.0, 8.9), (0.8, 0.7), (0.3, 0.2)):
            with self.subTest(
                baseline_quality=baseline_quality, after_quality=after_quality
            ):
                baseline = row(quality=baseline_quality)
                after = row("after", call="after-a", quality=after_quality)
                after.update(input_tokens=50, output_tokens=10, cost_usd=0.5)

                report = ledger.summarize([baseline, after], tolerance=0.1)

                self.assertTrue(report["quality_parity"])
                self.assertEqual(report["quality_regressions"], [])

    def test_quality_tolerance_epsilon_regression_fails(self):
        after = row("after", call="after-a", quality=8.8999999)
        after.update(input_tokens=50, output_tokens=10, cost_usd=0.5)

        report = ledger.summarize([row(), after], tolerance=0.1)

        self.assertFalse(report["quality_parity"])
        self.assertFalse(report["optimization_pass"])
        self.assertEqual(
            report["quality_regressions"],
            [{"task_id": "a", "baseline": 9.0, "after": 8.8999999, "delta": -0.1}],
        )

    def test_valid_multi_task_pairs_preserve_aggregate_and_identity_reporting(self):
        baseline_a = row(task="a", call="baseline-a", quality=9.0)
        after_a = row("after", task="a", call="after-a", quality=8.95)
        baseline_b = row(task="b", call="baseline-b", quality=8.0)
        after_b = row("after", task="b", call="after-b", quality=8.0)
        for record in (baseline_b, after_b):
            record["input_sha256"] = "4" * 64
        for record in (after_a, after_b):
            record.update(input_tokens=50, output_tokens=10, cost_usd=0.5)

        report = ledger.summarize(
            [baseline_a, after_a, baseline_b, after_b], tolerance=0.1
        )

        self.assertTrue(report["optimization_pass"])
        self.assertEqual(report["quality_regressions"], [])
        self.assertEqual(report["baseline"]["calls"], 2)
        self.assertEqual(report["after"]["calls"], 2)
        self.assertEqual(
            report["workload_identities"],
            [
                {
                    "task_id": "a",
                    "benchmark_sha256": BENCHMARK_SHA256,
                    "input_sha256": INPUT_SHA256,
                    "rubric_sha256": RUBRIC_SHA256,
                },
                {
                    "task_id": "b",
                    "benchmark_sha256": BENCHMARK_SHA256,
                    "input_sha256": "4" * 64,
                    "rubric_sha256": RUBRIC_SHA256,
                },
            ],
        )

    def test_no_measurable_savings_fails_optimization(self):
        after = row("after", call="call-2")
        report = ledger.summarize([row(), after], tolerance=0.1)
        self.assertFalse(report["measurable_savings"])
        self.assertFalse(report["optimization_pass"])

    def test_zero_cost_baseline_cannot_claim_savings(self):
        baseline = row()
        after = row("after", call="call-2")
        baseline["cost_usd"] = 0.0
        after.update(cost_usd=0.0, input_tokens=50, output_tokens=10)
        report = ledger.summarize([baseline, after], tolerance=0.1)
        self.assertIsNone(report["savings"]["cost_percent"])
        self.assertTrue(report["measurable_savings"])

    def test_unmatched_tasks_fail_optimization(self):
        after = row("after", call="call-2")
        after.update(input_tokens=50, output_tokens=10, cost_usd=0.5)
        unmatched = row(task="unmatched", call="call-3")
        report = ledger.summarize([row(), after, unmatched], tolerance=0.1)
        self.assertFalse(report["complete_pairing"])
        self.assertFalse(report["optimization_pass"])

    def test_model_mismatch_fails_closed(self):
        record = row()
        record["actual_model"] = "model-b"
        with self.assertRaisesRegex(ValueError, "model mismatch"):
            ledger.validate(record, today=TODAY, max_pricing_age_days=2)

    def test_pair_with_mismatched_workload_identity_fails_closed(self):
        for field in ("benchmark_sha256", "input_sha256", "rubric_sha256"):
            with self.subTest(field=field):
                after = row("after", call="call-2")
                after[field] = "4" * 64
                with self.assertRaisesRegex(
                    ValueError,
                    f"workload identity mismatch for task a: {field}",
                ):
                    ledger.summarize([row(), after], tolerance=0.1)

    def test_workload_identity_hashes_are_required(self):
        record = row()
        del record["benchmark_sha256"]

        with self.assertRaisesRegex(ValueError, "missing fields: benchmark_sha256"):
            ledger.validate(record, today=TODAY, max_pricing_age_days=2)

    def test_workload_identity_hashes_must_be_canonical_sha256(self):
        for field in ("benchmark_sha256", "input_sha256", "rubric_sha256"):
            with self.subTest(field=field):
                record = row()
                record[field] = "NOT-A-SHA"
                with self.assertRaisesRegex(
                    ValueError,
                    f"{field} must be 64 lowercase hexadecimal characters",
                ):
                    ledger.validate(record, today=TODAY, max_pricing_age_days=2)

    def test_stale_pricing_fails_closed(self):
        record = row()
        record["pricing_as_of"] = "2026-07-09"
        with self.assertRaisesRegex(ValueError, "stale pricing"):
            ledger.validate(record, today=TODAY, max_pricing_age_days=2)

    def test_duplicate_and_corrupt_records_fail_closed(self):
        encoded = json.dumps(row())
        with self.assertRaisesRegex(ValueError, "duplicate call_id"):
            ledger.read_records(
                io.StringIO(encoded + "\n" + encoded + "\n"),
                source="x",
                today=TODAY,
                max_pricing_age_days=2,
            )
        with self.assertRaisesRegex(ValueError, "corrupt JSON"):
            ledger.read_records(
                io.StringIO("{bad\n"), source="x", today=TODAY, max_pricing_age_days=2
            )

    def test_duplicate_phase_task_fails_even_with_new_call_id(self):
        first, second = row(), row(call="call-2")
        text = json.dumps(first) + "\n" + json.dumps(second) + "\n"
        with self.assertRaisesRegex(ValueError, "duplicate phase/task"):
            ledger.read_records(
                io.StringIO(text), source="x", today=TODAY, max_pricing_age_days=2
            )

    def test_append_is_sorted_append_only_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "calls.jsonl"
            record = row()
            ledger.append_record(path, record, today=TODAY, max_pricing_age_days=2)
            self.assertEqual(json.loads(path.read_text()), record)
            self.assertEqual(
                path.read_text().strip(),
                json.dumps(record, sort_keys=True, separators=(",", ":")),
            )

    def test_record_cli_requires_workload_identity_hashes(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--today",
                "2026-07-12",
                "record",
                "/tmp/not-written-token-ledger.jsonl",
                "--call-id",
                "call-1",
                "--task-id",
                "a",
                "--declared-model",
                "model-a",
                "--actual-model",
                "model-a",
                "--pricing-source",
                "provider-receipt",
                "--pricing-as-of",
                "2026-07-12",
                "--phase",
                "baseline",
                "--input-tokens",
                "100",
                "--output-tokens",
                "20",
                "--cost-usd",
                "1",
                "--latency-ms",
                "100",
                "--quality",
                "9",
                "--success",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--benchmark-sha256", result.stderr)


if __name__ == "__main__":
    unittest.main()
