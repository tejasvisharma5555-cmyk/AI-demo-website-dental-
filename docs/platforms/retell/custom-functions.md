# Where Retell needs a custom function

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

Native first; custom only for these gaps.

| Gap | Typical client | Our approach |
|---|---|---|
| Booking into Google Calendar, Outlook, Acuity, Square | Most small businesses | `custom` tool → our endpoint (availability + book), or move client to Cal.com (native) |
| Practice/industry software (dental PMS like Dentrix/Open Dental/Eaglesoft, medical EHR, legal, salon) | Dental, medical, legal, salons | `custom` tool → our endpoint calling the vendor API |
| Email to owner/staff after each call | Almost every client | Agent `webhook_url`, event `call_analyzed` → our endpoint sends email with summary + extracted fields |
| CRM not in catalog | Varies | `custom` tool or `mcp` tool |
| Payments / deposits | Service businesses | `custom` tool creating a payment link, sent by SMS. Never take card numbers by voice |
| Per-caller routing/context from client data | Repeat-caller businesses | Number `inbound_webhook_url` → our endpoint |
| Lookups needing secrets | Any | `custom` tool (code tool can't hold secrets) |

Middle ground with no hosting: the `code` tool runs JS with `fetch()` in
Retell's sandbox. Use only for logic or public APIs without secrets.

## Spec for our endpoints
- Request: `POST` JSON `{"name","call","args"}` (or just args if
  `args_at_root: true`). `call` includes the live transcript and dynamic variables.
- Header `X-Retell-Signature`: HMAC-SHA256 of the **raw** body, verify with
  the Retell API key (SDK `Retell.verify(rawBody, apiKey, signature)`). Reject
  invalid with 401. GET/DELETE: verify against empty string.
- Response: any 2xx. Body is stringified for the LLM, capped at 15,000 chars.
  Only a JSON object can fill `response_variables`.
- URL must be public HTTPS; Retell blocks localhost/private IPs.
- Set `timeout_ms` ~10,000 for in-call tools; callers won't wait 2 minutes.
- Webhooks (`webhook_url`) use the same signature scheme; events:
  `call_started`, `call_ended`, `call_analyzed` (+ chat equivalents).
