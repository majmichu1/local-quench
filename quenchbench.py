#!/usr/bin/env python3
"""Run QuenchBench (or SWE-bench, Terminal-Bench, Aider Polyglot) on your own model, from the command line.

    python3 quenchbench.py                  # asks: model server, model, benchmark, size
    python3 quenchbench.py --server http://localhost:1234 --model qwen3.8-27b --suite quenchbench --size quick --yes

What it does:
  1. asks which model server to use and lists the models it serves,
  2. asks which benchmark to run and how much of it,
  3. downloads the latest Local Quench build for this computer from the GitHub releases (once, checked
     against the release's SHA-256; the benchmark runs inside it, without opening a window),
  4. runs it and prints each task as it finishes, then the score.

This script is only the launcher: the agent, the benchmark runner and the QuenchBench tasks are inside
the app, the same as when you start a benchmark from its window.

Needs Python 3.9+ and nothing else. Everything (the app, settings, results) stays in one folder,
~/QuenchBench by default (--home to change it); your own Local Quench settings are not touched.
Results are not uploaded anywhere. To put a result on the public leaderboard, let the script copy the
run into the Local Quench app at the end, then share it from the app (Benchmarks).

Windows 10/11 and 64-bit Linux. No macOS build yet.
"""

from __future__ import annotations

import argparse
import hashlib
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
MANIFESTS = (f"https://github.com/{REPO}/releases/latest/download/latest.json",
             "https://localquench.com/releases/latest.json")
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

SUITES = [  # id, label, needs Docker or Podman, free disk space it needs (GB)
    ("quenchbench", "QuenchBench: which kinds of coding work the model handles (sections x languages)", False, 2),
    ("aider-polyglot", "Aider Polyglot: 225 Exercism exercises in 6 languages (beta)", True, 5),
    ("swe-verified", "SWE-bench Verified: 500 real GitHub issues in Python", True, 60),
    ("swe-multilingual", "SWE-bench Multilingual: 300 issues in 9 languages (beta)", True, 60),
    ("terminal-bench-2", "Terminal-Bench 2.0: 89 tasks in a terminal (beta)", True, 40),
]

SIZES = [  # QuenchBench only; the same names and numbers as the app and localquench.com/bench.html
    ("smoke", "ultra quick: one task per kind of work (13), about one to two hours on a laptop GPU"),
    ("quick", "quick: one task per kind of work and language (63)"),
    ("full", "full: every task (537), for comparing models closely"),
]

DONE = ("passed", "failed", "error", "skipped")
APP_SUITE = {"quenchbench": "forge"}  # the id the app has used since before the name QuenchBench (every version knows it)
YES = ("", "y", "yes", "t", "tak")
LONG_LIST = 40  # more models than this (cloud providers): type the id instead of picking a number


def say(text: str = "") -> None:
    print(text, flush=True)


def stop(text: str, code: int = 1) -> None:
    print(f"\n{text}", file=sys.stderr, flush=True)
    sys.exit(code)


