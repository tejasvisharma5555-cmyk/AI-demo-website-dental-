---
name: receptionist-faq
description: Receptionist library module for answering common questions accurately from a knowledge base — hours, location, services, prices, insurance, policies — without guessing. Use inside build-receptionist for every client.
---

# FAQ

## Sources, in order of trust
1. The owner's answers (`brief.md`).
2. The client's website and Google Business profile (`research.md`, marked "found").
3. Industry defaults from `docs/industries/<type>.md`. Only for general explanations ("what
   happens at a first visit"), **never** for client facts like prices, insurance, or hours.

## Build the knowledge base
- Write `receptionist/knowledge-base.md` as short Q&A pairs, phrased the way callers ask, with
  one fact per answer. Cover the top questions from the business-type research.
- Upload it as `knowledge_base_texts`, plus the client's website pages as `knowledge_base_urls`
  with `enable_auto_refresh: true` so site changes flow in. Attach it via `knowledge_base_ids`.
- Put the **critical facts directly in the prompt** too (hours, address, phone, main services),
  so they never depend on retrieval.
- Add `boosted_keywords` and `pronunciation_dictionary` entries for the business name, staff
  names, street names, and industry terms.

## Prompt section
```
## Answering questions
- Answer from the knowledge base and the facts above. Keep answers to 1–2 sentences, then offer next steps ("Would you like to book?").
- If the answer isn't there, say you're not sure and offer to take a message or transfer. Never guess prices, insurance coverage, or availability.
- Say addresses, phone numbers, and times clearly; spell out anything confusing.
- Don't give medical, legal, or financial advice — offer an appointment or staff callback instead.
```

## Edge cases
- Price questions → give prices only if the owner provided them. Otherwise "it depends on what
  you need; the team can give an exact quote", and offer to book or take a message.
- "Do you take my insurance?" → answer from the owner's list. If the plan isn't on it, say
  staff will verify — never say "no" unless the owner said so.
- Questions about competitors or unrelated topics → steer politely back.

## Required test cases
1. Hours question.
2. Address and parking or directions question.
3. A question not in the knowledge base → no guessing, a message is offered.
4. Price question with no owner price → no number invented.
5. An insurance plan not in the list → "staff will verify".

## Post-call fields
`question_topics` (text), `unanswered_question` (text — feeds back into the knowledge base).
