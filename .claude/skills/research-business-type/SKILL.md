---
name: research-business-type
description: Research a business type (dental practice, salon, plumber, law firm, etc.) before building an AI receptionist for a client — what its calls sound like, what callers ask for, what they need to book, what gets transferred — then draft the call flow, prompt, and functions, and finish with at most six questions only the owner can answer. Use at the start of every client build, after the platform change check.
---

# Research a business type

Goal: walk into the owner conversation already knowing how this kind of business runs, with a
draft receptionist in hand, so the owner only fills in the facts that are unique to them.

## Inputs
- The owner's description of the client (name, type, location, anything else said).
- The platform knowledge in `docs/platforms/<platform>/`. Retell is the default: read
  `capabilities.md` and `custom-functions.md` before step 4.

## Step 1 — Reuse what we already know
Check `docs/industries/<business-type>.md` (e.g. `dental.md`, `hair-salon.md`, `plumbing.md`).
- If it exists and was verified within ~90 days: reuse it. Research only what's specific to this
  client (their region's rules, their specialty, their website).
- If it's missing or stale: do the full research in step 2 and write or update it.

## Step 2 — Research how calls to this business sound
Use real sources: industry guides, front-desk and receptionist training material, call-handling
scripts, practice-management vendor docs, forums where owners and front-desk staff talk, and
regulations. Look at the client's website and Google Business profile for their services, hours,
and the questions customers ask. Capture:

1. **Who calls and why** — the call mix, roughly by share. Example for dental: new patients,
   existing patients booking or rescheduling, emergencies (pain, broken tooth), insurance and
   billing questions, labs/vendors, spam.
2. **What callers ask** — the top 15–25 questions, in the caller's own words, with what a good
   answer needs (e.g. "Do you take Delta Dental?" → the client's accepted-insurance list).
3. **What booking needs** — appointment types, typical durations, the details collected (name,
   DOB, phone, insurance, reason, new or existing), who can be booked with whom, lead times,
   cancellation policy, deposits.
4. **What gets transferred or escalated** — true emergencies, upset callers, clinical questions,
   billing disputes, anything the receptionist must not answer, plus after-hours handling.
5. **What's said on the phone vs. never said** — industry terms and phrasing callers expect;
   things staff never say (diagnoses, prices without a consult, legal advice).
6. **Compliance** — privacy law (e.g. HIPAA → confirm identity before discussing records, keep
   minimum details), call-recording consent for the client's state/country, telemarketing rules
   if there are outbound calls, and accessibility.
7. **Edge cases** — wrong numbers, sales calls, children calling, non-English callers,
   emergencies that need 911, and callers asking if they're talking to a bot.

Write the reusable parts to `docs/industries/<business-type>.md`:
- Start with `Last verified: YYYY-MM-DD` and list sources.
- No client data.
- Sections: Call mix · Top questions · Booking · Transfers & escalation · Language ·
  Compliance · Edge cases · Default answers (sensible defaults to use when the owner doesn't say).

## Step 3 — Write the client research
Create `clients/<client-slug>/` from `clients/_template/` if needed. Fill `research.md` with the
industry summary as it applies to this client, plus anything found on their website or listings.
Mark each fact as **found** (with source) or **assumed**.

## Step 4 — Draft the receptionist
Write these into `clients/<client-slug>/receptionist/`. Use placeholders like `{{hours}}` for
anything only the owner knows.

- **`call-flow.md`** — the path for each call type from step 2:
  greeting → identify the need → handle it (answer / book / take a message / transfer) → confirm → close.
  Include an after-hours branch and an emergency branch. Prefer a single-prompt agent; use a
  conversation flow only if the paths must be strict (see the platform docs).
- **`prompt.md`** — the full agent prompt:
  - identity and tone
  - what the business does
  - how to handle each call type
  - booking rules
  - transfer rules
  - hard "never say" rules
  - pronunciation of names and terms
  - compliance lines (recording disclosure, identity checks)

  Keep it short and direct, following the platform's prompting guide.
- **`functions.md`** — every tool the agent needs. For each: purpose, when it fires, and inputs
  and outputs. Mark each one:
  - **Native** — a built-in tool or integration (name it, e.g. Retell `transfer_call`,
    Cal.com `Book Appointment`).
  - **Custom** — a function we must build (why, and what it calls).
  - **Fallback** — what the agent does if the function isn't possible, e.g. take a callback
    request and text the staff.
- **`knowledge-base.md`** — the FAQ answers. Use the client's real info where found, and
  `{{placeholders}}` elsewhere.
- **`post-call.md`** — what to extract after each call (caller name, reason, urgency, booked
  yes/no, callback needed) and who gets notified.

## Step 5 — Ask the owner (six questions max, one batch)
List every remaining `{{placeholder}}` and assumption. Remove anything that was:
- found in research or on the client's site;
- technical — we decide those (CLAUDE.md rule 2);
- covered by a sensible default from `docs/industries/<type>.md` — keep it as an assumption instead.

From what's left, pick the **six (or fewer)** answers that change the build the most. Prefer
questions that resolve several placeholders at once. Write them in plain language, the way you'd
ask a business owner. Each must be answerable without technical knowledge. Typical topics:
- hours, and how emergencies are handled after hours
- which booking system or calendar they use (they know the name — don't ask about APIs)
- which numbers to transfer to, and for what
- services or insurance they don't take
- the tone they want
- anything the receptionist must never say

Save the questions to `clients/<client-slug>/brief.md`, then ask the owner in one message.
Fill every unasked gap with the default and list it under **Assumed** in the final report.

## Step 6 — After the answers
Replace the placeholders and update `brief.md`. Note anything that changed the draft. Then
continue to the build (CLAUDE.md workflow step 5).
