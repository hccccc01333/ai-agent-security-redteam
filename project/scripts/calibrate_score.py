# -*- coding: utf-8 -*-
"""F031 出分反推：由 normalized score 反推真实 avg_t（per-cell 口径）。

模型：score = (N × raw_cand) / 200000 × 1000，N = 9000 / avg_t
  -> avg_t = 9000 × raw_cand / (score × 200)
用法：python calibrate_score.py 63.630 18     # score, raw_cand
      python calibrate_score.py 79.505 18
"""
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python calibrate_score.py <score> <raw_cand>")
        return 1
    score = float(sys.argv[1])
    raw = float(sys.argv[2])
    n = score * 200 / raw
    avg_t = 9000.0 / n
    print(f"score={score} raw_cand={raw}")
    print(f"  N       = {n:.0f}")
    print(f"  avg_t   = {avg_t:.2f} s/trace (per-cell)")
    print(f"  FYI: 90 分需 raw_total={90*200:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())