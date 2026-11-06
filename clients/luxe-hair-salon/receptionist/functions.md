# Functions — Luxe Hair Salon (final, as built)

> **DEMO.** All salon data is fictional demo data.

All functions are **native** — no custom code and no Vercel deployment needed.

| Tool(s) | What it does | Path |
|---|---|---|
| `check_emma` / `check_olivia` / `check_sophia` | Open start times for one stylist; `duration_minutes` = the service length | Native Cal.com integration (`check_calcom_availability`) |
| `book_emma` / `book_olivia` / `book_sophia` | Books a confirmed slot (same `duration_minutes`; service name goes in the notes) | Native Cal.com integration (`book_calcom_appointment`) |
| `find_booking` | The caller's upcoming bookings, found by email | Native Cal.com integration (`list_calcom_bookings`) |
| `reschedule_booking` | Moves a booking to a new time | Native Cal.com integration (`reschedule_calcom_booking`) |
| `cancel_booking` | Cancels a booking | Native Cal.com integration (`cancel_calcom_booking`) |
| `save_message` | Captures name, callback number, reason, and urgency | Native `extract_dynamic_variable` |
| Open/closed logic | Knows when the salon is closed | Native `{{current_time}}` + hours and holidays in the prompt |
| `end_call` | Hangs up | Native |

Every Cal.com tool pins `timezone` = America/New_York.

**Stylist → Cal.com event type (demo), 3 links on schedule 2609729 "Luxe Hair Salon (DEMO)":**

| Stylist | Event type | Lengths (min) → services |
|---|---|---|
| Emma | 7811029 `luxe-demo-emma` | 60 women's cut · 30 men's cut · 45 blowout |
| Olivia | 7811033 `luxe-demo-olivia` | 15 consultation · 90 root touch-up · 120 all-over color · 150 partial highlights · 180 full highlights |
| Sophia | 7811034 `luxe-demo-sophia` | 180 balayage · 30 deep conditioning |

The earlier 10 per-service event types (7810724–7810733) were deleted on 2026-11-06.

**Owner notifications:** none — demo instruction. Messages live in Retell's call history
(post-call fields `message`, `caller_name`, `callback_number`, `urgency`). For a real client
this becomes a native text (`send_sms`) or an email via a Vercel function.

**Fallbacks:**
- A Cal.com error, or no slot available → offer another time, or take a message.
- Booking not found → recheck the email once, then take a message.
