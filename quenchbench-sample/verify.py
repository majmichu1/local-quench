#!/usr/bin/env python3
"""Check every task in this QuenchBench sample: the starting project fails its checks and the reference solution
passes them (for test-writing tasks: the reference tests pass on the real code and catch every mutant; for reading
tasks: the reference answer contains every key fact the grader looks for, and an empty answer does not).

    python3 verify.py [section ...]

Standalone: Python 3.9+, no packages needed (PyYAML is used when it is installed, else a small reader takes the
few fields needed from task.yaml), plus the toolchains of the tasks you check (node, go, bash; for the web tasks, run
this script with a Python that has Playwright). Nothing is written outside a
temporary folder.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = f'"{sys.executable}"'  # the Python running this script (for the web tasks: one with Playwright installed)
CHECK = {"python": f"{PY} -m unittest discover -q -p 'test_hidden*.py'", "javascript": "node --test hidden.test.mjs",
         "go": "go test -count=1 ./...", "bash": "bash hidden_test.sh",
         "web": f"{PY} -m unittest discover -q -p 'test_hidden*.py'",
         "c": "cc -std=c11 -Wall -O1 -g -o .forge_test *.c -lm && ./.forge_test", "rust": "cargo test --offline -q"}
SELF = {"python": f"{PY} -m unittest discover -q", "javascript": "node --test", "go": "go test -count=1 ./...",
        "bash": "bash test.sh", "c": "cc -std=c11 -Wall -O1 -g -o .forge_test *.c -lm && ./.forge_test",
        "rust": "cargo test --offline -q"}


def load(path: Path) -> dict:
    try:
        import yaml  # the full reader when it is installed

        return yaml.safe_load(path.read_text("utf-8"))
    except ImportError:
        pass
    text = path.read_text("utf-8")  # the fields this script needs, from the plain layout the generator writes
    out: dict = {"grade": re.search(r"^grade: *(\S+)", text, re.M).group(1)}
    m = re.search(r"^answer:\n((?:- .*\n)+)", text, re.M)
    out["answer"] = [json.loads(x[2:]) if x[2:].startswith('"') else x[2:].strip("'") for x in m.group(1).splitlines()] if m else []
    m = re.search(r"^  impl: *(\S+)", text, re.M)
    out["mutation"] = {"impl": m.group(1)} if m else {}
    m = re.search(r"^timeout: *(\d+)", text, re.M)
    out["timeout"] = int(m.group(1)) if m else 120
    return out


def run(cmd: str, cwd: Path, timeout: float) -> int:
    try:
        return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return 124


def fresh(lang_dir: Path, tmp: Path) -> Path:
    work = tmp / "w"
    if (lang_dir / "repo").is_dir():
        shutil.copytree(lang_dir / "repo", work)
    else:  # some terminal tasks build their starting state in setup.sh (a git history, say)
        work.mkdir()
    if (lang_dir / "setup.sh").is_file():
        run(f"bash {lang_dir / 'setup.sh'}", work, 300)
    if not (work / ".git").exists():  # the benchmark starts every task from a commit, to diff against
        for cmd in ("git init -q", "git add -A", "git -c user.name=q -c user.email=q@local commit -qm start --allow-empty"):
            run(cmd, work, 60)
    if (HERE / "forge_ui.py").is_file() and lang_dir.name == "web":
        shutil.copy(HERE / "forge_ui.py", work / "forge_ui.py")
    return work


def overlay(src: Path, work: Path) -> None:
    for f in src.rglob("*") if src.is_dir() else []:
        if f.is_file() and f.name != "ANSWER.md":
            dst = work / f.relative_to(src)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, dst)
    if src.name == "solution" and (src.parent / "solution.sh").is_file():  # a fix made with commands (git, say)
        run(f"bash {src.parent / 'solution.sh'}", work, 300)


def verify(task_dir: Path) -> tuple[bool, str]:
    spec = load(task_dir / "task.yaml")
    lang_dir = next(p for p in task_dir.iterdir() if p.is_dir())
    lang, kind = lang_dir.name, spec.get("grade", "tests")
    timeout = float(spec.get("timeout") or 120)
    if kind == "answer":
        ref = (lang_dir / "solution" / "ANSWER.md").read_text("utf-8")
        missing = [p for p in spec.get("answer") or [] if not re.search(p, ref, re.I | re.M)]
        empty_ok = all(re.search(p, "", re.I | re.M) for p in spec.get("answer") or [])
        return not missing and not empty_ok, f"reference answer has every key fact{'' if not missing else ': missing ' + str(missing)}"
    with tempfile.TemporaryDirectory() as t:
        work = fresh(lang_dir, Path(t))
        if kind == "mutation":
            overlay(lang_dir / "solution", work)
            impl = (spec.get("mutation") or {}).get("impl")
            if isinstance(impl, dict):
                impl = impl.get(lang)
            if run(SELF[lang], work, timeout) != 0:
                return False, "reference tests fail on the real code"
            survived = []
            for m in sorted((lang_dir / "mutants").glob("*")):
                shutil.copy(m, work / impl)
                if run(SELF[lang], work, timeout) == 0:
                    survived.append(m.name)
            return not survived, "reference tests catch every mutant" if not survived else f"mutants survived: {survived}"
        overlay(lang_dir / "hidden", work)
        start = run(CHECK[lang], work, timeout)
    with tempfile.TemporaryDirectory() as t:
        work = fresh(lang_dir, Path(t))
        overlay(lang_dir / "solution", work)
        overlay(lang_dir / "hidden", work)
        done = run(CHECK[lang], work, timeout)
    ok = start != 0 and done == 0
    return ok, f"start {'fails' if start else 'PASSES (bad)'}, solution {'passes' if done == 0 else 'FAILS (bad)'}"


def main() -> None:
    wanted = set(sys.argv[1:])
    tasks = sorted(p.parent for p in (HERE / "tasks").glob("*/*/task.yaml") if not wanted or p.parent.parent.name in wanted)
    bad = 0
    for t in tasks:
        lang = next(p for p in t.iterdir() if p.is_dir()).name
        if not shutil.which({"python": "python3", "web": "python3", "javascript": "node", "go": "go", "bash": "bash",
                             "c": "cc", "rust": "cargo"}[lang]):
            print(f"  skip  {t.parent.name}/{t.name} ({lang}: toolchain not installed)")
            continue
        ok, why = verify(t)
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'}  {t.parent.name}/{t.name} ({lang}): {why}")
    print(f"{len(tasks) - bad} of {len(tasks)} tasks verified" + ("" if not bad else f"; {bad} failed"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
