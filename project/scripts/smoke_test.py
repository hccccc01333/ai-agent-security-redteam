"""Local deterministic smoke test for attack.py (no GPU / API key)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
PROJECT = ROOT / "project"

sys.path.insert(0, str(DATA))
sys.path.insert(0, str(PROJECT))

from aicomp_sdk.agents import build_agent  # noqa: E402
from aicomp_sdk.attacks import AttackRunConfig  # noqa: E402
from aicomp_sdk.attacks.baselines.guardrail_allow import Guardrail as AllowAll  # noqa: E402
from aicomp_sdk.attacks.baselines.guardrail_rules import Guardrail as RulesGuardrail  # noqa: E402
from aicomp_sdk.core.env.sandbox import SandboxEnv  # noqa: E402
from aicomp_sdk.core.predicates import eval_predicates  # noqa: E402
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail  # noqa: E402
from aicomp_sdk.scoring import score_attack  # noqa: E402
from attack import AttackAlgorithm  # noqa: E402

GUARDRAILS = {
    "allow": AllowAll,
    "rules": RulesGuardrail,
    "optimal": OptimalGuardrail,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test attack.py locally")
    parser.add_argument("--budget-s", type=float, default=15.0)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--max-steps", type=int, default=80)
    parser.add_argument(
        "--guardrail",
        choices=sorted(GUARDRAILS),
        default="allow",
        help="allow=verify search works; optimal≈public LB; rules=weak baseline",
    )
    args = parser.parse_args()

    fixtures = DATA / "aicomp_sdk" / "fixtures"
    if not fixtures.exists():
        raise SystemExit(f"fixtures not found: {fixtures}")

    guardrail_cls = GUARDRAILS[args.guardrail]
    env = SandboxEnv(
        seed=args.seed,
        fixtures_dir=fixtures,
        agent=build_agent("deterministic"),
        guardrail=guardrail_cls(),
    )

    attacker = AttackAlgorithm({"branch_batch": 8, "max_turns": 10})
    candidates = attacker.run(
        env,
        AttackRunConfig(time_budget_s=args.budget_s, max_steps=args.max_steps),
    )
    print(f"guardrail={args.guardrail} candidates={len(candidates)}")

    replay_findings: list[dict] = []
    pred_counts: dict[str, int] = {}
    sample_n = min(40, len(candidates))
    for cand in candidates[:sample_n]:
        env.reset()
        refused = False
        for msg in cand.user_messages:
            result = env.interact(msg, max_tool_hops=8)
            if getattr(result, "agent_refused", False):
                refused = True
                break
        if refused:
            continue
        trace = env.export_trace_dict()
        preds = eval_predicates(trace)
        if preds:
            for p in preds:
                name = str(p.get("predicate"))
                pred_counts[name] = pred_counts.get(name, 0) + 1
            replay_findings.append(
                {
                    "user_messages": list(cand.user_messages),
                    "predicates": preds,
                    "cell_signature": {"hash": f"local-{len(replay_findings)}"},
                }
            )

    print(f"replay_hits={len(replay_findings)}/{sample_n}")
    print(f"predicate_counts={pred_counts}")
    for i, f in enumerate(replay_findings[:8], 1):
        names = [p.get("predicate") for p in f["predicates"]]
        chain = " -> ".join(f["user_messages"])
        if len(chain) > 140:
            chain = chain[:137] + "..."
        print(f"[{i}] {names} | {chain}")

    approx = score_attack(replay_findings)
    print(f"approx_normalized_score_on_sample={approx:.4f}")
    if args.guardrail != "allow" and len(candidates) == 0:
        print(
            "note: deterministic often scores 0 under optimal; "
            "direct EXFIL/CONFUSED templates target real gpt-oss/gemma agents."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
