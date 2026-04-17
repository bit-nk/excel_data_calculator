"""CLI for the UAT parallel-run validation harness.

Usage:
    python -m scripts.parallel_run --report-id 42 --baseline baseline_2026-03.csv
    python -m scripts.parallel_run --report-id 42 --baseline baseline.csv --tolerance 0.05 --json

Exits non-zero when reconciliation fails, so it can be wired into CI as a
gate before a report is marked SENT_TO_ACCOUNTING during the parallel-run
billing cycle required by SoW §5 Phase 5.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path

from app.core.database import async_session
from app.services.parallel_run import ParallelRunValidator


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Parallel-run reconciliation")
    p.add_argument("--report-id", type=int, required=True, help="ChargebackReport.id to reconcile")
    p.add_argument("--baseline", type=Path, required=True, help="Path to baseline CSV")
    p.add_argument("--tolerance", type=Decimal, default=Decimal("0.01"), help="Per-line $ tolerance")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a human-readable summary")
    return p


async def _run(args) -> int:
    csv_text = args.baseline.read_text(encoding="utf-8")
    async with async_session() as session:
        validator = ParallelRunValidator(session, tolerance=args.tolerance)
        result = await validator.reconcile(args.report_id, csv_text)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        _print_human(result)

    return 0 if result.passed else 1


def _print_human(result) -> None:
    print(f"Report:        {result.report_id} ({result.billing_period})")
    print(f"Tolerance:     ${result.tolerance}")
    print(f"Status:        {'PASS' if result.passed else 'FAIL'}")
    if result.missing_in_engine:
        print(f"Missing in engine:   {', '.join(result.missing_in_engine)}")
    if result.missing_in_baseline:
        print(f"Missing in baseline: {', '.join(result.missing_in_baseline)}")

    out_of_tol = [d for d in result.deltas if not d.within_tolerance]
    if out_of_tol:
        print("\nOut-of-tolerance deltas:")
        for d in out_of_tol:
            print(f"  {d.business_unit_code:>6}  {d.field:<16}"
                  f"  baseline={d.baseline!s:>14}  engine={d.engine!s:>14}  delta={d.delta!s:>10}")
    else:
        print("\nAll per-BU lines within tolerance.")

    print("\nGrand-total deltas:")
    for k, v in result.totals_delta.items():
        print(f"  {k:<16} {v!s:>14}")


def main() -> None:
    args = _build_parser().parse_args()
    sys.exit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
