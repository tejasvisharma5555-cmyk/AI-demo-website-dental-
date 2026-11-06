# Retell native integrations

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

An integration is an **App** (a workspace connection). Create it once, then
add its tools to any agent as `integration_app` tools.

## API
- Catalog (providers + tool templates): `GET /list-app-templates`
- Create connection: `POST /create-app` with `type`, `provider`, `name`,
  `auth_config` (API-key providers), `tenant_url` / `tenant_id` where needed.
  OAuth providers **reject** `auth_config` and must be connected by the owner in
  the dashboard (Integrations page); no connect endpoint in the public API.
- Check creds: `POST /test-app-auth/{app_id}`; list: `GET /list-apps`.
- Resolve a tool's inputs: `POST /get-app-tool-schema/{app_id}` (multi-round,
  repeat until `complete`).
- Up to 20 apps per provider. Credentials are stored encrypted, never returned.
- Tool calls time out after 3–14 s; on failure the agent keeps talking, so
  the prompt must say what to do when a lookup/booking fails.
- Testing a create/update tool writes **real** records.

## Providers (live catalog, 2026-11-06)

| Provider (`provider`) | Type | Auth | Connect via API? | Tool templates |
|---|---|---|---|---|
| `calcom` | calendar | api_key or OAuth | Yes (API key) | check_calcom_availability, book_calcom_appointment, list_calcom_bookings, get_calcom_booking, reschedule_calcom_booking, cancel_calcom_booking |
| `calendly` | calendar | api_key | Yes | check_calendly_availability, book_calendly_appointment, list_calendly_bookings, get_calendly_booking, cancel_calendly_booking |
| `gohighlevel` | crm (+calendar) | api_key + Location ID (`tenant_id`) | Yes | contacts, tags, opportunities, tasks, notes, check_ghl_availability, book/get/reschedule/cancel_ghl_appointment (18 total) |
| `hubspot` | crm | api_key (private app token) | Yes | search/get/create/update contact, deals, companies, tasks, create_hubspot_note, log_hubspot_call (14) |
| `salesforce` | crm | OAuth (client ID/secret + instance URL) | Dashboard | contacts, leads, accounts, opportunities, cases, tasks, notes, custom objects, SOQL (18) |
| `microsoft_dynamics` | crm | OAuth | Dashboard | contacts, phone call log, notes, tasks (7) |
| `zoho` | crm | OAuth | Dashboard | contacts, deals, tasks, notes, log_zoho_call (8) |
| `zendesk` | support | OAuth + Zendesk URL | Dashboard | users, tickets, comments (7) |
| `notion` | knowledge_base | api_key | Yes | none (KB sync only) |
| `google_drive` | knowledge_base | OAuth | Dashboard | none (KB sync only) |
| `microsoft_onedrive` | knowledge_base | OAuth | Dashboard | none (KB sync only) |

**Not native** (needs a custom function): Google Calendar, Outlook/Microsoft
365 calendar, Acuity, Square, practice-management systems (dental, medical,
legal), email, payments.

## CRM extras
CRM connections can also sync contacts into Retell and write post-call
extraction results back (`GET/POST /get-crm-config`, `/update-crm-config`,
`/run-sync-job`). Only one CRM can drive contact sync per workspace.
