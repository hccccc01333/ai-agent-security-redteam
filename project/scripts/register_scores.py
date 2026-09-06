"""Register public scores from a raw Kaggle submissions JSON dump.

Why this exists: the kaggle Python library's competition_submissions() only
returns ~20 rows on this machine, while the raw v1 API returns 50+. This script
consumes a dump saved from the raw API (curl) and back-fills every registered
experiment whose submission_ref appears in it.

Usage:
  curl -sS -H "Authorization: Bearer $KAGGLE_API_TOKEN" \
    "https://www.kaggle.com/api/v1/competitions/submissions/list/ai-agent-security-multi-step-tool-attacks" \
    -o registry/kaggle_subs_latest.json
  python scripts/register_scores.py [--dump registry/kaggle_subs_latest.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "experiments.jsonl"
SUBMISSIONS = ROOT / "registry" / "submissions.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def save_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Register scores from a raw Kaggle submissions dump")
    ap.add_argument("--dump", default=str(ROOT / "registry" / "kaggle_subs_latest.json"))
    args = ap.parse_args()

    dump_path = Path(args.dump)
    if not dump_path.exists():
        print(f"FAIL dump not found: {dump_path}", file=sys.stderr)
        return 1
    rows = json.loads(dump_path.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)

    subs = load_jsonl(SUBMISSIONS)
    sub_by_ref = {str(r["ref"]): r for r in subs}
    changed_subs = 0
    for row in rows:
        ref = str(row.get("ref", ""))
        if not ref:
            continue
        sub_by_ref[ref] = {
            "ref": ref,
            "fileName": str(row.get("fileName", "")),
            "date": str(row.get("date", "")),
            "description": str(row.get("description", "")),
            "status": str(row.get("status", "")),
            "publicScore": str(row.get("publicScore", "")),
            "privateScore": str(row.get("privateScore", "")),
        }
        changed_subs += 1
    save_jsonl(SUBMISSIONS, list(sub_by_ref.values()))

    experiments = load_jsonl(REGISTRY)
    updated = 0
    for e in experiments:
        ref = str(e.get("decision", {}).get("submission_ref") or "")
        row = next((r for r in rows if str(r.get("ref")) == ref), None)
        if row is None or not row.get("publicScore"):
            continue
        score = float(row["publicScore"])
        if e.get("metrics", {}).get("public_score") == score:
            continue
        date_text = str(row.get("date", ""))[:19]
        feedback_hours = None
        try:
            submitted_at = datetime.fromisoformat(
                date_text.replace("Z", "+00:00") if date_text.endswith("Z") else date_text + "+00:00"
            )
            feedback_hours = round((now - submitted_at).total_seconds() / 3600.0, 2)
        except Exception:
            pass
        e.setdefault("metrics", {})["public_score"] = score
        e["metrics"]["score_seen_at"] = now.isoformat(timespec="seconds")
        if feedback_hours is not None:
            e["metrics"]["feedback_hours"] = feedback_hours
        e.setdefault("decision", {})["public_score"] = score
        parent = next((x for x in experiments if x.get("experiment_id") == e.get("parent_id")), None)
        pscore = (parent or {}).get("metrics", {}).get("public_score")
        e["decision"]["status"] = "promoted" if pscore is not None and score >= float(pscore) else "rejected"
        e["decision"]["reason"] = f"LB {score} vs parent {pscore}"
        updated += 1
        print(f"REGISTERED {e['experiment_id']}: {score} "
              f"({feedback_hours if feedback_hours is not None else 'n/a'}h) "
              f"vs parent {pscore} -> {e['decision']['status']}")
    save_jsonl(REGISTRY, experiments)
    print(f"DONE submissions_rows={len(rows)} subs_updated={changed_subs} experiments_updated={updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
