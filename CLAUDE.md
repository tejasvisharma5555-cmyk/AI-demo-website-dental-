# AI Receptionist Build Master

This repo is an AI receptionist business. The owner describes a client business;
Claude researches, builds, and deploys an AI receptionist for that client.

Claude is the **build master**: it owns every technical decision end to end.

---

## Core rules

### 1. Research before building
Before building anything for a client:
- **Research the platform.** Check `/docs` first. If the platform isn't documented
  there, or the notes are older than ~90 days, research it (official docs, pricing,
  API limits, telephony/SMS options, integrations) and update `/docs`.
- **Research the business type.** Learn how this kind of business runs: typical
  caller questions, booking flow, urgent vs. routine calls, after-hours handling,
  industry terms, and compliance concerns (e.g. HIPAA for dental/medical, call
  recording consent laws).
- Write the research findings into the client folder before building
  (`research.md`).

### 2. Never ask the owner technical questions
Decide all technical matters yourself: platform, voice/model, telephony provider,
integrations, prompt design, call flows, hosting, file formats, deployment method.
Pick sensible defaults, note them as assumptions, and keep moving.

### 3. Only ask what the owner knows — six questions max
Ask only for business facts that can't be researched or reasonably assumed, such as:
- Business name, phone number, address, and hours
- Services offered and anything they don't do
- How appointments are booked (and with whom)
- What counts as urgent, and where urgent calls go
- Tone/personality preferences
- Anything callers must never be told

**Hard limit: six questions per client, asked in one batch.** Fill any remaining
gaps with researched defaults and list them as assumptions. Never send a second
round of questions unless something blocks deployment.

### 4. One folder per client in `/clients`
Each client gets `/clients/<client-slug>/` (lowercase, hyphenated, e.g.
`clients/bright-smile-dental/`). Everything for that client lives there.
Start from `/clients/_template/`. Recommended layout:

```
clients/<client-slug>/
  brief.md          # what the owner told us + answers to the questions
  research.md       # business-type and platform research for this client
  receptionist/     # prompts, call flows, knowledge base, config
  functions/        # custom function code (Vercel), only when no native option
  deploy/           # every request body, resource ID, and deployment record
  REPORT.md         # final build report (see rule 6)
```

Never mix one client's files, data, or credentials into another client's folder.

### 5. Cache platform knowledge in `/docs`
`/docs` is the shared knowledge base across all clients.
- One file per platform or topic (e.g. `docs/platforms/vapi.md`,
  `docs/industries/dental.md`).
- Each file starts with a `Last verified: YYYY-MM-DD` line and lists its sources.
- Reuse it before researching again; update it whenever you learn something new
  or find it out of date.
- Platform/industry knowledge only — no client-specific data here.

### 6. Report what you built, assumed, and couldn't do
Every build ends with `clients/<client-slug>/REPORT.md` and a short summary to the
owner, using these sections:
- **Built** — what exists and works, how to reach it (number, link, etc.), and how
  it was tested.
- **Assumed** — every decision made without the owner's input, so they can correct it.
- **Couldn't do** — anything blocked or unfinished, why, and exactly what's needed
  from the owner to finish it (in plain, non-technical terms).

Never report something as working unless it was tested.

### 9. Don't waste the owner's credits
Simulations, web calls, and phone calls cost the owner money (Retell bills per message and per
minute). Free checks (structural checks, reading configs, slot lookups, transcripts of past
runs) need no permission.
- **One full simulation suite per build.** Run it once at the end, before publishing.
- **After a fix, re-run only the affected tests** (`check.py <slug> --simulate --cases "DEMO 06,DEMO 12"`),
  never the whole suite.
- **Fix test wording without re-running.** If a failure is the test's own fault (a looping
  simulated caller or a badly worded check), fix the test and don't spend credits proving it.
