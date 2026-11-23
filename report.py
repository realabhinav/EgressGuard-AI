"""Render a Markdown audit report: python report.py demo.json"""
import argparse
import json
from pathlib import Path
from audit import audit


def report(data):
    findings = audit(data["records"], data["pages"])
    lines = ["# Configuration audit", "",
             f"Reviewed {len(data['records'])} records. Found {len(findings)} policy matches."]
    for finding in findings:
        lines.extend(["", f"## {finding['asset']} / {finding['rule']}",
                      f"Observed value: {json.dumps(finding['observed'])}", "",
                      finding["recommendation"], "",
                      f"Evidence: {finding['source'] or 'Manual review required'}"])
    return "\n".join(lines)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("input", type=Path)
    args = cli.parse_args()
    print(report(json.loads(args.input.read_text(encoding="utf-8"))))
