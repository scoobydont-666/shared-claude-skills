#!/usr/bin/env python3
"""Fast CI: pure planning, capacity arithmetic, evidence checks and advisory hooks.

No execution, network, scheduler, cache deletion, lease creation or approval.
All policy/context/capacity/evidence inputs require custody in the host harness.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import re
import signal
import sys
import time
from pathlib import Path

MAX_BYTES = 131072
MAX_ITEMS = 512
RESOURCES = {"cpu", "memory_mb", "disk_mb", "pids"}
IDENTITY = {
    "repository",
    "base_sha",
    "head_sha",
    "tested_sha",
    "visibility",
    "trust",
    "event",
    "toolchain_digest",
    "dependency_digest",
    "suite_digest",
    "harness_digest",
    "platform",
}
EVENTS = {"pull_request", "push", "merge_group", "schedule", "manual"}


class Invalid(ValueError):
    """Input is malformed or cannot safely express the requested operation."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Invalid(reason)


def obj(value: object, keys: set[str]) -> dict:
    require(type(value) is dict and set(value) == keys, "object fields")
    return value


def integer(value: object, low: int = 0, high: int = 10**12) -> int:
    require(type(value) is int and low <= value <= high, "integer bounds")
    return value


def text(value: object, limit: int = 256) -> str:
    require(type(value) is str and 0 < len(value) <= limit, "string bounds")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in value), "control character")
    return value


def items(value: object, low: int = 0, high: int = MAX_ITEMS) -> list:
    require(type(value) is list and low <= len(value) <= high, "list bounds")
    return value


def digest(value: object, git: bool = False) -> str:
    text(value)
    require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}" if git else r"[0-9a-f]{64}", value) is not None, "digest shape")
    return value


def unique(values: list) -> None:
    require(len(values) == len(set(values)), "duplicate value")


def path(value: object) -> str:
    value = text(value, 1024)
    require(not value.startswith("/") and "\\" not in value and ":" not in value, "relative POSIX path required")
    require(all(p not in {"", ".", ".."} for p in value.split("/")), "path traversal")
    return value


def encode(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def hashed(value: object) -> str:
    return hashlib.sha256(encode(value)).hexdigest()


def pairs(values: list) -> dict:
    result = {}
    for key, value in values:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def nesting(value: object, depth: int = 0) -> None:
    require(depth <= 32, "nesting limit")
    if type(value) is dict:
        require(len(value) <= MAX_ITEMS, "object limit")
        for child in value.values():
            nesting(child, depth + 1)
    elif type(value) is float:
        require(math.isfinite(value), "nonfinite number")
    elif type(value) is list:
        require(len(value) <= MAX_ITEMS, "list limit")
        for child in value:
            nesting(child, depth + 1)


def parse(raw: bytes) -> object:
    require(len(raw) <= MAX_BYTES, "input limit")
    value = json.loads(
        raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=lambda _: require(False, "nonfinite number")
    )
    nesting(value)
    return value


def load(filename: str) -> object:
    if filename == "-":
        return parse(sys.stdin.buffer.read(MAX_BYTES + 1))
    with Path(filename).open("rb") as source:
        return parse(source.read(MAX_BYTES + 1))


def validate_policy(policy: object) -> dict:
    obj(policy, {"schema", "jobs", "global_paths"})
    require(policy["schema"] == "fast-ci-policy/v1", "policy schema")
    for pattern in items(policy["global_paths"], 1):
        path(pattern)
    jobs = items(policy["jobs"], 1, 128)
    ids = []
    for job in jobs:
        obj(job, {"id", "paths", "needs", "always", "min_tests"})
        require(re.fullmatch(r"[a-z][a-z0-9-]{0,63}", text(job["id"])) is not None, "job identifier")
        ids.append(job["id"])
        for pattern in items(job["paths"], 1):
            path(pattern)
        for need in items(job["needs"], 0, 128):
            text(need)
        unique(job["needs"])
        require(type(job["always"]) is bool, "always boolean")
        integer(job["min_tests"], 0, 10**7)
    unique(ids)
    require(any(job["always"] for job in jobs), "mandatory control job required")
    by_id = {job["id"]: job for job in jobs}
    visiting, done = set(), set()

    def visit(name: str) -> None:
        require(name in by_id, "unknown prerequisite")
        require(name not in visiting, "dependency cycle")
        if name in done:
            return
        visiting.add(name)
        for need in by_id[name]["needs"]:
            visit(need)
        visiting.remove(name)
        done.add(name)

    for name in ids:
        visit(name)
    return by_id


def validate_context(context: object) -> dict:
    obj(context, IDENTITY | {"schema", "changes"})
    require(context["schema"] == "fast-ci-context/v1", "context schema")
    require(
        re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text(context["repository"])) is not None, "repository identity"
    )
    for key in ("base_sha", "head_sha", "tested_sha"):
        digest(context[key], git=True)
    for key in ("toolchain_digest", "dependency_digest", "suite_digest", "harness_digest"):
        digest(context[key])
    text(context["platform"])
    require(context["visibility"] in {"public", "private"}, "repository visibility")
    require(context["trust"] in {"internal", "untrusted"}, "trust class")
    require(context["event"] in EVENTS, "event")
    if context["changes"] is not None:
        for changed in items(context["changes"]):
            path(changed)
        unique(context["changes"])
    return context


