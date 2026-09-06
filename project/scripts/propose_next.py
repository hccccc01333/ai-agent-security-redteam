"""Next-experiment proposer (semi-automatic scheduler, Frontis-MA1 stage 4).

Reads registry + experience + anchors and drafts a 07-style task contract for
the next single bucket. The Research Director (user) approves before execution;
this script never creates variants or submits anything.

Usage (from project/):
  python scripts/propose_next.py --bucket pred_exfil
  python scripts/propose_next.py --bucket knob_probe
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "experiments.jsonl"


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


def resolve(entries: list[dict], ref: str) -> dict | None:
    rl = ref.lower()
    for e in entries:
        if e.get("experiment_id", "").lower() == rl:
            return e
    for e in entries:
        if Path(e.get("variant_file", "")).stem.lower() == rl:
            return e
    return None


SUGGESTIONS = {
    "pred_exfil": {
        "blocked": True,
        "note": "payload 轮换已被证伪（EXP-010）：SDK 只认 SECRET_MARKER/trace-read secrets，且 score cell 不含消息文本，轮换不增 cell。单消息族唯一杠杆仍是成交率/成本（W1 探针轴在途）；双 post 期望为负（34 raw @ 2x 成本 < 18 raw @ 1x）",
    },
    "knob_probe": {
        "waiting": True,
        "target": "探针稳定性",
        "change": "PROBE_REPS 5->8（成交率门槛不变）",
        "expected_mechanism": "更多探针样本降低小样本选型噪声，选中模板在填充期更稳；EXP-013 已由 W1=87.930（>=87.8）解锁同轴",
        "candidate_file": "variants/x6_reps8_fire65.py",
        "validation_trust": "low",
        "notes": "mock 3 盐仅参考（先例：W1 2/3 盐仍 +0.135）；硬门禁=ast/no_op/smoke；公榜判定 >=87.93；候选文件已存在（08-02 创建），本轮重新评估登记",
    },
    "pred_uta": {
        "blocked": True,
        "note": "多谓词/不可信源路径历史全部失败（EXP-005/EXP-009）；必须先用 09_crossover 合同或用户给出新的单谓词入口",
    },
}


def experience_gate(change: str) -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "registry.py"), "check", "--change", change],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    out = (r.stdout + r.stderr).strip()
    return r.returncode == 0, out


def main() -> int:
    ap = argparse.ArgumentParser(description="Draft the next 07 task contract")
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--parent", default=None)
    ap.add_argument("--id", default=None, help="candidate id, default auto (x1_payload_rot ...)")
    args = ap.parse_args()

    entries = load_jsonl(REGISTRY)
    sug = SUGGESTIONS.get(args.bucket)
    if sug is None:
        print(f"NO_SUGGESTION bucket={args.bucket} (Draft 需要用户给方向；可用桶: {', '.join(sorted(SUGGESTIONS))})")
        return 4
    if sug.get("waiting"):
        w1 = resolve(entries, "w1_probe5_fire65")
        if w1 is None or w1.get("metrics", {}).get("public_score") is None:
            print(f"BLOCKED {args.bucket}: W1 公榜未出（PENDING），同轴下一档不可提案")
            print(f"  {sug['note']}")
            return 3
    if sug.get("blocked"):
        print(f"BLOCKED {args.bucket}: {sug['note']}")
        return 3

    # anchor selection
    parent_id = args.parent
    if parent_id is None:
        w1 = resolve(entries, "w1_probe5_fire65")
        if w1 is not None and w1.get("metrics", {}).get("public_score") is not None:
            parent_id = "w1_probe5_fire65" if float(w1["metrics"]["public_score"]) >= 87.795 else "Q5"
        else:
            parent_id = "Q5"
    parent = resolve(entries, parent_id) or {"experiment_id": parent_id, "metrics": {"public_score": None}}
    parent_score = parent.get("metrics", {}).get("public_score")

    ok, gate_out = experience_gate(sug["change"])
    if not ok:
        print("BLOCKED experience_check:")
        print(gate_out)
        return 2

    cid = args.id or "x1_payload_rot"
    contract = f"""operation: improve
candidate_id: {cid}
parent_id: {parent['experiment_id']}
parent_variant: {parent.get('variant_file', 'variants/q5_inj_short.py')}
bucket: {args.bucket}

objective: 在不改 Q5 骨架与模板体的前提下，把 EXFIL unique cell 密度提高（payload 轮换）

single_hypothesis:
  target: {sug['target']}
  change: {sug['change']}
  expected_mechanism: {sug['expected_mechanism']}

experience_check: PASS（{gate_out.splitlines()[0] if gate_out else 'no ban'}）

allowed_files:
  - project/{sug['candidate_file']}
  - project/attack.py

frozen_files:
  - project/variants/*
  - project/scripts/*
  - project/registry/*
  - project/notebooks/kernel_submit/*
  - 咨询包/memory/*
  - 咨询包/prompts/*

required_runs:
  - python scripts/evaluate_candidate.py --variant {sug['candidate_file']} --parent {parent.get('variant_file', 'variants/q5_inj_short.py')} --bucket {args.bucket} --hypothesis "{sug['change']}" --mock --copy-attack --validation-trust {sug['validation_trust']}
  - python scripts/registry.py check --change "{sug['change']}"
  - （用户说「提交」后）powershell -File scripts/submit_one.ps1 -Variant {Path(sug['candidate_file']).name} -Msg "{cid}: payload rotation"

promotion_gate:
  ast/no_op/smoke: pass
  mock_stability: pass (3 salts, salt=''/'1'/'2')
  public_verdict: >= {parent_score if parent_score is not None else 'parent 公榜分'}

notes: {sug.get('notes', '')}
"""
    print(contract)
    print(f"PROPOSAL {cid} READY — 需用户批准后才实现/评估/提交")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
