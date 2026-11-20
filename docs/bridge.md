# Agent bridge: Claude Code, Codex and Claude Desktop use your local models

The agent bridge lets another agent on this computer hand a coding task to a local model in Local Quench, follow it,
and read the result. `LocalQuench mcp` is a small MCP server over stdio. The agent starts it, and it forwards each
tool call to the running app. Every chat rule still applies there: your mode limit, blocked paths, the sandbox (on Linux)
and approvals.

Tested on 2026-10-31 with Claude Code 2.1.316 (`claude mcp list` showed it connected, and two `claude -p` runs used
it, one with an approval), and with an automated end-to-end test that talks the protocol line by line. Claude Desktop
was tested in November 2026 as well. Codex has not been tried yet; its config below follows its documented format.

## 1. Turn it on in Local Quench
Open Settings, Agent bridge:
- Turn on **Allow other agents to start tasks**.
- Pick **Highest mode a task may run in**. The default, Auto (safe), runs edits and read-only commands. Every other
  command waits for you.

The same page shows the exact command for this computer. Local Quench must be running whenever the agent uses it.

## 2. Add it to the agent

### Claude Code
Add the server once, for all your projects (`--scope user`). Pick the line for how you run Local Quench:

```sh
# AppImage (Linux): the path of the AppImage file itself
claude mcp add --scope user local-quench -- ~/Applications/LocalQuench-x86_64.AppImage mcp

# Windows (PowerShell or cmd): the LocalQuench.exe in the unzipped folder (0.1.31 and newer: the folder LocalQuench;
# 0.1.30 and older: the folder local-forge)
claude mcp add --scope user local-quench -- "C:\Users\YOU\LocalQuench\LocalQuench.exe" mcp
```

The command on the Settings page, Agent bridge, is the one for your computer and is the one to use. If you added the
bridge with a path ending in `local-forge.exe`, add it again with `LocalQuench.exe` after updating to 0.1.31.

If you start Local Quench with `LQ_HOME` set, also add `-e LQ_HOME=...` with the same value. The
MCP server looks for the running app in that data folder. The Settings page adds this for you.

Check it:

```sh
claude mcp list                      # local-quench: ... - ✓ Connected
LocalQuench.AppImage mcp --check     # prints whether a task could start, and the names of the tools this server offers
```

`--check` prints nothing in a terminal on Windows, because the exe has no console. Use `claude mcp list` there.

Optional: the skill tells Claude when to delegate work and how to check it:

```sh
# or install the plugin below, which includes it
```

### Codex
Add this to `~/.codex/config.toml` (on Windows: `%USERPROFILE%\.codex\config.toml`):

```toml
[mcp_servers.local-quench]
command = "/home/YOU/Applications/LocalQuench-x86_64.AppImage"   # or "C:\\Users\\YOU\\...\\LocalQuench.exe"
args = ["mcp"]
startup_timeout_sec = 30
tool_timeout_sec = 120
```

Inside a TOML string, a Windows path needs each backslash doubled.

### Claude Desktop
Go to Settings, Developer, Edit config. Add this to `claude_desktop_config.json`, then restart Claude Desktop:

```json
{ "mcpServers": { "local-quench": { "command": "C:\\Users\\YOU\\LocalQuench\\LocalQuench.exe", "args": ["mcp"] } } }
```

### The Claude Code plugin (optional, recommended)
It adds a skill that tells Claude Code when to delegate, to wait with `until_done` (0.1.21 and later) instead of polling, and to check
every claim of the local model before repeating it. In Claude Code:

```
/plugin install local-quench --marketplace majmichu1/local-quench
```

The plugin does not add the MCP server itself (its path depends on where Local Quench is installed): add it with the
command above, from Settings, Agent bridge.

## 3. A first prompt
In Claude Code, inside a project:

> Use local-quench to have my local model add pytest tests for `add()` in calc.py. Follow it until it is done, then
> show me the diff and tell me whether the tests are right.

Claude calls `lq_models`, then `lq_run` with the folder, then `lq_wait` (or `lq_status` with `wait=55`) until the task is
done. It reads `lq_result` and `lq_diff`, then checks the work. The task also shows up in Local Quench's sidebar under "Agents", and you can
watch it there live.

