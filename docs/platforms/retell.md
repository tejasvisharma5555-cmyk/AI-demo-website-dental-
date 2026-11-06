Last verified: 2026-11-06

# Retell (voice platform)

Our default voice platform for AI receptionists.

## API basics
- Base URL: `https://api.retellai.com`
- Auth: `Authorization: Bearer $RETELL_API_KEY` on every request (key in `.env`)
- Content type: `application/json`

## Key test (read-only)
```bash
curl -sS -X POST https://api.retellai.com/v2/list-agents \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```
Expected: HTTP 200 with `{"items": [...], "has_more": false}`.
2026-11-06: HTTP 200, 0 agents in the account.

## Gotchas
- `GET /list-agents` and `GET /list-chat-agents` were removed on 2026-07-31.
  They now return HTTP 400 "Deprecated API usage". Use `POST /v2/list-agents`.
  - It returns voice and chat agents together under `items`.
  - To get only one kind, filter in the body:
    `{"filter_criteria": {"channel": {"type": "string", "op": "eq", "value": "voice"}}}`.
  - Pagination: while `has_more` is true, send back the returned `pagination_key`.

## Sources
- https://docs.retellai.com/api-references
- https://docs.retellai.com/deprecation-notice/2026/07-31_agent_list_endpoints
