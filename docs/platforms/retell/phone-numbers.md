# Retell phone numbers

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

## Get a number
- **Buy**: `POST /create-phone-number` with `area_code` (US 3-digit),
  `country_code` (US/CA only), `toll_free`, `number_provider` (twilio|telnyx),
  `nickname`, `inbound_agents`. Requires a payment method on the workspace.
  US number $2/month. New numbers may need ~2 min before outbound works (409 + retry-after).
- **Import** (client keeps their carrier): `POST /import-phone-number` with
  `phone_number`, `termination_uri` (Twilio trunks end in `.pstn.twilio.com`),
  optional SIP auth. Guides exist for Twilio, Telnyx, Vonage, Avaya, Genesys,
  Five9, Amazon Connect. Inbound SIP: `sip:sip.retellai.com` (TCP recommended).
- **Simplest path for a client with an existing number**: buy a Retell number
  and have the client forward their line to it. No SIP work.

## Bind agents
`PATCH /update-phone-number/{phone_number}` with
`inbound_agents: [{"agent_id":"...","weight":1}]` (weights sum to 1; several =
A/B split). Also `outbound_agents`, `inbound_sms_agents`, `outbound_sms_agents`.
Old single `inbound_agent_id` fields were removed 2026-03-31.

## Per-number settings
- `inbound_webhook_url`: Retell POSTs before the call connects (10 s timeout,
  3 attempts). Reply with `call_inbound`: `override_agent_id`, `dynamic_variables`,
  `metadata`, `agent_override`, or `reject: true`. Use for caller lookup,
  after-hours routing.
- `fallback_number`: used when concurrency is full (~40 s wait) or when
  `inbound_fallback_enabled` (backup mode) is on.
- `allowed_inbound_country_list` / `allowed_outbound_country_list`.

## SMS
- Only Retell Twilio or custom-telephony numbers, US only, not toll-free.
- A2P 10DLC approval: business profile → brand ($4/$45) → campaign ($15);
  2–3 weeks; then $20/month per number + $0.01/SMS.
- To send during calls without A2P, send from an SMS-approved Retell number.
- Treat SMS as an "Assumed / Couldn't do" item for any build with a deadline.

## Limits
- Concurrency is per workspace (`GET /get-concurrency`); inbound can reserve slots.
- Outbound to 15 countries; numbers only US/CA unless imported.
