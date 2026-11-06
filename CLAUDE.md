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
docs/platforms/<platform>.md          # how to build + deploy on a platform
docs/business-types/<type>.md         # what callers ask, must-handle scenarios,
                                      # compliance/privacy notes, sample FAQs
```

- Start every doc with `Last verified: YYYY-MM-DD` and the sources used.
- Re-verify a doc if it is older than 90 days or the platform behaves
  differently than documented; update it in place.
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

## Secrets

Never commit API keys, passwords, or client credentials. Reference them by
name in `decisions.md`; store them in the platform or environment settings.

## Skills

_Reserved. Skills for research, building, deploying, and testing will be
added here. When a skill covers a step above, use it instead of the default
approach._

<!-- Add skills below this line -->
