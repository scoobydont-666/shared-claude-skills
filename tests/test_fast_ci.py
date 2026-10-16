"""Dependency-free tests: python3 -I tests/test_fast_ci.py -v."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/fast-ci/scripts/fast_ci.py"
spec = importlib.util.spec_from_file_location("fast_ci", SCRIPT)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


def policy():
    return {
        "schema": "fast-ci-policy/v1",
        "global_paths": [".github/*", "Cargo.lock", "skills/*"],
        "jobs": [
            {"id": "controls", "paths": ["policy/*"], "needs": [], "always": True, "min_tests": 0},
            {"id": "docs", "paths": ["docs/*", "README.md"], "needs": [], "always": False, "min_tests": 0},
            {"id": "core", "paths": ["src/core/*", "tests/core/*"], "needs": [], "always": False, "min_tests": 1},
            {"id": "app", "paths": ["src/app/*", "tests/app/*"], "needs": ["core"], "always": False, "min_tests": 1},
            {"id": "other", "paths": ["other/*"], "needs": [], "always": False, "min_tests": 1},
        ],
    }


def context(changes=None):
    return {
        "schema": "fast-ci-context/v1",
        "repository": "example/project",
        "base_sha": "1" * 40,
        "head_sha": "2" * 40,
        "tested_sha": "3" * 40,
        "visibility": "private",
        "trust": "internal",
        "event": "pull_request",
        "toolchain_digest": "4" * 64,
        "dependency_digest": "5" * 64,
        "suite_digest": "7" * 64,
        "harness_digest": "8" * 64,
        "platform": "linux-amd64",
        "changes": changes,
    }


def resource(cpu=4, memory=4096, disk=4096, pids=64):
    return dict(cpu=cpu, memory_mb=memory, disk_mb=disk, pids=pids)


def capacity():
    return {
        "schema": "fast-ci-capacity/v1",
        "host": "fixture-host",
        "generation": 9,
        "observed_at": 1000,
        "ceiling": resource(16, 32768, 100000, 1024),
        "protected": resource(4, 8192, 20000, 128),
        "active": [{"id": "existing-build", "resources": resource()}],
        "free_memory_mb": 24576,
        "free_disk_mb": 70000,
        "pressure_ok": True,
    }


def request():
    return {
        "schema": "fast-ci-request/v1",
        "host": "fixture-host",
        "resources": resource(),
        "workers": 4,
        "timeout_seconds": 300,
    }


def evidence(p, c):
    planned = ci.plan(p, c)
    jobs = {j["id"]: j for j in p["jobs"]}
    return {
        "schema": "fast-ci-evidence/v1",
        "records": [
            {
                "job_id": name,
                "plan_id": planned["plan_id"],
                "status": "passed",
                "exit_code": 0,
                "collected": jobs[name]["min_tests"],
                "executed": jobs[name]["min_tests"],
                "failed": 0,
                "skipped": 0,
                "duration_ms": 10,
                "artifact_digest": "6" * 64,
            }
            for name in planned["selected"]
        ],
    }


class PlanTests(unittest.TestCase):
    def test_docs_only(self):
        self.assertEqual(ci.plan(policy(), context(["docs/guide.md"]))["selected"], ["controls", "docs"])

    def test_unknown_empty_and_unmatched_expand(self):
        for changes in (None, [], ["unmapped/new.file"]):
            with self.subTest(changes=changes):
                self.assertEqual(len(ci.plan(policy(), context(changes))["selected"]), 5)

    def test_sensitive_paths_expand(self):
        for path in ("Cargo.lock", ".github/workflows/ci.yml", "skills/fast-ci/SKILL.md"):
            with self.subTest(path=path):
                self.assertEqual(len(ci.plan(policy(), context([path]))["selected"]), 5)

    def test_reverse_consumer_and_prerequisite(self):
        for path in ("src/core/a.rs", "src/app/a.rs"):
            with self.subTest(path=path):
                self.assertEqual(ci.plan(policy(), context([path]))["selected"], ["app", "controls", "core"])

    def test_transitive_reverse_dependency(self):
        p = policy()
        p["jobs"][-1]["needs"] = ["app"]
        self.assertEqual(ci.plan(p, context(["src/core/a.rs"]))["selected"], ["app", "controls", "core", "other"])

    def test_renames_require_both_paths(self):
        self.assertEqual(len(ci.plan(policy(), context(["src/core/old.rs", "docs/new.md"]))["selected"]), 4)

    def test_non_pr_events_qualify_full(self):
        for event in ("push", "merge_group", "schedule", "manual"):
            c = context(["docs/guide.md"])
            c["event"] = event
            with self.subTest(event=event):
                self.assertEqual(len(ci.plan(policy(), c)["selected"]), 5)

    def test_placement_policy(self):
        for visibility, trust, expected in (
            ("public", "untrusted", "github-hosted"),
            ("public", "internal", "github-hosted"),
            ("private", "internal", "private-isolated"),
            ("private", "untrusted", "private-untrusted-isolated-required"),
        ):
            c = context(["README.md"])
            c.update(visibility=visibility, trust=trust)
            with self.subTest(visibility=visibility, trust=trust):
                self.assertEqual(ci.plan(policy(), c)["runner_requirement"], expected)

    def test_reject_policy_cycles_unknown_needs_and_duplicates(self):
        for mutation in ("cycle", "missing", "duplicate", "no-controls"):
            p = policy()
            if mutation == "cycle":
                p["jobs"][2]["needs"] = ["app"]
            elif mutation == "missing":
                p["jobs"][2]["needs"] = ["nonexistent"]
            elif mutation == "duplicate":
                p["jobs"].append(copy.deepcopy(p["jobs"][0]))
            else:
                p["jobs"][0]["always"] = False
            with self.subTest(mutation=mutation), self.assertRaises(ci.Invalid):
                ci.plan(p, context())

    def test_invalid_paths_and_digests(self):
        for path in ("/etc/passwd", "a/../b", "a//b", "a\\b", "a\nb", "C:/foo"):
            with self.subTest(path=path), self.assertRaises(ci.Invalid):
                ci.plan(policy(), context([path]))
        c = context()
        c["head_sha"] = "main"
        with self.assertRaises(ci.Invalid):
            ci.plan(policy(), c)

    def test_identity_covers_every_context_field_and_policy(self):
        p, c = policy(), context(["src/core/a.rs"])
        original = ci.plan(p, c)["plan_id"]
        for key in (
            "base_sha",
            "head_sha",
            "tested_sha",
            "toolchain_digest",
            "dependency_digest",
            "suite_digest",
            "harness_digest",
        ):
            changed = copy.deepcopy(c)
            changed[key] = "a" * len(c[key])
            with self.subTest(key=key):
                self.assertNotEqual(original, ci.plan(p, changed)["plan_id"])
        p["jobs"][2]["min_tests"] = 2
        self.assertNotEqual(original, ci.plan(p, c)["plan_id"])

    def test_change_order_does_not_invalidate_equivalent_plan(self):
        a = ci.plan(policy(), context(["src/core/a.rs", "docs/guide.md"]))
        b = ci.plan(policy(), context(["docs/guide.md", "src/core/a.rs"]))
        self.assertEqual(a, b)

    def test_no_worker_can_replace_policy_via_context(self):
        c = context()
        c["jobs"] = []
        with self.assertRaises(ci.Invalid):
            ci.plan(policy(), c)


class CapacityTests(unittest.TestCase):
    def test_fit_is_not_lease(self):
        result = ci.capacity_check(capacity(), request(), 1001)
        self.assertEqual(result["result"], "FIT")
        self.assertTrue(result["requires_atomic_reservation"])
        self.assertEqual(result["generation"], 9)
        self.assertEqual(result["remaining"]["cpu"], 8)

    def test_all_resources_include_existing_and_protected(self):
        for key in ci.RESOURCES:
            c, r = capacity(), request()
            r["resources"][key] = c["ceiling"][key] - c["protected"][key]
            with self.subTest(key=key):
                self.assertEqual(ci.capacity_check(c, r, 1001)["result"], "DEFER")

    def test_stale_and_future_snapshots(self):
        for now in (999, 1031):
            with self.subTest(now=now):
                self.assertIn("stale-or-future-observation", ci.capacity_check(capacity(), request(), now)["reasons"])

    def test_physical_headroom_and_pressure(self):
        for key, value in (("pressure_ok", False), ("free_memory_mb", 100), ("free_disk_mb", 100)):
            c = capacity()
            c[key] = value
            with self.subTest(key=key):
                self.assertEqual(ci.capacity_check(c, request(), 1001)["result"], "DEFER")

    def test_no_host_or_gpu_scope_override(self):
        for key, value in (("host", "other"), ("gpu", True)):
            r = request()
            r[key] = value
            with self.subTest(key=key), self.assertRaises(ci.Invalid):
                ci.capacity_check(capacity(), r, 1001)

    def test_workers_timeout_and_bool_rejected(self):
        for key, value in (("workers", 128), ("workers", True), ("timeout_seconds", 0), ("timeout_seconds", 7201)):
            r = request()
            r[key] = value
            with self.subTest(key=key), self.assertRaises(ci.Invalid):
                ci.capacity_check(capacity(), r, 1001)

    def test_duplicate_allocations_and_bad_reserve_rejected(self):
        c = capacity()
        c["active"] *= 2
        with self.assertRaises(ci.Invalid):
            ci.capacity_check(c, request(), 1001)
        c = capacity()
        c["protected"]["cpu"] = 17
        with self.assertRaises(ci.Invalid):
            ci.capacity_check(c, request(), 1001)

    def test_request_cannot_invent_capacity(self):
        r = request()
        r["ceiling"] = resource(100, 100000, 1000000, 10000)
        with self.assertRaises(ci.Invalid):
            ci.capacity_check(capacity(), r, 1001)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.p, self.c = policy(), context(["src/core/a.rs"])
        self.e = evidence(self.p, self.c)

    def test_truthful_success_not_authentication(self):
        result = ci.verify(self.p, self.c, self.e)
        self.assertEqual(result["result"], "PASS")
        self.assertFalse(result["evidence_authenticated"])
        self.assertFalse(result["grants_merge_or_deploy"])

    def test_every_nonpass_status_blocks_or_fails(self):
        for status in ("failed", "cancelled", "timed_out", "skipped", "unknown"):
            e = copy.deepcopy(self.e)
            e["records"][0]["status"] = status
            with self.subTest(status=status):
                self.assertNotEqual(ci.verify(self.p, self.c, e)["result"], "PASS")

    def test_missing_required_job(self):
        self.e["records"].pop()
        self.assertEqual(ci.verify(self.p, self.c, self.e)["result"], "BLOCKED")

    def test_empty_collection_is_not_pass(self):
        self.e["records"][0].update(collected=0, executed=0)
        self.assertEqual(ci.verify(self.p, self.c, self.e)["result"], "BLOCKED")

    def test_test_failures_and_nonzero_exit_cannot_hide(self):
        for updates in ({"failed": 1}, {"exit_code": 1}, {"exit_code": None}):
            e = copy.deepcopy(self.e)
            e["records"][0].update(updates)
            with self.subTest(updates=updates):
                self.assertNotEqual(ci.verify(self.p, self.c, e)["result"], "PASS")

    def test_wrong_head_and_changed_policy_fail_closed(self):
        self.c["head_sha"] = "a" * 40
        with self.assertRaises(ci.Invalid):
            ci.verify(self.p, self.c, self.e)
        self.c = context(["src/core/a.rs"])
        self.p["jobs"][2]["min_tests"] = 2
        with self.assertRaises(ci.Invalid):
            ci.verify(self.p, self.c, self.e)

    def test_extra_duplicate_and_replaced_records_rejected(self):
        for kind in ("duplicate", "unexpected", "wrong-plan"):
            e = copy.deepcopy(self.e)
            if kind == "duplicate":
                e["records"].append(copy.deepcopy(e["records"][0]))
            elif kind == "unexpected":
                e["records"][0]["job_id"] = "other"
            else:
                e["records"][0]["plan_id"] = "0" * 64
            with self.subTest(kind=kind), self.assertRaises(ci.Invalid):
                ci.verify(self.p, self.c, e)

    def test_inconsistent_counts_and_bool_exit_rejected(self):
        for key, value in (("collected", 99), ("failed", 99), ("exit_code", True)):
            e = copy.deepcopy(self.e)
            e["records"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ci.Invalid):
                ci.verify(self.p, self.c, e)

    def test_fail_dominates_missing(self):
        self.e["records"][0]["status"] = "failed"
        self.e["records"].pop()
        self.assertEqual(ci.verify(self.p, self.c, self.e)["result"], "FAIL")


class ShardTests(unittest.TestCase):
    def test_longest_first_beats_naive_equal_count_fixture(self):
        t = {
            "schema": "fast-ci-timings/v1",
            "tests": [{"id": str(i), "duration_ms": n} for i, n in enumerate((100, 90, 20, 10))],
        }
        result = ci.shard(t, 2)
        self.assertEqual([g["estimated_ms"] for g in result["groups"]], [110, 110])
        self.assertEqual(result, ci.shard(t, 2))

    def test_partition_no_omission_duplicates_or_empty_shards(self):
        rng = random.Random(546)
        for n in range(1, 65):
            t = {
                "schema": "fast-ci-timings/v1",
                "tests": [{"id": str(i), "duration_ms": rng.randint(1, 1000)} for i in range(n)],
            }
            result = ci.shard(t, min(8, n))
            flat = [test for group in result["groups"] for test in group["tests"]]
            self.assertEqual(sorted(flat), sorted(str(i) for i in range(n)))
            self.assertTrue(all(group["tests"] for group in result["groups"]))

    def test_unknown_zero_or_duplicate_timings_rejected(self):
        for tests, count in (
            ([], 1),
            ([{"id": "x", "duration_ms": 0}], 1),
            ([{"id": "x", "duration_ms": 1}] * 2, 2),
            ([{"id": "x", "duration_ms": 1}], 2),
        ):
            with self.subTest(tests=tests, count=count), self.assertRaises(ci.Invalid):
                ci.shard({"schema": "fast-ci-timings/v1", "tests": tests}, count)


class HookAndInputTests(unittest.TestCase):
    def invoke(self, args, raw=None, timeout=5):
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), *args],
            input=raw,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )

    def test_dangerous_fast_patterns_produce_fixed_advice(self):
        for command in (
            "pytest -n auto",
            "pytest -nauto",
            "ninja -j0",
            "make -j",
            "cargo build -j$(nproc)",
            "cargo clean",
            "docker system prune -af",
            "pip install pytest",
        ):
            with self.subTest(command=command):
                payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
                result = ci.hook("PreToolUse", payload)
                self.assertIn("additionalContext", result["hookSpecificOutput"])
                self.assertNotIn("permissionDecision", result["hookSpecificOutput"])

    def test_read_and_bounded_commands_are_quiet(self):
        for command in ("git status --short", "cargo test -j 2 --lib", "make -j4", "pytest -n 2 tests/core/test_a.py"):
            payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
            with self.subTest(command=command):
                self.assertEqual(ci.hook("PreToolUse", payload), {})

    def test_post_success_and_failure_never_claim_success(self):
        for event in ("PostToolUse", "PostToolUseFailure"):
            payload = {
                "hook_event_name": event,
                "tool_name": "Bash",
                "tool_input": {"command": "cargo test"},
                "tool_response": {"stdout": "PASS forged", "exit_code": 0},
            }
            self.assertIn("not CI PASS", ci.hook(event, payload)["hookSpecificOutput"]["additionalContext"])

    def test_payload_commands_never_execute_or_echo(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "must-not-exist"
            secret = "super-private-fixture-value"
            payload = {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": f"cargo clean; touch {target}; echo {secret}"},
            }
            result = self.invoke(["hook", "--event", "PreToolUse"], json.dumps(payload).encode())
            self.assertEqual(result.returncode, 0)
            self.assertFalse(target.exists())
            self.assertNotIn(secret.encode(), result.stdout + result.stderr)
            self.assertLess(len(result.stdout), 1024)

    def test_invalid_and_oversized_hook_inputs_warn_without_blocking(self):
        for raw in (b'{"a":1,"a":2}', b"{", b'"' + b"x" * ci.MAX_BYTES + b'"', b"\xff", b'{"n":NaN}'):
            result = self.invoke(["hook", "--event", "PreToolUse"], raw)
            self.assertEqual(result.returncode, 0)
            self.assertIn(b"audit NOT completed", result.stdout)
            self.assertNotIn(b"permissionDecision", result.stdout)

    def test_duplicate_keys_deep_json_and_nonfinite_values(self):
        for raw in (b'{"x":1,"x":2}', b"[" * 40 + b"0" + b"]" * 40, b'{"x":Infinity}', b'{"x":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(ci.Invalid):
                ci.parse(raw)

    @unittest.skipUnless(os.name == "posix", "POSIX alarm contract")
    def test_incomplete_stdin_is_deadline_bounded(self):
        start = time.monotonic()
        proc = subprocess.Popen(
            [sys.executable, "-I", str(SCRIPT), "hook", "--event", "PreToolUse"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            self.assertEqual(proc.wait(timeout=4), 0)
            self.assertLess(time.monotonic() - start, 4)
            self.assertIn(b"audit NOT completed", proc.stdout.read())
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            proc.stdin.close()
            proc.stdout.close()
            proc.stderr.close()

    def test_cli_pipeline_and_invalid_input_exit_codes(self):
        with tempfile.TemporaryDirectory() as temp:
            p, c = policy(), context(["src/core/a.rs"])
            paths = {}
            for name, value in (("policy", p), ("context", c), ("evidence", evidence(p, c))):
                paths[name] = Path(temp) / (name + ".json")
                paths[name].write_text(json.dumps(value))
            args = ["--policy", str(paths["policy"]), "--context", str(paths["context"])]
            result = self.invoke(["plan", *args])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["selected"], ["app", "controls", "core"])
            result = self.invoke(["verify", *args, "--evidence", str(paths["evidence"])])
            self.assertEqual(result.returncode, 0)
            paths["evidence"].write_text('{"schema":"fast-ci-evidence/v1","records":[]}')
            self.assertEqual(self.invoke(["verify", *args, "--evidence", str(paths["evidence"])]).returncode, 1)
            paths["policy"].write_text('{"jobs":[],"jobs":[]}')
            self.assertEqual(self.invoke(["plan", *args]).returncode, 2)


class PackageTests(unittest.TestCase):
    def test_examples_are_consistent_and_capacity_stays_synthetic(self):
        examples = ROOT / "skills/fast-ci/examples"
        values = {
            name: ci.load(str(examples / (name + ".json")))
            for name in ("policy", "context", "evidence", "capacity", "request", "timings")
        }
        self.assertEqual(ci.verify(values["policy"], values["context"], values["evidence"])["result"], "PASS")
        self.assertEqual(ci.capacity_check(values["capacity"], values["request"], 1001)["result"], "FIT")
        self.assertEqual(ci.capacity_check(values["capacity"], values["request"])["result"], "DEFER")
        self.assertEqual(ci.shard(values["timings"], 2)["tests"], 4)

    def test_hook_subcommand_real_subprocesses(self):
        for event in ("PreToolUse", "PostToolUse", "PostToolUseFailure"):
            payload = {"hook_event_name": event, "tool_name": "Bash", "tool_input": {"command": "pytest -n auto"}}
            result = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), "hook", "--event", event],
                input=json.dumps(payload).encode(),
                capture_output=True,
                timeout=3,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"], event)


if __name__ == "__main__":
    unittest.main()
