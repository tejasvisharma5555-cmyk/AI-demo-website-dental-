# Retell deprecations

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

Check `docs.retellai.com/deprecation-notice/overview` when the fingerprint changes.

## Already removed (don't use)
| Removed | Use instead |
|---|---|
| Legacy list endpoints (`GET /list-agents` etc., 2026-06-15 / 07-31) | `POST /v2/list-agents` and other `/v2`, `/v3` list endpoints |
| Built-in Cal.com tools `check_availability_cal`, `book_appointment_cal` (2026-09-30, migrated 10-31) | Cal.com integration (`integration_app`) |
| Phone number single-agent fields (2026-03-31) | `inbound_agents` / `outbound_agents` arrays with weights |
| Legacy get-agent-versions endpoints (2026-09-15) | `GET /list-agent-versions/{agent_id}` |
| Separate publish endpoints (2026-07-20) | `POST /publish-agent-version/{agent_id}` |
| Update Call on live calls (2026-08-31) | `PATCH /v2/update-live-call/{id}` for live calls |
| Legacy SIP endpoint, legacy browser JS SDK, legacy MCP server (retell.stlmcp.com) | Current SIP URI, v3 web call, current MCP |
| Multilingual as single setting (2026-07-31) | locale array |
| Conversation node tools (2026-04-18) | Subagent node |
| Implicit cold transfer (2026-01-23) | Explicit cold transfer mode |
| ElevenLabs Turbo, older GPT-4.1 nano / Claude Sonnet 4.5 / Gemini Flash / OpenAI Realtime models | Replacement models (see notices) |

## Upcoming
| Date | Change | Our rule |
|---|---|---|
| 2026-12-15 | Multi-prompt agent creation ends; editing ends 2027-02-01 | Build single prompt or conversation flow only |
| 2027-01-31 | Legacy model fields (`model`, etc.) | Use `model_config` on Retell LLM / flows |
