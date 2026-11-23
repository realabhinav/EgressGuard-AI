"""Compare uncached and cached retrieval calls on the same fixture."""
import json
from pathlib import Path
from unittest.mock import patch
import audit

data = json.loads(Path(__file__).with_name("demo.json").read_text())
with patch.object(audit, "evidence", wraps=audit.evidence) as ranker:
    # A one-record invocation cannot reuse results across records.
    baseline = [f for r in data["records"] for f in audit.audit([r], data["pages"])]
    before = ranker.call_count
    ranker.reset_mock()
    optimized = audit.audit(data["records"], data["pages"])
    after = ranker.call_count
assert baseline == optimized
print(f"Ranking calls {before} -> {after}. Reduction {(before-after)/before:.0%}. Identical findings: {len(optimized)}.")
