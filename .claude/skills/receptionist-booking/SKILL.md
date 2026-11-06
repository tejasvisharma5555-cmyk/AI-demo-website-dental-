---
name: receptionist-booking
description: Receptionist library module for booking new appointments by phone — checking real availability, collecting the caller's details, confirming, and booking into the client's calendar or practice system (native integration first, custom function only if needed). Use inside build-receptionist whenever the client takes appointments.
---

# Booking

## Owner facts needed
These usually come from the brief; anything missing falls back to the industry defaults.
- Which booking system or calendar they use, by its product name.
- Appointment types, how long each takes, and who can do which.
- How far ahead people can book, and the minimum notice.
- Details staff always collect, e.g. name, phone, DOB, insurance, reason, new or existing.

## Pick the path (build-receptionist §1)
| Client's system | Path |
|---|---|
| Cal.com / Calendly / GoHighLevel calendar | **Native** integration tools: `Check Availability` + `Book Appointment`. One tool pair per appointment type/event type. Calendly booking needs a paid Calendly plan |
| Google / Outlook calendar only | Connect it to Cal.com and go native, **or** a custom function to the calendar API |
| Practice software with an API (e.g. dental PMS) | **Custom** Vercel functions `check_availability` + `book_appointment` |
| No API / no access | **Fallback**: take a booking request (preferred days and times), send an SMS or email to staff, and tell the caller they'll get a confirmation call. Never promise a slot |

## Prompt section
```
## Booking
- Find out the reason for the visit and if they're new or existing, then pick the appointment type.
- Ask for preferred day/time, then call check_availability. Offer at most 2–3 options at a time.
- Collect: {{required_fields}}. Read the phone number back digit by digit.
- Confirm all details in one sentence and wait for a clear "yes" before booking.
- Call book_appointment. Only say it's booked once the tool succeeds.
- If no slot fits, offer the next available, or take a callback request.
- Never give clinical advice or quote prices that aren't in the knowledge base.
```

## Tools
- Availability tool + booking tool (integration or `custom`):
  - set `speak_during_execution` with a filler like "Let me check the schedule.";
  - map `response_variables` for the booking ID / UID (needed for reschedule and cancel).
- `send_sms` confirmation after booking, if SMS is set up.
- Timezone: pass the client's `timezone` and say times in the client's local time.

## Edge cases
- The caller asks for "the soonest" → check from today forward.
- Someone books for another person (parent and child) → collect the patient's details, not the caller's.
- The caller is unsure about their insurance → book anyway, flag it in post-call, and let staff verify.
- The tool fails or times out → apologise, take a callback request, and don't retry more than once.

## Required test cases (with `tool_mocks`)
1. A new caller books the first slot offered.
2. The caller rejects the first options and books a later one.
3. No availability → a callback request is taken.
4. The booking tool errors → graceful fallback.
5. The caller changes a detail at the confirmation step → corrected before booking.

## Post-call fields
`appointment_booked` (bool), `appointment_type`, `appointment_time`, `new_or_existing`, `booking_id`.
