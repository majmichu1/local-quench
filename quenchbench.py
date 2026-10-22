#!/usr/bin/env python3
"""Run QuenchBench (or SWE-bench, Terminal-Bench, Aider Polyglot) on your own model, from the command line.

    python3 quenchbench.py                  # asks: model server, model, benchmark, size
    python3 quenchbench.py --server http://localhost:1234 --model qwen3.8-27b --suite forge --size quick --yes

What it does:
  1. downloads the latest Local Quench build for this computer from the GitHub releases (once; the
     benchmark runs inside it, without opening a window),
  2. asks which model server to use and lists the models it serves,
  3. asks which benchmark to run and how much of it,
  4. runs it and prints each task as it finishes, then the score.

Needs Python 3.9+ and nothing else. Everything (the app, settings, results) stays in one folder,
~/QuenchBench by default (--home to change it); your own Local Quench settings are not touched.
Results are not uploaded anywhere. To put a result on the public leaderboard, let the script copy the
run into the Local Quench app at the end, then share it from the app (Benchmarks).

Windows 10/11 and 64-bit Linux. No macOS build yet.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO = "majmichu1/local-quench"
UA = {"User-Agent": "quenchbench-script"}

SERVERS = [  # id, label, address, cloud (needs an API key), environment variable for the key
    ("lmstudio", "LM Studio", "http://localhost:1234", False, ""),
    ("ollama", "Ollama", "http://localhost:11434", False, ""),
    ("llama-server", "llama.cpp (llama-server)", "http://localhost:8080", False, ""),
    ("vllm", "vLLM", "http://localhost:8000", False, ""),
    ("nvidia", "NVIDIA build (free key from build.nvidia.com)", "https://integrate.api.nvidia.com", True,
     "NVIDIA_API_KEY"),
    ("openrouter", "OpenRouter", "https://openrouter.ai/api", True, "OPENROUTER_API_KEY"),
]

SUITES = [  # id, label, needs Docker or Podman
    ("forge", "QuenchBench: which kinds of coding work the model handles (sections x languages)", False),
    ("aider-polyglot", "Aider Polyglot: 225 Exercism exercises in 6 languages (beta)", True),
    ("swe-verified", "SWE-bench Verified: 500 real GitHub issues in Python", True),
    ("swe-multilingual", "SWE-bench Multilingual: 300 issues in 9 languages (beta)", True),
    ("terminal-bench-2", "Terminal-Bench 2.0: 89 tasks in a terminal (beta)", True),
]

SIZES = [  # QuenchBench only
    ("smoke", "a handful of tasks, a few minutes: checks that everything works"),
    ("quick", "a sample of every section, about an hour on a local GPU"),
    ("full", "all tasks, several hours"),
]

DONE = ("passed", "failed", "error", "skipped")


def say(text: str = "") -> None:
    print(text, flush=True)


def stop(text: str) -> None:
    print(f"\n{text}", file=sys.stderr, flush=True)
    sys.exit(1)


def choose(title: str, options: list[str], default: int = 0) -> int:
    say(f"\n{title}")
    for i, label in enumerate(options, 1):
        say(f"  {i}) {label}")
    while True:
        try:
            answer = input(f"Choose 1-{len(options)} [{default + 1}]: ").strip()
        except EOFError:  # nobody to ask (piped, scheduled): take the default
            answer = ""
        if not answer:
            return default
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1


def get_json(url: str, headers: dict[str, str] | None = None, timeout: float = 15) -> object:
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


# --- the app ------------------------------------------------------------------------------------------

def asset_name() -> str:
    if sys.platform == "win32":
        return "windows-x64.zip"
    if sys.platform.startswith("linux") and platform.machine() in ("x86_64", "AMD64"):
        return "x86_64.AppImage"
    stop("Local Quench has builds for Windows (64-bit) and Linux (x86_64) only, so the benchmark cannot run "
         "on this computer yet.")
    return ""


def app_path(home: Path) -> Path:
    if sys.platform == "win32":
        return home / "app" / "local-forge" / "local-forge.exe"
    return home / "app" / "LocalQuench.AppImage"


def download(url: str, target: Path) -> None:
    tmp = target.with_suffix(target.suffix + ".part")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as out:
        total = int(resp.headers.get("Content-Length") or 0)
        got = 0
        while chunk := resp.read(1 << 20):
            out.write(chunk)
            got += len(chunk)
            if total:
                print(f"\r  {got >> 20} / {total >> 20} MB", end="", flush=True)
    say()
    tmp.replace(target)


def install_app(home: Path, update: bool) -> Path:
    """The newest release, downloaded once into home/app; again only with --update."""
    exe = app_path(home)
    version_file = home / "app" / "version.txt"
    if exe.exists() and not update:
        return exe
    try:
        release = get_json(f"https://api.github.com/repos/{REPO}/releases/latest")
    except (urllib.error.URLError, OSError) as exc:
        if exe.exists():
            say(f"Could not check for a newer build ({exc}); using the one already here.")
            return exe
        stop(f"Could not reach GitHub to download Local Quench: {exc}")
    tag = release["tag_name"]
    if exe.exists() and version_file.exists() and version_file.read_text().strip() == tag:
        return exe
    want = asset_name()
    asset = next((a for a in release["assets"] if a["name"].endswith(want)), None)
    if not asset:
        stop(f"The release {tag} has no {want} build.")
    say(f"Downloading Local Quench {tag} ({asset['size'] >> 20} MB), once...")
    (home / "app").mkdir(parents=True, exist_ok=True)
    if want.endswith(".zip"):
        archive = home / "app" / asset["name"]
        download(asset["browser_download_url"], archive)
        shutil.rmtree(home / "app" / "local-forge", ignore_errors=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(home / "app")
        archive.unlink()
    else:
        download(asset["browser_download_url"], exe)
        exe.chmod(exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if not exe.exists():
        stop(f"The download did not contain {exe.name}.")
    version_file.write_text(tag)
    return exe


# --- model server and model ---------------------------------------------------------------------------

def list_models(base: str, key: str) -> list[str]:
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    data = get_json(base.rstrip("/") + "/v1/models", headers)
    ids = [m.get("id", "") for m in (data.get("data") or [])] if isinstance(data, dict) else []
    return sorted(i for i in ids if i and "embed" not in i.lower())


def pick_server(args: argparse.Namespace) -> tuple[str, str, str, bool]:
    """(provider id, address, API key, cloud)."""
    if args.server:
        known = next((s for s in SERVERS if s[2].rstrip("/") == args.server.rstrip("/")), None)
        pid, cloud, env = (known[0], known[3], known[4]) if known else ("custom", False, "")
        return pid, args.server, os.environ.get(args.key_env or env, ""), cloud
    i = choose("Which model server?", [f"{label}  ({url})" for _, label, url, _, _ in SERVERS] + ["Another address"])
    if i == len(SERVERS):
        url = input("Address of an OpenAI-compatible server, e.g. http://192.168.1.20:1234: ").strip()
        return "custom", url, os.environ.get(args.key_env, "") if args.key_env else "", False
    pid, label, url, cloud, env = SERVERS[i]
    key = os.environ.get(env, "")
    if cloud and not key:
        import getpass

        key = getpass.getpass(f"{label} API key (or set {env} next time; it is not saved): ").strip()
    return pid, url, key, cloud


def pick_model(args: argparse.Namespace, base: str, key: str) -> str:
    try:
        models = list_models(base, key)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        stop(f"Cannot reach the model server at {base} ({exc}). Start it (in LM Studio: Developer > Start "
             "server), or pass --server with its address.")
    if args.model:
        if models and args.model not in models:
            say(f"Note: {args.model} is not in the server's list; trying it anyway.")
        return args.model
    if not models:
        stop("The server lists no models. Load one (or download one) and start again.")
    return models[choose("Which model?", models)]


# --- the run -----------------------------------------------------------------------------------------

def write_settings(config: Path, pid: str, base: str, key: str, cloud: bool, model: str) -> None:
    path = config / "settings.json"
    data = json.loads(path.read_text("utf-8")) if path.exists() else {}
    providers = [p for p in data.get("providers") or [] if p.get("id") != pid]
    providers.append({"id": pid, "label": dict((s[0], s[1]) for s in SERVERS).get(pid, "Custom server"),
                      "base_url": base, "kind": "cloud" if cloud else "local", "api_key": key})
    data.update(base_url=base, active_provider=pid, providers=providers, active_model=model)
    config.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), "utf-8")


def forget_key(config: Path, pid: str) -> None:
    path = config / "settings.json"
    try:
        data = json.loads(path.read_text("utf-8"))
        for p in data.get("providers") or []:
            if p.get("id") == pid:
                p["api_key"] = ""
        path.write_text(json.dumps(data, indent=2), "utf-8")
    except (OSError, ValueError):
        pass


def newest_run(bench: Path, since: float) -> Path | None:
    runs = [f for f in bench.glob("*/run.json") if f.stat().st_mtime >= since]
    return max(runs, key=lambda f: f.stat().st_mtime) if runs else None


def read_run(path: Path | None) -> dict:
    try:
        return json.loads(path.read_text("utf-8")) if path else {}
    except (OSError, ValueError):
        return {}  # caught mid-write: read again next time


def follow(proc: subprocess.Popen, bench: Path, since: float) -> dict:
    """Print each task as it finishes, from the run's own results file (the same on every system)."""
    seen: set[str] = set()
    run_file = None
    run: dict = {}
    while True:
        finished = proc.poll() is not None
        run_file = run_file or newest_run(bench, since)
        run = read_run(run_file) or run
        tasks = run.get("tasks") or []
        for t in tasks:
            if t.get("status") in DONE and t.get("task_id") not in seen:
                seen.add(t["task_id"])
                detail = f"  ({t['detail']})" if t.get("detail") and t["status"] != "passed" else ""
                say(f"[{len(seen)}/{len(tasks)}] {t['status']:<7} {t['task_id']}{detail}")
        if finished:
            return read_run(run_file) or run
        time.sleep(2)