def plan(policy: object, context: object) -> dict:
    """Select affected jobs plus reverse dependents and prerequisite closure.

    Unknown or empty change evidence expands to ALL jobs; no implicit docs skip.
    Paths must include both sides of renames/deletes from a trusted diff producer.
    """
    jobs = validate_policy(policy)
    validate_context(context)
    changed = context["changes"]
    selected = {name for name, job in jobs.items() if job["always"]}
    matched = set()
    for name, job in jobs.items():
        for filename in changed or []:
            if any(fnmatch.fnmatchcase(filename, p) for p in job["paths"]):
                selected.add(name)
                matched.add(filename)
    global_change = any(fnmatch.fnmatchcase(f, p) for f in changed or [] for p in policy["global_paths"])
    full = (
        not changed
        or global_change
        or set(changed) - matched
        or context["event"] in {"push", "merge_group", "schedule", "manual"}
    )
    if full:
        selected = set(jobs)
        reason = "conservative-full"
    else:
        reason = "affected-and-dependencies"
        # First traverse reverse dependents of directly affected/always jobs.
        # Then prerequisites; this avoids expanding unrelated sibling consumers
        # solely because they share a prerequisite added in the second phase.
        while True:
            before = set(selected)
            selected |= {n for n, j in jobs.items() if set(j["needs"]) & selected}
            if selected == before:
                break
        while True:
            before = set(selected)
            selected |= {dep for n in selected for dep in jobs[n]["needs"]}
            if selected == before:
                break
    result = {
        "schema": "fast-ci-plan/v1",
        "identity": {k: context[k] for k in sorted(IDENTITY)},
        "policy_digest": hashed(policy),
        "context_digest": hashed({**context, "changes": None if changed is None else sorted(changed)}),
        "runner_requirement": (
            "github-hosted"
            if context["visibility"] == "public"
            else "private-isolated"
            if context["trust"] == "internal"
            else "private-untrusted-isolated-required"
        ),
        "selected": sorted(selected),
        "reason": reason,
        "not_applicable": sorted(set(jobs) - selected),
    }
    result["plan_id"] = hashed(result)
    return result


def resources(value: object) -> dict:
    obj(value, RESOURCES)
    for amount in value.values():
        integer(amount)
    return value


