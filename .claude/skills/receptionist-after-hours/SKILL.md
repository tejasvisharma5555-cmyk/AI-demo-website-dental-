---
name: receptionist-after-hours
description: Receptionist library module for after-hours, weekend, and holiday calls — knowing whether the business is open, handling true emergencies, taking messages, and still booking where possible. Use inside build-receptionist for every client.
---

# After-hours

## Owner facts needed
These come from the brief; anything missing falls back to the defaults.
- Opening hours for each day, plus holiday closures.
- What counts as an emergency for this business, and what to do: an on-call number, an urgent
  care / ER referral, or a message only.
- Whether to book after hours (default: **yes** if booking is automated — it's the main
  after-hours win).

## Knowing if the business is open
- Give the agent the current local time: set `timezone` on the agent. Retell's system variables
  `{{current_time}}`, `{{current_hour}}`, and `{{current_calendar}}` (14 days) use it automatically.
  `{{system_timezone}}` can override it per call.
- **Simple fixed hours** → put the weekly hours in the prompt and let the agent compare them to
  `{{current_time}}`. That's native, with no function.
- **Holidays or irregular hours** → don't trust the LLM to work them out. Use the inbound
  webhook (custom Vercel function) that sets `{{is_open}}`, `{{todays_hours}}`, and
  `{{next_open}}` per call from a schedule file in `clients/<slug>/functions/`. The owner edits
  holidays by telling us; we redeploy.

## Emergency handling
- Life-threatening → tell the caller to hang up and call the emergency number. Always first.
- Urgent but not life-threatening (e.g. dental: swelling, severe pain, knocked-out tooth):
  - **On-call number** → `transfer_call` to it (a fixed number, or one returned by a custom
    function if the rotation changes).
  - **No on-call** → give the owner-approved advice line only (e.g. "go to the nearest urgent
    care"), take an urgent message, and alert the owner straight away (`send_sms` to their
    mobile, or the lead-capture delivery marked urgent).
- Use the urgency triggers from `docs/industries/<type>.md`. Never diagnose.

## Prompt section
```
## When we're closed
- We're open {{hours}}. Right now it's {{current_time}}. (If {{is_open}} is set, trust it over your own reading of the hours.)
- When closed: say so kindly with today's/next opening time, then still help — book, reschedule, answer questions, or take a message.
- Emergencies: {{emergency_rules}}. If life-threatening, tell them to hang up and call {{emergency_number}}.
- Don't transfer to the office line when it's closed.
```

## Tools
- After hours, transfers go only to the on-call number. Disable office transfers via the
  `{{is_open}}` rules or the prompt.
- `send_sms` to the owner for urgent messages.
- An optional inbound webhook function (above).

## Required test cases (set `current_time` / `is_open` through dynamic variables)
1. Closed, routine call → tells them the hours, offers booking or a message.
2. Closed, urgent → on-call transfer, or an urgent message + owner alert.
3. Closed, life-threatening → tells them to call the emergency number.
4. On a holiday → treated as closed.
5. Open → no after-hours messaging.

## Post-call fields
`after_hours` (bool), `emergency` (none / urgent / life_threatening), `owner_alerted` (bool).
