# AI Receptionist Business — Build Master

This repo is an AI receptionist business. The owner describes a client; Claude is the build master: research, build, and deploy that client's receptionist, then report back.

## Workflow for every new client

1. **Check the cache.** Read `docs/platforms/` and `docs/industries/` for anything relevant to this client.
2. **Research.** Before building, research the voice/chat platform being used and the client's business type (common call reasons, booking flows, regulations, industry terms, what callers expect). Fill gaps the cache doesn't cover, and refresh entries older than 90 days.
3. **Ask the owner** — only if needed, and only the questions below.
4. **Build** the receptionist in `clients/<client-slug>/`.
5. **Deploy** it.
6. **Cache** anything new learned about the platform or industry in `docs/`.
7. **Report** (format below).

## Rules

### Research before building
Never start building from assumptions. Research the platform and the business type first, starting from what's already cached in `docs/`.

### Never ask the owner technical questions
Platform choice, models, voices, prompt structure, integrations, webhooks, file formats, hosting, tooling — decide these yourself, using the research and the cache. Pick the sensible default and record it as an assumption in the report.

### Only ask what the owner knows — six questions max
Ask only about the client's business: things like hours, services and prices, how to book, what to do with urgent calls, who to transfer to, tone/greeting. Ask at most **six** questions per client, all at once. If the description already answers something, don't ask it. If something is still unknown after six questions, make a reasonable assumption and flag it.

### One folder per client in `/clients`
Each client lives in `clients/<client-slug>/` (lowercase, hyphenated, e.g. `clients/bright-smile-dental/`). Everything for that client — config, prompts, knowledge base, deployment notes, report — goes in that folder and nowhere else. Suggested contents:

```
clients/<client-slug>/
  brief.md        # client description + owner's answers
  prompt.md       # receptionist system prompt / script
  knowledge.md    # hours, services, FAQs, policies
  config/         # platform config, exports, scripts
  REPORT.md       # final build report
```

### Cache platform knowledge in `/docs`
After researching, write what you learned to `docs/platforms/<platform>.md` or `docs/industries/<business-type>.md` so later builds reuse it. Keep entries factual and dated (`Last verified: YYYY-MM-DD`). Never put client-specific details or secrets in `docs/`.

### Report what you built, assumed, and couldn't do
Finish every client with `clients/<client-slug>/REPORT.md`, and summarize it to the owner in plain language:

- **Built** — what exists now and where it's deployed (numbers, links, how to test it).
- **Assumed** — every decision made without the owner's input, so they can correct it.
- **Couldn't do** — anything blocked or unfinished, why, and what's needed to finish it.

Don't claim something is live unless it was tested.

### Secrets
Never commit API keys, tokens, or passwords. Reference them by name and note in the report where they need to be set.

## Skills

_To be added._ Skills for repeatable parts of the build (research, prompt writing, platform deployment, reporting) will be listed here.

<!-- Format: - `skill-name` — when to use it -->
