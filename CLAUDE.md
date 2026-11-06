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
  deploy/           # deployment config and steps actually taken
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

---

## Workflow

1. Owner describes the client.
2. Check `/docs`; research platform + business type; update `/docs`.
3. Create `clients/<client-slug>/` from the template; write `brief.md` and `research.md`.
4. Ask the owner up to six business questions (one batch).
5. Build the receptionist; test it.
6. Deploy.
7. Write `REPORT.md` and summarize Built / Assumed / Couldn't do.

---

## Secrets
Never commit API keys, phone-provider credentials, or patient/customer data.
Reference secrets by name in config; keep values out of the repo.

---

## Skills

_Reserved — skills will be added here next._

<!--
List each skill with: name, when to use it, and what it produces.
Example:
- `research-platform` — use when a platform isn't in /docs; writes docs/platforms/<name>.md
-->
