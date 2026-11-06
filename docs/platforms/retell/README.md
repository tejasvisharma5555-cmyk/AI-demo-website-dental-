Last verified: 2026-11-06

# Retell (voice platform)

Our default voice platform for AI receptionists. Researched with the
`research-voice-platform` skill from Retell's full docs (349 pages) and its OpenAPI spec.

| File | What's in it |
|---|---|
| [capabilities.md](capabilities.md) | Everything Retell does natively, and how to set each thing up through the API |
| [api-cheatsheet.md](api-cheatsheet.md) | The endpoints we use, by task, with minimal bodies |
| [custom-functions.md](custom-functions.md) | What Retell can't do natively and what to build instead |
| [SOURCE.md](SOURCE.md) | Sources, research date, change-detection fingerprint |

## API basics
- Base URL: `https://api.retellai.com`
- Auth: `Authorization: Bearer $RETELL_API_KEY` on every request (key in `.env`)
- Content type: `application/json` (knowledge-base create/add-sources use `multipart/form-data`)
- Official SDKs, CLI, and MCP server exist; **we use the REST API** (CLAUDE.md rule 7).

## Key test (read-only)
```bash
curl -sS -X POST https://api.retellai.com/v2/list-agents \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```
Expected: HTTP 200 with `{"items": [...], "has_more": false}`.
2026-11-06: HTTP 200, 0 agents in the account.
`GET /get-api-key-info` also exists for checking a key.

## Default receptionist recipe (our choice)
1. **Knowledge base** of the client's FAQ, services, hours, and policies → `POST /create-knowledge-base`.
2. **Response engine**: a single-prompt Retell LLM → `POST /create-retell-llm`, with:
   - `general_prompt`, `begin_message`, `knowledge_base_ids`, and `model_config`
     (`{"type":"cascading","primary":{"model":...,"tier":"fast"},"backup":{...}}`);
   - `general_tools`: `end_call`, `transfer_call` (to staff and urgent lines), and
     `send_sms` (confirmations) if SMS is set up.
   - Booking: an `integration_app` tool if the client uses Cal.com, Calendly, or GoHighLevel;
     otherwise a `custom` function.
   - Switch to a conversation flow only when the call logic is strictly branching.
3. **Agent** → `POST /create-agent` with `response_engine`, `voice_id`, `language`, `timezone`,
   `webhook_url`, `post_call_analysis_data`, `data_storage_setting`, and `boosted_keywords` for
   the client's names and terms.
4. **Test** with saved simulation test cases (`/create-test-case-definition` + `/create-batch-test`),
   then a web call (`/v3/create-web-call`).
5. **Publish** a version → `POST /publish-agent-version/{agent_id}`.
6. **Phone number** → `POST /create-phone-number` (Twilio provider, set `inbound_agents` and
   `fallback_number` = the office line), then a real test call.
7. Healthcare clients: the owner self-signs a BAA **before** any real patient calls. Set
   `data_storage_setting` and retention accordingly.

## Gotchas (from deprecation notices; all already past or upcoming)
- `GET /list-agents` was removed 2026-07-31 → use `POST /v2/list-agents`. Results are in
  `items`; page with `pagination_key` while `has_more` is true.
- Other legacy list endpoints are gone (removed 2026-06-15) → use the `v2`/`v3` versions.
- **Multi-prompt agents**: creation ends 2026-12-15 and editing ends 2027-02-01 → use a
  single-prompt or conversation-flow agent.
- **Model fields**: `model`, `s2s_model`, and `model_choice` are deprecated (2027-01-31) → use
  `model_config.primary` (`{model, tier}`; tier replaces `model_high_priority`/`model_ultrafast`).
- **Phone numbers**: the single-agent fields (`inbound_agent_id` etc.) are deprecated → use the
  weighted lists `inbound_agents` / `outbound_agents` (weights must sum to 1).
- **Built-in Cal.com tools** were removed (2026-10-31) → use the Cal.com integration app.
- **Cal.com app by API key** needs `"tenant_url": "cal.com"` (or `"cal.eu"`). Without it,
  `POST /create-app` returns 400 "Domain must be cal.com or cal.eu". Verified 2026-11-06. A new
  app shows `connection_status: not_connected` until first use; `POST /test-app-auth/{id}`
  returns `{"success": true}` when the key works.
- **Conversation nodes** no longer take tools → use a subagent node.
- **Agent versions**: use `GET /list-agent-versions/{id}` and `POST /publish-agent-version/{id}`.
- **Update Call** only works on ended calls; for live changes use `PATCH /v2/update-live-call`.
- **SIP**: the old endpoint was retired → use `sip:sip.retellai.com`.
- **Web calls**: use `POST /v3/create-web-call`.
