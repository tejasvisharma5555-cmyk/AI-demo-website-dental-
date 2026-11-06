---
name: receptionist-lead-capture
description: Receptionist library module for capturing new-customer leads and messages — collecting name, contact details, and need, then delivering them to the owner (native CRM first, SMS/email via custom function otherwise). Use inside build-receptionist for every client; it's also the fallback whenever booking or transfer isn't possible.
---

# Lead capture and messages

## Owner facts needed
These usually come from the brief; anything missing falls back to the defaults.
- Where leads and messages should go: their CRM by product name, an email address, or a mobile
  number for texts.
- How fast they promise a callback. Default: "within one business day".

## What to collect
- Always: name, callback number (default to `{{user_number}}`, confirm it), reason for calling,
  and the best time to call back.
- By industry: from `docs/industries/<type>.md` (e.g. dental: new or existing patient,
  insurance; home services: address, job type, urgency).
- Keep it to the minimum. For healthcare, no detailed medical history over the phone.

## Pick the delivery path
| Destination | Path |
|---|---|
| HubSpot / Salesforce / GoHighLevel / Zoho / Dynamics / Zendesk | **Native**: create a contact/lead + note or task tool during or after the call (`post_session_tools`) |
| Owner's mobile (text) | **Native** `send_sms` to the owner's number, or a post-call SMS step. Needs an SMS-capable number |
| Email / Slack / spreadsheet / anything else | **Custom**: Vercel function triggered by the `call_analyzed` webhook (or a post-call HTTP step) that sends the summary |

Prefer **post-call delivery** (after the call ends) built from the post-call extraction, so the
caller never waits on a tool and the message includes the full summary.

## Prompt section
```
## Taking a message or new enquiry
- Get their name, the best number to reach them (confirm the number they're calling from), and what they need.
- Read the number back digit by digit.
- Tell them {{callback_promise}}. Don't promise a specific person or time unless you know it.
- Before ending, ask "Is there anything else you'd like me to pass on?"
```

## Tools
- `extract_dynamic_variable` (or post-call extraction) for: `caller_name`, `callback_number`,
  `reason`, `best_time`, plus industry fields.
- The delivery step from the table above.

## Edge cases
- The caller refuses to give a number → use the caller ID and flag it.
- A spam or sales call → no lead is created. Mark it `spam` in post-call.
- An urgent issue → hand off to the **transfer** or **after-hours** module instead of just a message.

## Required test cases
1. A new enquiry is captured with all fields.
2. The caller gives a different callback number → the new number is used.
3. A sales call is not logged as a lead.
4. The delivery tool is mocked and called with the correct summary.

## Post-call fields
`lead` (bool), `caller_name`, `callback_number`, `reason`, `best_time`, `urgency` (low / normal / urgent), `spam` (bool).
