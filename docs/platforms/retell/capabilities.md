Last verified: 2026-11-06

# Retell — capability map

Legend: **API** = can be set up through the REST API · **Dashboard** = needs a human in the
Retell dashboard (becomes an owner task) · **Native** = no code of ours needed.

## 1. Agent building

| Capability | Native | How to set it up | Notes |
|---|---|---|---|
| Single-prompt agent | Yes | API: `POST /create-retell-llm` → `POST /create-agent` | Retell recommends starting here |
| Conversation-flow agent | Yes | API: `POST /create-conversation-flow` → `POST /create-agent` (`response_engine.type` = flow) | Node types include conversation, subagent, function, code, transfer, SMS, logic split, extract-variable, end, global, MCP, and press-digit. Subflows are reusable components (`/create-conversation-flow-component`) |
| Multi-prompt agent | Deprecated | — | Creation ends 2026-12-15 — don't use |
| Custom LLM over WebSocket | Yes | We'd host a WebSocket server | Only if we ever need our own LLM. Not our default |
| Model choice | Yes | `model_config: {type: cascading, primary, backup, temperature}` | Text models from OpenAI, Anthropic, and Google (`LLMModel` enum in the spec). `backup` takes over when the primary is slow. Speech-to-speech and full-duplex (`gpt-live-1`) are also available |
| Voice | Yes | `voice_id`, `voice_model`, `voice_speed`, `voice_temperature`, `fallback_voice_ids`; `GET /list-voices`; `/clone-voice`; community voices | A fallback voice is required with custom or third-party voices |
| Language / multilingual | Yes | `language` (one locale, or an array for multilingual) | The scalar `"multi"` value was removed 2026-07-31 |
| Knowledge base | Yes | API: `POST /create-knowledge-base` (multipart: files, texts, URLs), `/add-knowledge-base-sources/{id}`, `/refresh-knowledge-base/{id}`. Attach via `knowledge_base_ids` on the LLM | `enable_auto_refresh` re-crawls URLs. Google Drive, OneDrive, and Notion sync via integrations |
| Dynamic variables | Yes | `{{var}}` in prompts. Set per call (`retell_llm_dynamic_variables`), via the inbound webhook, by tools (`response_variables`), or with `default_dynamic_variables` | Stored in plaintext — no secrets |
| Pre-call / post-call workflow | Yes | `pre_session_tools`, `post_session_tools` on the agent | Look up the caller before the agent speaks; log or notify after the call. Steps run as a dependency graph |
| Post-call extraction | Yes | `post_call_analysis_data` (boolean, selector, text, number fields), `post_call_analysis_model`; `PUT /rerun-call-analysis/{call_id}` | Results arrive in the `call_analyzed` webhook and in `GET /v2/get-call` |
| Contacts and contact memory | Yes | `/create-contact`, `/list-contacts`, `/get-contact-by-phone/{n}`; `contact_memory_config` on the agent | Remembers callers across calls and SMS |
| Guardrails | Yes | `guardrail_config` | Prohibited-topic filtering on input and output |
| Agent Handbook presets | Yes | `handbook_config` | Ready-made best-practice prompt presets for personality, accuracy, and safety |
| Pronunciation / boosted keywords | Yes | `pronunciation_dictionary` (IPA/CMU), `boosted_keywords` | Use for clinic, staff, and drug names |
| Speech behaviour | Yes | `interruption_sensitivity`, `responsiveness`, `enable_backchannel`, `denoising_mode`, `ambient_sound`, `end_call_after_silence_ms`, `max_call_duration_ms`, `reminder_trigger_ms` | |
| Voicemail / IVR handling | Yes | `voicemail_option`, `ivr_option` | Mainly for outbound calls |
| Caller keypad input (DTMF) | Yes | `allow_user_dtmf`, `user_dtmf_options` | |
| Do-not-call detection | Yes | `enable_dnc_detection` | |
| Versions and publishing | Yes | `/create-agent-version`, `/publish-agent-version`, `GET /list-agent-versions`; a phone number can pin `agent_version` | Test the draft, then publish |
| A/B testing | Yes | Weighted `inbound_agents` on a number | |
| Chat / SMS agent | Yes | `/create-chat-agent`, `/create-sms-chat`, `/create-chat-completion`; website widget | |

## 2. Built-in tools (`general_tools` on a Retell LLM, or flow nodes)

