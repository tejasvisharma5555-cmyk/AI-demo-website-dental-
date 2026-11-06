---
name: receptionist-cancel-reschedule
description: Receptionist library module for cancelling and rescheduling existing appointments by phone — finding the caller's booking, verifying identity, applying the client's cancellation policy, and moving or cancelling it (native integration first, custom function only if needed). Use inside build-receptionist whenever the client takes appointments.
---

# Cancel and reschedule

## Owner facts needed
These usually come from the brief; anything missing falls back to the industry defaults.
- The cancellation policy: notice required, fees, and the no-show rule.
- Whether the receptionist may cancel at all, or should always offer to reschedule first.

## Pick the path
| Client's system | Path |
|---|---|
| Cal.com | **Native**: `List Bookings` (by email) → `Check Availability` → `Reschedule Booking` / `Cancel Booking` |
| Calendly | **Native**: `List Bookings` → `Cancel Booking`. **No native reschedule**: cancel, then `Book Appointment` the new slot (book first, then cancel, so the caller never loses their spot) |
| GoHighLevel | **Native** reschedule and cancel tools |
| Practice software with an API | **Custom** Vercel functions `find_appointment`, `reschedule_appointment`, `cancel_appointment` |
| No API | **Fallback**: take the request (who, which appointment, new preference), notify staff, tell the caller staff will confirm |

## Finding the booking
- Most systems find bookings by email. Callers don't always remember theirs, so where possible
  look up by **caller phone** (`{{user_number}}`) first — custom function or CRM lookup — and fall
  back to asking for email or name + date.
- Verify identity before discussing the appointment: name + date of birth (healthcare) or
  name + appointment date. Never read out another person's appointment details.

## Prompt section
```
## Cancel or reschedule
- Find their appointment first and confirm it's the right one ("your cleaning on Tuesday at 3?").
- Always offer to reschedule before cancelling.
- Rescheduling: check availability, offer 2–3 options, confirm, then move it. Only say it's done once the tool succeeds.
- Cancelling: if inside {{cancellation_notice}}, mention the policy kindly ({{cancellation_policy}}). Confirm, then cancel.
- If you can't find the appointment, take their details for staff to follow up.
```

## Tools
- Lookup, reschedule, and cancel tools, with `response_variables` for the booking UID.
- `send_sms` confirmation of the new time or the cancellation.

## Edge cases
- Several upcoming bookings → list them briefly and ask which one.
- A same-day cancellation for a healthcare client → also offer a waitlist or callback.
- The caller wants to cancel all future appointments → staff handover (transfer or message).

## Required test cases
1. Reschedule to a new slot.
2. Cancel with the policy mentioned (inside the notice window).
3. Booking not found → message taken.
4. Several bookings → the right one is chosen.
5. Identity mismatch → no details disclosed.

## Post-call fields
`action` (rescheduled / cancelled / request_taken), `old_time`, `new_time`, `late_cancellation` (bool).
