"""f035d autonomous monitor + final-shot launcher (2026-08-31).

Polls Kaggle submissions; when the trigger conditions are met, pushes the
F035D launch package (rebuilt from variants/f035d_pool.py = byte-identical
to kernel_stage/jed-attack-v1/submit.ipynb) and submits the final daily shot.

Submit conditions (only when today's used quota == 4, i.e. 1 shot left):
  a) f035b (ref 55895314) is no longer PENDING (scored) -> judge + submit
  b) Beijing time >= 07:30 and f035b still PENDING        -> force submit
Quota states: used>=5 -> stop (exhausted); used<4 -> stop (new day, no force).

Safety guards: never resubmit if a submission already mentions F035D; the
launch package content MUST be F035D (rebuild + verify against launch pkg);
push/submit retry <= 2 times, then stop with an explicit error record.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(ROOT)
REG = os.path.join(PROJECT, "registry")
os.makedirs(REG, exist_ok=True)

COMP = "ai-agent-security-multi-step-tool-attacks"
KERNEL = "afterrain42/jed-attack-v1"
F035B_REF = "55895314"
ANCHOR = 80.775
DEADLINE_BJ = (7, 30)  # Beijing HH:MM
POLL_S = int(os.environ.get("F035D_POLL_S", "240"))
MAX_ATTEMPTS = 3  # 1 initial + up to 2 retries

LOG = os.path.join(REG, "f035d_monitor.log")
STATUS = os.path.join(REG, "f035d_monitor_status.txt")

F035D_SRC = os.path.join(PROJECT, "variants", "f035d_pool.py")
BUILD_PY = os.path.join(ROOT, "build_submit_notebook.py")
NB_DIR = os.path.join(PROJECT, "notebooks", "kernel_submit")
NB_NOTEBOOK = os.path.join(NB_DIR, "submit.ipynb")
NB_META = os.path.join(NB_DIR, "kernel-metadata.json")
LAUNCH_NOTEBOOK = os.path.join(PROJECT, "kernel_stage", "jed-attack-v1", "submit.ipynb")
STAGE = os.path.join(os.path.expanduser("~"), "kaggle_kernels", "jed-attack-v1")

F035D_TITLE = "F035D — 多习语混合池 + 编码多样化"
SUBMIT_MSG = "f035D multi-idiom S+R mix"


def log(msg: str) -> None:
    line = f"[{_dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def set_status(s: str) -> None:
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write(s)
    log("STATUS=" + s)


def now_bj() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc).astimezone(_dt.timezone(_dt.timedelta(hours=8)))


def get_subs():
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    return api.competition_submissions(COMP)


def is_pending(s) -> bool:
    return "PENDING" in str(getattr(s, "status", "") or "")


def find_f035b(subs):
    for s in subs:
        if str(getattr(s, "ref", "")) == F035B_REF:
            return s
    return None


def count_today_used(subs) -> int:
    today = _dt.datetime.now(_dt.timezone.utc).date().isoformat()
    n = 0
    for s in subs:
        d = str(getattr(s, "date", "") or "")
        if d[:10] == today:
            n += 1
    return n


def has_f035d(subs) -> bool:
    return any("F035D" in (getattr(s, "description", "") or "") for s in subs)


def notebook_is_f035d(path: str) -> bool:
    try:
        nb = json.load(open(path, encoding="utf-8"))
        srcs = []
        for c in nb.get("cells", []):
            if c.get("cell_type") == "code":
                s = c.get("source", "")
                srcs.append("".join(s) if isinstance(s, list) else s)
        head = "".join(srcs)
        return F035D_TITLE in head
    except Exception as e:
        log(f"notebook check error: {e}")
        return False


def rebuild_f035d() -> bool:
    r = subprocess.run([sys.executable, BUILD_PY, F035D_SRC], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        log("rebuild FAILED: " + (r.stdout[-1500:] + r.stderr[-1500:]))
        return False
    if not notebook_is_f035d(NB_NOTEBOOK):
        log("rebuilt notebook is NOT F035D -> abort")
        return False
    if os.path.exists(LAUNCH_NOTEBOOK):
        a = hashlib.md5(open(LAUNCH_NOTEBOOK, "rb").read()).hexdigest()
        b = hashlib.md5(open(NB_NOTEBOOK, "rb").read()).hexdigest()
        if a != b:
            log(f"rebuilt notebook differs from launch package ({a} vs {b}) -> abort")
            return False
    log(f"F035D notebook rebuilt + verified ({os.path.getsize(NB_NOTEBOOK)} bytes, md5 ok)")
    return True


def push_kernel() -> int:
    os.makedirs(STAGE, exist_ok=True)
    shutil.copyfile(NB_NOTEBOOK, os.path.join(STAGE, "submit.ipynb"))
    if os.path.exists(NB_META):
        shutil.copyfile(NB_META, os.path.join(STAGE, "kernel-metadata.json"))
    last_err = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        r = subprocess.run(["kaggle", "kernels", "push", "-p", STAGE],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        log(f"push attempt {attempt}: {out[-1200:]}")
        m = re.search(r"Kernel version (\d+) successfully pushed", out)
        if m:
            ver = int(m.group(1))
            log(f"pushed kernel v{ver}")
            return ver
        if re.search(r"CPU session limit|429|503|timeout", out, re.I):
            log("push transient, retry in 30s")
            time.sleep(30)
            continue
        last_err = out[-2000:]
        if attempt < MAX_ATTEMPTS:
            log("push failed, retry in 20s")
            time.sleep(20)
    log("push FAILED after attempts: " + last_err)
    return 0


def wait_kernel_complete(ver: int) -> bool:
    for i in range(1, 51):
        r = subprocess.run(["kaggle", "kernels", "status", "-k", KERNEL],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        s = ((r.stdout or "") + (r.stderr or "")).strip()
        if "COMPLETE" in s:
            log(f"kernel v{ver} COMPLETE")
            return True
        if re.search(r"ERROR|CANCEL", s):
            log(f"kernel v{ver} failed: {s}")
            return False
        time.sleep(12)
    log("timeout waiting kernel complete")
    return False


def submit_f035d(ver: int) -> str:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = api.competition_submit_code(
                file_name="submission.csv",
                message=SUBMIT_MSG,
                competition=COMP,
                kernel=KERNEL,
                kernel_version=ver,
            )
            log(f"submit response: {resp}")
            m = re.search(r"ref[^0-9]{0,6}(\d{5,})", str(resp), re.I)
            if m:
                return m.group(1)
            time.sleep(20)
            for s in get_subs():
                if SUBMIT_MSG in (getattr(s, "description", "") or ""):
                    return str(getattr(s, "ref", ""))
            log("no ref parsed; will re-check in list later")
            return ""
        except Exception as e:
            log(f"submit attempt {attempt} failed: {e}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(20)
    return ""


def do_submit(reason: str) -> None:
    set_status(f"SUBMIT_START:{reason}")
    subs = get_subs()
    if has_f035d(subs):
        log("F035D already in submission list -> not resubmitting")
        set_status("ALREADY_SUBMITTED")
        sys.exit(0)
    used = count_today_used(subs)
    if used != 4:
        log(f"quota not exactly 4 (used={used}) at submit time -> no forced submit")
        set_status(f"QUOTA_CHANGED:{used}")
        sys.exit(0)
    if not rebuild_f035d():
        set_status("REBUILD_FAILED")
        sys.exit(1)
    ver = push_kernel()
    if not ver:
        set_status("PUSH_FAILED")
        sys.exit(1)
    if not wait_kernel_complete(ver):
        set_status("KERNEL_FAILED")
        sys.exit(1)
    ref = submit_f035d(ver)
    if ref:
        set_status(f"SUBMITTED_F035D:{ref}")
        log(f"F035D SUBMITTED ref={ref} kernel_v={ver}")
        time.sleep(15)
        try:
            for s in get_subs():
                if str(getattr(s, "ref", "")) == ref:
                    log(f"confirmed in list: status={s.status} desc={(getattr(s,'description','') or '')[:60]}")
                    break
        except Exception as e:
            log(f"post-submit list check error: {e}")
        sys.exit(0)
    set_status("SUBMIT_NO_REF")
    sys.exit(1)


def main() -> None:
    log(f"=== f035d monitor start (poll={POLL_S}s, deadline BJ {DEADLINE_BJ[0]:02d}:{DEADLINE_BJ[1]:02d}) ===")
    set_status("RUNNING")
    while True:
        try:
            subs = get_subs()
            used = count_today_used(subs)
            f035b = find_f035b(subs)
            bj = now_bj()
            bj_min = bj.hour * 60 + bj.minute

            if has_f035d(subs):
                log("F035D already submitted -> stop")
                set_status("ALREADY_SUBMITTED")
                return
            if used >= 5:
                log(f"quota exhausted (used={used}) -> stop")
                set_status("QUOTA_EXHAUSTED")
                return
            if used < 4:
                log(f"quota refreshed / new day (used={used}) -> stop, no forced submit")
                set_status("QUOTA_REFRESHED")
                return

            if f035b is not None and not is_pending(f035b):
                score = getattr(f035b, "public_score", None)
                if score is not None:
                    judge = "GENERAL_METHOD_VALID" if float(score) >= ANCHOR else "NEW_ROUTE_DEAD"
                    log(f"f035b SCORED = {score} ({judge})")
                    set_status(f"F035B_SCORED:{score}")
                else:
                    log("f035b terminal without score -> submit final shot")
                    set_status("F035B_TERMINAL")
                do_submit(f"f035b_scored:{score}")
                return

            if bj_min >= DEADLINE_BJ[0] * 60 + DEADLINE_BJ[1]:
                log(f"deadline BJ {bj.strftime('%H:%M')} reached, f035b still PENDING -> force submit")
                set_status("DEADLINE_FORCE")
                do_submit("deadline")
                return

            log(f"poll bj={bj.strftime('%Y-%m-%d %H:%M')} used={used} f035b_pending; sleep {POLL_S}s")
            time.sleep(POLL_S)
        except KeyboardInterrupt:
            set_status("STOPPED")
            return
        except Exception as e:
            log("monitor error: " + traceback.format_exc())
            set_status(f"ERROR:{e}")
            time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        log("fatal: " + traceback.format_exc())
        set_status("FATAL")
        sys.exit(1)
