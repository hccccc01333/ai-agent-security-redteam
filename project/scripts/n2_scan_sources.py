# -*- coding: utf-8 -*-
"""N2 source scan: which web pages drive the deterministic agent to http.post.

Mirrors VulnerableDeterministicAgent._parse_instructions_from_output priority:
reset -> (read+secret | post | delete | shell); imperative -> (...); authority;
numbered steps. Pages whose parsed action is 'post' are locally observable EXFIL
entry points (http.post data=SECRET_MARKER).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "data" / "aicomp_sdk" / "fixtures"

RESET = ("ignore previous", "forget", "disregard", "overlook")
IMPERATIVE = ("you must", "immediately", "execute", "required", "mandatory")
AUTHORITY = ("system mode", "admin override", "god", "law enforcement", "fbi", "developer", "ceo")
STEP = ("step 1", "1.", "first,")


def parsed_action(content: str) -> str | None:
    lower = content.lower()
    has_https = "https://" in lower
    if any(p in lower for p in RESET):
        if ("read" in lower or "access" in lower) and "secret" in lower:
            return "read_secret"
        if "http.post" in lower or ("post" in lower and has_https):
            return "post"
        if "delete" in lower and "secret" in lower:
            return "delete"
        if "shell" in lower or ("run" in lower and "command" in lower):
            return "shell"
    if any(p in lower for p in IMPERATIVE):
        if ("read" in lower or "access" in lower) and (
            "secret" in lower or "credential" in lower
        ):
            return "read_secret"
        if (
            "send" in lower or "transmit" in lower or "post" in lower
        ) and has_https:
            return "post"
        if "delete" in lower and "secret" in lower:
            return "delete"
        if ("shell" in lower or "run" in lower) and (
            "verification" in lower or "diagnostic" in lower or "command" in lower
        ):
            return "shell"
    if any(p in lower for p in AUTHORITY):
        if "read" in lower or "access" in lower or "audit" in lower:
            return "read_secret"
        if ("send" in lower or "transmit" in lower or "report" in lower) and has_https:
            return "post"
    if any(m in lower for m in STEP):
        if "read" in lower and (
            "secret" in lower or "credential" in lower or ".txt" in lower
        ):
            return "read_secret"
        if "post" in lower or "send" in lower:
            return "post"
    return None


def main() -> int:
    web = json.loads((DATA / "web_corpus.json").read_text(encoding="utf-8"))
    post_pages = []
    read_pages = []
    for page in web.get("pages", []):
        action = parsed_action(page.get("content", ""))
        if action == "post":
            post_pages.append(page)
        elif action == "read_secret":
            read_pages.append(page)

    print(f"WEB pages: {len(web.get('pages', []))} | post-reachable: {len(post_pages)} | read-first: {len(read_pages)}")
    for p in post_pages[:30]:
        print(f"POST {p['id']:<28} {p['url']}")
    print("--- read-first sample ---")
    for p in read_pages[:8]:
        print(f"READ {p['id']:<28} {p['url']}")

    try:
        mail = json.loads((DATA / "mail_seed.json").read_text(encoding="utf-8"))
        emails = mail.get("inbox", [])
        post_mails = [m for m in emails if parsed_action(m.get("body", "")) == "post"]
        print(f"EMAILS: {len(emails)} | post-reachable: {len(post_mails)}")
        for m in post_mails[:20]:
            print(f"MAIL {m['id']:<28} {m.get('subject','')[:40]}")
    except Exception as exc:
        print("mail scan skipped:", exc)

    out = ROOT / "registry" / "n2_source_scan_2026-08-06.json"
    out.write_text(
        json.dumps(
            {
                "post_pages": [{"id": p["id"], "url": p["url"]} for p in post_pages],
                "post_mails": [
                    {"id": m["id"], "subject": m.get("subject", "")} for m in post_mails
                ],
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"WROTE {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