def capacity_check(capacity: object, request: object, now: float | None = None) -> dict:
    """A fit calculation, NOT a reservation. Run under the existing allocator lock."""
    obj(
        capacity,
        {
            "schema",
            "host",
            "generation",
            "observed_at",
            "ceiling",
            "protected",
            "active",
            "free_memory_mb",
            "free_disk_mb",
            "pressure_ok",
        },
    )
    obj(request, {"schema", "host", "resources", "workers", "timeout_seconds"})
    require(capacity["schema"] == "fast-ci-capacity/v1", "capacity schema")
    require(request["schema"] == "fast-ci-request/v1", "request schema")
    text(capacity["host"])
    text(request["host"])
    require(capacity["host"] == request["host"], "wrong host")
    integer(capacity["generation"], 1)
    observed = capacity["observed_at"]
    require(type(observed) in {int, float} and math.isfinite(observed), "timestamp")
    now = time.time() if now is None else now
    require(type(now) in {int, float} and math.isfinite(now), "clock")
    integer(request["timeout_seconds"], 1, 7200)
    workers = integer(request["workers"], 1, 256)
    wanted = resources(request["resources"])
    require(all(v > 0 for v in wanted.values()), "positive request required")
    require(workers <= wanted["cpu"] and workers <= wanted["pids"], "worker budget")
    ceiling = resources(capacity["ceiling"])
    protected = resources(capacity["protected"])
    require(all(protected[k] <= ceiling[k] for k in RESOURCES), "invalid protected reserve")
    remaining = {k: ceiling[k] - protected[k] for k in RESOURCES}
    ids = []
    for allocation in items(capacity["active"], 0, 128):
        obj(allocation, {"id", "resources"})
        ids.append(text(allocation["id"]))
        for key, amount in resources(allocation["resources"]).items():
            remaining[key] -= amount
    unique(ids)
    integer(capacity["free_memory_mb"])
    integer(capacity["free_disk_mb"])
    require(type(capacity["pressure_ok"]) is bool, "pressure boolean")
    reasons = []
    if not 0 <= now - observed <= 30:
        reasons.append("stale-or-future-observation")
    if not capacity["pressure_ok"]:
        reasons.append("host-pressure")
    reasons += ["insufficient-" + k for k in sorted(RESOURCES) if wanted[k] > remaining[k]]
    if wanted["memory_mb"] + protected["memory_mb"] > capacity["free_memory_mb"]:
        reasons.append("physical-memory-headroom")
    if wanted["disk_mb"] + protected["disk_mb"] > capacity["free_disk_mb"]:
        reasons.append("physical-disk-headroom")
    return {
        "schema": "fast-ci-fit/v1",
        "result": "DEFER" if reasons else "FIT",
        "reasons": reasons,
        "remaining": remaining,
        "generation": capacity["generation"],
        "requires_atomic_reservation": True,
        "workers": workers,
    }


def verify(policy: object, context: object, evidence: object) -> dict:
    """Recompute expected jobs from custodied inputs, never worker-supplied plan."""
    expected = plan(policy, context)
    obj(evidence, {"schema", "records"})
    require(evidence["schema"] == "fast-ci-evidence/v1", "evidence schema")
    jobs = validate_policy(policy)
    seen, failures, blocked = set(), [], []
    for record in items(evidence["records"], 0, 128):
        obj(
            record,
            {
                "job_id",
                "plan_id",
                "status",
                "exit_code",
                "collected",
                "executed",
                "failed",
                "skipped",
                "duration_ms",
                "artifact_digest",
            },
        )
        name = text(record["job_id"])
        require(name not in seen, "duplicate job evidence")
        require(name in expected["selected"], "unexpected job evidence")
        seen.add(name)
        require(digest(record["plan_id"]) == expected["plan_id"], "wrong plan identity")
        digest(record["artifact_digest"])
        for key in ("collected", "executed", "failed", "skipped", "duration_ms"):
            integer(record[key])
        if record["exit_code"] is not None:
            integer(record["exit_code"], -255, 255)
        require(record["collected"] == record["executed"] + record["skipped"], "test accounting")
        require(record["failed"] <= record["executed"], "failure accounting")
        status = record["status"]
        require(status in {"passed", "failed", "skipped", "cancelled", "timed_out", "unknown"}, "job status")
        if status == "failed" or record["failed"] or record["exit_code"] not in {0, None}:
            failures.append(name)
        elif status != "passed" or record["exit_code"] != 0 or record["executed"] < jobs[name]["min_tests"]:
            blocked.append(name)
    blocked += sorted(set(expected["selected"]) - seen)
    return {
        "schema": "fast-ci-summary/v1",
        "plan_id": expected["plan_id"],
        "result": "FAIL" if failures else "BLOCKED" if blocked else "PASS",
        "failed": sorted(failures),
        "blocked": sorted(blocked),
        "expected": expected["selected"],
        "not_applicable": expected["not_applicable"],
        "evidence_authenticated": False,
        "grants_merge_or_deploy": False,
    }


def shard(timings: object, count: int) -> dict:
    """Deterministic longest-processing-time placement; never drops a test."""
    obj(timings, {"schema", "tests"})
    require(timings["schema"] == "fast-ci-timings/v1", "timings schema")
    tests = items(timings["tests"], 1)
    integer(count, 1, min(32, len(tests)))
    names = []
    for test in tests:
        obj(test, {"id", "duration_ms"})
        names.append(text(test["id"], 1024))
        integer(test["duration_ms"], 1, 86400000)
    unique(names)
    groups = [{"tests": [], "estimated_ms": 0} for _ in range(count)]
    for test in sorted(tests, key=lambda t: (-t["duration_ms"], t["id"])):
        index = min(range(count), key=lambda i: (groups[i]["estimated_ms"], i))
        groups[index]["tests"].append(test["id"])
        groups[index]["estimated_ms"] += test["duration_ms"]
    return {"schema": "fast-ci-shards/v1", "groups": groups, "tests": len(tests), "estimates_are_not_evidence": True}


