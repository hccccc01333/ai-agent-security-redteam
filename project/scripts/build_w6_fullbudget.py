"""Build W6: W3 (state-space, ladder best 76.860) at full replay budget.

W-ladder verdict (2026-08-13):
  W2 74.475 = REPLAY_SAFE 0.90 cost ~8.4 vs W1 anchor
  W3 76.860 = +2.4 from snapshot/restore (BEST)
  W4/W5 = mutation pools regressed -> direction closed
W6 = W3 + REPLAY_SAFE 0.996 (full fill) + hedge 2% (keep private insurance
small).  Expected ~85 if fill scales linearly; replay safety mirrors W1 (0.996
completed on identical candidate structure).

Usage (from project/):
  python scripts/build_w6_fullbudget.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "variants" / "w3_state_exfil.py"
DST = ROOT / "variants" / "w6_fullbudget_exfil.py"


def main() -> int:
    src = SRC.read_text(encoding="utf-8")
    src = src.replace("REPLAY_SAFE = 0.90", "REPLAY_SAFE = 0.996")
    src = src.replace("HEDGE_FRACTION = 0.04", "HEDGE_FRACTION = 0.02")
    src = src.replace("[w3-state-exfil]", "[w6-state-fullbudget]")
    DST.write_text(src, encoding="utf-8")
    print(f"wrote {DST}  lines={len(src.splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
