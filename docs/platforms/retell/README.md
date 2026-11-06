# Retell (voice)

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

Retell hosts the whole receptionist: speech-to-text, LLM, voice, telephony,
tools, knowledge base, testing, and analytics. We configure it entirely over
its REST API.

## Auth
- Base URL: `https://api.retellai.com`
- Header: `Authorization: Bearer $RETELL_API_KEY` (from `.env`)
- Key test: `GET /get-api-key-info` → 200 with org name and key name.
  Bad key → 401.
- Network hosts needed: `api.retellai.com` (API), `docs.retellai.com` (docs).

## Build order for a receptionist (all via API)
1. **Knowledge base** (optional): `POST /create-knowledge-base` (multipart:
   `knowledge_base_texts`, `knowledge_base_urls`, files; `enable_auto_refresh`
   for URLs). Website URL of the client is the usual source.
2. **Integrations** (if any): `POST /create-app` for API-key providers;
   OAuth providers need the owner to connect in the dashboard. See
   [integrations.md](integrations.md).
3. **Response engine**: `POST /create-retell-llm` with `general_prompt`,
   `begin_message`, `model_config`, `general_tools`, `knowledge_base_ids`,
   `default_dynamic_variables`. Single prompt is the default choice; use
   `POST /create-conversation-flow` only when the call must follow strict steps.
   **Never create multi-prompt (states) agents**: deprecated, see
   [deprecations.md](deprecations.md).
4. **Agent**: `POST /create-agent` with `response_engine`
   (`{"type":"retell-llm","llm_id":...}` or `{"type":"conversation-flow",...}`)
   and `voice_id` (from `GET /list-voices`). Set `language`, `timezone`,
   `webhook_url`, `post_call_analysis_data`, `end_call_after_silence_ms`,
   `max_call_duration_ms`, `voicemail_option`, `data_storage_setting`.
5. **Publish**: `POST /publish-agent-version/{agent_id}`. Drafts via
   `POST /create-agent-version/{agent_id}`; list with `GET /list-agent-versions/{agent_id}`.
6. **Test**: text simulation first, then a web call. See [testing.md](testing.md).
7. **Phone number**: buy (`POST /create-phone-number`) or import
   (`POST /import-phone-number`), then bind with `inbound_agents`.
   See [phone-numbers.md](phone-numbers.md).

## Files
- [capabilities.md](capabilities.md): native vs custom, at a glance. Start here.
- [tools.md](tools.md): built-in tool types and JSON shapes.
- [integrations.md](integrations.md): native CRM/calendar/helpdesk/KB providers.
- [phone-numbers.md](phone-numbers.md): buy, import, bind, webhook, SMS.
- [testing.md](testing.md): test methods, APIs, costs, default test plan.
- [custom-functions.md](custom-functions.md): gaps we must build ourselves.
- [deprecations.md](deprecations.md): removed and upcoming changes. Check before every build.
- `_source/`: llms.txt snapshot + fingerprint for change detection.

## API conventions
- List endpoints are versioned: `POST /v2/list-agents`, `GET /v2/list-phone-numbers`,
  `GET /v2/list-retell-llms`, `GET /v2/list-conversation-flows`, `POST /v3/list-calls`,
  `POST /v3/list-chats`. Paginated responses are `{"items":[...],"has_more":bool}`.
  Unversioned `GET /list-voices`, `GET /list-knowledge-bases` return plain arrays.
- Calls: `POST /v2/create-phone-call`, `POST /v3/create-web-call`, `GET /v2/get-call/{id}`.
- Updates are `PATCH` and partial.
- Official SDKs exist (TypeScript `retell-sdk`, Python `retell-sdk`), but we use REST.
  The SDK's `verify()` helper is still the easiest way to check webhook signatures.
