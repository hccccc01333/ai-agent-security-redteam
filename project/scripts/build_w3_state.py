"""Build W3: W2 + state-space probing via env.snapshot()/restore().

The gateway exposes snapshot/restore env ops (jed_attack_gateway.py), which the
attacker can use to branch from an identical environment state.  W1/W2 call
env.reset() before every probe (fresh state); W3 instead snapshots the current
state, runs the probe, then restores - so every template is measured from the
SAME context.  Local sim MockEnv now supports snapshot/restore too, so the gate
can validate the code path.  Falls back to reset() when unavailable.

Usage (from project/):
  python scripts/build_w3_state.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "variants" / "w2_adaptive_exfil.py"
DST = ROOT / "variants" / "w3_state_exfil.py"


def main() -> int:
    src = SRC.read_text(encoding="utf-8")

    old_trial = """            started = time.monotonic()
            try:
                env.reset()
                env.interact(message, max_tool_hops=max_tool_hops)
                trace = env.export_trace_dict()
"""
    new_trial = """            started = time.monotonic()
            try:
                if hasattr(env, "snapshot") and hasattr(env, "restore"):
                    _snap = env.snapshot()
                    env.interact(message, max_tool_hops=max_tool_hops)
                    trace = env.export_trace_dict()
                    env.restore(_snap)
                else:
                    env.reset()
                    env.interact(message, max_tool_hops=max_tool_hops)
                    trace = env.export_trace_dict()
"""
    assert old_trial in src, "trial body not found"
    src = src.replace(old_trial, new_trial, 1)
    src = src.replace("[w2-adaptive-exfil]", "[w3-state-exfil]")
    src = src.replace("W2: W1 core", "W3: W2 + snapshot/restore state-space probes")

    DST.write_text(src, encoding="utf-8")
    print(f"wrote {DST}  lines={len(src.splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
