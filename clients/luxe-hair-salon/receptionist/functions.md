# Functions — Luxe Hair Salon (draft)

| Function | What it does | Path | Notes |
|---|---|---|---|
| `check_availability_<group>` (one per service group) | Open slots for that service | **Native** — Cal.com `check_calcom_availability`, pinned to the group's event type | Event types are created in Cal.com during the build from the owner's menu (Q2) |
| `book_<group>` (one per service group) | Books the confirmed slot | **Native** — Cal.com `book_calcom_appointment` | Inputs from the conversation: name, email, start time; mobile + service + notes go in the booking notes |
| `find_booking` | Finds the caller's upcoming bookings by email | **Native** — Cal.com `list_calcom_bookings` | The booking UID maps to `{{booking_uid}}` |
| `reschedule_booking` | Moves a booking | **Native** — Cal.com `reschedule_calcom_booking` | |
| `cancel_booking` | Cancels a booking | **Native** — Cal.com `cancel_calcom_booking` | |
| `capture_message` | Saves the caller's name, number, reason, urgency, and best time | **Native** — `extract_dynamic_variable` + post-call extraction | |
| `notify_owner` | Sends the message to the owner | **Native** if a text: `send_sms` from an SMS-approved Retell number (no carrier registration). **Custom** if email: a Vercel function on the `call_analyzed` webhook | Decided by Q6 |
| Open/closed check | Knows whether the salon is open | **Native** — `{{current_time}}` (agent timezone America/New_York) + weekly hours in the prompt | Holidays are listed in the prompt |
| `end_call` | Hangs up cleanly | **Native** | |

**Fallbacks**
- Cal.com tool error or timeout → apologise and take a booking request as a message.
- Booking not found by email → take a message.

**Not needed:** call transfer (not requested) and custom booking code (Cal.com covers it).
