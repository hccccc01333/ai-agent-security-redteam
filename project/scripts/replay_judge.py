"""Deterministic full-replay judge (medium-trust local evaluator).

Runs attack.run against the local sandbox (deterministic agent), replays the
returned candidates under the chosen guardrail, and reports predicate hits,
unique score-cell diversity and approximate score. Trust depends on the attack
family: multi-step (write/read -> http.post) families get a real signal here;
direct single-message EXFIL families are NOT representable (trust=low).

Usage (from project/):
  python scripts/replay_judge.py --budget-s 120 --guardrail optimal --max-replay 200
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "data"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DATA))
sys.path.insert(0, str(ROOT / "scripts"))

from aicomp_sdk.agents import build_agent  # noqa: E402
from aicomp_sdk.attacks import AttackRunConfig  # noqa: E402
from aicomp_sdk.attacks.baselines.guardrail_allow import Guardrail as AllowAll  # noqa: E402
from aicomp_sdk.core.cells import cell_signature  # noqa: E402
from aicomp_sdk.core.env.sandbox import SandboxEnv  # noqa: E402
from aicomp_sdk.core.predicates import eval_predicates  # noqa: E402
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail  # noqa: E402
from aicomp_sdk.scoring import score_attack, score_attack_raw  # noqa: E402
from private_proxy import Guardrail as PrivateProxyGuardrail  # noqa: E402
from attack import AttackAlgorithm  # noqa: E402

GUARDRAILS = {
    "allow": AllowAll,
    "optimal": OptimalGuardrail,
    "private_proxy": PrivateProxyGuardrail,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic full-replay judge")
    ap.add_argument("--budget-s", type=float, default=120.0)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--guardrail", choices=sorted(GUARDRAILS), default="optimal")
    ap.add_argument("--max-replay", type=int, default=200)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    fixtures = DATA / "aicomp_sdk" / "fixtures"
    guardrail_cls = GUARDRAILS[args.guardrail]
    env = SandboxEnv(
        seed=args.seed,
        fixtures_dir=fixtures,
        agent=build_agent("deterministic"),
        guardrail=guardrail_cls(),
    )
    attacker = AttackAlgorithm({"branch_batch": 8, "max_turns": 10})
    t0 = time.monotonic()
    candidates = attacker.run(env, AttackRunConfig(time_budget_s=args.budget_s, max_steps=80))
    search_s = round(time.monotonic() - t0, 1)

    findings: list[dict] = []
    pred_counts: dict[str, int] = {}
    cells: set[str] = set()
    refused_n = 0
    t1 = time.monotonic()
    sample_n = min(args.max_replay, len(candidates))
    all_msgs = sorted(m for cand in candidates for m in cand.user_messages)
    candidates_hash = hashlib.sha256("\n".join(all_msgs).encode("utf-8")).hexdigest()[:16]
    for cand in candidates[:sample_n]:
        env.reset()
        refused = False
        for msg in cand.user_messages:
            result = env.interact(msg, max_tool_hops=8)
            if getattr(result, "agent_refused", False):
                refused = True
                break
        if refused:
            refused_n += 1
            continue
        trace = env.export_trace_dict()
        preds = eval_predicates(trace)
        if preds:
            sig = cell_signature(
                trace.get("tool_events") or [],
                egress_data=[],
                user_messages=list(cand.user_messages),
            )
            cells.add(sig["hash"])
            for p in preds:
                name = str(p.get("predicate"))
                pred_counts[name] = pred_counts.get(name, 0) + 1
            findings.append(
                {
                    "user_messages": list(cand.user_messages),
                    "predicates": preds,
                    "score_cell_signature": {"hash": sig["hash"]},
                }
            )
    replay_s = round(time.monotonic() - t1, 1)

    result = {
        "search_candidates": len(candidates),
        "candidates_hash": candidates_hash,
        "replayed": sample_n,
        "refused": refused_n,
        "hits": len(findings),
        "predicate_counts": pred_counts,
        "unique_cells": len(cells),
        "approx_raw": round(score_attack_raw(findings), 1),
        "approx_norm": round(score_attack(findings), 4),
        "search_s": search_s,
        "replay_s": replay_s,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(
            f"guardrail={args.guardrail} candidates={result['search_candidates']} "
            f"replayed={result['replayed']} refused={result['refused']} hits={result['hits']} "
            f"unique_cells={result['unique_cells']} approx_raw={result['approx_raw']} "
            f"approx_norm={result['approx_norm']} search_s={result['search_s']} replay_s={result['replay_s']}"
        )
        print(f"predicate_counts={pred_counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
