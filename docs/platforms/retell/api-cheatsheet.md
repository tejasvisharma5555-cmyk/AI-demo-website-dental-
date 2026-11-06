Last verified: 2026-11-06

# Retell — API cheatsheet

All calls use `https://api.retellai.com` and `-H "Authorization: Bearer $RETELL_API_KEY"`.
The full spec is at https://docs.retellai.com/openapi.yaml — check it for every field.

## Build
| Task | Call | Minimal body |
|---|---|---|
| Knowledge base | `POST /create-knowledge-base` (multipart) | `knowledge_base_name`, `knowledge_base_texts` / `_urls` / `_files` |
| Add KB sources | `POST /add-knowledge-base-sources/{kb_id}` (multipart) | same as above |
| Prompt engine | `POST /create-retell-llm` | `{"general_prompt":"...","begin_message":"...","model_config":{"type":"cascading","primary":{"model":"<model>","tier":"fast"}},"knowledge_base_ids":[...],"general_tools":[...]}` |
| Agent | `POST /create-agent` | `{"response_engine":{"type":"retell-llm","llm_id":"..."},"voice_id":"...","agent_name":"...","language":"en-US","timezone":"America/New_York"}` |
| Update | `PATCH /update-retell-llm/{id}`, `PATCH /update-agent/{id}` | changed fields only |
| Voices | `GET /list-voices`, `GET /get-voice/{id}` | — |
| Integration app | `POST /create-app` | `{"type":"calendar","provider":"...","auth_config":{...}}` (API-key providers only) |
| App tools | `GET /list-app-templates`, `POST /get-app-tool-schema/{app_id}` | — |
| Publish | `POST /create-agent-version/{id}`, `POST /publish-agent-version/{id}` | — |

## Test
| Task | Call |
|---|---|
| Test case | `POST /create-test-case-definition` — `name`, `response_engine`, `user_prompt`, `metrics` (+ `tool_mocks`, `dynamic_variables`) |
| Run batch | `POST /create-batch-test` — `test_case_definition_ids`, `response_engine` |
| Results | `GET /get-batch-test/{id}`, `GET /v2/list-test-runs/{batch_id}`, `GET /get-test-run/{id}` |
| Web call | `POST /v3/create-web-call` — `agent_id` |
| Phone call | `POST /v2/create-phone-call` — `from_number`, `to_number` |

## Deploy
| Task | Call |
|---|---|
| Buy number | `POST /create-phone-number` — `{"area_code":212,"number_provider":"twilio","inbound_agents":[{"agent_id":"...","weight":1}],"fallback_number":"+1...","nickname":"..."}` |
| Import number | `POST /import-phone-number` — `phone_number`, `termination_uri` |
| Rebind | `PATCH /update-phone-number/{e164}` |
| List numbers | `GET /v2/list-phone-numbers` |

## Monitor
| Task | Call |
|---|---|
| Calls | `POST /v3/list-calls`, `GET /v2/get-call/{id}` |
| Concurrency | `GET /get-concurrency` |
| Agents | `POST /v2/list-agents` (body `{}` or `filter_criteria`) |
| Key check | `GET /get-api-key-info` |
