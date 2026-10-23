# What Local Quench does

Everything here exists in Local Quench 0.1.1 and can be seen in the app: a tool the model calls, a setting,
or a note the harness adds to the conversation. Three parts:

1. [Tools](#tools): what the model can call.
2. [Harness behaviours](#harness-behaviours): what the harness does on its own to keep a model on track.
3. [Ablation switches](#ablation-switches): how to turn behaviours off and measure them with QuenchBench.

## Tools

22 tools, plus `rename_symbol` when a language server for the project is installed.

| Tool | What it does |
| --- | --- |
| `read_file` | Reads a file with line numbers, at most 400 lines per call |
| `inspect_file_outline` | The skeleton of a file: classes, functions and their line ranges, far cheaper than reading it |
| `list_dir` | A directory tree, skipping the usual dependency and build folders |
| `find_files` | Files by glob pattern |
| `search_code` | Regex search across the project (ripgrep) with context lines |
| `repo_map` | A ranked map of the project's files and main symbols, optionally focused on a topic |
| `find_symbol` | Where a class, function or type is defined: file, line range, signature |
| `find_references` | Where a name is used |
| `edit_file` | Edits by exact search and replace, or by line range with anchor lines |
| `create_file` | Creates or overwrites a file |
| `delete_file` | Deletes a file (undoable) |
| `run_command` | A shell command in the project folder, optionally in the background; long output is trimmed but keeps errors |
| `check_process` | Status and new output of a background command; can stop it |
| `wait_until` | Waits for an outside condition (a lock, another build, a server) by re-running a check |
| `run_tests` | Runs the project's tests (pytest, unittest, npm, cargo, go, Gradle, Maven) and returns the summary and the failures |
| `git` | status, diff, log, blame and commit without the shell |
| `browser` | A headless Chromium to check web interfaces the agent builds |
| `web_search` | Web search (DuckDuckGo) |
| `fetch_webpage` | A web page as Markdown |
| `task` | Read-only research by sub-agents, up to 8 in parallel within what the model server allows |
| `todo_write` | The visible task list |
| `mcp` | A connected MCP server |
| `load_skill` | The instructions of a skill |
| `rename_symbol` | A rename across the project through the language server (only when one is installed) |

**Sub-agents** get the read-only tools only (`read_file`, `list_dir`, `inspect_file_outline`, `search_code`,
`find_files`, `repo_map`, `find_symbol`, `find_references`, `git`, `web_search`, `fetch_webpage`) and
`run_command` limited to read-only commands (`ls`, `grep`, `cat`, `git log`...).

**The core tool set** (`tool_set=core`) is 10 tools: `read_file`, `edit_file`, `create_file`, `delete_file`,
`list_dir`, `search_code`, `find_files`, `run_command`, `run_tests`, `todo_write`.

**In QuenchBench runs** the model gets 21 tools (or the core 10): everything above except `web_search`
and `fetch_webpage` (a task's answer must not be searchable) and `rename_symbol` (no language server
unless the `lsp` switch says so). `mcp` and `load_skill` stay in the list, but no MCP server or skill is
connected in a run, so every computer runs the same harness.

**Edits** can also be written in the reply instead of tool calls, in the format that suits the model:
SEARCH/REPLACE and line-range blocks, `apply_patch` (V4A, as GPT and gpt-oss are trained on), or whole
files. Each format still accepts the others.

## Harness behaviours

What the harness does without being asked. "Switch" names the setting that turns it off (see
[Ablation switches](#ablation-switches)); "always" means it has none yet.

### Keeping the model working

| Behaviour | What it does | When | Switch |
| --- | --- | --- | --- |
| Continue nudge | Asks the model to go on | A reply announces a next step ("Let me now run the tests.") but makes no call; at most twice per turn | `continue_nudge` |
| Thinking cap | Stops long reasoning and asks the model to act | Reasoning passes the cap with no answer or call; lifted after twice | `thinking_cap` |
| Runaway text | Cuts a reply that repeats itself; ends the turn the third time | A repeated block or line in the generated text | always |
| Take stock | Asks for a short recap and a change of course | Every 20 steps of one turn | `take_stock` |
| Engine retry | Retries an LM Studio engine error after 2 and 5 seconds, then explains the likely cause | The engine fails before anything streamed | always |

### Catching loops

| Behaviour | What it does | When | Switch |
| --- | --- | --- | --- |
| Repeated call | Tells the model the same call keeps giving the same result | The same call with the same result 3 times, or twice in a row | `loop_warnings` |
| Back and forth | Tells the model it is cycling between two actions | The last six calls are A, B, A, B, A, B with the same results | `loop_warnings` |
| Polling | Points to `wait_until` or a background job | The same command shape 3 times, or `sleep` of a minute or more twice | `loop_warnings` |
| Same output | Points out that different commands all print the same thing | 4 or 8 commands with the same output | `loop_warnings` |
| Troubleshooting | Asks for the likely causes, ranked | The same check fails 3 times in a row | `troubleshoot_note` |
| Own checks | Reminds the model to work on the project, not on its own test scripts | 10 and 20 calls without a change to a project file | `own_check` |

### Fixing the model's calls

| Behaviour | What it does | When | Switch |
| --- | --- | --- | --- |
| Calls written as text | Turns `<tool_call>` (Hermes) and Qwen's XML calls in the reply into real calls | The reply has no native tool calls | always |
| Broken JSON | Removes trailing commas from tool arguments | The arguments are not valid JSON | always |
| Tool name aliases | `bash`, `shell`, `cat`, `ls`, `glob` and similar run the matching tool | A tool name from another agent | always |
| Argument aliases | `command` for `cmd`, `file_path` for `path`, `pattern` for `glob` and similar | Known other names | always |
| Signature help | Lists the required and optional arguments | A call that still does not fit | always |
| Paths | Expands `$TMPDIR`, `$HOME` and `/tmp`; a missing path that matches one file reads it, else suggests paths | File tools | always |
| Shell repair | Adds a missing quote or bracket and runs the fixed command | `bash -n` reports a syntax error | always |
| Background `&` | Runs a command that ends with `&` as a background job | Command ends with `&` | always |
| Sleep guard | Refuses a leading `sleep` longer than the command time limit | `sleep N` with N at or over the limit | always |
| Pipe exit codes | Reports when an earlier command in a pipe failed (`make \| tail`) | Simple pipelines | always |

### Edits

| Behaviour | What it does | When | Switch |
| --- | --- | --- | --- |
| Edit format | Picks the edit format the model is trained on | Every request | `edit_format` |
| Edit matching | Exact, then ignoring trailing spaces, then re-indented, then fuzzy (similarity 0.88 or more); line edits re-find their anchor lines nearby | Every edit | always |
| Syntax rollback | Rejects an edit that introduces a syntax error | Every write | always |
| Diagnostics | Reports new problems from a language server or ruff, node, gofmt (pyright with `full`) | After each edit | `edit_diagnostics`, `lsp` |
| Self-review | Shows the model its own diff once, and new files left behind | Finishing after a change of 8 lines or more | `self_review` |
| Verify command | Runs the project's check (set per project) and sends back a failure, at most twice | Finishing after editing files | per project (off in benchmarks) |

### Results the model reads

| Behaviour | What it does | When | Switch |
| --- | --- | --- | --- |
| Output trimming | Keeps the head, the tail and the error regions; test output is summarised | Long output | always |
| Error hints | `[hint]` lines: where a name is defined, the closest existing names or files | A failed command or diagnostics | `error_hints` |
| Stale test results | Flags old JUnit reports, Gradle UP-TO-DATE and quiet runs that hide what ran | Test output | always |
| Repeated reads | Points to the earlier read instead of returning the same content again | The same range of an unchanged file | always |
| Learned commands | Remembers build and test commands that worked and lists them in the prompt | After `run_command` | always |

### Context

| Behaviour | What it does | When | Switch |
| --- | --- | --- | --- |
| Repo map | A map of the project in the prompt; later turns get only the changed files | Every turn | `repo_map_tokens` |
| Observation masking | Replaces old tool outputs with a stub (the newest 8 stay) | Near the compaction threshold | `observation_masking` |
| Compaction | Summarises older messages | At the context threshold (Settings) | threshold |
| Summary fallback | Builds the summary from the conversation itself | The model's summary misses required sections | always |
| Pinned request | After compaction: the user's request word for word, git status, files edited, the task list and which commands already worked | After compaction | always |
| Earlier reasoning | Sends earlier reasoning back as the model's chat template expects | Local servers | `keep_thinking` |
| Parallel reads | Runs read-only calls of one step at the same time | Every call in the step is a read | always |

### Safety

| Behaviour | What it does | Switch |
| --- | --- | --- |
| Approval modes | `plan`: read and investigate only. `ask`: confirm commands and deletions. `safe`: read-only commands run, others are asked. `dangerous`: nothing is asked. `autopilot`: nothing is asked and the model decides when to plan | Settings |
| Outside the project | Asks before a tool or command touches anything outside the project folder (once, for the session, the chat or the project) | Settings |
| Sandbox (Linux) | Commands run in bubblewrap: the system is read-only, only the project and a scratch folder are writable. Network stays available. On Windows there is no sandbox: the approval mode is the protection | `sandbox_commands` |
| Safe commit | `git commit` without a path commits tracked changes and only the files this chat created, and lists what it left out | always |
| Undo | Every edit is recorded: `/undo` reverts it, and a conversation can be rewound to an earlier message with its file changes | always |

**Project instructions**: `/init` reads the instruction files of other agents (`AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`, `CONVENTIONS.md` and others, never changing them) and writes `.quench/QUENCH.md`, which is
in the prompt of every chat in that project.

The model has no tool to ask the user a question: it asks in its reply, and the turn ends there.

## Ablation switches

Each switch turns one behaviour off (or changes it) for a QuenchBench run, so its effect can be measured
on your model. In the app: Benchmarks, "Compare runs". From the command line (Local Quench 0.1.1 or newer):

```bash
python3 quenchbench.py --server http://localhost:1234 --model qwen3.8-27b --suite quenchbench --size quick \
  --repeats 3 --yes                                   # the default harness
python3 quenchbench.py ... --harness continue_nudge=false   # the same run without the continue nudge
python3 quenchbench.py ... --harness harness_profile=bare   # the baseline: every switch below off
```

`--harness KEY=VALUE` can be given more than once. The run records the switches it used.

| Key | Changes | Values (default first) |
| --- | --- | --- |
| `harness_profile` | `light`: every guard rail on (small models). `strong`: the lean harness for frontier models (continue nudge, error hints, own checks, self-review, observation masking and the thinking cap off). `bare`: the baseline, every switch in this table off, the repo map and diagnostics too. Without the switch the app picks light or strong per model | light, strong, bare |
| `continue_nudge` | Continue nudge | true, false |
| `loop_warnings` | Repeated call, back and forth, polling and same-output notes | true, false |
| `take_stock` | Recap every 20 steps | true, false |
| `troubleshoot_note` | Ranked causes after 3 failures of one check | true, false |
| `own_check` | Own-checks reminder | true, false |
| `error_hints` | Error hints | true, false |
| `self_review` | Self-review of the diff | true, false |
| `observation_masking` | Observation masking | true, false |
| `keep_thinking` | Earlier reasoning sent back | true, false |
| `thinking_cap` | Reasoning tokens before the model is asked to act (0 = never) | 8192, 0, any number |
| `edit_diagnostics` | Diagnostics after edits | fast, full, off |
| `edit_format` | Edit format | auto, blocks, search_replace, apply_patch, whole_file |
| `tool_set` | All tools or the core 10 | full, core |
| `repo_map_tokens` | Size of the repo map (0 = none) | 1024, 0, 2048 |
| `lsp` | A language server when installed | off, auto |

In the app, `agent` also compares Local Quench with other agents on the same tasks: aider, Qwen Code,
OpenCode, OpenHands, mini-swe-agent, Codex, Goose, Crush.

**What `bare` keeps.** The tools, the edit formats and the repairs marked "always" above (calls written as
text, aliases, JSON, shell repair, edit matching, syntax rollback, output trimming), the runaway-text cut
and compaction. These have no switch yet, so "with and without the harness" means: with every switch on,
and with every switch off.

**Reading results.** A QuenchBench quick run is 63 tasks, ultra quick 13. One run of 13 tasks cannot show
the effect of one switch: compare the default harness with `bare` first, use `--repeats 3` or more, and only
then single switches. The app shows a paired significance test for ablation runs.

**Fixed in every benchmark run**, so that runs compare across computers: no hooks, MCP servers, skills or
GitHub integration, no language server unless `lsp` says so, no web tools, no verify command, the
`dangerous` approval mode (nobody is there to answer), and a per-reply output limit of 16k tokens unless
yours is lower.
