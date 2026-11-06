# AI Receptionist Build Master

This repo is an AI receptionist business. The owner describes a client; you
research, build, and deploy that client's receptionist end to end.

## Rules

1. **Research before building.** For every client, research both the
   platform the receptionist runs on and the client's business type before
   writing anything. Check `/docs` first; only go to the web for what is
   missing or stale.
2. **Never ask the owner technical questions.** Platform choice, voice/model,
   prompts, integrations, call flows, config, hosting, deployment: decide
   these yourself, pick sensible defaults, and record the decision.
3. **Only ask what the owner knows, six questions max.** Ask only about the
   business itself (hours, services, prices, booking rules, who to transfer
   to, tone, things never to say). Never ask anything research or the
   client's website can answer. Ask all questions in one batch, not one at
   a time. If you need nothing, ask nothing.
4. **One folder per client in `/clients`.** Everything for a client lives in
   `clients/<client-slug>/` (lowercase, hyphenated, e.g. `bright-smile-dental`).
   Nothing client-specific goes anywhere else.
5. **Cache platform knowledge in `/docs`.** Anything you learn that applies
   beyond one client goes into `/docs` so the next build is faster.
6. **Report what you built, assumed, and couldn't do.** Every build ends
   with a report in that three-part format (see below). Never claim
   something is deployed or tested unless you verified it.

## Workflow

1. **Intake**: create `clients/<slug>/brief.md` from the owner's description.
2. **Research**: read `docs/platforms/` and `docs/business-types/`. Fill gaps
   from the web (platform docs, client's website, competitors). Write
   client-specific findings to `clients/<slug>/research.md`; write reusable
   findings back to `/docs`.
3. **Questions**: if anything only the owner knows is still missing, ask up
   to six plain-language questions in one message. Otherwise proceed.
4. **Build**: write the receptionist (prompt, knowledge base, call flows,
   platform config) in `clients/<slug>/build/`.
5. **Deploy**: deploy to the chosen platform. If credentials or access are
   missing, prepare everything so deployment is one step, and say so.
6. **Test**: run test conversations covering the common scenarios for that
   business type (booking, hours, pricing, emergencies, transfer to human,
   off-topic). Log results in `clients/<slug>/tests.md`.
7. **Report**: write `clients/<slug>/report.md` and summarize it to the owner.

## Client folder layout

```
clients/<slug>/
  brief.md       # what the owner told you + answers to your questions
  research.md    # client-specific findings (website, services, competitors)
  decisions.md   # technical choices you made and why
  build/         # prompts, knowledge base, flows, platform config
  tests.md       # test conversations and outcomes
  report.md      # final report (built / assumed / couldn't do)
```

## Docs cache

```
docs/platforms/<platform>/            # full platform research (see research-platform skill):
                                      # capabilities, tools, integrations, phone numbers,
                                      # testing, custom-function gaps, deprecations
docs/business-types/<type>.md         # what callers ask, must-handle scenarios,
                                      # compliance/privacy notes, sample FAQs
```

- Start every doc with `Last verified: YYYY-MM-DD` and the sources used.
- Platform docs are refreshed only when the platform's docs change (the
  `research-platform` fingerprint check), or when the live API contradicts
  them. Update in place.
- Before every build, read `capabilities.md` and `deprecations.md` for the
  platform. Use native features first; custom functions only for listed gaps.
- Record gotchas and workarounds, not just the happy path.
- Never put client data or secrets in `/docs`.

## Report format

```
## Built
- What exists, where it lives, how it was deployed, how it was tested.

## Assumed
- Every default or guess made without owner confirmation, so they can correct it.

## Couldn't do
- What is missing or blocked, why, and the exact next step to unblock it.
```

## Platforms and API keys

Whenever the owner gives a platform and an API key, do all of these, immediately:

1. **Save the key to `.env`** as `<PLATFORM>_API_KEY=<key>` (e.g.
   `RETELL_API_KEY`). Add the variable name, with no value, to `.env.example`.
   `.env` is gitignored; confirm with `git check-ignore .env` before any commit.
2. **Use the platform's REST API** for all build and deploy work. No
   dashboards, no SDK-only workflows. Load the key from `.env`, never hardcode it.
3. **Test the key with one API call**: a read-only call (e.g. key info or
   list voices). Report whether it worked (status code + what came back).
4. **Run the `research-platform` skill** for that platform (it skips itself
   if the cached docs are still current).

If the network blocks the platform's host, request access to that host and
retry; never fake or mock the test result.

### Known platforms

| Platform | Use | Env var | API base | Docs cache |
|---|---|---|---|---|
| Retell | Voice | `RETELL_API_KEY` | `https://api.retellai.com` | `docs/platforms/retell/` |

## Secrets

Never commit API keys, passwords, or client credentials. Keys live only in
`.env` (gitignored). Reference them by variable name in `decisions.md` and
`/docs`; never paste a key's value into any committed file.

## Skills

Skills live in `.claude/skills/<name>/SKILL.md`. When a skill covers a step,
use it instead of the default approach.

| Skill | When to run | Output |
|---|---|---|
| `research-platform` | Whenever a new platform is connected (platform + key given). Before a build, run its fingerprint check; re-run the research only if the platform's docs changed. | `docs/platforms/<platform>/` |

<!-- Add skills below this line -->
