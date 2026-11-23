import csv
import io
import json
from pathlib import Path

import streamlit as st

from audit import audit
from cloudops.advisor import analyze
from report import report

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="EgressGuard AI", layout="wide")
st.title("EgressGuard AI")
audit_tab, cloud_tab = st.tabs(["Configuration audit", "CloudOps capacity review"])

with audit_tab:
    st.header("Configuration audit")
    upload = st.file_uploader("Configuration export (.json) · sample loaded by default", type="json")
    try:
        data = json.loads(upload.getvalue() if upload else (ROOT / "demo.json").read_bytes())
        results = audit(data["records"], data["pages"])
        left, middle, right = st.columns(3)
        left.metric("Records reviewed", len(data["records"]))
        middle.metric("Policy matches", len(results))
        right.metric("Findings with evidence", sum(bool(row["source"]) for row in results))
        if results:
            st.dataframe(results, hide_index=True, use_container_width=True)
        else:
            st.info("No configured rule matched this export.")
        st.download_button("Download audit report", report(data), "audit-report.md", "text/markdown")
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        st.error(f"Check the records and pages in the JSON export. {error}")

with cloud_tab:
    st.header("CloudOps capacity review")
    st.caption("Upload resource, cpu_pct, p95_ms and hourly_usd columns, or explore the synthetic sample.")
    upload = st.file_uploader("Monitoring export (.csv)", type="csv")
    try:
        content = upload.getvalue() if upload else (ROOT / "cloudops" / "sample.csv").read_bytes()
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        required = {"resource", "cpu_pct", "p95_ms", "hourly_usd"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required CSV columns.")
        rows = analyze(reader)
        st.dataframe(rows, hide_index=True, use_container_width=True)
        st.download_button("Download capacity review", json.dumps(rows, indent=2), "capacity.json", "application/json")
    except (ValueError, KeyError, TypeError, csv.Error) as error:
        st.error(f"Check the monitoring export. {error}")