def ask(prompt: str, default: str = "", unattended: str | None = None) -> str:
    """One answer: the default on Enter; when nobody can answer (piped, scheduled), `unattended` if given."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        say()
        return default if unattended is None else unattended


def choose(title: str, options: list[str], default: int = 0) -> int:
    say(f"\n{title}")
    for i, label in enumerate(options, 1):
        say(f"  {i}) {label}")
    while True:
        answer = ask(f"Choose 1-{len(options)} [{default + 1}]: ")
        if not answer:
            return default
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1


def version_tuple(version: str) -> tuple[int, int, int]:
    """(major, minor, patch) of "0.1.1", "v0.1.1" or "0.1.1-beta"; (0, 0, 0) when unknown."""
    import re

    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", version or "")
    return (int(m[1]), int(m[2]), int(m[3])) if m else (0, 0, 0)


def get_json(url: str, headers: dict[str, str] | None = None, timeout: float = 15) -> object:
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


# --- the app ------------------------------------------------------------------------------------------

def platform_key() -> str:
    """The build for this computer, as the release manifest names it."""
    if sys.platform == "win32":
        return "windows"
    if sys.platform.startswith("linux") and platform.machine() in ("x86_64", "AMD64"):
        return "linux-appimage"
    stop("Local Quench has builds for Windows (64-bit) and Linux (x86_64) only, so the benchmark cannot run "
         "on this computer yet.")
    return ""


def app_path(home: Path) -> Path:
    if sys.platform == "win32":
        # the zip holds one folder (local-forge/ so far) with LocalQuench.exe (0.1.1+) or local-forge.exe
        for name in ("LocalQuench.exe", "local-forge.exe"):
            found = sorted((home / "app").glob(f"*/{name}"))
            if found:
                return found[0]
        return home / "app" / "local-forge" / "LocalQuench.exe"
    # the AppImage unpacked once: runs without FUSE (libfuse2 is missing on Ubuntu 22.04+ and in containers)
    return home / "app" / "squashfs-root" / "AppRun"


def download(url: str, target: Path, size: int, sha256: str) -> None:
    tmp = target.with_name(target.name + ".part")
    req = urllib.request.Request(url, headers=UA)
    digest = hashlib.sha256()
    got = 0
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as out:
        total = size or int(resp.headers.get("Content-Length") or 0)
        while chunk := resp.read(1 << 20):
            out.write(chunk)
            digest.update(chunk)
            got += len(chunk)
            if total and sys.stdout.isatty():  # a log file gets the line below, not a counter per megabyte
                print(f"\r  {got >> 20} / {total >> 20} MB", end="", flush=True)
    say("\r" if sys.stdout.isatty() else f"  {got >> 20} MB downloaded")
    if total and got != total:
        tmp.unlink(missing_ok=True)
        stop(f"The download stopped after {got >> 20} of {total >> 20} MB. Run the script again.")
    if not sha256:
        tmp.unlink(missing_ok=True)
        stop("The release lists no SHA-256 checksum for this build, so the download cannot be checked. "
             "Please open an issue.")
    if digest.hexdigest() != sha256.lower():
        tmp.unlink(missing_ok=True)
        stop("The download does not match the release's SHA-256 checksum, so it was deleted. Run the script "
             "again; if it happens twice, please open an issue.")
    tmp.replace(target)


def manifest() -> dict:
    errors = []
    for url in MANIFESTS:
        try:
            data = get_json(url)
            if isinstance(data, dict) and data.get("platforms"):
                return data
            errors.append(f"{url}: no builds listed")
        except (urllib.error.URLError, OSError, ValueError) as exc:
            errors.append(f"{url}: {exc}")
    stop("Could not find the latest Local Quench release:\n  " + "\n  ".join(errors))
    return {}


def install_app(home: Path, update: bool) -> tuple[Path, str]:
    """The newest release, downloaded once into home/app; again only with --update. (path, version)"""
    exe = app_path(home)
    version_file = home / "app" / "version.txt"
    have = version_file.read_text().strip() if version_file.exists() else ""
    if exe.exists() and not update:
        return exe, have
    try:
        info = manifest()
    except SystemExit:
        if exe.exists():
            say("Could not check for a newer build; using the one already here.")
            return exe, have
        raise
    version = str(info.get("version") or "")
    if exe.exists() and have == version:
        return exe, have
    build = (info.get("platforms") or {}).get(platform_key())
    if not build or not build.get("url"):
        stop(f"Local Quench {version} has no build for this computer.")
    say(f"Downloading Local Quench {version} ({int(build.get('size') or 0) >> 20} MB), once...")
    app = home / "app"
    app.mkdir(parents=True, exist_ok=True)
    name = build["url"].rsplit("/", 1)[-1]
    if name.endswith(".zip"):
        archive = app / name
        download(build["url"], archive, int(build.get("size") or 0), str(build.get("sha256") or ""))
        for old in app.iterdir():  # the previous build's folder, whatever its name
            if old.is_dir():
                shutil.rmtree(old, ignore_errors=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(app)
        archive.unlink()
    else:
        image = app / "LocalQuench.AppImage"
        download(build["url"], image, int(build.get("size") or 0), str(build.get("sha256") or ""))
        image.chmod(image.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        shutil.rmtree(app / "squashfs-root", ignore_errors=True)
        say("Unpacking...")
        done = subprocess.run([str(image), "--appimage-extract"], cwd=app, stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE, text=True)
        if done.returncode != 0:
            stop(f"Could not unpack the AppImage: {done.stderr.strip()[-500:]}")
        image.unlink()
    exe = app_path(home)
    if not exe.exists():
        stop(f"The download did not contain {exe.name}. Please open an issue.")
    version_file.write_text(version)
    return exe, version


# --- model server and model ---------------------------------------------------------------------------

def server_base(url: str) -> str:
    """The server's address without /v1 (the app adds it), so ".../v1" works as well as "..."."""
    url = url.strip().rstrip("/")
    return url[:-3] if url.endswith("/v1") else url


