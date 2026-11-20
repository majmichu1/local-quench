# Ask a Bigger Model: a local model asks a stronger one

Your local model keeps doing the work. When it is stuck, it may ask a stronger model for advice: a diagnosis, a plan,
what to check next. The stronger model only advises. It cannot edit a file or run a command. The tool the
model gets is `ask_advisor(question, files?, context?)`.

In the app the feature is called **Ask a Bigger Model** (Settings › Quench). It is not the **Model Advisor**, which
recommends a model and quantization for your graphics card.

## Where the advice comes from
Pick one in Settings › Quench › Ask a Bigger Model:
- **A coding CLI you already use, on your own plan**: Claude Code (`claude -p`, read-only plan mode), Codex (`codex exec
  --sandbox read-only`), Gemini CLI or Qwen Code. No API credits are bought; the question counts against your plan.
- **A provider set up in Local Quench**: an API key, OpenRouter's free models, or a bigger model on another computer in
  your network.
- You choose the model the advisor answers with.

## 1. Turn it on
1. Settings › Quench › Ask a Bigger Model: choose where the advice comes from.
2. Agree to the consent text. It names who receives the data. Your agreement is stored per advisor and checked by the
   app's server. Choosing another advisor turns the feature off until you agree again.
3. **Let the model ask for advice** on, in the same section (a chat's own settings can turn it off for that chat).

## 2. What happens in a chat
- The model decides when to ask. The harness never asks the advisor without your yes. The system prompt tells the model to ask when it is stuck (the
  same error after two real attempts, a failure it cannot explain, a design or risky change it is unsure about), not
  for what it can find out by reading or running the code, and to send the exact error, what it tried and the files
  that matter.
- Before each question you see what would be sent and approve it, unless the chat runs without approvals or you chose
  "always" for this advisor in this chat.
- The answer comes back to the model as a tool result. The model goes on working with it.

## When the model is stuck and does not ask
A model that goes in circles does not notice it, so it never asks. Local Quench notices, for any
tool:
- the same error of the same tool for the 4th time in a turn, after a hint or a note was already given for it;
- the same result of one tool three times in a row;
- two reminders to use the MCP server your request names, with no working call to it between them;
- four failed calls of one tool in a row;
- loop detection (the same call with the same result, two actions alternating, reasoning in circles).

Then the turn waits and you get one question, on the computer, the tablet and the phone, in every permission mode
(also Autopilot and Skip permissions, because it is about sending data out): "The model seems stuck: the same error 4
times: AttributeError ... Ask Claude Code for advice?" with **Yes, ask** and **No, let it continue**.
- **Yes**: Local Quench asks the advisor itself, with your request, the step in progress of the model's plan, its last
  steps and the repeated error (no files; keys and tokens cut out, like any question). The question counts toward
  the limits below. The advice is shown in the chat ("Asked Claude Code because ...", it folds away) and given to
  your model, which carries on with the work.
- **No**: the model carries on. The same reason is not asked about again in that turn; a different one may be, three
  questions a turn at most.
- A limit already reached: no question; a line in the chat says the advisor was not asked and why.
- No advisor set up or agreed to: no question; once per chat a line says "The model seems stuck (...). You can set
  up Ask a Bigger Model in Settings to get advice in moments like this."
- Never in a benchmark, a night run or the Chat tab.

## 3. What is sent
- Your request in this turn, the model's question and context, and the files it names, read from the project.
- Never: blocked paths, files outside the project, files that look like secrets (`.env`, `*.pem`), unless your own
  request names them. Known keys and tokens are cut out of everything sent.

## 4. Limits
- Questions per turn (default 3, Settings › Quench › Ask a Bigger Model) and per day (default 30, in the settings
  file).
- A timeout per question (default 5 minutes).
- The CLI runs in an empty temporary folder: it knows only what Local Quench sends. It reads the project itself only
  if you turn on **Let the advisor CLI read the project**, you trusted that CLI's config in this project (a repo's
  `.claude`, `.codex`, `.gemini` or `.qwen` settings can run commands when the CLI starts there), and the project has
  no blocked paths.

## 5. What it cannot promise
The CLIs have their own read tools and run as you, so they can read files on this computer beyond what Local Quench
sends: Codex's read-only sandbox reads the whole disk; Gemini and Qwen read what their tools allow. Claude Code gets
deny rules for Local Quench's settings and data and for `~/.ssh`, and starts without your MCP servers; the others
have no such switch. The consent text says so.

## 6. What it costs
Recap › Ask a Bigger Model lists every question: which local model asked, which advisor answered, tokens, and the
money spent (API) or the API value of a plan's use. It is never counted as a saving.

## When something is wrong
- "The advisor is not available in this chat": the feature is off, or you have not agreed to this advisor.
- "No more advisor questions in this turn": the per-turn limit; the model goes on without.
- A signed-out CLI: the answer says to sign in to that CLI again.
