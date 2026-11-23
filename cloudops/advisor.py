"""Analyze a synthetic monitoring export. Run python advisor.py sample.csv"""
import argparse
import csv
import json
import math
from pathlib import Path


def analyze(rows):
    observations = []
    for row in rows:
        cpu, latency, cost = (float(row[key]) for key in ("cpu_pct", "p95_ms", "hourly_usd"))
        if not all(math.isfinite(x) for x in (cpu, latency, cost)) or not (0 <= cpu <= 100 and latency >= 0 and cost >= 0):
            raise ValueError(f"Invalid metrics for {row['resource']}")
        if cpu >= 80 and latency >= 300:
            advice = "Inspect queue depth and evaluate additional capacity."
        elif latency >= 300:
            advice = "Inspect downstream waits before increasing capacity."
        elif cpu < 20 and cost >= 1:
            advice = "Review sustained utilization for rightsizing."
        else:
            advice = "Continue monitoring."
        observations.append(dict(resource=row["resource"], cpu_pct=cpu, p95_ms=latency,
                                 hourly_usd=cost, recommendation=advice))
    return observations


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("input", type=Path)
    cli.add_argument("--format", choices=("json", "markdown"), default="json")
    args = cli.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as source:
        results = analyze(csv.DictReader(source))
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print("# Capacity review\n")
        for row in results:
            print(f"- {row['resource']} ({row['cpu_pct']}% CPU, p95 {row['p95_ms']} ms, "
                  f"${row['hourly_usd']}/hour): {row['recommendation']}")