| Tool `type` | What it does | Required fields |
|---|---|---|
| `end_call` | Hang up when done | name |
| `transfer_call` | Cold, warm, or agentic-warm transfer to a human | name, `transfer_destination`, `transfer_option` |
| `bridge_transfer` / `cancel_transfer` | Used by transfer agents in warm transfers | name |
| `agent_swap` | Hand the call to another AI agent | name, `agent_id`, `post_call_analysis_setting` |
| `send_sms` | Text the caller or another number mid-call | name, `sms_content` — needs an SMS-capable number (§4) |
| `press_digit` | Navigate an IVR (outbound) | name |
| `extract_dynamic_variable` | Capture typed values (text, number, boolean, enum) | name, `variables`, `description` |
| `code` | Run JavaScript in Retell's sandbox, with `fetch()` | name, `code` — max 20,000 characters, 5–60 s timeout (30 s default). **No LLM-supplied arguments and no secrets**. Requests come from IP 35.166.138.221 |
| `custom` | HTTP call to **our** endpoint | name, `url` — see §3b |
| `integration_app` | A tool from a connected provider (§3) | name, `app_id`, `provider`, `app_tool_template_name` |
| `mcp` | Call a remote MCP server's tools | name, `description`; servers listed in `mcps` on the LLM |

Options on most tools: `speak_during_execution`, `speak_after_execution`,
`execution_message_description`, and `response_variables` (JSON path → dynamic variable).

## 3. Integrations (native, no hosting)

Connect once per workspace, then use as `integration_app` tools in any agent.
API: `POST /create-app` (`type`, `provider`, `auth_config`), `/test-app-auth/{id}`,
`GET /list-app-templates`, `/get-app-tool-schema/{id}`. **OAuth providers cannot be connected
through the API** — the spec has no connect-app endpoint, so a person must sign in once on the
dashboard's Integrations page. Limit: 20 apps per provider.

| Provider | Type | What the agent can do | Credential | Connect via |
|---|---|---|---|---|
| Cal.com | Calendar | Check availability, book, list, get, reschedule, and cancel bookings | OAuth **or** API key | API (key) or Dashboard |
| Calendly | Calendar | Check availability, book (**paid Calendly plan only**), list, get, cancel. Availability checks cover 7 days at a time | Personal access token | API |
| GoHighLevel | CRM + calendar | Contacts, tags, opportunities, tasks, notes; book, reschedule, and cancel on its calendars | Private token + Location ID | API |
| HubSpot | CRM | Contacts, deals, companies, tasks, notes, call logging | Private app token | API |
| Salesforce | CRM | Contacts, leads, cases, opportunities, SOQL, tasks | Client ID/secret + instance URL | API |
| Dynamics 365 | CRM | Contacts, tasks, notes, phone-call logs | OAuth | Dashboard |
| Zoho CRM | CRM | Contacts, deals, tasks, notes, calls | OAuth | Dashboard |
| Zendesk | Support | Identify the caller, read/create/update tickets, comments | OAuth + Zendesk URL | Dashboard |
| Google Drive / OneDrive | Knowledge base | Synced files, refreshed every 24 h | OAuth | Dashboard |
| Notion | Knowledge base | Synced pages, refreshed every 24 h | API key | API |

CRM contact sync (two-way field mappings, writing extraction results back to the CRM):
`/get-crm-config`, `/update-crm-config`, `/run-sync-job`.
Testing an integration tool sends a **real** request: lookups read live data, and creates
write real records.

### 3b. Custom function (anything else)
- Retell sends `POST {url}` with body `{name, call, args}`. `call` includes the transcript so far.
  The "args only" option sends a flat body instead.
- The `X-Retell-Signature` header is an HMAC-SHA256 of the body, made with the API key. **Always verify it.**
- Timeout 1 s–10 min (default 2 min); retries are opt-in via `max_retry`.
- `response_variables` map response JSON paths to dynamic variables.
- Retell blocks private and local addresses, so the endpoint must be publicly reachable over HTTPS.

## 4. Phone numbers & telephony

