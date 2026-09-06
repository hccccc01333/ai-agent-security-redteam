# -*- coding: utf-8 -*-
"""Extract first-page abstract text from downloaded arXiv PDFs (per dimension)."""
import re
import pathlib

import fitz


ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
OUT = ROOT / "extracted"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for folder in sorted(PAPERS.iterdir()):
        if not folder.is_dir() or not folder.name.startswith(("D1_", "D2_", "D3_")):
            continue
        prefix = folder.name.split("_", 1)[0]
        readme = (folder / "README.md").read_text(encoding="utf-8")
        ids = re.findall(r"^\|\s*\d+\s*\|\s*(\d{4}\.\d{4,5})\s*\|", readme, re.M)
        titles = dict(
            re.findall(r"^\|\s*\d+\s*\|\s*(\d{4}\.\d{4,5})\s*\|\s*(.+?)\s*\|\s*20\d\d", readme, re.M)
        )
        lines = []
        for pid in ids:
            pdf = folder / f"arXiv_{pid}.pdf"
            if not pdf.exists():
                lines.append(f"===== {pid} =====\nMISSING PDF\n")
                continue
            try:
                doc = fitz.open(pdf)
                text = ""
                for i in range(min(2, doc.page_count)):
                    text += doc[i].get_text()
                text = re.sub(r"\s+", " ", text).strip()
                cut = text.find("1 Introduction")
                if cut == -1:
                    cut = text.find("Introduction")
                body = text[: cut if 200 < cut < 2600 else 2200]
                lines.append(
                    f"===== {pid} =====\nTITLE: {titles.get(pid, '?')}\n{body}\n"
                )
            except Exception as exc:  # noqa: BLE001
                lines.append(f"===== {pid} =====\nERROR: {exc}\n")
        (OUT / f"{prefix}.txt").write_text("\n".join(lines), encoding="utf-8")
        print(prefix, "ids:", len(ids), "chars:", sum(len(line) for line in lines))


if __name__ == "__main__":
    main()
