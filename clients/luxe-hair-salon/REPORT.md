# Build Report — Luxe Hair Salon

> **DEMO BUILD — fictional business.** Luxe Hair Salon, its stylists (Emma, Olivia, Sophia),
> prices, hours, and policies are all **demo data**. There is no real address, phone number,
> website, staff contact, or customer.

Built 2026-11-06 with: research-voice-platform (change check) → research-business-type →
build-receptionist (library skills: booking, cancel-reschedule, FAQ, lead capture,
after-hours) → validate-receptionist.

## Built
| What | Where | Status |
|---|---|---|
| Receptionist **"Sophia"**, warm upscale salon tone | Retell agent `agent_7dd2e9e07fd10fc34d66dd5efb` "Luxe Hair Salon DEMO - Sophia" | **Published** (version 0) |
| Prompt engine with 25 tools | Retell LLM `llm_80272405ae8a1a3b94f223e76843` | All 25 tools registered ✔ |
| Knowledge base (services, prices, stylists, hours, policies — demo) | `knowledge_base_e67edd453c19686f` | Indexed ✔ |
| Cal.com connection (native, no custom code) | Retell app `app_e7c5b5d3ef6dc166798af57f` | Auth test passed ✔ |
| Demo schedule (Tue–Fri 9–7, Sat 9–6, Sun 10–4, Mon closed, 6 holidays closed) | Cal.com schedule 2609729 "Luxe Hair Salon (DEMO)" — not the account default | Slots verified ✔ |
| 10 demo services, one per specialist stylist | Cal.com event types 7810724–7810733 ("Luxe DEMO · … with Emma/Olivia/Sophia") | Slots verified ✔ |
| Voice-orb test page | `node .claude/skills/validate-receptionist/scripts/test-page/server.mjs luxe-hair-salon` → http://localhost:5173 (shown in the app preview as "luxe-voice-test") | Page works ✔; calls blocked by Retell credits ✗ |
| Phone number | — | **Not purchased** (demo instruction) |

**What Sophia handles:**
- **Answering questions:** hours, prices, services, stylists, and policies.
- **Booking:** checks real availability and books one of the 10 services, with stylist requests
  sent to the right specialist.
- **Changing bookings:** finds a booking by email, reschedules or cancels it, and mentions the
  24-hour note (no fee).
- **New colour clients:** recommends the free consultation before a big colour change.
- **After hours:** says the salon is closed, but still books and changes appointments.
- **Messages:** takes the caller's name, number, and reason, says the team will follow up
  within one business day, and flags an urgent message for a reaction after a service.

**Not built:** owner notifications (demo instruction). Messages are read in Retell call history.

## Tested
**Structural checks: 8/8 passed** (`deploy/validation.json`): agent exists and is published;
LLM, tools, and model configured; knowledge base ready; Cal.com authenticates. The phone number
is skipped (demo).

**Cal.com:**
- Live slot checks: balayage on Saturday returns starts from 9:00 to 15:00 (the 3-hour service
  ends by 6 PM).
- Monday returns no slots.
- The original "15 min meeting" and Avant Garde schedule are unchanged.

**Simulation, run 1: 9/13 passed** (`deploy/retell/simulation-run-1.json`). Every Cal.com tool
was mocked, so no real bookings were made.

| Result | Tests |
|---|---|
| ✔ Pass | New-client booking; rejected times + corrected email; no availability; booking tool error; reschedule; booking not found; hours/location/parking; prices + unknown question; skin reaction → urgent message |
| ✗ 06 Cancel | The caller pre-declined rescheduling, so Sophia didn't offer it; also my "no fee" check was badly worded. **Fixed:** the prompt now always offers a reschedule; test rewritten |
| ✗ 10, 11 After hours | Sophia handled both correctly (message saved; booking made) but never *said* the salon was closed. **Fixed:** the prompt now requires saying so in the first reply |
| ⚠ 12 Stylist | Sophia was correct (redirected Emma → Olivia, booked, refused to double-book); my simulated caller looped. **Fixed:** test rewritten |

**Run 2 (after fixes): not run** — Retell returned *HTTP 402 "Credit balance exhausted"*. The
published version includes the fixes, but **they are untested** until credits are added.

**Not tested:**
- **A real Cal.com booking through Sophia.** Simulations are mocked; the slot checks and
  connection were live.
- **Voice quality and latency.** No web call was possible without credits.

