# EgressGuard AI
A portable implementation of the evidence-ranking and audit stages of EgressGuard. Run with Python 3.10+ from this directory.

    python audit.py demo.json
    python -m unittest -v

The synthetic export contains six records. Three deterministic rules produce five findings. Each finding preserves the observed value and the source ID of the highest-ranked page. Replace the records and page excerpts with your own exported inputs. Inputs are local JSON. BM25 scores exact terms, character trigrams capture partial overlap, and reciprocal rank fusion combines their ordered lists. Ties preserve input order.

The included pages are original demonstration text. Missing fields are skipped and require separate completeness checks. A high-ranked page remains a candidate for human review. This portable edition has no network actions, firewall changes, PDF ingestion, or hosted model dependency.