def app_bench_dir() -> Path:
    """Where the installed Local Quench app keeps its benchmark runs (the same rules as the app)."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "local-forge" / "bench"


def offer_to_app(folder: Path, yes: bool) -> None:
    """Copy the run into the app, where it can be compared and shared to the leaderboard."""
    target = app_bench_dir()
    if not folder.name or not target.parent.is_dir() or (target / folder.name).exists():
        return
    if yes or input("Copy this run into the Local Quench app (to compare it or share it there)? [Y/n] "
                    ).strip().lower() in ("", "y", "yes", "t", "tak"):
        target.mkdir(parents=True, exist_ok=True)
        shutil.copytree(folder, target / folder.name)
        say("Copied: open Local Quench > Benchmarks.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", default="", help="model server address, e.g. http://localhost:1234")
    ap.add_argument("--key-env", default="", metavar="VAR", help="environment variable that holds the API key")
    ap.add_argument("--model", default="", help="model id as the server lists it")
    ap.add_argument("--suite", default="", choices=[s[0] for s in SUITES], help="which benchmark")
    ap.add_argument("--size", default="", choices=[s[0] for s in SIZES], help="QuenchBench: how many tasks")
    ap.add_argument("--limit", type=int, default=0, help="only the first N tasks (0 = all)")
    ap.add_argument("--task-minutes", type=int, default=30, help="time limit per task (default 30)")
    ap.add_argument("--home", default=str(Path.home() / "QuenchBench"), help="folder for the app and the results")
    ap.add_argument("--update", action="store_true", help="download the newest Local Quench build first")
    ap.add_argument("--yes", action="store_true", help="do not ask before starting")
    args = ap.parse_args()

    home = Path(args.home).expanduser().resolve()
    exe = install_app(home, args.update)
    env = {**os.environ, "FORGE_HOME": str(home / "data")}  # the app's own settings stay as they are
    if exe.suffix == ".AppImage" and not (shutil.which("fusermount") or shutil.which("fusermount3")):
        env["APPIMAGE_EXTRACT_AND_RUN"] = "1"  # no FUSE (containers, some minimal installs): unpack and run
    config, bench = home / "data" / "config", home / "data" / "data" / "bench"

    pid, base, key, cloud = pick_server(args)
    model = pick_model(args, base, key)
    if args.suite:
        suite = next(s for s in SUITES if s[0] == args.suite)
    else:
        suite = SUITES[choose("Which benchmark?", [label for _, label, _ in SUITES])]
    if suite[2] and not (shutil.which("docker") or shutil.which("podman")):
        stop(f"{suite[0]} runs every task in a container: install Docker or Podman first, or pick QuenchBench.")
    size = args.size or "full"
    if suite[0] == "forge" and not args.size:
        size = SIZES[choose("How much of QuenchBench?", [f"{n}: {d}" for n, d in SIZES], default=1)][0]

    cmd = [str(exe), "bench", "--suite", suite[0], "--model", model, "--task-minutes", str(args.task_minutes)]
    if suite[0] == "forge":
        cmd += ["--size", size]
    if args.limit:
        cmd += ["--limit", str(args.limit)]
    say(f"\nModel {model} on {base}\nBenchmark {suite[0]}" + (f" ({size})" if suite[0] == "forge" else ""))
    if cloud:
        say("This is a cloud provider: the tasks' code is sent to it, and it may cost money.")
    if not args.yes and input("Start? [Y/n] ").strip().lower() not in ("", "y", "yes", "t", "tak"):
        return

    write_settings(config, pid, base, key, cloud, model)
    log = home / "last-run.log"
    home.mkdir(parents=True, exist_ok=True)
    since = time.time() - 1
    say("Running. Ctrl+C stops it.\n")
    try:
        with open(log, "w", encoding="utf-8") as out:
            proc = subprocess.Popen(cmd, env=env, stdout=out, stderr=subprocess.STDOUT)
            try:
                run = follow(proc, bench, since)
            except KeyboardInterrupt:
                proc.terminate()
                proc.wait(timeout=60)
                stop(f"Stopped. The results so far are in {bench}.")
    finally:
        if key:
            forget_key(config, pid)

    if not run:
        stop(f"The benchmark did not start. What the app said is in {log}:\n\n"
             + log.read_text("utf-8", errors="replace")[-2000:])
    rate = f" ({run['pass_rate']}%)" if run.get("pass_rate") is not None else ""
    say(f"\n{run.get('state', '?')}: passed {run.get('passed', 0)}/{run.get('done', 0)} of {run.get('total', 0)}"
        f"{rate}, {run.get('seconds', 0)} s, {run.get('tokens', 0):,} tokens")
    if run.get("weighted") is not None:
        say(f"Weighted score: {run['weighted']}%")
    if run.get("message"):
        say(run["message"])
    folder = bench / str(run.get("id", ""))
    say(f"Results, logs and diffs: {folder}")
    offer_to_app(folder, args.yes)
    if proc.returncode:
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