## 4. Approvals
Approvals stay with you. The calling agent cannot answer them.
- In ask or safe mode, a command, a delete, or a file outside the project folder makes the task wait. The question
  appears in Local Quench, on the desktop or on your paired phone. Answer it there.
- Meanwhile the agent's `lq_wait`/`lq_status` reports `"state": "waiting_for_approval"` and `"waiting_for": "<the
  command>"`, with a note telling it to tell you. Claude Code then says, for example: "The task is waiting for your
  approval in Local Quench. It wants to run `python -m pytest -q`." It keeps calling `lq_wait`, which returns as
  soon as you answer.
- `lq_cancel` stops the task. An open question gets the answer no.

## 4a. Waiting, when the client shows fewer tools
If the agent lists fewer tools than the table below (for example no `lq_wait`), it started an older MCP server: the path in
`claude mcp add` points at an older Local Quench file, or the agent session began before an update. `LocalQuench mcp --check`
prints the tool names the server offers. Restart the agent session and check the path in `claude mcp list`. Waiting works
meanwhile with `lq_status` and `wait=55`, which takes the same `wait` and `until_done` as `lq_wait`.

## 4b. A task that runs long or loops
`lq_cancel` stops a running task at once, also one that repeats the same step again and again (tested: a model that
reads the same file 400 times is stopped within a second, no step follows). Its edits stay. While a task runs, the
status note says so when it has run over 10 minutes or 40 steps, and when the last steps in `recent_steps` repeat: "it
looks stuck in a loop; lq_cancel stops it".

## 4c. Verify: a check the task must pass
`lq_run` takes `verify`, a shell command (for example `python3 -m unittest`), and `verify_timeout` (seconds, default
300, at most 1800). When the task ends normally (state done), Local Quench runs the command in the task's folder (the
copy, with `workspace=copy`) through the same door as a command the model runs in a chat: the task's mode, the approval
(a mode that asks the person asks here too: the state is `waiting_for_approval` with the command), the sandbox (Linux), blocked
paths and the timeout. In plan mode the command does not run. The task stays `running` until it has run, so `lq_wait`
returns after it. `lq_status` and `lq_result` then have

```json
"verify": {"command": "python3 -m unittest", "passed": true, "exit_code": 0, "seconds": 2.1, "output_tail": "...", "ran": true}
```

`ran: false` (with `passed: false`, `exit_code: null`) means it did not run: plan mode, or the person said no; the output
tail says why. A cancelled or failed task does not run it. `lq_send` runs it again at the end of the follow-up.

## 4d. Workspace copy: the task does not touch your folder
`lq_run` with `workspace: "copy"` (default `"folder"`): the task works in a copy in Local Quench's data folder
(`bridge-copies/`), and your folder stays as it is.
- A git repository: a `git worktree` of HEAD (its hooks do not run) with your uncommitted changes copied over: modified
  and untracked files, deletions. Ignored files (`node_modules`, `.venv` ...) are not there.