## Assumed
- **Model:** `claude-5.5-haiku` (newest small, fast Claude model, strong with tools), with backup
  `gemini-3.8-flash` (newest Flash, different provider). Both offer only the *standard* speed
  tier; fast isn't available for either. Retell publishes no per-model latency figures; real
  latency gets measured on the first voice call.
- **Voice:** Retell platform voice "Marissa" (American, female, tuned for phone audio).
- **Booking:** one Cal.com event type per service, named with its specialist stylist. "Next
  available" = the earliest slot for that service. 30-minute start intervals (15 for the
  consultation). 60-minute minimum notice.
- **Booking details:** callers give name, email, and mobile (required by Cal.com) at booking.
  Existing bookings are found by email.
- **Holidays closed:** Thanksgiving 2026-11-26, Christmas 2026-12-25, New Year 2027-01-01,
  Memorial Day 2027-05-31, Independence Day 2027-07-04, Labor Day 2027-09-06. They need adding
  again for later years.
- **Opening line:** discloses the virtual assistant and that the call may be recorded (NY safe
  default).
- **Call data:** stored in full, kept 90 days. Max call 15 min; hang up after 30 s of silence.
- **Unknown topics** (payment methods, gift cards, products, kids' cuts, extensions, weddings):
  "the salon team can confirm", and Sophia offers to take a message.

## Couldn't do
1. **Re-run the simulation and make voice test calls.** Retell credits ran out.

   > **TL;DR: top up Retell so Sophia can take test calls**
   > 1. Open the Retell dashboard → **Billing**.
   > 2. Add credits (a small amount is plenty for a demo; turning on auto-recharge is optional).
   > 3. Reply "done". I'll re-run all 13 tests and you can call Sophia from the orb page.

2. **Separate calendars per stylist.** The Cal.com account is one person's calendar, so Emma,
   Olivia, and Sophia can't be booked at the same hour. Avant Garde bookings on the shared
   account also block Luxe slots. Fine for a demo; a real salon would need Cal.com Teams (one
   member per stylist). No action needed now.
3. **Cal.com account timezone** is set to India time. Luxe bookings use New York time
   correctly, but the account's own emails may show India time. Left alone because the account
   is shared and you said not to change other setups. No action needed for the demo.

## Try these three calls (demo)
Tap the orb at http://localhost:5173 once credits are added. Use an `@example.com` email so
Cal.com sends no real confirmation emails.

1. **The everyday call: book a haircut**
   - **Say:** "Hi, I'm Maya, I've never been in before. Can I get a women's haircut this
     Saturday morning?" Pick a time; give "maya@example.com" and any 631 number.
   - **Expect:** Sophia checks availability, offers 2–3 real times with Emma, reads your email
     back letter by letter, confirms everything, then books.
   - **Check after:** Cal.com → Bookings shows "Luxe DEMO · Women's haircut & styling with
     Emma" at that time.

2. **The tricky one: wrong stylist, big colour change, then move the haircut**
   - **Say:** "I want balayage with Emma — I'm going from dark brown to blonde." Then: "Also,
     can you move my Saturday haircut to Sunday? It's under maya@example.com."
   - **Expect:** Sophia explains Sophia (the stylist) does balayage, recommends the free colour
     consultation with Olivia, then finds your haircut by email, offers Sunday times, and moves
     it.
   - **Check after:** Cal.com shows the haircut on Sunday. Then call once more and cancel it to
     clean up: Sophia should offer to reschedule first, and mention the 24-hour note only if
     it's inside 24 hours.

3. **The handoff: a reaction after colour**
   - **Say:** "I had colour done two days ago and my scalp is itchy and red. I want the owner
     to call me."
   - **Expect:** Sophia suggests seeing a pharmacist or doctor, doesn't diagnose or promise a
     refund, takes your name and number, marks it urgent, and says the team will follow up
     within one business day.
   - **Check after:** Retell → Call History → this call shows `urgency: urgent` and the message
     in its post-call fields.

## Files
- **Client folder:** `clients/luxe-hair-salon/` — `brief.md`, `research.md`, `receptionist/`
  (prompt, flow, functions, knowledge base, post-call).
- **Deploy records:** `deploy/` — Cal.com schedule and event types, Retell
  app/KB/LLM/agent/publish/tests, `ids.json`, `validation.json`, `simulation-run-1.json`.
- **Rebuild scripts:** `deploy/build_retell.py`, `deploy/build_tests.py` (re-run them to push
  prompt or test changes).
