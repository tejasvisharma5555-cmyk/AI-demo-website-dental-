# Functions — Luxe Hair Salon (final, as built)

> **DEMO.** All salon data is fictional demo data.

All functions are **native** — no custom code and no Vercel deployment needed.

| Tool(s) | What it does | Path |
|---|---|---|
| `check_<service>` ×10 | Open start times for one service | Native Cal.com integration (`check_calcom_availability`), pinned to that service's demo event type |
| `book_<service>` ×10 | Books a confirmed slot (name, email, E.164 mobile, notes) | Native Cal.com integration (`book_calcom_appointment`) |
| `find_booking` | The caller's upcoming bookings, found by email | Native Cal.com integration (`list_calcom_bookings`) |
| `reschedule_booking` | Moves a booking to a new time | Native Cal.com integration (`reschedule_calcom_booking`) |
| `cancel_booking` | Cancels a booking | Native Cal.com integration (`cancel_calcom_booking`) |
| `save_message` | Captures name, callback number, reason, and urgency | Native `extract_dynamic_variable` |
| Open/closed logic | Knows when the salon is closed | Native `{{current_time}}` (agent timezone America/New_York) + hours and holidays in the prompt |
| `end_call` | Hangs up | Native |

Every Cal.com tool pins `timezone` = America/New_York.

**Service → Cal.com event type (demo):** see `deploy/calcom/event-types.json`.

| Service | Stylist | Event type ID |
|---|---|---|
| Women's haircut & styling | Emma | 7810724 |
| Men's haircut | Emma | 7810725 |
| Blowout | Emma | 7810726 |
| Root touch-up | Olivia | 7810727 |
| All-over color | Olivia | 7810728 |
| Partial highlights | Olivia | 7810729 |
| Full highlights | Olivia | 7810730 |
| Color consultation | Olivia | 7810731 |
| Balayage | Sophia | 7810732 |
| Deep conditioning | Sophia | 7810733 |

All 10 use the schedule "Luxe Hair Salon (DEMO)", ID 2609729.

**Owner notifications:** none — demo instruction. Messages live in Retell's call history
(post-call fields `message`, `caller_name`, `callback_number`, `urgency`). For a real client
this becomes a native text (`send_sms`) or an email via a Vercel function.

**Fallbacks:**
- A Cal.com error, or no slot available → offer another time, or take a message.
- Booking not found → recheck the email once, then take a message.
