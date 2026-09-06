"""Sync Kaggle submissions into the registry (score watcher).

Fetches the submission list via the Kaggle API, refreshes
registry/submissions.jsonl, and back-fills public scores for registered
experiments whose submission_ref resolved. Verdict is computed against the
registered parent's public score.

Requires KAGGLE_API_TOKEN (Machine/Process env) and the kaggle package.

Usage (from project/):
  python scripts/sync_submissions.py
"""

from __future__ import annotations

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


def resolve(entries: list[dict], ref: str) -> dict | None:
    rl = ref.lower()
    for e in entries:
        if e.get("experiment_id", "").lower() == rl:
            return e
    for e in entries:
        if Path(e.get("variant_file", "")).stem.lower() == rl:
            return e
    return None


def main() -> int:
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    subs = api.competition_submissions(competition="ai-agent-security-multi-step-tool-attacks")

    rows: list[dict] = []
    for s in subs:
        rows.append(
            {
                "ref": str(getattr(s, "ref", "")),
                "fileName": str(getattr(s, "fileName", "")),
                "date": str(getattr(s, "date", ""))[:19],
                "description": (getattr(s, "description", "") or "").replace("\n", " "),
                "status": str(getattr(s, "status", "")),
                "publicScore": getattr(s, "public_score", None) or "",
                "privateScore": getattr(s, "private_score", None) or "",
            }
        )
    existing = {r["ref"]: r for r in load_jsonl(SUBMISSIONS)}
    for row in rows:
        existing[row["ref"]] = row
    merged = sorted(existing.values(), key=lambda r: int(r.get("ref") or 0), reverse=True)
    save_jsonl(SUBMISSIONS, merged)

    by_ref = {r["ref"]: r for r in rows}
    experiments = load_jsonl(REGISTRY)
    changed = 0
    pending = []
    for e in experiments:
        ref = str(e.get("decision", {}).get("submission_ref") or "")
        row = by_ref.get(ref)
        if not row:
            continue
        score = row.get("publicScore")
        status_text = str(row.get("status", ""))
        if score in (None, ""):
            if "ERROR" in status_text.upper():
                if e.get("decision", {}).get("status") != "error":
                    e.setdefault("decision", {})["status"] = "error"
                    e.setdefault("decision", {})["failure"] = status_text
                    e.setdefault("decision", {})["recovery"] = "fix_resubmit"
                    changed += 1
                    print(f"ALERT ERROR {e.get('experiment_id')} ref={ref} status={status_text}")
            elif "COMPLETE" in status_text.upper() and e.get("decision", {}).get("status") in (None, "local_pass", "submitted"):
                e.setdefault("decision", {})["status"] = "no_score"
                e.setdefault("decision", {})["failure"] = "COMPLETE without public score"
                e.setdefault("decision", {})["recovery"] = "fix_resubmit"
                changed += 1
                print(f"ALERT NO_SCORE {e.get('experiment_id')} ref={ref} status={status_text}")
            pending.append((e.get("experiment_id"), ref, row.get("status")))
            continue
        score_f = float(score)
        if e.get("metrics", {}).get("public_score") == score_f:
            continue
        seen_at = datetime.now(timezone.utc)
        feedback_hours = None
        date_text = str(row.get("date", "")).strip()
        if date_text:
            try:
                submitted_at = datetime.fromisoformat(date_text[:19]).replace(tzinfo=timezone.utc)
                feedback_hours = round((seen_at - submitted_at).total_seconds() / 3600.0, 2)
            except Exception:
                pass
        e.setdefault("metrics", {})["public_score"] = score_f
        e.setdefault("metrics", {})["score_seen_at"] = seen_at.isoformat(timespec="seconds")
        if feedback_hours is not None:
            e.setdefault("metrics", {})["feedback_hours"] = feedback_hours
        e.setdefault("decision", {})["public_score"] = score_f
        parent = resolve(experiments, e.get("parent_id")) if e.get("parent_id") else None
        pscore = (parent or {}).get("metrics", {}).get("public_score")
        if pscore is not None:
            e["decision"]["status"] = "promoted" if score_f >= float(pscore) else "rejected"
            e["decision"]["reason"] = f"LB {score_f} vs parent {pscore}"
        else:
            e["decision"]["status"] = "scored"
        changed += 1
        print(
            f"FEEDBACK {e['experiment_id']}: score={score_f} "
            f"feedback_hours={feedback_hours if feedback_hours is not None else 'n/a'}"
        )
    save_jsonl(REGISTRY, experiments)

    from collections import Counter
    daily: Counter = Counter()
    error_n = 0
    for r in merged:
        date_key = str(r.get("date", ""))[:10]
        if date_key:
            daily[date_key] += 1
        if "ERROR" in str(r.get("status", "")).upper():
            error_n += 1

    print(f"SYNC submissions={len(rows)} experiments_updated={changed} error_rows={error_n}")
    for day, n in sorted(daily.items())[-3:]:
        print(f"  DAILY {day}: {n} submissions")
    for eid, ref, status in pending:
        print(f"  PENDING {eid} ref={ref} status={status}")
    for e in experiments:
        score = e.get("metrics", {}).get("public_score")
        if score is not None:
            print(f"  SCORED {e['experiment_id']} = {score} status={e['decision'].get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
