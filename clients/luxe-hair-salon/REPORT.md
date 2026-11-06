# Build Report — Luxe Hair Salon

> **DEMO BUILD — fictional business.** Luxe Hair Salon, its stylists (Emma, Olivia, Sophia),
> prices, hours, and policies are all **demo data**. There is no real address, phone number,
> website, staff contact, or customer.

Built 2026-11-06 with: research-voice-platform (change check) → research-business-type →
build-receptionist (library skills: booking, cancel-reschedule, FAQ, lead capture,
after-hours) → validate-receptionist.

## Update 2026-11-06 — no re-confirming at the end (version 5)
- **Owner:** in the text chat, Sophia kept asking for confirmation again at the end.
- **Fix:**
  - she confirms a booking, change, or cancellation exactly once;
  - after any yes ("yeah", "ok", "sure") she acts immediately and never asks again, even if the
    caller repeats the details;
  - after booking she says only "You're all set. Anything else?";
  - when the caller is done: "Thanks for calling, bye!" and she hangs up, with no summary.
- **Not tested** (owner request).

## Update 2026-11-06 — greeting fix + fewer words (version 4)
- **Problem:** the generated greeting spoke Sophia's reasoning out loud ("Friday at 6:33 PM: the
  salon closes at 7 PM today, so we're open right now.").
- **Fix:** fixed greeting "Hi, Luxe Hair Salon, this is Sophia, the virtual assistant. This call
  may be recorded. How can I help?"
- **Closed notice:** she now mentions the salon is closed only if the caller asks for a person,
  asks if it's open, or wants a same-day appointment while closed.
- **Shorter prompt:** one sentence per reply. She never says the time, day, hours, or what she's
  checking unless asked. After booking she says only "You're all set. Anything else?"
- **Not tested** (owner request). Free structural checks pass.

## Update 2026-11-06 — 3 stylist links instead of 10 (owner request)
- **Cal.com:** 3 links now, one per stylist, each offering several lengths:
  - Emma `luxe-demo-emma` (30/45/60 min)
  - Olivia `luxe-demo-olivia` (15/90/120/150/180 min)
  - Sophia `luxe-demo-sophia` (30/180 min)

  All on the "Luxe Hair Salon (DEMO)" schedule. The 10 per-service links were deleted. The
  Avant Garde schedule and the "15 min meeting" are untouched.
- **Sophia (the receptionist):** published **version 3**. She uses `check_<stylist>` /
  `book_<stylist>` and passes the service length. That's 11 tools instead of 25.
- **Checked (free):** slots per length (e.g. Sophia's Saturday: 3 h balayage last start 3:00 PM,
  30 min treatment last start 5:30 PM); tools wired to the right link and lengths; structural
  checks 7/7.
- **Not tested** — no test calls or simulations, at the owner's request.
- **Still one shared calendar:** all 3 links sit on one Cal.com user, so two stylists can't be
  booked at the same hour. Separate calendars need one Cal.com user per stylist (Cal.com Teams).
- Simulation test definitions updated to the new tool names (saved, not run).

## Update 2026-11-06 — "too talkative" fix (owner feedback after first test call)
**Problems seen in the owner's web call** (`call_bfbd0794f685ff19cf3d1988bf0`; latency p50 977 ms,
LLM 602 ms):
- Booking confirmed three times; email checked twice.
- Spoke twice around every tool ("let me check…" plus "one moment…").
- Said "thanks for the reference info": the knowledge base text was being read as caller speech.
- Stopped mid-sentence on every "yeah".
- Read out a whole day's openings.
- Accepted an invalid email until Cal.com rejected it.

**Changes, now live as published version 2:**
- New "How you talk" rules:
  - at most two short sentences per reply;
  - never repeat or re-confirm what the caller already said or confirmed;
  - "yeah" means yes;
  - no narrating or thinking out loud;
  - don't list services unless asked.
- **Booking:** offers two times only, asks for name, mobile, and email in one question, checks
  the email format, confirms once, then says only "You're all set. You'll get a confirmation
  email. Anything else?"
- **Tool lines:** every tool now says just "One sec."
- **Knowledge base removed:** all facts were already in the prompt, so this fixes the
  "reference info" replies and saves a retrieval step.
- **Interruptions:** sensitivity 0.9 → 0.6, so a "yeah" doesn't stop her mid-sentence.
- **Greeting:** shorter and generated, so it now says "We're closed right now, but I can still
  book you in or take a message" when closed. Fixes the after-hours failures from run 1.
- **Cancel:** respects "I don't want to reschedule"; adds the 24-hour note only when it applies.

**Tested:**
- 14 simulations (13 original + new #14 "no repeated confirmations"), all Cal.com tools mocked.
- Version 1: 14/14. Version 2: 13/14, then **14/14 on re-run**. The one miss was wording on
  "booking not found" ("left a message for the team to cancel"), which the grader read as
  claiming a cancellation.
- Structural checks 8/8. Results: `deploy/retell/simulation-run-2.json`, `simulation-run-3.json`.
- **Not re-tested by voice yet:** try the orb again.

**Note — your test booking is real:** Men's haircut with Emma, Sat Nov 7 at 5:30 PM, under
"Anthony Sharma", email `anthony@gmail.com`. Cal.com sent a confirmation to that address, which
may belong to a stranger. It's still on the calendar. Cancel it in Cal.com if you want the slot
back, and use `@example.com` emails for tests.

## Built
| What | Where | Status |
|---|---|---|
| Receptionist **"Sophia"**, warm upscale salon tone | Retell agent `agent_7dd2e9e07fd10fc34d66dd5efb` "Luxe Hair Salon DEMO - Sophia" | **Published** (version 2 — see update above) |
| Prompt engine with 25 tools | Retell LLM `llm_80272405ae8a1a3b94f223e76843` | All 25 tools registered ✔ |
| Knowledge base (services, prices, stylists, hours, policies — demo) | `knowledge_base_e67edd453c19686f` | Detached in v1+ (facts are in the prompt) |
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
1. ~~Re-run the simulation and make voice test calls~~ — **resolved**: credits were topped up;
   simulations re-run (14/14) and the owner made a web call. The original blocker was:

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
