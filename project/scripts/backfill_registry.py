"""Backfill experiment registry from historical submissions (one-off / re-runnable).

Maps each visible submission (submissions_full.csv) to its variant file via the
description's series token, computes code hashes, wires parents per variant
headers, and merges entries into registry/experiments.jsonl. Existing entries
(Q5/S2/V5/W1, which carry evaluator data) are preserved and only filled in.

Usage (from project/):
  python scripts/backfill_registry.py
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ROOT / "variants"
SUBMISSIONS_CSV = ROOT / "submissions_full.csv"
EXPERIMENTS = ROOT / "registry" / "experiments.jsonl"
Q5_ANCHOR = 87.795

# series token (first word of submission description) -> variant file
SERIES_TO_FILE = {
    "F2": "f2_e3_pack.py",
    "F4": "f4_minfire030.py",
    "G1": "g1_multimsg_route.py",
    "G2": "g2_cell_diverse.py",
    "H1": "h1_f1xf4.py",
    "A": "a_model_route.py",
    "B": "b_multipred.py",
    "C": "c_cand_struct.py",
    "D": "d_search_struct.py",
    "P1": "p1_minfire02.py",
    "P2": "p2_hard_route.py",
    "P3": "p3_margin45.py",
    "P4": "p4_replay998.py",
    "P5": "p5_three_tpl.py",
    "Q1": "q1_replay997.py",
    "Q2": "q2_minfire032.py",
    "Q3": "q3_margin50.py",
    "Q4": "q4_plain_ok.py",
    "Q5": "q5_inj_short.py",
    "R1": "r1_dual_forge.py",
    "R2": "r2_minfire032.py",
    "R3": "r3_soft_inj.py",
    "R4": "r4_prefer_close.py",
    "R5": "r5_firelat.py",
    "S1": "s1_replay995.py",
    "S2": "s2_minfire033.py",
    "S3": "s3_inj_dot.py",
    "S4": "s4_inj_ok.py",
    "S5": "s5_margin55.py",
    "T1": "t1_forge_nl.py",
    "T2": "t2_comm_short.py",
    "T3": "t3_short_host.py",
    "T4": "t4_bareok_answer.py",
    "T5": "t5_replay9965.py",
    "E1": "e1_pack.py",
    "E2": "e2_replay996.py",
    "E3": "e3_probe3.py",
    "E4": "e4_tensorliu_safe.py",
    "E5": "e5_bare.py",
    "U1": "u1_lat_route.py",
    "U2": "u2_short_host.py",
    "U3": "u3_minfire02.py",
    "U4": "u4_dual_fill.py",
    "U5": "u5_haodou_stack.py",
    "V1": "v1_lat_split_fill.py",
    "V2": "v2_replay_sizing.py",
    "V3": "v3_single_fill.py",
    "V4": "v4_adaptive_margin.py",
    "V5": "v5_v12_host.py",
    "W1": "w1_probe5_fire65.py",
}

# series token -> (parent token, parent variant file); None parent = root/unknown
PARENT_BY_TOKEN = {
    "F2": ("E3", "e3_probe3.py"),
    "F4": ("E3", "e3_probe3.py"),
    "G1": ("E3", "e3_probe3.py"),
    "G2": ("E3", "e3_probe3.py"),
    "H1": ("F1", "f1_e3_replay996.py"),
    "A": (None, "base_f1xf2.py"),
    "B": (None, "base_f1xf2.py"),
    "C": (None, "base_f1xf2.py"),
    "D": (None, "base_f1xf2.py"),
    "P1": ("F1", "f1_e3_replay996.py"),
    "P2": ("F1", "f1_e3_replay996.py"),
    "P3": ("F1", "f1_e3_replay996.py"),
    "P4": ("F1", "f1_e3_replay996.py"),
    "P5": ("F1", "f1_e3_replay996.py"),
    "Q1": ("F1", "f1_e3_replay996.py"),
    "Q2": ("F1", "f1_e3_replay996.py"),
    "Q3": ("F1", "f1_e3_replay996.py"),
    "Q4": ("F1", "f1_e3_replay996.py"),
    "Q5": ("F1", "f1_e3_replay996.py"),
    "R1": ("Q5", "q5_inj_short.py"),
    "R2": ("Q5", "q5_inj_short.py"),
    "R3": ("Q5", "q5_inj_short.py"),
    "R4": ("Q5", "q5_inj_short.py"),
    "R5": ("Q5", "q5_inj_short.py"),
    "S1": ("Q5", "q5_inj_short.py"),
    "S2": ("Q5", "q5_inj_short.py"),
    "S3": ("Q5", "q5_inj_short.py"),
    "S4": ("Q5", "q5_inj_short.py"),
    "S5": ("Q5", "q5_inj_short.py"),
    "T1": ("Q5", "q5_inj_short.py"),
    "T2": ("Q5", "q5_inj_short.py"),
    "T3": ("Q5", "q5_inj_short.py"),
    "T4": ("Q5", "q5_inj_short.py"),
    "T5": ("Q5", "q5_inj_short.py"),
    "U1": ("Q5", "q5_inj_short.py"),
    "U2": ("Q5", "q5_inj_short.py"),
    "U3": ("Q5", "q5_inj_short.py"),
    "U4": ("Q5", "q5_inj_short.py"),
    "U5": ("Q5", "q5_inj_short.py"),
    "V1": ("Q5", "q5_inj_short.py"),
    "V2": ("Q5", "q5_inj_short.py"),
    "V3": ("Q5", "q5_inj_short.py"),
    "V4": ("Q5", "q5_inj_short.py"),
    "V5": ("Q5", "q5_inj_short.py"),
    "W1": ("Q5", "q5_inj_short.py"),
}

BUCKET_BY_TOKEN = {
    "F2": "e3_line",
    "F4": "e3_line",
    "G1": "e3_line",
    "G2": "e3_line",
    "H1": "e3_line",
    "A": "f1xf2_structure",
    "B": "f1xf2_structure",
    "C": "f1xf2_structure",
    "D": "f1xf2_structure",
    "E1": "reference_stack",
    "E2": "reference_stack",
    "E3": "reference_stack",
    "E4": "reference_stack",
    "E5": "reference_stack",
}


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    with open(SUBMISSIONS_CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    score_by_token: dict[str, float | None] = {}
    ref_by_token: dict[str, str] = {}
    status_by_token: dict[str, str] = {}
    for row in rows:
        desc = (row.get("description") or "").strip()
        tok = desc.split()[0].rstrip(":") if desc else ""
        if tok not in SERIES_TO_FILE:
            continue
        score = row.get("publicScore") or None
        score_by_token[tok] = float(score) if score else score_by_token.get(tok)
        ref_by_token[tok] = row.get("ref", "")
        status_by_token[tok] = row.get("status", "")

    existing = {e["experiment_id"]: e for e in load_jsonl(EXPERIMENTS)}

    def find_existing(tok: str) -> dict | None:
        exact = existing.get(tok)
        tlower = tok.lower()
        stem_match = None
        for e in existing.values():
            stem = Path(e.get("variant_file", "")).stem.lower()
            if stem == tlower or stem.startswith(tlower + "_"):
                if stem_match is None or e.get("decision", {}).get("submission_ref"):
                    stem_match = e
        if exact is not None:
            if exact.get("decision", {}).get("submission_ref"):
                return exact
            if stem_match is not None and stem_match.get("decision", {}).get("submission_ref"):
                return stem_match
            return exact
        return stem_match
    added = 0
    updated = 0
    for tok, file_name in SERIES_TO_FILE.items():
        variant_path = VARIANTS / file_name
        if not variant_path.exists():
            continue
        score = score_by_token.get(tok)
        ref = ref_by_token.get(tok, "")
        status = status_by_token.get(tok, "")
        parent_token, parent_file = PARENT_BY_TOKEN.get(tok, (None, None))
        entry = find_existing(tok)
        if entry is not None:
            if tok in existing and existing[tok] is not entry:
                del existing[tok]  # drop duplicate keyed by series token
            changed = False
            if entry.get("metrics", {}).get("public_score") is None and score is not None:
                entry.setdefault("metrics", {})["public_score"] = score
                entry.setdefault("decision", {})["public_score"] = score
                changed = True
            if ref and not entry.get("provenance", {}).get("submission_ref"):
                entry.setdefault("provenance", {})["submission_ref"] = ref
                entry.setdefault("decision", {})["submission_ref"] = ref
                changed = True
            if changed:
                updated += 1
            continue
        parent_score = score_by_token.get(parent_token) if parent_token else None
        if score is None:
            decision_status = "error" if "ERROR" in status else "no_score"
            reason = f"submission {status}"
        else:
            reference = parent_score if parent_score is not None else Q5_ANCHOR
            decision_status = "promoted" if score >= reference else "rejected"
            reason = f"lb {score} vs parent {reference}"
        if tok == "Q5":
            decision_status = "promoted_best"
            reason = "all-time best 87.795"
        existing[tok] = {
            "experiment_id": tok,
            "registered_at": "2026-08-02T06:00:00Z",
            "variant_file": f"variants/{file_name}",
            "parent_id": parent_token,
            "parent_variant": f"variants/{parent_file}" if parent_file else None,
            "operator": "improve",
            "bucket": BUCKET_BY_TOKEN.get(tok, "q5_line"),
            "hypothesis": {"change": (rows and "backfilled from submission history") or "", "expected_mechanism": ""},
            "provenance": {
                "code_hash": sha256_hex(variant_path),
                "parent_code_hash": (
                    sha256_hex(VARIANTS / parent_file) if parent_file and (VARIANTS / parent_file).exists() else None
                ),
                "submission_ref": ref or None,
            },
            "metrics": {"public_score": score},
            "audits": {"backfill": "pass"},
            "decision": {
                "status": decision_status,
                "submitted": True,
                "submission_ref": ref or None,
                "public_score": score,
                "reason": reason,
            },
        }
        added += 1

    save_jsonl(EXPERIMENTS, list(existing.values()))
    scored = sum(1 for e in existing.values() if e.get("metrics", {}).get("public_score") is not None)
    print(f"BACKFILL entries={len(existing)} added={added} updated={updated} scored={scored}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
