# -*- coding: utf-8 -*-
"""Extract full text from downloaded arXiv PDFs (per dimension) for deep reading.

Output: extracted_full/<DIM>_<arxivid>.txt (one file per paper, all pages).
"""
import re
import pathlib

import fitz


ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
OUT = ROOT / "extracted_full"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    total = 0
    for folder in sorted(PAPERS.iterdir()):
        if not folder.is_dir() or not folder.name.startswith(("D1_", "D2_", "D3_")):
            continue
        prefix = folder.name.split("_", 1)[0]
        for pdf in sorted(folder.glob("arXiv_*.pdf")):
            pid = pdf.stem.replace("arXiv_", "")
            try:
                doc = fitz.open(pdf)
                parts = []
                for i in range(doc.page_count):
                    parts.append(f"\n\n----- [page {i + 1}] -----\n" + doc[i].get_text())
                text = "".join(parts)
                text = re.sub(r"[ \t]+", " ", text)
                (OUT / f"{prefix}_{pid}.txt").write_text(text, encoding="utf-8")
                total += 1
                print(f"{prefix}_{pid}: {doc.page_count} pages, {len(text)} chars")
            except Exception as exc:  # noqa: BLE001
                print(f"{prefix}_{pid}: ERROR {exc}")
    print("done:", total)


if __name__ == "__main__":
    main()