| Capability | Native | How | Notes |
|---|---|---|---|
| Buy a number | Yes | API: `POST /create-phone-number` (`area_code`, `country_code`, `toll_free`, `number_provider`, `inbound_agents`, `fallback_number`, `inbound_webhook_url`, `nickname`) | US/CA only. Twilio US or CA $2/mo, toll-free $5/mo; Telnyx US $2/mo. **Needs a payment method** (and KYC for outbound/SMS) — owner task |
| Bring your own number (SIP) | Yes | API: `POST /import-phone-number` (`phone_number`, `termination_uri`, SIP auth) | Twilio, Telnyx, Vonage, Genesys, Five9, Avaya, Amazon Connect guides. SIP server: `sip:sip.retellai.com` |
| Keep the client's existing number | Partly | Client forwards their line to the Retell number, or ports it to a SIP trunk | Forwarding is the simplest path — the owner does it with their carrier |
| Bind agents / A/B split | Yes | `inbound_agents` / `outbound_agents` (weights summing to 1), optional `agent_version` | |
| Per-call routing and context | Yes | Inbound webhook per number: Retell POSTs `from_number`/`to_number`; we reply with an agent override and dynamic variables, or reject | Needs our endpoint. 10 s timeout, 3 attempts |
| Overflow / backup | Yes | `fallback_number`. Concurrency full for ~40 s → transfer to the fallback. "Backup mode" (dashboard) diverts all new calls | Set to the office line |
| Outbound calls | Yes | `POST /v2/create-phone-call` (`from_number`, `to_number`, `retell_llm_dynamic_variables`) | Campaigns run through the Dialer (DNC scrubbing). Batch calls are deprecated |
| SMS | Partly | Retell Twilio numbers after **A2P 10DLC approval**: business profile (free), brand ($4 low-volume / $45 standard), campaign ($15), then $20/mo per number. **Or** send from an SMS-approved Retell number with no A2P | US only, not toll-free, Telnyx not supported. Registration is an owner task |
| Spam-label protection | Yes | Business profile → verified number / branded caller ID (dashboard) | Matters for outbound only |
| International | Partly | Calls to 15 countries from Retell numbers | Other countries need custom telephony |

## 5. Testing

| Method | API? | Cost | Use for |
|---|---|---|---|
| Simulation test cases | **API**: `/create-test-case-definition` (`name`, `response_engine`, `user_prompt`, `metrics`, `dynamic_variables`, `tool_mocks`) → `/create-batch-test` → `/get-batch-test`, `/v2/list-test-runs` | ~$0.001–0.05 per message (agent model + simulated-user model) + 1 analysis unit per case | Graded, repeatable checks of prompt/flow behaviour. Use `tool_mocks` so tests don't write real bookings |
| LLM Playground | API: `/agent-playground-completion/{agent_id}` | Per message | Single-turn debugging |
| Web call | API: `/v3/create-web-call` returns an access token; talking needs a browser client | Per minute | Real voice, latency, and interruptions |
| Phone call | API: `/v2/create-phone-call` to a test number, or dial in | Per minute | Transfers, DTMF, carrier audio — final check before go-live |
| Call review | API: `GET /v2/get-call/{id}`, `POST /v3/list-calls` | Free | Read transcripts, latency, `disconnection_reason`, extraction results |

## 6. Webhooks & monitoring
- Agent-level `webhook_url` + `webhook_events`: `call_started`, `call_ended`, `call_analyzed`,
  `transcript_updated`, `transfer_*`. Default: started, ended, analyzed.
- Verify with `X-Retell-Signature` (HMAC of the raw body with the API key). Retell also publishes
  IPs for allowlisting.
- Live calls: `/v2/listen-live-call`, `/v2/take-over-live-call`, `PATCH /v2/update-live-call`, `/v2/stop-call`.
- Alert rules, analytics dashboards, and AI QA scoring are dashboard features.

## 7. Compliance
- HIPAA compliant, SOC 2 Type 1 & 2, GDPR. **A signed BAA is required before sending PHI.** It's
  self-serve and free at click-agreements.retellai.com — the owner signs, since it's a legal
  agreement.
- Per agent: `data_storage_setting` (`everything` / `everything_except_pii` /
  `basic_attributes_only`), `data_storage_retention_days` (1 day–2 years), `pii_config`,
  signed recording URLs (`opt_in_signed_url`, `signed_url_expiration_ms`).
- Call-recording consent rules: our job, via the opening line (see the industry docs).

## 8. Limits & billing
- Concurrency: 20 simultaneous calls per workspace on pay-as-you-go. Can be raised; burst
  mode costs extra; inbound capacity can be reserved.
- Billing: prepaid credits with auto-recharge (since 2026-09-30). Calls bill per minute by model
  and voice — see retellai.com/pricing, which isn't in the docs.
- A dynamic opening message has a 10-second minimum charge; long prompts cost extra.
- API keys can be scoped to read or edit per area (Build/Monitor/Deploy). Public keys (domain
  allowlists) are for web widgets.
