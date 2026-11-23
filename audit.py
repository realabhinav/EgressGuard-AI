"""Offline, read-only audit of exported configuration records."""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path


def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def evidence(query, pages):
    """Fuse Okapi BM25 and character-trigram TF-IDF cosine rankings."""
    docs = [words(page["text"]) for page in pages]
    if not docs or not all(docs):
        raise ValueError("Supply at least one nonempty evidence page")
    n = len(docs)
    avg = sum(map(len, docs)) / n
    scores = []
    for doc in docs:
        score = 0
        for term in set(words(query)):
            df = sum(term in other for other in docs)
            tf = doc.count(term)
            score += math.log1p((n-df+0.5)/(df+0.5))*tf*2.2/(tf+1.2*(0.25+0.75*len(doc)/avg))
        scores.append(score)

    def grams(text):
        text = " ".join(words(text))
        return Counter(text[i:i+3] for i in range(len(text)-2))

    corpus = [grams(page["text"]) for page in pages]
    idf = {g: 1+math.log((n+1)/(1+sum(g in d for d in corpus))) for g in set().union(*corpus)}

    def vector(counts):
        weights = {g: count*idf[g] for g, count in counts.items() if g in idf}
        norm = math.sqrt(sum(x*x for x in weights.values())) or 1
        return {g: x/norm for g, x in weights.items()}

    q = vector(grams(query))
    cosine = [sum(q.get(g, 0)*v for g,v in vector(d).items()) for d in corpus]
    fused = Counter()
    for ranking in (scores, cosine):
        for rank, i in enumerate(sorted(range(n), key=ranking.__getitem__, reverse=True), 1):
            if ranking[i] > 0:
                fused[i] += 1/(60+rank)
    if fused:
        return pages[fused.most_common(1)[0][0]]["source"]
    return None


RULES = {
    "firewall_open": ("firewall", "destination", "*", "Restrict wildcard outbound destinations"),
    "proxy_missing": ("proxy", "logging", False, "Enable proxy logging"),
    "owner_missing": ("inventory", "owner", "", "Assign an accountable asset owner"),
}


def audit(records, pages):
    findings = []
    sources = {}
    for record in records:
        for rule, (kind, field, trigger, message) in RULES.items():
            if record["type"] == kind and field in record and record[field] == trigger:
                if rule not in sources:
                    sources[rule] = evidence(message, pages)
                findings.append(dict(asset=record["id"], rule=rule, observed=record[field],
                                     recommendation=message, source=sources[rule]))
    return findings


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf8"))
    print(json.dumps(audit(data["records"], data["pages"]), indent=2))
