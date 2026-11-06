# Testing on Retell

Last verified: 2026-11-06
Sources: docs.retellai.com/llms.txt, llms-full.txt (349 pages), openapi.yaml; live read-only API calls.

There is **no free sandbox**: tests bill at production rates. Text tests
cost ~$0.001–0.05 per message; voice tests ~$0.07–0.31 per minute
(+ ~$0.015/min telephony on phone tests). Run most checks as text.

| Method | API | Use for |
|---|---|---|
| Playground completion | `POST /agent-playground-completion/{agent_id}` (stateless; send full history, get new messages) | Fast scripted text checks from code |
| Simulation test cases | `POST /create-test-case-definition` (`name`, `response_engine`, `user_prompt`, `metrics`, optional `dynamic_variables`, `tool_mocks`, `llm_model`) | Graded, repeatable scenarios |
| Batch test | `POST /create-batch-test` (`test_case_definition_ids`, `response_engine`) → `GET /get-batch-test/{id}`, `GET /v2/list-test-runs/{batch_id}`, `GET /get-test-run/{id}` | Regression suite after every change |
| Web call | `POST /v3/create-web-call` → access token for a browser client | Hear voice, latency, interruptions |
| Phone call | Call the number / `POST /v2/create-phone-call` | Final check: transfers, DTMF, carrier audio |

Notes:
- Simulation doesn't support custom-LLM agents (we don't use them).
- `tool_mocks` lets us test custom functions without a live endpoint.
- Batch grading adds one analysis unit per case.

## Default receptionist test plan
Create one test case per scenario, run as a batch, log results in
`clients/<slug>/tests.md`:
1. Book an appointment (happy path)
2. Caller wants a time that isn't available
3. Hours / location / parking question (knowledge base)
4. Price or insurance question
5. Emergency / urgent → transfer
6. Asks for a human → transfer
7. Off-topic or abusive caller → polite end
8. Caller gives incomplete info (no phone/name)
9. After-hours call
10. Wrong number / spam
Then one web call to check voice and pacing.
