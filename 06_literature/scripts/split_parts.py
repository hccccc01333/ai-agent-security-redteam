# -*- coding: utf-8 -*-
"""Split extracted abstract files into small chunks for batch reading."""
import re
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "extracted"
PER_PART = 6


def split_file(name: str, prefix: str) -> None:
    text = (EXTRACTED / name).read_text(encoding="utf-8")
    matches = list(re.finditer(r"===== (\d{4}\.\d{4,5}) =====", text))
    entries = []
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        entries.append(f"{m.group(0)}{text[start:end]}")
    parts = [entries[i : i + PER_PART] for i in range(0, len(entries), PER_PART)]
    for idx, part in enumerate(parts, 1):
        (EXTRACTED / f"{prefix}_part{idx}.txt").write_text(
            "\n=====".join(part), encoding="utf-8"
        )
        print(prefix, idx, len(part), "papers")


def main() -> None:
    split_file("D1.txt", "D1")
    split_file("D2.txt", "D2")
    split_file("D3.txt", "D3")


if __name__ == "__main__":
    main()
