# Retell AI (voice platform)

Last verified: 2026-11-06
Sources: https://docs.retellai.com (API reference pages and deprecation notices)

## Basics
- Base URL: `https://api.retellai.com`
- Auth header: `Authorization: Bearer $RETELL_API_KEY` (key from `.env`)
- JSON bodies: `Content-Type: application/json`
- Key test (read-only): `POST /v2/list-agents?limit=1` with body `{}` → `200` and `{"items":[...],"has_more":...}`. A bad key returns `401`.

## How a receptionist is put together
1. Create the brain: `POST /create-retell-llm` → `llm_id`. Body uses `general_prompt`, `begin_message`, `general_tools`, `default_dynamic_variables`, `knowledge_base_ids`, `model_config`.
2. Pick a voice: `GET /list-voices` → array of voices (`voice_id`, `voice_name`, `provider`, `gender`).
3. Create the agent: `POST /create-agent` with `response_engine: {"type":"retell-llm","llm_id":"..."}` and `voice_id` → `agent_id`.
4. Test in the browser: `POST /v3/create-web-call` with `agent_id` → `call_id`, `access_token`.
5. Put it on a phone number: the phone-number endpoints (see below).

## Endpoints (verified)
| Purpose | Method + path |
|---|---|
| List agents | `POST /v2/list-agents` (query `limit` ≤1000, `sort_order`, `pagination_key`; body `filter_criteria` optional, e.g. `channel` eq `voice`) |
| Create agent | `POST /create-agent` (required: `response_engine`, `voice_id`) |
| Create Retell LLM | `POST /create-retell-llm` |
| List voices | `GET /list-voices` |
| Outbound phone call | `POST /v2/create-phone-call` (required: `from_number`, `to_number`, E.164) |
| Web call | `POST /v3/create-web-call` (required: `agent_id`) |
| List calls | `POST /v3/list-calls` |
| List phone numbers | `GET /v2/list-phone-numbers` |

List endpoints return `items`, `has_more`, `pagination_key`. Pass `pagination_key` back while `has_more` is true.

## Not yet verified (read the page before using)
`get-agent`, `update-agent`, `create-phone-number` (buy), `import-phone-number`, `update-phone-number`, `get-call`, and the request body for `v3/list-calls`.

## Retired endpoints — do not use
- `GET /list-agents`, `GET /list-chat-agents` → removed 2026-07-31; returns `400 "Deprecated API usage is no longer supported"`. Use `POST /v2/list-agents`.
- Removed 2026-06-15: `GET /list-phone-numbers`, `GET /list-retell-llms`, `GET /list-conversation-flows`, `POST /v2/list-calls`, `GET /list-chat` → use the `/v2/` or `/v3/` versions.
- Fields removed 2026-06-15: `analysis_summary_prompt`, `analysis_successful_prompt`, `analysis_user_sentiment_prompt` → use `post_call_analysis_data` with `type: "system-presets"`.
- On the Retell LLM body, `model`, `s2s_model`, `model_temperature`, `states`, `backup_model` are deprecated → use `model_config`.

## Upcoming changes to watch
- 2026-12-15: multi-prompt agent change.
- 2027-01-31: legacy model fields retired.

## Gotchas
- Retell-purchased numbers can only place outbound calls to US numbers.
