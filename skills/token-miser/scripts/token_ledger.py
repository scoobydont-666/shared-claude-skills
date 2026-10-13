#!/usr/bin/env python3
"""Append validated call receipts; summarize paired benchmark observations."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import math
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any


PHASES = ("baseline", "after")
IDENTITY_FIELDS = ("benchmark_sha256", "input_sha256", "rubric_sha256")
REQUIRED = {
    "schema_version",
    "call_id",
    "phase",
    "task_id",
    "declared_model",
    "actual_model",
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "cost_usd",
    "latency_ms",
    "quality",
    "success",
    "pricing_source",
    "pricing_as_of",
} | set(IDENTITY_FIELDS)


def bounded_number(value: str, *, maximum: float | None = None) -> float:
    parsed = float(value)
    if (
        not math.isfinite(parsed)
        or parsed < 0
        or (maximum is not None and parsed > maximum)
    ):
        limit = f" and <= {maximum}" if maximum is not None else ""
        raise argparse.ArgumentTypeError(f"must be finite, non-negative{limit}")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def sha256_digest(value: str) -> str:
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise argparse.ArgumentTypeError("must be 64 lowercase hexadecimal characters")
    return value


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"invalid ISO pricing date: {value}") from error


def validate(
    record: dict[str, Any], *, today: dt.date, max_pricing_age_days: int
) -> None:
    missing = REQUIRED - record.keys()
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    if record["schema_version"] != 1:
        raise ValueError("unsupported schema_version")
    if record["phase"] not in PHASES:
        raise ValueError(f"invalid phase: {record['phase']}")
    if record["declared_model"] != record["actual_model"]:
        raise ValueError(
            f"model mismatch for {record['call_id']}: declared "
            f"{record['declared_model']!r}, actual {record['actual_model']!r}"
        )
    pricing_date = parse_date(record["pricing_as_of"])
    age = (today - pricing_date).days
    if age < 0 or age > max_pricing_age_days:
        raise ValueError(f"stale pricing for {record['call_id']}: age {age} days")
    if not record["pricing_source"].strip():
        raise ValueError("pricing_source must not be empty")
    for field in ("input_tokens", "output_tokens", "cached_input_tokens"):
        if (
            not isinstance(record[field], int)
            or isinstance(record[field], bool)
            or record[field] < 0
        ):
            raise ValueError(f"{field} must be a non-negative integer")
    for field in ("cost_usd", "latency_ms", "quality"):
        value = record[field]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(f"{field} must be finite and non-negative")
    if record["quality"] > 10:
        raise ValueError("quality must be <= 10")
    if not isinstance(record["success"], bool):
        raise ValueError("success must be boolean")
    for field in IDENTITY_FIELDS:
        value = record[field]
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"{field} must be 64 lowercase hexadecimal characters")


def read_records(
    stream: Any, *, source: str, today: dt.date, max_pricing_age_days: int
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    call_ids: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    for line_number, line in enumerate(stream, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{source}:{line_number}: corrupt JSON: {error.msg}"
            ) from error
        if not isinstance(record, dict):
            raise ValueError(f"{source}:{line_number}: record must be an object")
        try:
            validate(record, today=today, max_pricing_age_days=max_pricing_age_days)
        except ValueError as error:
            raise ValueError(f"{source}:{line_number}: {error}") from error
        call_id = record["call_id"]
        pair = (record["phase"], record["task_id"])
        if call_id in call_ids:
            raise ValueError(f"{source}:{line_number}: duplicate call_id: {call_id}")
        if pair in pairs:
            raise ValueError(
                f"{source}:{line_number}: duplicate phase/task: {pair[0]}/{pair[1]}"
            )
        call_ids.add(call_id)
        pairs.add(pair)
        records.append(record)
    return records


def load_records(
    path: Path, *, today: dt.date, max_pricing_age_days: int
) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        records = read_records(
            stream,
            source=str(path),
            today=today,
            max_pricing_age_days=max_pricing_age_days,
        )
    if not records:
        raise ValueError(f"{path}: no records")
    return records


def append_record(
    path: Path, record: dict[str, Any], *, today: dt.date, max_pricing_age_days: int
) -> None:
    validate(record, today=today, max_pricing_age_days=max_pricing_age_days)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        existing = read_records(
            stream,
            source=str(path),
            today=today,
            max_pricing_age_days=max_pricing_age_days,
        )
        if any(row["call_id"] == record["call_id"] for row in existing):
            raise ValueError(f"duplicate call_id: {record['call_id']}")
        if any(
            (row["phase"], row["task_id"]) == (record["phase"], record["task_id"])
            for row in existing
        ):
            raise ValueError(
                f"duplicate phase/task: {record['phase']}/{record['task_id']}"
            )
        stream.seek(0, 2)
        stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush()


def percent_saved(before: float, after: float) -> float | None:
    return None if before == 0 else round((before - after) / before * 100, 6)


def summarize(records: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    call_ids: set[str] = set()
    for row in records:
        call_id = row["call_id"]
        pair = (row["phase"], row["task_id"])
        if call_id in call_ids:
            raise ValueError(f"duplicate call_id: {call_id}")
        if pair in indexed:
            raise ValueError(f"duplicate phase/task: {pair[0]}/{pair[1]}")
        call_ids.add(call_id)
        indexed[pair] = row
    baseline_tasks = {task for phase, task in indexed if phase == "baseline"}
    after_tasks = {task for phase, task in indexed if phase == "after"}
    matched = sorted(baseline_tasks & after_tasks)
    unmatched = sorted(baseline_tasks ^ after_tasks)
    if not matched:
        raise ValueError("no paired baseline/after tasks")
    workload_identities = []
    for task in matched:
        baseline_row = indexed[("baseline", task)]
        after_row = indexed[("after", task)]
        mismatched = [
            field
            for field in IDENTITY_FIELDS
            if baseline_row[field] != after_row[field]
        ]
        if mismatched:
            raise ValueError(
                f"workload identity mismatch for task {task}: {', '.join(mismatched)}"
            )
        workload_identities.append(
            {
                "task_id": task,
                **{field: baseline_row[field] for field in IDENTITY_FIELDS},
            }
        )

    def aggregate(phase: str) -> dict[str, Any]:
        rows = [indexed[(phase, task)] for task in matched]
        return {
            "calls": len(rows),
            "tokens": sum(row["input_tokens"] + row["output_tokens"] for row in rows),
            "cached_input_tokens": sum(row["cached_input_tokens"] for row in rows),
            "cost_usd": round(sum(row["cost_usd"] for row in rows), 10),
            "mean_latency_ms": round(
                sum(row["latency_ms"] for row in rows) / len(rows), 6
            ),
            "mean_quality": round(sum(row["quality"] for row in rows) / len(rows), 6),
            "all_successful": all(row["success"] for row in rows),
        }

    baseline, after = aggregate("baseline"), aggregate("after")
    quality_delta = round(after["mean_quality"] - baseline["mean_quality"], 6)
    quality_regressions = []
    decimal_tolerance = Decimal(str(tolerance))
    for task in matched:
        before_quality = indexed[("baseline", task)]["quality"]
        after_quality = indexed[("after", task)]["quality"]
        raw_task_delta = after_quality - before_quality
        exact_task_delta = Decimal(str(after_quality)) - Decimal(str(before_quality))
        if exact_task_delta < -decimal_tolerance:
            quality_regressions.append(
                {
                    "task_id": task,
                    "baseline": before_quality,
                    "after": after_quality,
                    "delta": round(raw_task_delta, 6),
                }
            )
    parity = (
        not quality_regressions
        and baseline["all_successful"]
        and after["all_successful"]
    )
    cost_savings = percent_saved(baseline["cost_usd"], after["cost_usd"])
    token_savings = percent_saved(baseline["tokens"], after["tokens"])
    measurable_savings = any(
        saving is not None and saving > 0 for saving in (cost_savings, token_savings)
    )
    complete_pairing = not unmatched
    return {
        "schema_version": 1,
        "paired_tasks": matched,
        "workload_identities": workload_identities,
        "unmatched_tasks": unmatched,
        "quality_tolerance": tolerance,
        "quality_delta": quality_delta,
        "quality_regressions": quality_regressions,
        "quality_parity": parity,
        "complete_pairing": complete_pairing,
        "measurable_savings": measurable_savings,
        "optimization_pass": parity and complete_pairing and measurable_savings,
        "baseline": baseline,
        "after": after,
        "savings": {
            "tokens_percent": token_savings,
            "cost_percent": cost_savings,
            "latency_percent": percent_saved(
                baseline["mean_latency_ms"], after["mean_latency_ms"]
            ),
        },
    }


def markdown(report: dict[str, Any]) -> str:
    before, after, savings = report["baseline"], report["after"], report["savings"]
    regressed = (
        ", ".join(
            f"{row['task_id']} ({row['delta']})"
            for row in report["quality_regressions"]
        )
        or "none"
    )
    return (
        "\n".join(
            [
                "# Token-Miser Receipt Summary",
                "",
                f"Quality parity: **{'PASS' if report['quality_parity'] else 'FAIL'}** "
                f"(delta {report['quality_delta']}, tolerance {report['quality_tolerance']})",
                "",
                "| Metric | Baseline | After | Savings % |",
                "|---|---:|---:|---:|",
                f"| Tokens | {before['tokens']} | {after['tokens']} | {savings['tokens_percent']} |",
                f"| Cost USD | {before['cost_usd']} | {after['cost_usd']} | {savings['cost_percent']} |",
                f"| Mean latency ms | {before['mean_latency_ms']} | {after['mean_latency_ms']} | {savings['latency_percent']} |",
                "",
                f"Regressed tasks: {regressed}",
                f"Paired tasks: {len(report['paired_tasks'])}; unmatched: {len(report['unmatched_tasks'])}",
            ]
        )
        + "\n"
    )


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument(
        "--today", type=parse_date, default=dt.date.today(), help=argparse.SUPPRESS
    )
    root.add_argument("--max-pricing-age-days", type=nonnegative_int, default=2)
    commands = root.add_subparsers(dest="command", required=True)
    record = commands.add_parser("record", help="append one provider call receipt")
    record.add_argument("ledger", type=Path)
    for option in (
        "call-id",
        "task-id",
        "declared-model",
        "actual-model",
        "pricing-source",
        "pricing-as-of",
    ):
        record.add_argument(f"--{option}", required=True)
    for option in ("benchmark-sha256", "input-sha256", "rubric-sha256"):
        record.add_argument(f"--{option}", type=sha256_digest, required=True)
    record.add_argument("--phase", choices=PHASES, required=True)
    record.add_argument("--input-tokens", type=nonnegative_int, required=True)
    record.add_argument("--output-tokens", type=nonnegative_int, required=True)
    record.add_argument("--cached-input-tokens", type=nonnegative_int, default=0)
    record.add_argument(
        "--cost-usd", type=lambda value: bounded_number(value), required=True
    )
    record.add_argument(
        "--latency-ms", type=lambda value: bounded_number(value), required=True
    )
    record.add_argument(
        "--quality", type=lambda value: bounded_number(value, maximum=10), required=True
    )
    outcome = record.add_mutually_exclusive_group(required=True)
    outcome.add_argument("--success", action="store_true")
    outcome.add_argument("--failure", dest="success", action="store_false")
    report = commands.add_parser(
        "report", help="summarize receipts from the canonical benchmark"
    )
    report.add_argument("ledger", type=Path)
    report.add_argument(
        "--quality-tolerance",
        type=lambda value: bounded_number(value, maximum=10),
        default=0.1,
    )
    report.add_argument("--format", choices=("json", "markdown"), default="json")
    return root


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "record":
            record = {
                "schema_version": 1,
                "call_id": args.call_id,
                "phase": args.phase,
                "task_id": args.task_id,
                "declared_model": args.declared_model,
                "actual_model": args.actual_model,
                "input_tokens": args.input_tokens,
                "output_tokens": args.output_tokens,
                "cached_input_tokens": args.cached_input_tokens,
                "cost_usd": args.cost_usd,
                "latency_ms": args.latency_ms,
                "quality": args.quality,
                "success": args.success,
                "pricing_source": args.pricing_source,
                "pricing_as_of": args.pricing_as_of,
                "benchmark_sha256": args.benchmark_sha256,
                "input_sha256": args.input_sha256,
                "rubric_sha256": args.rubric_sha256,
            }
            append_record(
                args.ledger,
                record,
                today=args.today,
                max_pricing_age_days=args.max_pricing_age_days,
            )
            return 0
        report = summarize(
            load_records(
                args.ledger,
                today=args.today,
                max_pricing_age_days=args.max_pricing_age_days,
            ),
            args.quality_tolerance,
        )
        sys.stdout.write(
            markdown(report)
            if args.format == "markdown"
            else json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        return 0 if report["optimization_pass"] else 2
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
