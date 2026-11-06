# Brief — Luxe Hair Salon

> **DEMO CLIENT.** Luxe Hair Salon is a **fictional business** used as a demo AI receptionist.
> Every business fact below is **demo data** supplied by the owner on 2026-11-06. No real
> address, phone number, website, staff contacts, or customers exist.

## What the owner told us (2026-11-06)
- Luxe Hair Salon, a hair salon in Huntington, NY (demo).
- The receptionist must: book appointments; check availability; cancel and reschedule; handle
  stylist requests; answer FAQs (hours, pricing, services); handle after-hours calls; take
  messages.
- Integration: Cal.com (key in `.env` as `CALCOM_API_KEY`; tested with HTTP 200).
- Build rules for the demo: receptionist named Sophia, warm, friendly, upscale tone. No paid
  phone number. No real texts or emails to staff. Don't touch other businesses' Cal.com setup.
  Label all fictional info as demo data.

## Questions asked (6, one batch) and answers — ALL DEMO DATA
1. **Business details:** Luxe Hair Salon, Huntington, New York. No website. Fictional location
   — don't invent a street address or phone number. Parking: "the salon team can confirm."
2. **Services and prices (USD, fictional):**

   | Service | Price | Duration |
   |---|---|---|
   | Women's haircut & styling | From $65 | 60 min |
   | Men's haircut | From $35 | 30 min |
   | Blowout | From $45 | 45 min |
   | Root touch-up | From $85 | 90 min |
   | All-over color | From $120 | 120 min |
   | Partial highlights | From $150 | 150 min |
   | Full highlights | From $200 | 180 min |
   | Balayage | From $225 | 180 min |
   | Deep conditioning treatment | From $40 | 30 min |
   | Color consultation | Free | 15 min |

3. **Hours (America/New_York):** Mon closed. Tue–Fri 9 AM–7 PM. Sat 9 AM–6 PM. Sun 10 AM–4 PM.
   Closed on major US holidays.
4. **Stylists (fictional):** Emma — haircuts and styling. Olivia — color and highlights.
   Sophia — balayage and treatments. Callers may request a stylist or take the next available
   slot. The Cal.com account is **shared with another business**: keep Luxe separate, and
   don't modify the Avant Garde schedule or the generic "15 min meeting".
5. **Policies (fictional):**
   - Cancellations: at least 24 h notice requested, no fee.
   - Deposits: not required.
   - Running late: more than 15 min late may require rescheduling.
   - New color clients: consultation recommended before major changes.
   - Patch tests: staff will confirm.
6. **After-hours messages:** capture name, phone, and reason. No real texts or emails. Tell
   callers the team will follow up within one business day.
