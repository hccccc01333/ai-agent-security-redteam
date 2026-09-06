"""Registry CLI for the JED Research OS (Frontis-MA1 adaptation).

Query / update machine-readable experiment state without reading raw JSONL.

Commands:
  status                          one-screen summary (anchors, pending, gates)
  get <experiment_id>             pretty-print one registry entry
  search [--bucket B] [--status S] [--limit N]
  parents <experiment_id>         lineage chain up to the root anchor
  check --change "<text>"         scan ban/reconsider rules in experience.jsonl
  mark <experiment_id> --status promoted|rejected|pool --reason "<text>"

Usage (from project/):
  python scripts/registry.py status
  python scripts/registry.py check --change "把 inj_close 的 analysis body 改成 ok"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "registry" / "experiments.jsonl"
EXPERIENCE = ROOT / "registry" / "experience.jsonl"


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
                print(f"WARN skip malformed line in {path.name}", file=sys.stderr)
    return out


def find(entries: list[dict], eid: str) -> dict | None:
    for e in entries:
        if e.get("experiment_id", "").lower() == eid.lower():
            return e
    return None


def resolve(entries: list[dict], ref: str) -> dict | None:
    """Resolve a parent reference: exact id first, then variant file stem."""
    exact = find(entries, ref)
    if exact is not None:
        return exact
    rl = ref.lower()
    for e in entries:
        if Path(e.get("variant_file", "")).stem.lower() == rl:
            return e
    return None


def cmd_status(entries: list[dict]) -> int:
    best = [e for e in entries if e.get("metrics", {}).get("public_score") is not None]
    best.sort(key=lambda e: float(e["metrics"]["public_score"]), reverse=True)
    pending = [
        e
        for e in entries
        if e.get("decision", {}).get("submitted")
        and e.get("metrics", {}).get("public_score") is None
        and e.get("decision", {}).get("status") not in ("error", "no_score")
    ]
    local_pass = [
        e
        for e in entries
        if e.get("decision", {}).get("status") == "local_pass"
        and not e.get("decision", {}).get("submitted")
    ]
    print("== Registry status ==")
    if best:
        top = best[0]
        print(f"best: {top['experiment_id']} public={top['metrics']['public_score']}")
    else:
        print("best: (none scored yet)")
    print(
        f"entries: {len(entries)}  pending_submissions: {len(pending)}  "
        f"local_pass_unsubmitted: {len(local_pass)}"
    )
    for e in pending:
        d = e["decision"]
        print(f"  PENDING {e['experiment_id']} ref={d.get('submission_ref')} kernel={d.get('kernel_version')}")
    return 0


def cmd_get(entries: list[dict], eid: str) -> int:
    e = resolve(entries, eid)
    if e is None:
        print(f"NOT FOUND: {eid}", file=sys.stderr)
        return 1
    print(json.dumps(e, ensure_ascii=False, indent=2))
    return 0


def cmd_search(entries: list[dict], bucket: str | None, status: str | None, limit: int) -> int:
    hits = entries
    if bucket:
        hits = [e for e in hits if e.get("bucket") == bucket]
    if status:
        hits = [e for e in hits if e.get("decision", {}).get("status") == status]
    hits = hits[-limit:] if limit else hits
    for e in hits:
        d = e["decision"]
        score = e.get("metrics", {}).get("public_score")
        print(f"{e['experiment_id']}\tbucket={e.get('bucket')}\tstatus={d.get('status')}\tpublic={score}")
    return 0


def cmd_parents(entries: list[dict], eid: str) -> int:
    chain: list[str] = []
    cur = resolve(entries, eid)
    while cur is not None:
        chain.append(cur["experiment_id"])
        pid = cur.get("parent_id")
        if not pid:
            break
        cur = resolve(entries, pid)
        if cur is None:
            chain.append(f"{pid} (not registered)")
            break
    print(" -> ".join(reversed(chain)) if chain else f"NOT FOUND: {eid}")
    return 0


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9_\u4e00-\u9fff]{2,}", text.lower()) if len(t) >= 2}


def cmd_check(change: str) -> int:
    experiences = load_jsonl(EXPERIENCE)
    change_lower = change.lower()
    flagged = False
    for exp in experiences:
        ban = " ".join(exp.get("ban_condition", []))
        rec = " ".join(exp.get("reconsider_when", []))
        ban_tokens = _tokens(ban) | _tokens(exp.get("pattern", ""))
        change_tokens = _tokens(change_lower)
        overlap = ban_tokens & change_tokens
        if len(overlap) >= 2:
            print(f"BAN  {exp['id']} ({exp['pattern']}) [{len(overlap)} tokens]: {ban}")
            flagged = True
        elif _tokens(rec) & change_tokens:
            print(f"RECONSIDER  {exp['id']} ({exp['pattern']}): {rec}")
    if not flagged:
        print("NO_BAN (check reconsider lines above if any)")
    return 1 if flagged else 0


def cmd_mark(entries: list[dict], eid: str, status: str, reason: str) -> int:
    e = resolve(entries, eid)
    if e is None:
        print(f"NOT FOUND: {eid}", file=sys.stderr)
        return 1
    e["decision"]["status"] = status
    if reason:
        e["decision"]["reason"] = reason
    lines = [json.dumps(obj, ensure_ascii=False) for obj in entries]
    EXPERIMENTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"MARKED {eid} -> {status}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="JED experiment registry CLI")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    p_get = sub.add_parser("get")
    p_get.add_argument("experiment_id")
    p_search = sub.add_parser("search")
    p_search.add_argument("--bucket", default=None)
    p_search.add_argument("--status", default=None)
    p_search.add_argument("--limit", type=int, default=0)
    p_parents = sub.add_parser("parents")
    p_parents.add_argument("experiment_id")
    p_check = sub.add_parser("check")
    p_check.add_argument("--change", required=True)
    p_mark = sub.add_parser("mark")
    p_mark.add_argument("experiment_id")
    p_mark.add_argument(
        "--status", required=True, choices=["promoted", "rejected", "pool", "local_pass", "local_fail"]
    )
    p_mark.add_argument("--reason", default="")

    args = ap.parse_args()
    entries = load_jsonl(EXPERIMENTS)
    if args.command == "status":
        return cmd_status(entries)
    if args.command == "get":
        return cmd_get(entries, args.experiment_id)
    if args.command == "search":
        return cmd_search(entries, args.bucket, args.status, args.limit)
    if args.command == "parents":
        return cmd_parents(entries, args.experiment_id)
    if args.command == "check":
        return cmd_check(args.change)
    if args.command == "mark":
        return cmd_mark(entries, args.experiment_id, args.status, args.reason)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