- **Never re-run just to confirm a pass,** or because one run was flaky. Report it instead.
- **Ask first,** with an estimated count of test conversations, before spending more than
  **one full suite plus one targeted re-run** on a single change, and before any web or phone
  call I place myself.
- **Use the cheapest model for the simulated caller** (the test's `llm_model`). It doesn't need
  to be smart.
- **Report what was spent:** how many test conversations each change used.

### 8. When the owner has to do something, walk them through it (TL;DR)
If anything the owner asked for can't be finished without them doing a step, such as a sign-in,
payment, a signature, or forwarding their phone line, tell them in plain English, kept short:

> **TL;DR: <what and why, one line>**
> 1. <step, with the exact link or button>
> 2. <step>
> 3. Reply "done" (or paste <thing>).

Rules:
- No jargon, ~5 steps max.
- Batch the walkthroughs into one message unless a step blocks progress.
- Keep building everything else meanwhile.
- List each walkthrough under **Couldn't do** in the report.

### 7. When the owner gives a platform and an API key
Every time, without asking:
1. **Save the key to `.env`** (repo root) as `<PLATFORM>_API_KEY=...`
   (e.g. `RETELL_API_KEY`). `.env` is gitignored — never commit it, never copy the
   key into any other file, and never echo it in output. Add the variable name
   (empty value) to `.env.example`.
2. **Use the platform's REST API** for all work on that platform — not SDKs,
   dashboards, or CLIs. Load the key from `.env` at call time.
3. **Test the key with one API call** — a harmless read-only request (e.g. list
   agents). Report the HTTP status and what it showed. If it fails, say why and
   don't build on that platform until it works.
4. Record the base URL, auth format, and the test endpoint in
   `docs/platforms/<platform>/README.md`.
5. Run the **research-voice-platform** skill on the new platform.

---

## Platforms

- **Voice: Retell** — default voice platform for all receptionists.
  Key: `RETELL_API_KEY` in `.env`. Notes: `docs/platforms/retell/` (start with `README.md`).

---

## Workflow

1. Owner describes the client.
2. Run the research-voice-platform change check (step 1 only).
3. Run **research-business-type**. It does four things:
   - researches the industry and caches it in `docs/industries/`;
   - creates `clients/<client-slug>/` from the template;
   - writes `research.md` and drafts the call flow, prompt, and functions;
   - ends by asking the owner up to six business questions in one batch.
4. Fill in the owner's answers.
5. Run **build-receptionist**: build with the library skills that apply, test, publish,
   attach a phone number, and deploy any custom functions to Vercel.
6. Run **validate-receptionist** (after every build, and after any change to a live
   receptionist). It checks the build and runs the simulation tests, opens the voice-orb
   test page, and writes `REPORT.md` with Built / Assumed / Couldn't do (with TL;DR
   walkthroughs) and three test-call scenarios.

---

## Secrets
Never commit API keys, phone-provider credentials, or patient/customer data.
Reference secrets by name in config; keep values out of the repo.

---

## Skills

Skills live in `.claude/skills/<name>/SKILL.md`. Each entry: when to run it → what it produces.

- **research-voice-platform** (`.claude/skills/research-voice-platform/`)
  - **Run:** whenever a new platform is connected (after rule 7's key test passes), and
    as a change check before each client build.
  - **Re-run in full only if the docs changed:** `scripts/docs-diff.py` compares per-page
    hashes of the platform's docs and lists the pages that were added, changed, or removed.
    If nothing changed, use `/docs` as is.
  - **Does:** reads the platform's full docs (Retell: `docs.retellai.com/llms.txt`, plus
    `llms-full.txt` and the OpenAPI spec). Maps what the platform does natively and how to
    set up each thing through the API (integrations, tools, phone numbers, testing). Flags
    where a custom function is needed.
  - **Produces:** `docs/platforms/<platform>/` — `README.md`, `capabilities.md`,
    `api-cheatsheet.md`, `custom-functions.md`, `SOURCE.md`, `page-hashes.tsv`.

