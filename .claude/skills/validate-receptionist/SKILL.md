---
name: validate-receptionist
description: Validate a client's AI receptionist after every build — confirm the agent exists and is published, functions are registered, integrations authenticate, and the phone number routes to it; run the simulation test suite; start a local voice-orb test page (a Retell web call in the browser) and open it for the owner; then report Built / Assumed / Couldn't do and give three realistic test-call scenarios for the business type. Run automatically at the end of build-receptionist, and again after any change to a live receptionist.
---

# Validate a receptionist

**Input:** `clients/<slug>/`, as left by build-receptionist. In particular
`deploy/retell/ids.json`:

```json
{
  "client_name": "Bright Smile Dental",
  "agent_id": "agent_...",
  "llm_id": "llm_...",
  "conversation_flow_id": null,
  "knowledge_base_ids": ["knowledge_base_..."],
  "app_ids": ["app_..."],
  "phone_number": "+1...",
  "expected_tools": ["check_availability", "book_appointment", "transfer_front_desk", "end_call"],
  "custom_function_urls": ["https://<slug>-functions.vercel.app/api/check-availability"],
  "test_case_definition_ids": ["..."]
}
```

If a number was deliberately not attached (for example a demo), set `"phone_number": null`
and `"phone_number_skipped_reason": "<why>"`. The check then shows as SKIP instead of FAIL.

If Retell returns **402 (credits exhausted)** for the simulation batch or web call, record it
under Couldn't do with a top-up walkthrough. Keep the last completed batch's results in
`deploy/retell/simulation-run-N.json`.

If `ids.json` is missing or incomplete, rebuild it from the files in `deploy/retell/` and from
`GET` calls to the API before validating.

## Credits first (CLAUDE.md rule 9)
- Structural checks are free.
- `--simulate` and web/phone calls spend the owner's Retell credits:
  - run the full suite **once** per build;
  - after a fix, use `--simulate --cases "DEMO 06,DEMO 12"` for only the affected tests;
  - never re-run to confirm a pass;
  - ask before spending more.
- Report how many test conversations were used.

## 1. Structural checks
```bash
python3 -I .claude/skills/validate-receptionist/scripts/check.py <slug> --simulate
```
Without `--simulate` it only runs the structural checks.

What it checks:
- **Agent** exists (`GET /get-agent`) and has a published version (`GET /list-agent-versions`).
- **Functions registered:** every name in `expected_tools` is on the Retell LLM (general and
  state tools) or in the conversation flow (tools and nodes). The model config is set.
- **Knowledge bases** have finished ingesting (`status: complete`).
- **Integrations authenticate:** `POST /test-app-auth/{app_id}` returns `success: true` for every app.
- **Phone number** exists and its `inbound_agents` include this agent.
- **Custom functions** (Vercel) are reachable and reject unsigned requests (401/403).
- **Simulation:** runs every saved test case as one batch (`/create-batch-test`), waits for it,
  and prints pass/fail with the reason for each failure.

Results go to `clients/<slug>/deploy/validation.json`.

**On failure:** fix the cause through the API (re-register the tool, re-publish, rebind the
number, redeploy the function), then re-run. If the fix needs the owner (for example, an
integration whose sign-in expired), write a TL;DR walkthrough (CLAUDE.md rule 8). Never report a
failed check as working.

The simulation suite must include the cases required by every library skill used in the build.
If any are missing, create them (`/create-test-case-definition`, with `tool_mocks` so nothing
real gets booked), add their IDs to `ids.json`, and re-run.

## 2. Voice-orb test page
A local page with one orb: tap it to talk to the agent through a Retell web call. The orb
pulses with the agent's voice. There are mute and end buttons.

```bash
node .claude/skills/validate-receptionist/scripts/test-page/server.mjs <slug> 5173
```
Run it in the background.

How it works:
- The server serves the page and Retell's browser SDK. The SDK is bundled locally in `vendor/`,
  so no CDN is needed; rebuild it with `vendor/build-sdk.sh`.
- The server forwards only the "create web call" request to Retell. It adds the API key from
  `.env` on the server side and always uses this client's agent. The key never reaches the
  browser, and no public key is needed.
- Test calls are tagged `metadata.source = "local-test-page"` in Retell's call history.

**Open it:**
- **Cloud session:** call `report_preview_port` with the port, so the owner's app can show it.
- **Local session:** open `http://localhost:5173` in the default browser (`open` / `xdg-open`).
- **Always:** load it once with Playwright and take a screenshot to confirm it renders. When
  clicking the orb in Playwright, use `force: true`, because the orb's breathing animation means
  it's never "stable". Then tell the owner how to use it: "tap the orb, allow the microphone, and
  talk." If the preview can't use the microphone, give the TL;DR for running it on their own
  computer:

  > **TL;DR: talk to your receptionist on your computer**
  > 1. Open the project folder in a terminal.
  > 2. Run `node .claude/skills/validate-receptionist/scripts/test-page/server.mjs <slug>`
  > 3. Open http://localhost:5173, tap the orb, and allow the microphone.

  This needs the repo and a `.env` with `RETELL_API_KEY` on their computer.

After the owner's test call, pull it with `POST /v3/list-calls` (filtered on the agent, newest
first). Note its latency and any problems in the report.

## 3. Three test-call scenarios
Write three phone scenarios the owner can act out, from `docs/industries/<type>.md` and this
client's call flow:
1. **The bread-and-butter call** — the most common call type, end to end (usually booking).
2. **The tricky one** — an edge case this business really gets (after-hours emergency, angry
   caller, booking for someone else, insurance it doesn't take).
3. **The handoff** — something the agent must not handle alone (transfer, or taking a message
   with an urgent flag).

For each scenario give:
- **Say:** what to say, as a short script with a persona (name and situation).
- **Expect:** what should happen.
- **Check after:** what to look at afterwards — the calendar entry, the text received, the
  transfer ringing, the call summary.

Number them, and use the client's real services and names.

## 4. Report
Update `clients/<slug>/REPORT.md` (CLAUDE.md rule 6) and give the owner a short summary:
- **Built** — the phone number, the test page link or command, what the receptionist handles,
  the structural checks (X/Y passed), the simulation results (X/Y passed), and measured latency.
- **Assumed** — every default chosen without the owner, including the model, voice, policies,
  and callback promise.
- **Couldn't do** — every failed check or blocked item, each with its TL;DR walkthrough.
- **Try these three calls** — the scenarios from step 3.

Commit `REPORT.md` and `deploy/validation.json`.
