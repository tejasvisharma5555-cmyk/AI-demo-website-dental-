---
name: build-receptionist
description: Build, test, publish, and deploy a client's AI receptionist on the voice platform (Retell by default) once research-business-type is done and the owner's answers are in. Reads /docs and the client research first, uses native integrations wherever they exist, writes custom functions only when there is no native option and deploys them to Vercel, picks the newest fast model, creates and publishes the agent, attaches a phone number, and saves everything to the client's folder.
---

# Build a receptionist

**Input:** `clients/<slug>/`, with `brief.md` (owner answers filled in), `research.md`, and the
drafts in `receptionist/` (call flow, prompt, functions, knowledge base, post-call).
**Output:** a live, tested receptionist on a phone number, with every config and ID saved in the
client folder and a `REPORT.md`.

## 0. Read first, every time
1. `docs/platforms/<platform>/` — README (recipe + gotchas), capabilities, api-cheatsheet,
   custom-functions. Run the research-voice-platform change check first; if the docs changed,
   update `/docs` before building.
2. `docs/industries/<type>.md` and everything in `clients/<slug>/`.
3. Decide which **receptionist library skills** apply (see CLAUDE.md, Skills section): booking,
   cancel-reschedule, FAQ, lead capture, transfer, after-hours. Read each one that applies and
   follow it for its part of the prompt and tools.

All platform work goes through the platform's REST API, with keys loaded from `.env` (rule 7).

## 1. Choose native vs. custom for every function
For each function in `receptionist/functions.md`, work down this list and stop at the first that fits:
1. **Built-in tool** (e.g. Retell `end_call`, `transfer_call`, `send_sms`, `extract_dynamic_variable`).
2. **Native integration** — the client's system is in the provider list (capabilities §3).
   - Check what's already connected: `GET /list-apps`. For tool names: `GET /list-app-templates`.
   - If the provider uses an API key and the owner has given it → connect it: `POST /create-app`.
   - If the provider needs an OAuth sign-in, or a key the owner hasn't given → owner walkthrough (§7).
3. **Platform code tool** — no secrets, no LLM-supplied arguments, no writes to private systems.
4. **Custom function on Vercel** (§2) — only when 1–3 can't do it.

Record the decision and its reason in `receptionist/functions.md`.

## 2. Custom functions → Vercel
Only for functions that reached option 4.
- **Vercel token:** if `VERCEL_TOKEN` isn't in `.env`, ask the owner once, using the TL;DR
  format (§7): "Create a token at vercel.com/account/tokens → paste it here." Then apply rule 7:
  save `VERCEL_TOKEN` to `.env`, test it with `GET https://api.vercel.com/v2/user`, and record
  the result in `docs/platforms/vercel/README.md`. Never ask again.
- **Code:** `clients/<slug>/functions/`, one Vercel project per client named `<slug>-functions`.
  Use Node serverless functions under `api/` (e.g. `api/check-availability.js`). Each function:
  - verifies the platform's request signature (Retell: `X-Retell-Signature`, HMAC of the raw
    body with the Retell API key);
  - answers in under ~3 s where possible;
  - returns short JSON the agent can read aloud;
  - logs no personal or health data.
- **Secrets:** set them as encrypted Vercel project env vars through the API
  (`POST /v10/projects/{project}/env`). Never put them in code or the repo.
- **Deploy:** through the Vercel REST API (`POST /v13/deployments` with the files inline,
  `target: "production"`). Save the production URL and deployment ID to
  `clients/<slug>/deploy/vercel.json`.
- **Test:** `curl` each endpoint with a correctly signed sample body (expect 200 and correct
  JSON) and once unsigned (expect 401) before wiring it to the agent.
- **Wire up:** add it as a `custom` tool with `url`, `parameters`, `response_variables`, and
  `speak_during_execution: true` with a short filler line.

