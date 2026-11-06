# Retell capability map

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

**Native** = config only via API. **Native, dashboard step** = needs the
owner to click once (OAuth, approvals). **Custom function** = we host an
endpoint (or use the code tool / MCP).

| Receptionist need | Status | How (API) | Notes |
|---|---|---|---|
| Answer calls 24/7 with a prompt | Native | `create-retell-llm` + `create-agent` + bind number | Single prompt default |
| Strict scripted flow | Native | `create-conversation-flow` | Nodes: conversation, subagent, function, code, logic split, transfer, SMS, end |
| Answer FAQs from website/docs | Native | `create-knowledge-base` → `knowledge_base_ids` on LLM | URL sources can auto-refresh |
| FAQs from Google Drive / OneDrive / Notion | Native, dashboard step | OAuth connect (Drive/OneDrive); Notion via API key | KB sync only, no tools |
| Transfer to a human | Native | `transfer_call` tool | Cold, warm, agentic warm |
| Hang up cleanly | Native | `end_call` tool | |
| Text the caller mid-call | Native, dashboard step | `send_sms` tool | Needs SMS-enabled number (A2P, 2–3 weeks) or SMS-approved Retell number |
| Navigate an IVR (outbound) | Native | `press_digit` tool | |
| Caller presses keys | Native | agent `allow_user_dtmf`, `user_dtmf_options` | |
| Capture caller details into variables | Native | `extract_dynamic_variable` tool | |
| Hand off to another AI agent | Native | `agent_swap` tool | |
| Book on Cal.com / Calendly | Native | `create-app` (API key) + `integration_app` tool | Old `check_availability_cal`/`book_appointment_cal` are removed |
| Book on GoHighLevel calendar | Native | `create-app` (API key + Location ID) | |
| Book on Google Calendar / Outlook / practice software (Dentrix, Open Dental, etc.) | **Custom function** | `custom` tool → our endpoint | Not supported natively |
| Look up / log caller in HubSpot, GoHighLevel | Native | `create-app` (API key) | |
| Salesforce, Dynamics 365, Zoho, Zendesk | Native, dashboard step | OAuth connect, then `integration_app` tools via API | |
| Other CRMs / databases | **Custom function** | `custom` tool or `mcp` tool | |
| Email the owner / staff after a call | **Custom function** | `webhook_url` (`call_analyzed`) → our endpoint sends email | No native email to arbitrary addresses |
| Call summary + structured data | Native | agent `post_call_analysis_data` | Sent in webhook + `get-call` |
| Pre-call caller lookup / post-call CRM update | Native | agent `pre_session_tools` / `post_session_tools` | Integration or custom tools |
| Per-caller context / route to different agent | Native (needs endpoint for dynamic) | number `inbound_webhook_url` | Our endpoint returns overrides |
| After-hours / overflow to a human number | Native | number `fallback_number`, backup mode | |
| Simple calculations, public API lookups | Native | `code` tool (JS, QuickJS sandbox, `fetch`) | No secrets in code tool |
| Take payments | **Custom function** | `custom` tool → payment provider | Watch PCI; prefer sending a payment link by SMS |
| Spanish / multilingual | Native | agent `language` | See supported languages page |
| Automated testing | Native | `create-test-case-definition` + `create-batch-test` | Text only, billed per message |
| Web call test (no phone) | Native | `POST /v3/create-web-call` | Needs browser client to talk |
| Live call monitoring / takeover | Native | `/v2/listen-live-call`, `/v2/take-over-live-call` | |
