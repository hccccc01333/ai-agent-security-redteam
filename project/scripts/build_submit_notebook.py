"""Rebuild notebooks/kernel_submit/submit.ipynb from project/attack.py.

Match high-scoring public kernels (Assia / Pilkwang):
- sys.argv reset + path bootstrap
- write /kaggle/working/attack.py
- competition rerun: serve() only
- dry-run only: placeholder submission.csv (do NOT write CSV during rerun)
"""

from __future__ import annotations

import json
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
ATTACK = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (ROOT / "attack.py")
NB_DIR = ROOT / "notebooks" / "kernel_submit"
NB_DIR.mkdir(parents=True, exist_ok=True)

attack_src = ATTACK.read_text(encoding="utf-8")
# Raw triple-quoted string like Assia; escape ''' if present.
if "'''" in attack_src:
    raise SystemExit("attack.py contains ''' — refuse to embed")
attack_raw = attack_src

cells = [
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys, glob, os, csv\n",
            "from pathlib import Path\n",
            "\n",
            "sys.argv = [sys.argv[0]]\n",
            "\n",
            "for candidate in glob.glob('/kaggle/input/**/kaggle_evaluation', recursive=True):\n",
            "    dataset_root = str(Path(candidate).parent)\n",
            "    if dataset_root not in sys.path:\n",
            "        sys.path.insert(0, dataset_root)\n",
            "    break\n",
            "\n",
            "print('Setup complete | IS_RERUN:', bool(os.getenv('KAGGLE_IS_COMPETITION_RERUN')))\n",
            "\n",
            f"attack_code = r'''{attack_raw}'''\n",
            "\n",
            "with open('/kaggle/working/attack.py', 'w', encoding='utf-8') as f:\n",
            "    f.write(attack_code)\n",
            "print('wrote attack.py', len(attack_code))\n",
            "\n",
            "import py_compile, ast\n",
            "py_compile.compile('/kaggle/working/attack.py', doraise=True)\n",
            "names = [n.name for n in ast.parse(attack_code).body if isinstance(n, ast.ClassDef)]\n",
            "assert 'AttackAlgorithm' in names, names\n",
            "print('compile+AST OK', names)\n",
            "\n",
            "if bool(os.getenv('KAGGLE_IS_COMPETITION_RERUN')):\n",
            "    import kaggle_evaluation.jed_attack_134815.jed_attack_inference_server as server\n",
            "    server.JEDAttackInferenceServer().serve()\n",
            "else:\n",
            "    # Dry-run only: needed so Kaggle can attach a code-submission artifact.\n",
            "    # Must NOT write this during competition rerun (Pilkwang / Assia pattern).\n",
            "    with open('/kaggle/working/submission.csv', 'w', newline='') as f:\n",
            "        w = csv.writer(f)\n",
            "        w.writerow(['Id', 'Score'])\n",
            "        for r in ['gpt_oss_public', 'gpt_oss_private', 'gemma_public', 'gemma_private']:\n",
            "            w.writerow([r, 0.0])\n",
            "    print('placeholder submission.csv written (dry-run)')\n",
        ],
    },
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}
(NB_DIR / "submit.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

meta_path = NB_DIR / "kernel-metadata.json"
meta = {
    "id": "afterrain42/jed-attack-v1",
    "title": "JED Attack v1",
    "code_file": "submit.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": False,
    "enable_tpu": False,
    "enable_internet": False,
    "keywords": [],
    "dataset_sources": [],
    "kernel_sources": [],
    "competition_sources": ["ai-agent-security-multi-step-tool-attacks"],
    "model_sources": [],
}
if meta_path.exists():
    old = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["id"] = old.get("id") or meta["id"]
meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(f"rebuilt {NB_DIR / 'submit.ipynb'} attack_chars={len(attack_src)}")
print(f"id={meta['id']} enable_gpu={meta['enable_gpu']}")
