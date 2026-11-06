---
name: receptionist-transfer
description: Receptionist library module for transferring calls to a human — who gets transferred, to which number, cold vs. warm transfer, and what happens when nobody answers. Uses the platform's native transfer tool. Use inside build-receptionist whenever the client has staff to hand calls to.
---

# Transfer to a human

## Owner facts needed
These come from the brief; there are no safe defaults for these numbers.
- Which number(s) to transfer to, and for what. For example: front desk for billing, the
  doctor's mobile for emergencies, the manager for complaints.
- When transfers are allowed (business hours only?). Outside them → the **after-hours** module.

## Native tool (Retell `transfer_call`)
- One tool per destination. Use a descriptive name and a description saying exactly when to use it:
  ```json
  {"type":"transfer_call","name":"transfer_front_desk",
   "description":"Transfer when the caller asks for a person, has a billing dispute, or is upset and wants staff.",
   "transfer_destination":{"type":"predefined","number":"{{front_desk_number}}"},
   "transfer_option":{"type":"warm_transfer", ...}}
  ```
- **Warm transfer** (default for receptionists): the agent briefs the staff member before
  connecting, so staff know who's calling and why. Use **cold transfer** only when the owner
  wants it or the destination is an automated line. Use **agentic warm transfer** when staff need
  a spoken summary and the chance to decline.
- Use a Retell Twilio number so the caller's ID can show to staff (`show_transferee_as_caller`).
- Put numbers in dynamic variables (`default_dynamic_variables`) so they can change without a
  prompt edit. Extension → `extension` field.
- If the destination is chosen by rules (location or time), use `inferred` with a short prompt,
  or set the number from the inbound webhook.

## Prompt section
```
## Transfers
- Transfer when: {{transfer_rules}}.
- Before transferring, say who you're connecting them to and why.
- If the transfer fails or nobody answers, apologise, take a message (name, number, reason), and say someone will call back {{callback_promise}}.
- Don't transfer for questions you can answer yourself, and don't transfer sales or spam calls.
```

## Failure handling
- Set the transfer ring time sensibly (~20–30 s) so callers don't wait forever.
- On failure → the **lead-capture** message flow, marked `urgency` from the reason.
- Emergencies that need 911/000/112 → tell the caller to hang up and dial it. Never transfer
  instead of that.

## Required test cases (simulation + one real phone test)
1. The caller asks for a person → transferred to the right destination.
2. A billing question → the billing destination.
3. Transfer fails (mocked) → a message is taken.
4. A question the agent can answer → no unnecessary transfer.
5. Phone test: a real transfer connects, and staff hear the warm-transfer briefing.

## Post-call fields
`transferred` (bool), `transfer_destination`, `transfer_reason`, `transfer_failed` (bool).