## 3. Pick the model (newest fast model — never an older default)
1. Get the platform's current model list from the live source. For Retell, that's the `LLMModel`
   enum in `https://docs.retellai.com/openapi.yaml` (download it fresh; don't trust the cache).
2. Check latency and tier info: the Retell `build/llm-options` docs page, the pricing page,
   recent model-replacement deprecation notices, and the dashboard's estimated-latency numbers
   if the owner has shared them.
3. Choose the **newest generation's fast/small model** that handles tool calls reliably. Set
   `tier: "fast"` if that model offers it. Set `backup` to a different fast model so a slow
   reply never holds up the call.
   Shape: `model_config: {type:"cascading", primary:{model, tier}, backup:{model, tier}}`.
4. After the agent is built, place 2–3 test calls. Read per-call latency from `GET /v2/get-call/{id}`.
   If p50 end-to-end latency is above ~1.2 s, try the next-fastest current model or tier and
   compare. Keep the faster one if tool use still passes.
5. Record the model, tier, backup, measured latency, and the reason in `REPORT.md` under Assumed.

## 4. Create and configure (Retell)
Save every request body and its response ID under `clients/<slug>/deploy/retell/`, as files named
for the resource: `knowledge-base.json`, `llm.json`, `agent.json`, `phone-number.json`, `tests.json`.
1. **Knowledge base** — `POST /create-knowledge-base`, using `receptionist/knowledge-base.md`
   plus the client's website URLs.
2. **Prompt engine** — `POST /create-retell-llm` with:
   - `general_prompt` from `receptionist/prompt.md`, plus the library skills' sections;
   - `begin_message` (including the recording disclosure where required);
   - `model_config` (§3), `knowledge_base_ids`, `general_tools`, `default_dynamic_variables`.
   - Use a conversation flow instead only if `call-flow.md` needs strict paths.
3. **Agent** — `POST /create-agent` with:
   - `response_engine`, `voice_id` (natural, region-appropriate, from `GET /list-voices`),
     `fallback_voice_ids`, `language`, `timezone`;
   - `boosted_keywords` and `pronunciation_dictionary` for the client's names and terms;
   - `post_call_analysis_data` from `receptionist/post-call.md`;
   - `data_storage_setting` and `data_storage_retention_days` (healthcare:
     `everything_except_pii` unless a BAA is signed and the owner wants recordings);
   - `end_call_after_silence_ms`, `max_call_duration_ms`.

## 5. Test before publishing
- **Simulation test cases:** at least one for each call type in `call-flow.md` and for every
  library skill used. Each library skill lists its required cases. Use `tool_mocks` so tests
  never write real bookings.
  Calls: `POST /create-test-case-definition` → `POST /create-batch-test` → `GET /get-batch-test`.
- Fix and re-run until they all pass. Save the results to `deploy/retell/tests.json`.
- One **web call** (`POST /v3/create-web-call`) to check voice and latency. If a browser can't be
  driven, note that and rely on the phone test.

## 6. Publish and attach a number
1. Publish: `POST /publish-agent-version/{agent_id}`.
2. **Phone number:**
   - **Buy one:** `POST /create-phone-number` with the client's `area_code`,
     `number_provider: "twilio"` (needed for SMS), and `inbound_agents:[{agent_id, weight:1}]`.
     Set `fallback_number` to the office line and add a `nickname`.
   - **Or import** the client's own number if they use their own phone system.
   - If the purchase fails because there's no payment method or KYC (identity verification) is
     pending → owner walkthrough (§7).
3. **Live phone test:** `POST /v2/create-phone-call` from the new number to a test line, or note
   that the owner should dial in. Check the result in `GET /v2/get-call/{id}`: transcript,
   latency, `disconnection_reason`.
4. Getting calls to the new number — the owner forwards their existing line or publishes the
   new number. Give them the walkthrough (§7).

## 7. Owner walkthroughs (TL;DR format)
Whenever something can't be finished without the owner doing a step themselves, tell them in
plain English, with no jargon:

> **TL;DR: <one-line what & why>**
> 1. <step, with the exact button or link>
> 2. <step>
> 3. Reply "done" (or paste <thing>).

Rules for walkthroughs:
- Max ~5 steps, one walkthrough per blocker.
- Batch them all into one message at the end of the build, unless one blocks the build itself.
- Keep building everything else that isn't blocked while you wait.
- List every walkthrough in `REPORT.md` under **Couldn't do**.

## 8. Save and report
- Everything goes in `clients/<slug>/` (never secrets):
  - `receptionist/` — final prompt, flow, functions, knowledge base, post-call;
  - `functions/` — custom function code;
  - `deploy/` — every request and response ID, the Vercel info, the phone number;
  - `REPORT.md`.
- `REPORT.md` (CLAUDE.md rule 6) has three sections:
  - **Built** — the number to call, what it handles, and the test results.
  - **Assumed** — every default chosen, including the model.
  - **Couldn't do** — the TL;DR walkthroughs.
- Commit and push.
