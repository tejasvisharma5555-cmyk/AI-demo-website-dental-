# Research — Luxe Hair Salon

Last updated: 2026-11-06. Industry background: `docs/industries/hair-salon.md`.
Platform: Retell (`docs/platforms/retell/`; docs unchanged since 2026-11-06).

## The business
| Fact | Status |
|---|---|
| Name: Luxe Hair Salon | **Found** (owner) |
| Location: Huntington, NY (Long Island), timezone America/New_York | **Found** (owner) |
| Functions wanted: book, cancel/reschedule, answer questions (hours, pricing, services), after-hours messages | **Found** (owner) |
| Booking system: Cal.com (key provided) | **Found** (owner) |
| Website, address, phone | **Not found.** No verified listing for "Luxe Hair Salon, Huntington NY" on the web. A site at luxehairsalon.vercel.app mentions free consultations, vegan-friendly colour, and 15 years in business, but shows no address and couldn't be fetched here. Unconfirmed that it's this salon → **ask** |
| Services, prices, durations | Not found → **ask** |
| Hours | Not found → **ask** (Cal.com has a schedule, but it's named for a different salon — see below) |
| Stylists | Not found → **ask** |
| Cancellation / deposit / late policy | Not found → **ask** |

## What the Cal.com account shows (read via API, 2026-11-06)
- Key works (`GET /v2/me` → 200). Account "DIALPILOT AI", username `dialpilot`.
- **Profile timezone is Asia/Kolkata.** The salon is in New York. Booking times follow the
  event's schedule (New York), but confirmation emails may show India time → fix during the
  build (set the profile or event timezone to America/New_York).
- **One event type only:** "15 min meeting" (15 min, Cal Video, $0). No salon services yet →
  the build creates one event type per service group.
- **One schedule: "avant garde salon Florida"** (America/New_York): Sun–Mon 10–6, Tue 9–7,
  Wed–Fri 9–8, Sat 8–7. It looks like another salon's hours. If this account is shared with
  other clients, their bookings would block Luxe's slots → **ask** whether the account is
  Luxe-only.
- Required booking fields: name, email (plus optional notes) → the agent must collect an email.

## What's already done
- Cal.com is connected to Retell as a native integration: app `app_e7c5b5d3ef6dc166798af57f`.
  The auth test passed (`deploy/retell/calcom-app.json`).

## Decisions (technical — ours)
- **Booking, cancel, reschedule:** all native through Retell's Cal.com tools. No custom code.
  - One Cal.com event type per service group, each with its true length, all on a "Luxe Hair
    Salon" schedule in New York time.
  - The agent maps the caller's service to the right event type.
- **Finding existing bookings:** Cal.com finds bookings by email → the agent asks for the
  email used at booking and spells it back. If it's not found → take a message for the salon.
- **FAQ:** knowledge base built from the owner's menu, prices, and policies. Critical facts
  (hours, address) also go in the prompt. Prices are said as "starting at" unless fixed.
- **After hours:** Retell's `{{current_time}}` (New York) + hours in the prompt. The agent
  still books, reschedules, and cancels after hours, and takes messages for everything else.
  - Message delivery depends on the owner's answer: a **text** (native `send_sms` from an
    SMS-approved Retell number — no carrier registration needed) or an **email** (small Vercel
    function on Retell's call-analyzed webhook).
- **Recording disclosure:** the opening line names the AI assistant and says the call may be
  recorded (NY safe default).
- **Agent type:** single-prompt Retell LLM, newest fast model (chosen at build time).

## Sources
See `docs/industries/hair-salon.md`. Cal.com facts come from the live API. Web search for the
salon itself: no verified listing (atly.com, bbb.org Huntington directories,
luxehairsalon.vercel.app search result).
