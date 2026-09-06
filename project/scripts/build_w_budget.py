"""Build W-series budget/hedge variants from the proven W3 state core.

W-ladder (CONC-0028): W3 (snapshot/restore) is the best core at 0.90;
budget = score.  These variants sweep REPLAY_SAFE x hedge on the same core:
  w8_midbudget_exfil:  REPLAY_SAFE 0.95, HEDGE 0.04
  w10_nohedge_exfil:   REPLAY_SAFE 0.996, HEDGE 0.0

Usage (from project/):
  python scripts/build_w_budget.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "variants" / "w3_state_exfil.py"

VARIANTS = (
    ("w8_midbudget_exfil.py", "w8-midbudget", 0.95, 0.04),
    ("w10_nohedge_exfil.py", "w10-nohedge", 0.996, 0.0),
    ("w9_nohedge_090_exfil.py", "w9-nohedge-090", 0.90, 0.0),
)


def main() -> int:
    base = SRC.read_text(encoding="utf-8")
    for out_name, tag, safe, hedge in VARIANTS:
        src = base.replace("REPLAY_SAFE = 0.90", "REPLAY_SAFE = %s" % safe)
        src = src.replace("HEDGE_FRACTION = 0.04", "HEDGE_FRACTION = %s" % hedge)
        src = src.replace("[w3-state-exfil]", "[%s]" % tag)
        dst = ROOT / "variants" / out_name
        dst.write_text(src, encoding="utf-8")
        print(f"wrote {dst}  safe={safe} hedge={hedge} lines={len(src.splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
