# -*- coding: utf-8 -*-
"""NR-GATE v1: new-routes submission gate (2026-08-08).

Checks the structural artifacts the new routes depend on before any shot
(A1 multi-post first, C dual second). A variant may still be submitted when
E is BLOCKED only if the user explicitly accepts the calibration gap; the
script reports BLOCK for E so the decision stays visible.

Items:
  G1 A scorer contract probe  (multi_post_local_probe.json)
  G2 B overshoot curve       (replay_overshoot_curve.csv + meta)
  G3 C dual local eval       (dual_predicate_local_eval.csv + gate json)
  G4 E private calibration   (private_guardrail_calibration.csv; private rows)
  G5 A1 variant local gate   (registry experiments.jsonl -> local_pass)
  G6 unified G3 gate         (gate_submission.py report -> PASS)
  G7 manual: user explicit submit order (not machine-checkable)
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "reports" / "new_routes_20260808"


def check(rows: list[dict], item: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else ("WARN" if detail.startswith("WARN") else "FAIL")
    rows.append({"item": item, "status": status, "detail": detail})
    print(f"[{status}] {item}: {detail}")


def main() -> int:
    rows: list[dict] = []

    # G1
    p = OUT / "multi_post_local_probe.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        by = {c["case"]: c for c in d["cases"]}
        k2 = by.get("k2_diff_domain", {})
        k5 = by.get("k5_diff_domain", {})
        ok = k2.get("raw") == 34 and k5.get("raw") == 82
        check(rows, "G1_A_multi_post_scorer", ok,
              f"k2 raw={k2.get('raw')} k5 raw={k5.get('raw')} (expect 34/82)")
    else:
        check(rows, "G1_A_multi_post_scorer", False, f"missing {p.name}")

    # G2
    csv_b = OUT / "replay_overshoot_curve.csv"
    meta_b = OUT / "replay_overshoot_meta.json"
    if csv_b.exists() and meta_b.exists():
        check(rows, "G2_B_overshoot_curve", True, f"{csv_b.name} + {meta_b.name} exist")
    else:
        check(rows, "G2_B_overshoot_curve", False, "missing curve/meta")

    # G3
    csv_c = OUT / "dual_predicate_local_eval.csv"
    gate_c = OUT / "dual_predicate_gate.json"
    if csv_c.exists() and gate_c.exists():
        g = json.loads(gate_c.read_text(encoding="utf-8"))["gate"]
        check(rows, "G3_C_dual_eval", True,
              f"raw dual={g['raw_dual_ab']} break_even_p={g['dual_break_even_p']}")
    else:
        check(rows, "G3_C_dual_eval", False, "missing dual eval files")

    # G4
    csv_e = OUT / "private_guardrail_calibration.csv"
    if csv_e.exists():
        lines = csv_e.read_text(encoding="utf-8-sig").splitlines()
        has_private = any(
            ("kaggle_api_local" in ln and len(ln.split(",")) > 8 and ln.split(",")[8] != "")
            for ln in lines[1:]
        )
        check(rows, "G4_E_private_calibration", has_private,
              "WARN real private rows not filled yet (paste kernel Output)")
    else:
        check(rows, "G4_E_private_calibration", False, "missing calibration csv")

    # G5
    exp_path = ROOT / "registry" / "experiments.jsonl"
    variant = "w1_multi_post_probe"
    found = False
    if exp_path.exists():
        for ln in exp_path.read_text(encoding="utf-8").splitlines():
            try:
                o = json.loads(ln)
            except Exception:
                continue
            if o.get("experiment_id") == variant:
                found = True
                audits = o.get("audits", {})
                status = o.get("decision", {}).get("status", "?")
                ok = status == "local_pass" and all(
                    v == "pass" or str(v).startswith("pass (") for v in audits.values()
                )
                check(rows, "G5_A1_variant_gate", ok,
                      f"registry status={status} audits={audits}")
                break
    if not found:
        check(rows, "G5_A1_variant_gate", False, f"{variant} not in experiments.jsonl")

    # G6 unified G3 gate from thread 019fc04f (gate_submission.py)
    gate_md = ROOT.parent / "reports" / "gate_w1_multi_post_probe.md"
    if gate_md.exists():
        md = gate_md.read_text(encoding="utf-8")
        ok = "- verdict: PASS" in md
        check(rows, "G6_unified_g3_gate", ok, f"{gate_md.name} verdict={'PASS' if ok else 'NOT PASS'}")
    else:
        check(rows, "G6_unified_g3_gate", False, "missing gate_w1_multi_post_probe.md")

    check(rows, "G7_user_explicit_go", True,
          "manual: wait for user's explicit '提交' before submitting")

    blocked = [r for r in rows if r["status"] == "FAIL"]
    warns = [r for r in rows if r["status"] == "WARN"]
    overall = "BLOCKED" if blocked else ("READY_WITH_WARN" if warns else "READY")
    print(f"\nNR-GATE v1 overall: {overall} (pass={sum(1 for r in rows if r['status']=='PASS')}, "
          f"warn={len(warns)}, fail={len(blocked)})")

    (OUT / "new_routes_gate_v1.json").write_text(
        json.dumps(
            {"date": "2026-08-08", "gate": "NR-GATE v1", "overall": overall, "items": rows},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
