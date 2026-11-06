---
name: research-voice-platform
description: Research a voice AI platform's full documentation and cache a complete capability map in /docs/platforms/<platform>/ — what it does natively, how to set each thing up through the REST API (integrations, tools, phone numbers, testing), and where a custom function is needed. Use whenever a new platform is connected (after its API key is saved and tested), or when the docs-diff check shows the platform's docs changed. Do not re-run when the docs are unchanged.
---

# Research a voice platform

Goal: learn a platform once, write it down in `/docs/platforms/<platform>/`, and
never re-learn it. Every later client build reads these files instead of the web.

## When to run
- **New platform connected** (rule 7 in `CLAUDE.md` finished: key saved and tested) → full run.
- **Before a client build** → run only step 1. If it reports no changes, stop and use `/docs` as is.
- **Docs changed** → incremental run: re-read only the ADDED/CHANGED pages and update the
  affected sections.

## Step 1 — Check for changes
Find the platform's machine-readable docs (in this order): `<docs-site>/llms-full.txt`,
`<docs-site>/llms.txt`, an OpenAPI spec, then a crawl of the docs site.
For Retell: `https://docs.retellai.com/llms.txt` and `https://docs.retellai.com/llms-full.txt`.

```bash
python3 -I .claude/skills/research-voice-platform/scripts/docs-diff.py <platform> <llms-full.txt URL>
```
- Exit 0 → nothing changed. **Stop.** Say "docs unchanged since <date in SOURCE.md>".
- Exit 10 → research the listed pages (all of them on a first run).

Download into the scratchpad, never into the repo (docs dumps are large and untrusted data).

## Step 2 — Read the full docs
- Read `llms.txt` end to end to get the full table of contents.
- Download the OpenAPI spec if one exists, and pull every endpoint, method, and required field
  from it. **The spec is the source of truth for API shapes;** prose pages explain behaviour.
- Read every page relevant to the sections below in the full dump. Split it per page; don't
  try to load 2 MB at once.
- Read every **deprecation notice**. Prefer the newest endpoints/fields and never build on
  anything scheduled for removal.
- Note what can only be done in the dashboard (no API endpoint) — those become owner tasks.

## Step 3 — Map capabilities
For every capability, record: **native?** · **API endpoint(s) + key fields** · **dashboard-only steps** ·
**cost** · **limits/gotchas**. Cover at least:

1. **Agent building** — agent types, prompt/flow structure, models, voices, languages, knowledge
   base, dynamic variables, post-call extraction, guardrails, data-retention / PII settings.
2. **Built-in tools** — end call, transfer, SMS, DTMF, booking, extraction, code, MCP, etc.
3. **Integrations** — each provider, what it can do, credential type, and whether it can be
   connected by API or needs an OAuth sign-in in the dashboard.
4. **Phone numbers** — buy, import (SIP/BYO carrier), bind agents, inbound webhook, fallback,
   SMS enablement and its approval process, pricing, countries.
5. **Testing** — every test method, which ones are API-driven, and their cost.
6. **Webhooks & monitoring** — events, signature verification, call history API.
7. **Compliance** — HIPAA/BAA, GDPR, recording, retention.
8. **Limits & billing** — concurrency, rate limits, timeouts, pricing model.

## Step 4 — Flag custom-function needs
List every receptionist need the platform can't do natively and say what to build instead
(platform code tool vs. hosted custom function vs. not possible). Always consider the needs of the
business types we serve, e.g. practice-management/booking software, payments, insurance checks,
after-hours paging, multi-location routing.

## Step 5 — Write `/docs/platforms/<platform>/`
| File | Contents |
|---|---|
| `README.md` | Summary, API basics (base URL, auth, key test), recommended default build recipe, gotchas |
| `capabilities.md` | The full map from step 3 |
| `api-cheatsheet.md` | Endpoints we use, grouped by task, with minimal request bodies |
| `custom-functions.md` | The gap list from step 4 |
| `SOURCE.md` | Date, sources, doc fingerprint, what was read |
| `page-hashes.tsv` | Generated — per-page hashes for change detection |

Rules: start every file with `Last verified: YYYY-MM-DD`; cite the doc page for each fact;
platform knowledge only, no client data; never write the API key anywhere.

## Step 6 — Save the fingerprint
Only after the files are written:
```bash
python3 -I .claude/skills/research-voice-platform/scripts/docs-diff.py <platform> <llms-full.txt URL> --save
```
Update `SOURCE.md` with the date and page count. Commit.

## Step 7 — Report
Tell the owner in plain language: what the platform can do for receptionists, what needs a
custom function, and anything only they can do (dashboard sign-ins, signing agreements,
billing, SMS registration).