- Any other folder: a plain copy without `node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `target` and
  `.git`, at most 2 GB.
- Files you blocked in Settings are left out of the copy, and the project's rules (blocked paths, folders you
  allowed) apply to the copy as to the original folder. A folder a task may not leave is the copy.
- `lq_result` shows `copy.path` and `folder`; `lq_diff` diffs against the copy's start (each file from before the task's
  first edit). Apply what you want to your folder yourself.
- `lq_cleanup(task_id)` removes the copy (and the worktree entry in the repository); the result and the diff stay
  readable. A copy also goes by itself 7 days after it was made (when any task starts). A copy of a running task stays.

## 4e. The numbers of a task, and the memory note
`lq_result` has `stats` (and `lq_status` the short part of it): `output_tok_s`, `prompt_tok_s` (from llama-server's own
timing; `prompt_tok_s_estimated: true` when it is fresh prompt tokens over the time to the first token), `prompt_tokens`,
`completion_tokens`, `context_used` and `context_size`, `time_to_first_token_s` (average, and `_max_`), `model_seconds`
(time in the model), `model_calls` and `placement`: for the app's own llama-server the layers on the GPU (`all 37 layers
on the GPU`, `20/37 ...`, and experts held on the CPU); for LM Studio the GPU offload it reports; otherwise `unknown`.

`lq_run` with a `model` other than the loaded one says so in `note` (and `memory_note`) when the app can tell what it
costs: with the app's own llama-server (one model at a time) the loaded one is unloaded first; with LM Studio when the
model will not fit in the GPU memory left ("This model will not fit next to the loaded one; the loaded model will be
unloaded first (about 15 s to swap)"). When the card cannot be read or the size is unknown, nothing is said.

## 5. Security: what the bridge guarantees and what it does not
Checked 2026-11-06 with automated tests; the fixes below are in 0.1.21.
- **The mode limit holds.** The agent asks for a mode per task; anything above **Highest mode** is lowered to it, an
  unknown mode becomes ask, and the response says `capped`. `lq_send` continues in the task's mode under the limit
  as it is now (also after a restart; in 0.1.2 a restart lost it) and cannot raise it.
- **The bridge's token opens the bridge only.** `bridge.json` (in the app's data folder, readable by your user only) holds
  a token derived from the app's own one, accepted on the bridge's own address and nowhere else (since 0.1.21; in 0.1.2 it was the
  app's token). With it nothing can answer an approval, change settings (the mode limit included) or read your other
  chats. A paired phone or tablet cannot use the bridge at all.
- **Closing the app ends it.** The token is new each time Local Quench starts, and `bridge.json` is removed when it
  stops. A file left behind by a crash holds a token nothing accepts.
- **Known secrets are cut from what goes back.** The result, the commands, the diff and the transcript pass through
  the same filter as data sharing (keys and tokens of known formats, passwords in URLs and command lines). The files
  in your project are not changed by it. A secret in an unknown format is not recognised, so keep secrets out of
  projects you delegate, or block their paths.
- **A task is a chat in that folder.** Blocked paths, the sandbox (Linux) and what you allowed for that project (a folder
  outside it, for example) apply to bridge tasks as to your own chats. Nothing wider: the task gets no permission
  your own chat in that folder would not have.
- **What it cannot promise.** The calling agent runs as you on this computer. If it can run commands itself (Claude
  Code's Bash tool, for example), it could read files or edit them without the bridge; the bridge does not add or
  remove that. The approvals and the mode limit protect what runs through Local Quench, not what the agent does on
  its own.

## Which backend a task runs on
`lq_models` lists every local backend that is set up or running: the built-in engine (its model folders, the loaded one
marked), LM Studio, and the local server the app is on. A backend that does not answer is reported `offline` in `backends`;
the others still list. `current` is the selection the way the top bar of Local Quench shows it.
`lq_run` takes `provider` (`engine`, `lmstudio` ...). With only `model`, the backend that has it is used; a model that is on
several backends with none loaded or selected gets an answer that lists the choices (call again with `provider`). With
neither, the current selection is used. A task on the built-in engine loads its model in its first turn, like a chat.

## Tools
| Tool | Arguments | Returns |
| --- | --- | --- |
| `lq_models` | none | models of every local backend (each with `provider`: `engine` for the built-in llama.cpp, `lmstudio` ...; loaded, `selected`, quantization, context, vision, tool calling, harness tier, scores, notes), `backends` (each `running` / `stopped` / `loading` / `online` / `offline`, with the error), `current` (the backend and model the person has selected in the app now), the highest mode, and a `note` when no model server or model is ready |
| `lq_run` | `task`, `folder` (absolute path) required; `mode` (plan, ask, safe, dangerous; default ask), `model`, `title`, `verify` (a shell command run when the task ends), `verify_timeout` (default 300, at most 1800), `workspace` (`folder` default, or `copy`), `provider` (`engine`, `lmstudio` ...) | `task_id` at once, the mode it got (`capped` when your limit lowered it), the folder, the model, the `provider` it runs on, `copy` (workspace=copy), `memory_note` when the model will not fit next to the loaded one |
| `lq_wait` | `task_id`; `seconds` 1-55 (default 45); `until_done` (Local Quench 0.1.21 and later; Claude Code: wait to the end, up to 4 h; Claude Code moves the call to the background after 2 minutes and tells the model when it returns) | the status (below) once the task is done, failed, cancelled or newly waiting for approval, or when the time is up. Sends `notifications/progress` when the client asked for them |
| `lq_status` | `task_id`; `wait` (seconds, at most 55) and `until_done`: wait like `lq_wait` | state (running, waiting_for_approval, done, failed, cancelled), `waiting_for`, steps, files changed, elapsed seconds, the latest message, `recent_steps` (the last few tool calls), `stats` (speed, tokens, context), `verify`, `error` when failed, a `note` saying what to do next |
| `lq_result` | `task_id` | the final answer (cut at 6000 characters, with a note), files with lines added and removed, commands with how each ended, `verify`, `copy` (workspace=copy), `stats` |
| `lq_diff` | `task_id`; `path` | a unified diff of each file, from before the task to now (cut at 24000 characters; pass `path` for one file) |
| `lq_send` | `task_id`, `message` | a follow-up in the same task (once it has stopped); follow it with `lq_wait`; runs `verify` again at its end |
| `lq_cancel` | `task_id` | stops the task (also one that loops); edits made so far stay |
| `lq_transcript` | `task_id` | the task's conversation as Markdown (the latest 24000 characters) |
| `lq_list` | `state` (running, waiting_for_approval, done, failed, cancelled), `limit` (default 20, at most 100) | the tasks started through the bridge, newest first: `task_id`, title, folder, model, state, started, steps; to find a task id after the conversation restarted |
| `lq_cleanup` | `task_id` | removes the copy a task worked in (`workspace=copy`); not while it runs |

Each tool result is cut at 24000 characters, with a note saying what was left out.

## When something is wrong
| The agent says | Meaning |
| --- | --- |
| "Local Quench is not running on this computer" | The app is closed. Start it. |
| "The agent bridge is off" | Turn it on in Settings, Agent bridge. |
| "cannot reach a model server" | LM Studio, llama-server or Ollama is not running, or Settings, Model server points elsewhere. |
| "No model is selected" | Pick a model in Local Quench, or have the agent pass `model` from `lq_models`. |
| "... is available on more than one backend" | The same model id is on the built-in engine and on LM Studio, and neither is loaded or selected: call `lq_run` again with `provider` set to one of the ids it names. |
| `"state": "failed"` with `error` | The model server failed mid-task (out of memory, unloaded). `lq_send` retries. |
| `claude mcp list` shows "Failed to connect" | The path in the command is wrong. Run the same command plus `--check` in a terminal. |
| The agent lists no `lq_wait`, `lq_diff`, `lq_cancel` or `lq_list` | It runs an MCP server of an older Local Quench (`--check` lists what the server offers). Restart the agent session, and check the path in `claude mcp list`. Waiting works meanwhile with `lq_status` and `wait=55` where the server has it; the status says `client_note` otherwise. |
| `lq_models` shows `quant` null | The quantization comes from the server, else the GGUF file's header, else the name. A model that none of them names stays null. |

## Protocol details
- MCP stdio uses one JSON-RPC message per line. Stdout carries protocol messages only. The server sends
  its own stdout to stderr so that a stray print cannot break the framing. Logs go to stderr.
- Protocol versions: 2025-11-25, 2025-06-18, 2025-03-26 and 2024-11-05. A client asking for another version gets
  the newest. The server declares only `tools`.
- Tool calls run in worker threads, so `ping` and other calls get answers while an `lq_wait` runs.
  `notifications/cancelled` ends a wait, and the cancelled request gets no answer.
- Errors: an unknown tool is JSON-RPC error -32602, an unknown method -32601, bad JSON -32700. Any other failure
  (bad arguments, the app closed, a bug) comes back as a tool result with `isError: true`. The server never exits on
  a bad message.
- Windows: the packaged exe is windowed, so the server opens the process's standard handles itself. Folders are accepted as `C:\...`, `C:/...`, `file:///C:/...`, `/c/...` (Git Bash) and
  `/mnt/c/...` (WSL).
