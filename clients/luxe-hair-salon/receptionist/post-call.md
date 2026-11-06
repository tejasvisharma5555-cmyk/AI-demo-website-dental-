# Post-call — Luxe Hair Salon (draft)

**Extraction fields** (`post_call_analysis_data`):

| Field | Type |
|---|---|
| `call_reason` | selector: book / reschedule / cancel / question / message / spam |
| `appointment_booked` | boolean |
| `service` | text |
| `appointment_time` | text |
| `rescheduled_or_cancelled` | selector: rescheduled / cancelled / none |
| `caller_name` | text |
| `callback_number` | text |
| `message` | text |
| `urgency` | selector: normal / urgent |
| `after_hours` | boolean |
| `unanswered_question` | text — feeds back into the knowledge base |

**Owner notification:**
- Sent after every call that has a message, or `urgency = urgent`.
- Goes by text or email (Q6) and contains: name, number, reason, best time, and urgency.
- Bookings, reschedules, and cancellations already show up in Cal.com (with its own emails),
  so no extra notice is sent for those.

**Data storage:** `everything` (not health data). Retention 1 year (assumed).