def list_models(base: str, key: str) -> list[str]:
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    data = get_json(base + "/v1/models", headers)
    ids = [m.get("id", "") for m in (data.get("data") or [])] if isinstance(data, dict) else []
    return sorted(i for i in ids if i and "embed" not in i.lower())


def pick_server(args: argparse.Namespace) -> tuple[str, str, str, bool]:
    """(provider id, address, API key, cloud)."""
    if args.server:
        base = server_base(args.server)
        known = next((s for s in SERVERS if s[2] == base), None)
        pid, cloud, env = (known[0], known[3], known[4]) if known else ("custom", False, "")
        key = os.environ.get(args.key_env or env, "") if (args.key_env or env) else ""
        if cloud and not key:
            stop(f"{known[1]} needs an API key: set {args.key_env or env}.")
        return pid, base, key, cloud
    i = choose("Which model server?", [f"{label}  ({url})" for _, label, url, _, _ in SERVERS] + ["Another address"])
    if i == len(SERVERS):
        url = server_base(ask("Address of an OpenAI-compatible server, e.g. http://192.168.1.20:1234: "))
        if not url:
            stop("No address given.")
        return "custom", url, os.environ.get(args.key_env, "") if args.key_env else "", False
    pid, label, url, cloud, env = SERVERS[i]
    key = os.environ.get(env, "")
    if cloud and not key:
        import getpass

        try:
            key = getpass.getpass(f"{label} API key (or set {env} next time; it is not saved): ").strip()
        except EOFError:
            key = ""
        if not key:
            stop(f"{label} needs an API key: set {env}.")
    return pid, url, key, cloud


def pick_model(args: argparse.Namespace, base: str, key: str) -> str:
    try:
        models = list_models(base, key)
    except urllib.error.HTTPError as exc:
        stop(f"The server at {base} answered {exc.code} for its model list"
             + (" (wrong or missing API key?)" if exc.code in (401, 403) else "")
             + ". Is the address right? Use the address without /v1, e.g. http://localhost:1234.")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        stop(f"Cannot reach the model server at {base} ({exc}). Start it (in LM Studio: Developer > Start "
             "server), or pass --server with its address.")
    if args.model:
        if models and args.model not in models:
            say(f"Note: {args.model} is not in the server's list; trying it anyway.")
        return args.model
    if not models:
        stop("The server lists no models. Load one (or download one) and start again.")
    if len(models) > LONG_LIST:
        while True:
            typed = ask(f"\nThe server offers {len(models)} models. Type the model id (or part of it): ")
            if not typed:
                stop("No model chosen. Pass --model ID.")
            hits = [m for m in models if typed.lower() in m.lower()]
            if typed in models:
                return typed
            if len(hits) == 1:
                return hits[0]
            if 1 < len(hits) <= LONG_LIST:
                return hits[choose("Which one?", hits)]
            say(f"{len(hits)} models match; be more specific." if hits else "No model matches.")
    return models[choose("Which model?", models)]


