"""Render a static attack.py from an engine candidate set (F009 P1).

The competition accepts any AttackAlgorithm; a static candidate list is valid
and is what the local simulator evaluates (mock fire + guardrail replay).
"""

from __future__ import annotations

from pathlib import Path

HEADER = '''\
from aicomp_sdk.attacks import AttackAlgorithmBase, AttackCandidate, AttackRunConfig


class AttackAlgorithm(AttackAlgorithmBase):
    def run(self, env, config=None):
        return [
            AttackCandidate(user_messages=tuple(messages))
            for messages in _CANDIDATES
        ]


_CANDIDATES = [
'''


def build_static_attack(candidates: list, out_path: Path) -> Path:
    lines = [HEADER]
    for cand in candidates:
        if len(cand.messages) == 1:
            rendered = f"{cand.messages[0]!r},"
        else:
            rendered = ",\n".join(repr(m) for m in cand.messages)
        lines.append(f"    ({rendered}),\n")
    lines.append("]\n")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(lines), encoding="utf-8")
    return out_path
