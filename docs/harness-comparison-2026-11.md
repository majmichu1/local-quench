# Local Quench and pi on QuenchBench Short: first comparison (November 2026)

We ran the same tasks with the same local model under two agent harnesses, Local Quench and
[pi](https://github.com/earendil-works/pi), to see how much the harness changes what a small local model gets done.
It is a first measurement, not a final one. Both runs had problems that came from my test machine and its setup,
listed below. When both harnesses have been measured again under exactly the same conditions, this file and the
[QuenchBench page](https://localquench.com/bench.html#harnesses) will be updated. Results can also be different with
other versions of either harness and with other models.

## Setup

- Model: Spark X2.6 4B, Q8_0, in LM Studio, on one laptop GPU (RTX 5060 Laptop, 8 GB).
- Tasks: QuenchBench Short, 26 tasks (two per section), three tries each, so 78 tries per harness.
- Four tasks at once, 30 minutes of model time per task, every task in its own container, graded by the same
  QuenchBench checks in the same image.
- Local Quench: run 20261102-104128-ed23, a 0.1.2 development build, Guided harness.
- pi: run 20261103-110733-b3fc, pi 1.4 with the community packages pi-tool-repair 0.3.9 and pi-anti-doom-loop
  0.0.14.

## What went wrong in the runs

- Local Quench: 3 tries were graded as failed because the grader could not create Go's build cache (a QuenchBench
  bug, fixed since), and 2 tries were cut by a reply length limit that has been removed since.
- pi: it ran its commands on the host instead of in the task container, so in the Go and Rust tasks it first ran into
  a missing or different toolchain. 11 tries ended when the anti-loop package stopped the request, and they count as
  failures here.
- Both are fixed in the benchmark now: an outside agent's commands run in the task container, and a stopped try is
  graded as the agent left it.

## Results

|  | Local Quench | pi |
|---|---|---|
| Solved tries | 36 of 78 (46.2%) | 26 of 78 (33.3%) |
| Likely range (95%) | 36 to 57% | 24 to 44% |
| Per round of tries (1st, 2nd, 3rd) | 12, 12, 12 | 7, 9, 10 |
| Median time per task | 15.1 min | 15.4 min |
| Model time per solved task | 35.5 min | 50.7 min |
| Stopped by the time limit | 13 | 25 |
| Output tokens per task (mean) | 15.4k | 16.1k |
| Input tokens per task (mean) | 427k | 339k |
| Steps per task (mean) | 24.2 | 21.5 |
| Largest context | 51,549 | 45,841 |

By task: both solved 13 tasks at least once, only Local Quench 4, only pi 2, neither 7. With 78 tries each, part of
the gap could still be chance (a paired test gives p of about 0.1) and the ranges overlap, so we read it as a first
result, not a verdict.

## Per task

Solved tries out of three. Every try, with what happened when it failed, is in
[harness-comparison-2026-11.csv](harness-comparison-2026-11.csv). The task conversations are not published.

| Task | Language | Local Quench | pi |
|---|---|---|---|
| algorithms/grid-dijkstra | go | 0/3 | 1/3 |
| algorithms/union-find | c | 3/3 | 0/3 |
| bugfix/bash-log-rotate | bash | 0/3 | 0/3 |
| bugfix/binary-search | javascript | 3/3 | 2/3 |
| build/bash-set-e-build | bash | 3/3 | 1/3 |
| build/py-import-cycle | python | 3/3 | 3/3 |
| data/unit-convert | rust | 0/3 | 0/3 |
| data/w2-json-patch | javascript | 0/3 | 0/3 |
| feature/c-ringbuf | c | 1/3 | 1/3 |
| feature/go-cursor-pagination | go | 2/3 | 0/3 |
| project/w2-agent-capacity | go | 1/3 | 1/3 |
| project/w2-csv-quoting | python | 2/3 | 3/3 |
| reading/batch-complexity | rust | 2/3 | 2/3 |
| reading/w2-pricing-pipeline | javascript | 1/3 | 2/3 |
| refactor/dedupe-email-check | python | 3/3 | 3/3 |
| refactor/link-store-interface | rust | 1/3 | 1/3 |
| security/c-image-overflow | c | 2/3 | 1/3 |
| security/c-strlcpy | c | 3/3 | 1/3 |
| terminal/find-duplicates-nul | bash | 0/3 | 0/3 |
| terminal/git-recover-deleted | bash | 3/3 | 3/3 |
| testing/retry-backoff-tests | go | 2/3 | 0/3 |
| testing/w2-resolver-tests | javascript | 1/3 | 0/3 |
| ui/ui-cart-totals | web | 0/3 | 0/3 |
| ui/ui-kanban-undo | web | 0/3 | 0/3 |
| vague/config-file-vague | python | 0/3 | 1/3 |
| vague/w2-rate-limit-vague | go | 0/3 | 0/3 |

All 26 tasks come with the app (QuenchBench Short). [quenchbench-sample/](../quenchbench-sample/) has a separate set of
26 tasks with their checks and reference solutions, to see what QuenchBench tasks look like.
