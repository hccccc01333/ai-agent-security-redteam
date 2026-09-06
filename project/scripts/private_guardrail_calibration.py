# -*- coding: utf-8 -*-
"""E: private-guardrail calibration table builder.

Real private scores are NOT exposed by the Kaggle API (privateScore is always
empty locally) and no `guardrail=private` gateway line is present in local logs,
so this script:
  1. aggregates every local submission (public score + family hint) into the
     calibration CSV (private columns empty, marked pending);
  2. adds P003 proxy estimates (guardrail-ladder survival) as a separate source;
  3. writes a TODO list of submission refs whose kernel Output logs should be
     pasted to fill real private rows.
"""

from __future__ import annotations

import csv
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "reports" / "new_routes_20260808"


def family_hint(desc: str) -> str:
    m = re.match(r"([A-Za-z0-9]+)", desc or "")
    return m.group(1).upper() if m else "?"


def main() -> int:
    rows = []
    subs_path = ROOT / "registry" / "submissions.jsonl"
    for ln in subs_path.read_text(encoding="utf-8").splitlines():
        try:
            o = json.loads(ln)
        except Exception:
            continue
        rows.append(
            {
                "source": "kaggle_api_local",
                "ref": o.get("ref", ""),
                "date": str(o.get("date", ""))[:10],
                "description": o.get("description", ""),
                "family_hint": family_hint(o.get("description", "")),
                "model": "both",
                "n": "",
                "public_score": o.get("publicScore", ""),
                "private_pass": "",
                "private_n": "",
                "private_pass_rate": "",
                "wilson_low": "",
                "wilson_high": "",
                "note": "privateScore empty via API; need kernel Output [GATEWAY] four-line scores",
            }
        )

    # P003 proxy rows (guardrail-ladder survival as a weak private surrogate).
    scan_path = ROOT.parent / "project" / "registry" / "guardrail_family_scan_2026-08-07.json"
    if scan_path.exists():
        scan = json.loads(scan_path.read_text(encoding="utf-8"))
        for fam in scan["families"]:
            g2 = fam["tiers"]["G2_sink_dlp"]["allowed"]
            g4 = fam["tiers"]["G4_decode_dlp"]["allowed"]
            g6 = fam["tiers"]["G6_persistent_taint"]["allowed"]
            rows.append(
                {
                    "source": "p003_proxy",
                    "ref": "",
                    "date": "2026-08-07",
                    "description": f"P003 ladder: {fam['family']}",
                    "family_hint": fam["family"],
                    "model": "both",
                    "n": "",
                    "public_score": fam["tiers"]["G1_optimal"]["raw"],
                    "private_pass": "G2/G4/G6 survival: " + "/".join(
                        "Y" if x == "✓" else "N" for x in (g2, g4, g6)
                    ),
                    "private_n": "",
                    "private_pass_rate": "",
                    "wilson_low": "",
                    "wilson_high": "",
                    "note": f"risk_class={fam['risk_class']}; proxy assumption, not real private",
                }
            )

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "private_guardrail_calibration.csv"
    fieldnames = [
        "source",
        "ref",
        "date",
        "description",
        "family_hint",
        "model",
        "n",
        "public_score",
        "private_pass",
        "private_n",
        "private_pass_rate",
        "wilson_low",
        "wilson_high",
        "note",
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    todo = {
        "date": "2026-08-08",
        "blocker": "no real private rows available locally (API privateScore empty; no guardrail=private logs)",
        "how_to_fill": "paste kernel Output for these refs; each contains [GATEWAY] gpt_oss_public/.../gemma_private = ...",
        "refs": ["55177036 (W1)", "55226459 (x5)", "55312630 (n6)", "55313760 (n7)", "55313831 (n6b)"],
    }
    (OUT / "private_calibration_todo.json").write_text(
        json.dumps(todo, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"WROTE {csv_path} ({len(rows)} rows)")
    print(json.dumps(todo, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
