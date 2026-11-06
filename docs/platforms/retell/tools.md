# Retell built-in tools

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

Tools go in `general_tools` on a Retell LLM (single prompt) or `tools` on a
conversation flow / subagent node. Names: `a-z`, digits, `_`; unique per agent.
Every tool has optional `description`, `speak_during_execution`,
`execution_message_description`, `execution_message_type` (`prompt`|`static_text`).

| `type` | Purpose | Required fields |
|---|---|---|
| `end_call` | Hang up | `name` |
| `transfer_call` | Route to human/number | `name`, `transfer_destination`, `transfer_option` |
| `send_sms` | Text during call | `name`, `sms_content` (sender defaults to agent number, destination to caller) |
| `press_digit` | Send DTMF | `name` |
| `extract_dynamic_variable` | Save values from conversation | `name`, `description`, `variables` |
| `agent_swap` | Hand to another AI agent | `name`, `agent_id`, `post_call_analysis_setting` |
| `integration_app` | Native integration action | `name`, `app_id`, `provider`, `app_tool_template_name` |
| `custom` | Call our HTTP endpoint | `name`, `url` (+ `parameters` JSON schema) |
| `code` | Run JS in Retell sandbox | `name`, `code` |
| `mcp` | Call a remote MCP server tool | `name`, `description` (+ `mcp_id`; servers in LLM `mcps`) |

Removed: `check_availability_cal`, `book_appointment_cal` (use `integration_app` with Cal.com).

## Examples

```json
{"type":"end_call","name":"end_call","description":"End the call when the caller is done."}
```

```json
{"type":"transfer_call","name":"transfer_to_front_desk",
 "description":"Transfer when the caller asks for a person or has an emergency.",
 "transfer_destination":{"type":"predefined","number":"+15555550123"},
 "transfer_option":{"type":"cold_transfer","cold_transfer_mode":"sip_invite"}}
```
- `transfer_destination`: `{"type":"predefined","number":"+1...","extension"?}` or
  `{"type":"inferred","prompt":"..."}` (LLM picks the number).
- `transfer_option.type`: `cold_transfer` | `warm_transfer` | `agentic_warm_transfer`.
  Cold needs explicit `cold_transfer_mode`: `sip_invite` (default choice, works on
  Retell numbers) or `sip_refer` (carrier must support REFER). Optional
  `on_hold_music`, `transfer_ring_duration_ms`, `show_transferee_as_caller`.

```json
{"type":"custom","name":"book_appointment","url":"https://<our-endpoint>/book",
 "method":"POST","description":"Book once the caller confirms date, time, name, phone.",
 "parameters":{"type":"object","properties":{
   "start_time":{"type":"string","description":"ISO 8601 start time"},
   "name":{"type":"string","description":"Caller full name"}},
  "required":["start_time","name"]},
 "speak_during_execution":true,"execution_message_description":"Let me book that for you.",
 "timeout_ms":10000}
```

## Other custom/code fields worth knowing
- `custom`: `headers`, `query_params` (never LLM-filled), `response_variables`
  (dot paths → dynamic variables), `args_at_root`, `max_retry` (0–5),
  `timeout_ms` (1,000–600,000, default 120,000), async mode, `enable_typing_sound`.
- `code`: no LLM-supplied params (reads dynamic variables + metadata only),
  default timeout 30 s, `fetch()` available. **No secrets** in code tool.