def container_ready() -> bool:
    """Docker or Podman installed, its daemon running, and usable by this user."""
    for tool in ("docker", "podman"):
        if shutil.which(tool):
            try:
                if subprocess.run([tool, "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  timeout=30).returncode == 0:
                    return True
            except (OSError, subprocess.TimeoutExpired):
                pass
    return False


# --- the run -----------------------------------------------------------------------------------------

def write_json_private(path: Path, data: dict) -> None:
    """Written whole (never half a file) and readable only by this user: it holds the API key during a run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    os.replace(tmp, path)


def read_settings(path: Path) -> dict:
    try:
        data = json.loads(path.read_text("utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}  # missing or damaged: start from the app's defaults


def write_settings(config: Path, pid: str, base: str, key: str, cloud: bool, model: str) -> None:
    path = config / "settings.json"
    data = read_settings(path)
    providers = [p for p in data.get("providers") or [] if isinstance(p, dict) and p.get("id") != pid]
    providers.append({"id": pid, "label": dict((s[0], s[1]) for s in SERVERS).get(pid, "Custom server"),
                      "base_url": base, "kind": "cloud" if cloud else "local", "api_key": key})
    data.update(base_url=base, active_provider=pid, providers=providers, active_model=model)
    write_json_private(path, data)


def forget_key(config: Path, pid: str) -> None:
    path = config / "settings.json"
    data = read_settings(path)
    for p in data.get("providers") or []:
        if isinstance(p, dict) and p.get("id") == pid:
            p["api_key"] = ""
    try:
        write_json_private(path, data)
    except OSError:
        pass


def newest_run(bench: Path, since: float) -> Path | None:
    found = []
    for f in bench.glob("*/run.json"):
        try:
            mtime = f.stat().st_mtime
        except OSError:  # removed between the listing and the stat
            continue
        if mtime >= since:
            found.append((mtime, f))
    return max(found)[1] if found else None


def read_run(path: Path | None) -> dict:
    try:
        data = json.loads(path.read_text("utf-8")) if path else {}
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}  # caught mid-write: read again next time


def follow(proc: subprocess.Popen, bench: Path, since: float) -> dict:
    """Print each task as it finishes, from the run's own results file (the same on every system)."""
    seen: set[str] = set()
    run_file = None
    run: dict = {}
    message = ""
    while True:
        finished = proc.poll() is not None
        run_file = run_file or newest_run(bench, since)
        run = read_run(run_file) or run
        if run.get("message") and run["message"] != message and not finished:
            message = run["message"]  # what the app is doing before the tasks: downloads, container builds
            say(message)
        tasks = run.get("tasks") or []
        for t in tasks:
            if t.get("status") in DONE and t.get("task_id") not in seen:
                seen.add(t["task_id"])
                first = next((x.strip() for x in str(t.get("detail") or "").splitlines() if x.strip()), "")
                detail = f"  ({first[:100]})" if first and t["status"] != "passed" else ""  # the full log is in the run folder
                say(f"[{len(seen)}/{len(tasks)}] {t['status']:<7} {t['task_id']}{detail}")
        if finished:
            return read_run(run_file) or run
        time.sleep(2)


def end(proc: subprocess.Popen) -> None:
    """Stop the app and what it started: first as Ctrl+C would (it then ends its tasks itself), then by force."""
    if proc.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        import signal

        proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=90)
    except subprocess.TimeoutExpired:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        proc.kill()
        proc.wait()


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
    if not target.parent.is_dir():
        say(f"To share it on the leaderboard: install Local Quench, open it once, and copy the folder above "
            f"into {target}.")
        return
    if (target / folder.name).exists():
        say("This run is already in the Local Quench app.")
        return
    if yes or ask("Copy this run into the Local Quench app (to compare it or share it there)? [Y/n] ",
                  unattended="n").lower() in YES:
        target.mkdir(parents=True, exist_ok=True)
        shutil.copytree(folder, target / folder.name)
        say("Copied: open Local Quench > Benchmarks.")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):  # a Windows console (cp1252) must not stop on a task's text
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", default="", help="model server address, e.g. http://localhost:1234")
    ap.add_argument("--key-env", default="", metavar="VAR", help="environment variable that holds the API key")
    ap.add_argument("--model", default="", help="model id as the server lists it")
    ap.add_argument("--suite", default="", choices=[s[0] for s in SUITES] + ["forge"],
                    help="which benchmark (forge: the old name of quenchbench)")
    ap.add_argument("--size", default="", choices=[s[0] for s in SIZES], help="QuenchBench: how many tasks")
    ap.add_argument("--limit", type=int, default=0,
                    help="only the first N tasks: to check that everything works, not for a score (0 = all)")
    ap.add_argument("--task-minutes", type=int, default=30, help="time limit per task (default 30)")
    ap.add_argument("--repeats", type=int, default=1, choices=range(1, 6), metavar="N",
                    help="run every task N times, 1-5: local models are random, repeats give steadier numbers "
                         "(Local Quench 0.1.1 or newer)")
    ap.add_argument("--harness", action="append", default=[], metavar="KEY=VALUE",
                    help="one harness switch for this run, e.g. continue_nudge=false (repeatable; docs/FEATURES.md; "
                         "Local Quench 0.1.1 or newer)")
    ap.add_argument("--remove-images", action="store_true",
                    help="SWE-bench and Terminal-Bench: delete each task's container image after it (saves tens of GB)")
    ap.add_argument("--home", default=str(Path.home() / "QuenchBench"), help="folder for the app and the results")
    ap.add_argument("--update", action="store_true", help="download the newest Local Quench build first")
    ap.add_argument("--yes", action="store_true", help="do not ask before starting")
    args = ap.parse_args()

    platform_key()  # before any question: no build for this computer, nothing to ask
    home = Path(args.home).expanduser().resolve()
    config, bench = home / "data" / "config", home / "data" / "data" / "bench"

    pid, base, key, cloud = pick_server(args)
    model = pick_model(args, base, key)
    if args.suite:
        suite = next(s for s in SUITES if s[0] == {"forge": "quenchbench"}.get(args.suite, args.suite))
    else:
        suite = SUITES[choose("Which benchmark?", [s[1] for s in SUITES])]
    if suite[2] and not container_ready():
        stop(f"{suite[0]} runs every task in a container: install Docker or Podman and start it (`docker info` "
             "must work for your user), or pick QuenchBench.")
    home.mkdir(parents=True, exist_ok=True)
    free_gb = shutil.disk_usage(home).free / 1e9
    if free_gb < suite[3]:
        say(f"Warning: {free_gb:.0f} GB free; {suite[0]} needs about {suite[3]} GB (container images and task files).")
    size = args.size or "full"
    if suite[0] == "quenchbench" and not args.size:
        size = SIZES[choose("How much of QuenchBench?", [d for _, d in SIZES], default=1)][0]

    say(f"\nModel {model} on {base}\nBenchmark {suite[0]}" + (f" ({size})" if suite[0] == "quenchbench" else ""))
    if cloud:
        say("This is a cloud provider: the tasks' code is sent to it, and it may cost money.")
    if not args.yes and ask("Start? [Y/n] ", unattended="n").lower() not in YES:
        # nobody to confirm (piped, scheduled) means no: a run can take hours, and cost money on a cloud model
        if not sys.stdin.isatty():
            stop("Not started: nobody can confirm here. Add --yes to start without asking.")
        return

    exe, version = install_app(home, args.update)
    cmd = [str(exe), "bench", "--suite", APP_SUITE.get(suite[0], suite[0]), "--model", model,
           "--task-minutes", str(args.task_minutes)]
    if suite[0] == "quenchbench":
        cmd += ["--size", size]
    if args.limit:
        cmd += ["--limit", str(args.limit)]
    if args.remove_images and suite[2]:
        cmd += ["--remove-images"]
    if args.harness:
        if version and version_tuple(version) < (0, 1, 1):
            stop(f"--harness needs Local Quench 0.1.1 or newer; this one is {version}. Add --update.")
        for pair in args.harness:
            cmd += ["--harness", pair]
    if args.repeats > 1:
        if version and version_tuple(version) < (0, 1, 1):
            stop(f"--repeats needs Local Quench 0.1.1 or newer; this one is {version}. Add --update.")
        cmd += ["--repeats", str(args.repeats)]
    # the app's own settings stay as they are (LQ_HOME from 0.1.1, FORGE_HOME before)
    env = {**os.environ, "LQ_HOME": str(home / "data"), "FORGE_HOME": str(home / "data")}
    write_settings(config, pid, base, key, cloud, model)
    log = home / "last-run.log"
    since = time.time() - 1
    say(f"Running in Local Quench {version or '(version unknown)'}. Ctrl+C stops it.\n")
    proc = None
    try:
        with open(log, "w", encoding="utf-8") as out:
            proc = subprocess.Popen(cmd, env=env, stdout=out, stderr=subprocess.STDOUT)
            run = follow(proc, bench, since)
    except KeyboardInterrupt:
        say("\nStopping...")
        if proc:
            end(proc)
        stop(f"Stopped. The results so far are in {bench}.", 130)
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
    if run.get("id"):
        folder = bench / str(run["id"])
        say(f"Results, logs and diffs: {folder}")
        offer_to_app(folder, args.yes)
    if proc.returncode or run.get("state") != "done":
        sys.exit(proc.returncode or 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop("Stopped.", 130)