CI_COMMAND = re.compile(r"\b(cargo|pytest|make|ninja|ctest|tox|uv|pip|npm|pnpm)\b|\bgo\s+test\b")
WARNINGS = (
    (
        r"\bnproc\b|(?:-n|--numprocesses)(?:\s*|=)auto\b|(?:-j|--jobs)(?:\s*|=)0\b",
        "unbounded-parallelism: use the admitted CPU/memory worker count, not host nproc or auto.",
    ),
    (
        r"\b(?:make|ninja)\b[^\n;]*\s-j(?:\s*(?:$|[;&|])|\s+--)",
        "unbounded-make: a bare -j can exhaust the host; require an explicit admitted limit.",
    ),
    (
        r"\bcargo\s+clean\b|\b(?:docker|podman)\s+(?:system|builder)\s+prune\b",
        "cache-destruction: preserve shared caches; inspect scoped ownership and retention first.",
    ),
    (
        r"\b(cargo\s+test[^\n;]*--workspace|pytest\s+tests/?(?:\s|$)|go\s+test\s+\./\.\.\.)",
        "broad-suite: use the affected plan first; retain full tests where risk or policy requires them.",
    ),
    (
        r"\b(?:pip|uv\s+pip)\s+install\b",
        "dependency-bootstrap: reuse a job-private pinned environment; avoid repeated installs per step.",
    ),
)


def hook(event: str, payload: object) -> dict:
    require(event in {"PreToolUse", "PostToolUse", "PostToolUseFailure"}, "unsupported hook event")
    require(type(payload) is dict, "hook envelope")
    require(payload.get("hook_event_name") == event, "hook event mismatch")
    if payload.get("tool_name") != "Bash":
        return {}
    tool = payload.get("tool_input")
    require(type(tool) is dict and type(tool.get("command")) is str, "hook command")
    command = tool["command"]
    require(len(command) <= 32768, "command limit")
    if event == "PreToolUse":
        advice = [message for pattern, message in WARNINGS if re.search(pattern, command)]
    else:
        advice = (
            [
                "Record exact-head structured CI evidence and all attempts; a tool return is not CI PASS. "
                "Diagnose the first cause before any bounded retry."
            ]
            if CI_COMMAND.search(command)
            else []
        )
    if not advice:
        return {}
    return {
        "hookSpecificOutput": {"hookEventName": event, "additionalContext": "fast-ci (advisory): " + " ".join(advice)}
    }


def expired(_signum: int, _frame: object) -> None:
    raise Invalid("input deadline")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in ("plan", "verify"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--policy", required=True)
        cmd.add_argument("--context", required=True)
        if name == "verify":
            cmd.add_argument("--evidence", required=True)
    cmd = sub.add_parser("fit")
    cmd.add_argument("--capacity", required=True)
    cmd.add_argument("--request", required=True)
    cmd = sub.add_parser("shard")
    cmd.add_argument("--timings", required=True)
    cmd.add_argument("--count", type=int, required=True)
    cmd = sub.add_parser("hook")
    cmd.add_argument("--event", choices=["PreToolUse", "PostToolUse", "PostToolUseFailure"], required=True)
    args = parser.parse_args()
    # Hooks also need a runtime-owned timeout, especially on non-POSIX hosts.
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, expired)
        signal.alarm(2)
    try:
        if args.operation == "plan":
            result = plan(load(args.policy), load(args.context))
        elif args.operation == "verify":
            result = verify(load(args.policy), load(args.context), load(args.evidence))
        elif args.operation == "fit":
            result = capacity_check(load(args.capacity), load(args.request))
        elif args.operation == "shard":
            result = shard(load(args.timings), args.count)
        else:
            result = hook(args.event, load("-"))
        print(encode(result).decode())
        return 0 if result.get("result", "PASS") in {"PASS", "FIT"} else 1
    except (Invalid, ValueError, TypeError, KeyError, OSError, RecursionError):
        # Never echo payloads, commands, exception text or credential-bearing paths.
        result = (
            {"systemMessage": "fast-ci: invalid or unavailable hook input; audit NOT completed."}
            if args.operation == "hook"
            else {"result": "BLOCKED", "reason": "invalid-input"}
        )
        print(encode(result).decode())
        return 0 if args.operation == "hook" else 2
    finally:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)


if __name__ == "__main__":
    raise SystemExit(main())