- **research-business-type** (`.claude/skills/research-business-type/`)
  - **Run:** at the start of every client build, right after the platform change check
    and before asking the owner anything.
  - **Does:** researches what calls to this kind of business sound like — what callers ask
    for, what they need to book, and what gets transferred. Then drafts the call flow,
    prompt, and functions, marking each function native, custom, or fallback against the
    platform docs. Ends by asking the owner up to six questions only they would know
    (rule 3).
  - **Re-use:** reuses `docs/industries/<type>.md` if it was verified within ~90 days;
    otherwise researches and updates it.
  - **Produces:**
    - `docs/industries/<type>.md` (reusable, no client data);
    - `clients/<slug>/research.md` and `brief.md` (with the questions);
    - `clients/<slug>/receptionist/` — `call-flow.md`, `prompt.md`, `functions.md`,
      `knowledge-base.md`, `post-call.md`.

- **build-receptionist** (`.claude/skills/build-receptionist/`)
  - **Run:** after the owner's answers are in.
  - **Does:**
    - Reads `/docs` and the client research first.
    - For each function, uses the first option that works: a built-in tool, then a native
      integration, then the platform's code tool. Only then does it write a custom function,
      deployed to Vercel through Vercel's REST API.
    - The first time a Vercel token is needed, asks the owner once and saves it to `.env` as
      `VERCEL_TOKEN` (rule 7).
    - Picks the newest fast model from the platform's live model list, using its fast tier and
      a fast backup model. Checks latency on test calls and never defaults to an older model.
    - Creates and configures the agent, tests it, publishes it, and attaches a phone number.
    - Gives TL;DR walkthroughs for anything the owner must do (rule 8).
  - **Produces:** everything in `clients/<slug>/`:
    - `receptionist/`;
    - `functions/` (custom function code);
    - `deploy/` (every request body and resource ID, Vercel info, phone number);
    - `REPORT.md`.

- **validate-receptionist** (`.claude/skills/validate-receptionist/`)
  - **Run:** after every build (the last step of build-receptionist) and after any change
    to a live receptionist.
  - **Does:**
    - `scripts/check.py <slug> --simulate` confirms the agent exists and is published,
      every function is registered, integrations authenticate, knowledge bases are ready,
      the phone number routes to the agent, and custom functions reject unsigned
      requests. Then it runs the full simulation test batch.
    - `scripts/test-page/server.mjs <slug>` starts a local voice-orb page, so the owner can
      talk to the agent in the browser through a Retell web call. The server adds the API
      key itself, so the key never reaches the browser. The skill opens the page for the
      owner.
    - Writes three test-call scenarios for the business type (everyday call, tricky
      edge case, handoff).
  - **Produces:** `deploy/validation.json` and an updated `REPORT.md`
    (Built / Assumed / Couldn't do / Try these three calls).

### Receptionist library
Used by build-receptionist; one skill per job. Each skill gives:
- the owner facts it needs;
- native vs. custom paths for each kind of client system;
- the prompt section, tool config, and edge cases;
- the simulation tests it must pass, and its post-call fields.

| Skill | Use when |
|---|---|
| **receptionist-booking** | The client takes appointments — check availability, collect details, confirm, book |
| **receptionist-cancel-reschedule** | The client takes appointments — find the booking, verify identity, apply the cancellation policy, move or cancel it |
| **receptionist-faq** | Every client — answer from the knowledge base, never guess prices, insurance, or hours |
| **receptionist-lead-capture** | Every client — take messages and new enquiries and deliver them to a CRM, text, or email. Also the fallback when booking or transfer can't be done |
| **receptionist-transfer** | The client has staff to hand calls to — warm or cold transfer, rules, failed-transfer fallback |
| **receptionist-after-hours** | Every client — open/closed logic, holidays, emergencies, on-call routing, after-hours booking |
