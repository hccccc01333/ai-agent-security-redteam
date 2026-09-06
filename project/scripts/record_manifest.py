"""Append a submission entry to the online-attribution manifest (F010).

Usage (from project/):
  python scripts/record_manifest.py --submission-id 55399999 --variant s5_balanced.py ^
      --family-mix '{"direct":0.25,"decompose":0.25,"tool_aware":0.25,"reframe":0.25}' ^
      --router r0 --selector sel0 --candidates 1250 --interactions 1250
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "submission_manifest.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Append submission manifest entry")
    ap.add_argument("--submission-id", required=True)
    ap.add_argument("--variant", required=True)
    ap.add_argument("--base", default="")
    ap.add_argument("--family-mix", required=True)
    ap.add_argument("--router", default="r0-static")
    ap.add_argument("--selector", default="sel0")
    ap.add_argument("--candidates", type=int, default=None)
    ap.add_argument("--interactions", type=int, default=None)
    ap.add_argument("--budget-safe", type=float, default=None)
    ap.add_argument("--mutation", default="none")
    ap.add_argument("--dedup", default="")
    ap.add_argument("--seed", default="n/a")
    args = ap.parse_args()

    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = {
        "submission_id": args.submission_id,
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "variant": args.variant,
        "base": args.base,
        "family_mix": json.loads(args.family_mix),
        "router_version": args.router,
        "selector_version": args.selector,
        "candidate_count": args.candidates,
        "interactions": args.interactions,
        "budget_safe": args.budget_safe,
        "mutation": args.mutation,
        "dedup": args.dedup,
        "seed": args.seed,
        "status": "PENDING",
        "public_score": None,
    }
    doc["entries"] = [e for e in doc["entries"] if e["submission_id"] != args.submission_id]
    doc["entries"].append(entry)
    MANIFEST.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest updated: {len(doc['entries'])} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
