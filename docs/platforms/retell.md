# Retell (voice)

Last verified: 2026-11-06
Sources: live API calls from this repo; docs.retellai.com not reachable from
the build environment (network policy), so endpoint notes below come from
direct testing.

## Auth
- Base URL: `https://api.retellai.com`
- Header: `Authorization: Bearer $RETELL_API_KEY` (key from `.env`)
- Keys look like `key_...`

## Key test
- `GET /list-voices` → 200, JSON array of voices (349 on 2026-11-06).
  Each item: `voice_id`, `voice_name`, `provider`, `gender`, `voice_type`,
  `preview_audio_url`.
- An invalid key on the same endpoint returns 401, so a 200
  means the key is valid.

## Gotchas
- `GET /list-agents` (legacy) returns **400**: "Deprecated API usage is no
  longer supported: Legacy agent list endpoints" (deprecated 2026-07-31).
  Replacement endpoint not yet confirmed; check
  https://docs.retellai.com/deprecation-notice/2026/07-31_agent_list_endpoints
  before building agent-listing logic.
- Cloud build environment must allow `api.retellai.com` (done: environment
  `ai-demo-website-dental`). `docs.retellai.com` is not allowed yet.
