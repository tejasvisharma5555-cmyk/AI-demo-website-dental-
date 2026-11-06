Last verified: 2026-11-06

# Retell — where a custom function is needed

Retell covers most receptionist needs natively (capabilities.md). These are the gaps.

**How to choose:**
- Use a `code` tool when it's a calculation, formatting, or a public API with no secrets.
- Use a hosted `custom` function when it needs secrets, private systems, the LLM's arguments, or writes data.
- Use the inbound webhook when the work happens before the call is answered.

| Need | Native? | What to build |
|---|---|---|
| **Booking in practice-management software** (dental: Dentrix, Open Dental, Eaglesoft, Curve, Denticon; medical EHRs; salon/spa systems) | No — only Cal.com, Calendly, and GoHighLevel are bookable natively | Hosted `custom` functions `check_availability` and `book_appointment` → the vendor API or a scheduling bridge. If the client has no API access: take a callback request instead (extraction + SMS/email to staff) |
| Booking when the client uses Google/Outlook calendar only | No | Connect the calendar to Cal.com (native integration), or build a hosted custom function to the calendar API |
| Look up an existing patient/customer in the practice's own system | No (only the listed CRMs) | Hosted custom function, or pre-call lookup via `pre_session_tools` + an HTTP step |
| Insurance-eligibility checks | No | Hosted custom function to a clearinghouse API. Usually out of scope: collect the details and hand off to staff |
| Payments / deposits | No | Don't take card numbers by voice (PCI). Send a payment link by SMS (`send_sms`) from our endpoint |
| Notify staff after a call (email, Slack, practice inbox) | Partly — SMS is native; CRM logging is native | `post_session_tools` HTTP step → our endpoint (email/Slack), or use the `call_analyzed` webhook |
| After-hours on-call paging / emergency escalation | Partly — `transfer_call` to a number is native | Native if the on-call number is fixed. If the rotation changes, a custom function returns tonight's number |
| Different behaviour by time of day / holidays | Partly — dynamic variables + prompt | Inbound webhook sets `{{is_open}}` and `{{todays_hours}}` from the client's schedule; or a `code` tool for simple fixed hours |
| Multi-location routing by caller area or choice | Partly — weighted agents, agent swap | Inbound webhook picks the agent or sets location variables |
| Write call results into an unsupported CRM / spreadsheet | No | Hosted endpoint on `call_analyzed`. Google Sheets triggers only *outbound* calls natively |
| Custom reporting to the client | Partly — the Retell dashboard exists, but clients shouldn't get access to our workspace | Our own endpoint/report from `call_analyzed` + `/v3/list-calls` |

**Hosting requirements for any custom function:**
- A public HTTPS endpoint (private IPs are blocked).
- Verify `X-Retell-Signature`.
- Respond well within the timeout; set `speak_during_execution` so callers don't hear silence.
- No PHI goes in logs unless the host is covered by a BAA.
