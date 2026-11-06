#!/usr/bin/env python3
"""Create the Luxe Hair Salon DEMO simulation test cases in Retell (idempotent by name).

Usage: python3 -I clients/luxe-hair-salon/deploy/build_tests.py
Every Cal.com tool is mocked in every case, so no test can touch the real calendar.
Saves the test case IDs into deploy/retell/ids.json and the definitions into deploy/retell/tests.json.
"""
import json
import os
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)
KEY = os.environ["RETELL_API_KEY"]
IDS = os.path.join(HERE, "retell", "ids.json")


def api(method, path, body=None):
    req = urllib.request.Request("https://api.retellai.com" + path, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            t = r.read()
            return r.status, json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        t = e.read()
        try:
            return e.code, json.loads(t)
        except ValueError:
            return e.code, {"raw": t[:300].decode(errors="replace")}


ids = json.load(open(IDS))
TOOLS = ids["expected_tools"]
ANY = {"type": "any"}
OPEN_TIMES = ["2026-11-14T10:00:00", "2026-11-14T11:30:00", "2026-11-14T14:00:00"]
LATER_TIMES = ["2026-11-15T10:00:00", "2026-11-15T12:00:00", "2026-11-18T16:30:00"]
OPEN_DAY = "Saturday, November 14"


def mocks(slots=None, book_ok=True, bookings=None):
    """Mock every Cal.com tool. Defaults: slots available, booking succeeds, one balayage booking on file."""
    slots = OPEN_TIMES + LATER_TIMES if slots is None else slots
    if bookings is None:
        bookings = [{"booking_uid": "demo-uid-balayage-1", "title": "Luxe DEMO · Balayage with Sophia between DIALPILOT AI and Jordan Lee",
                     "status": "accepted", "start_time": "2026-11-11T10:00:00-05:00", "end_time": "2026-11-11T13:00:00-05:00"}]
    out = []
    for t in TOOLS:
        if t.startswith("check_"):
            out.append({"tool_name": t, "input_match_rule": ANY, "output": json.dumps({"available_slots": slots})})
        elif t.startswith("book_"):
            out.append({"tool_name": t, "input_match_rule": ANY, "output": json.dumps(
                {"status": "success", "booking_uid": "demo-uid-new-1", "message": "Booking confirmed"} if book_ok
                else {"status": "error", "message": "Cal.com request failed: 503 Service Unavailable"})})
    out += [
        {"tool_name": "find_booking", "input_match_rule": ANY, "output": json.dumps({"bookings": bookings, "count": len(bookings)})},
        {"tool_name": "reschedule_booking", "input_match_rule": ANY, "output": json.dumps({"status": "success", "booking_uid": "demo-uid-balayage-2"})},
        {"tool_name": "cancel_booking", "input_match_rule": ANY, "output": json.dumps({"status": "success"})},
    ]
    return out


OPEN_NOW = {"current_time": "Tuesday, November 10, 2026 at 11:00 AM EST", "user_number": "+16315550142"}
CLOSED_NOW = {"current_time": "Monday, November 9, 2026 at 8:15 PM EST", "user_number": "+16315550142"}

CASES = [
    ("DEMO 01 booking: new client books women's haircut", OPEN_NOW, mocks(),
     "You are Maya Patel, a new client. You want a women's haircut this Saturday, any time in the morning. "
     "When offered times, pick the first one. Give your mobile as 631-555-0142 and email maya.patel@example.com. Confirm when asked.",
     ["The agent checked availability before offering times.",
      "The agent only offered times returned by the availability tool.",
      "The agent collected name, mobile number, and email, and read the email back.",
      "The agent confirmed the service, stylist Emma, day, and time and got a yes before calling book_womens_haircut.",
      "The agent said the appointment was booked only after the booking tool succeeded."]),
    ("DEMO 02 booking: rejects first options, corrects email", OPEN_NOW, mocks(),
     "You are Chris Romano. You want a blowout. Say none of the first times offered work and ask for Sunday instead; accept a Sunday time. "
     "Give email chris.romano@example.com but when the agent reads it back, say it's actually c.romano@example.com. Mobile 631-555-0199.",
     ["The agent offered alternative times after the caller rejected the first options.",
      "The agent used the corrected email c.romano@example.com when booking.",
      "The agent called book_blowout only after the caller confirmed."]),
    ("DEMO 03 booking: no availability", OPEN_NOW, mocks(slots=[]),
     "You are Dana Whitfield. You want balayage this week. Accept whatever the agent suggests next. Your number is 631-555-0177.",
     ["The agent did not invent any appointment times.",
      "The agent offered another option such as a different date or taking a message for the team.",
      "The agent did not claim an appointment was booked."]),
    ("DEMO 04 booking: booking tool error", OPEN_NOW, mocks(book_ok=False),
     "You are Priya Shah. Book a men's haircut for your husband Raj Shah, first time offered. Email raj.shah@example.com, mobile 631-555-0133. Confirm when asked.",
     ["After the booking tool returned an error, the agent did not say the appointment was booked.",
      "The agent apologised and offered a fallback such as taking a message or trying another way.",
      "The agent booked under the guest's name Raj Shah rather than the caller's name."]),
    ("DEMO 05 reschedule: balayage moved", OPEN_NOW, mocks(slots=LATER_TIMES),
     "You are Jordan Lee. You have a balayage booked and need to move it to next week. Your booking email is jordan.lee@example.com. Pick the first new time offered and confirm.",
     ["The agent asked for the booking email and called find_booking.",
      "The agent read back the existing balayage appointment and confirmed it was the right one.",
      "The agent checked availability with check_balayage before offering new times.",
      "The agent called reschedule_booking with booking_uid demo-uid-balayage-1 after the caller confirmed."]),
    ("DEMO 06 cancel: short notice, no fee", OPEN_NOW, mocks(),
     "You are Jordan Lee (jordan.lee@example.com). You want to cancel your balayage. If the agent offers to reschedule, politely decline. Then confirm the cancellation.",
     ["The agent offered to reschedule before cancelling.",
      "The agent mentioned the 24-hour notice request kindly.",
      "The agent did not say any cancellation fee would be charged.",
      "The agent called cancel_booking only after the caller confirmed."]),
    ("DEMO 07 cancel: booking not found", OPEN_NOW, mocks(bookings=[]),
     "You are Sam Ortiz (sam.ortiz@example.com). You want to cancel an appointment you think is on Friday. When the agent can't find it, agree to leave a message. Your number is 631-555-0188.",
     ["The agent did not claim to cancel anything.",
      "The agent offered to take a message for the salon team.",
      "The agent said the team would follow up within one business day."]),
    ("DEMO 08 FAQ: hours, location, parking", OPEN_NOW, mocks(),
     "You are a curious caller. Ask what the hours are on Monday and Sunday, what the address is, and whether there's parking. Then say thanks and goodbye.",
     ["The agent said the salon is closed on Mondays and open Sunday 10 AM to 4 PM.",
      "The agent did not invent a street address or phone number.",
      "The agent said the salon team can confirm parking details."]),
    ("DEMO 09 FAQ: prices and unknown question", OPEN_NOW, mocks(),
     "Ask how much balayage costs and how long it takes. Then ask whether they sell gift cards. Then say goodbye.",
     ["The agent said balayage starts from $225 and takes about 3 hours.",
      "The agent did not make up an answer about gift cards and offered that the team can confirm or take a message."]),
    ("DEMO 10 after hours: message for the team", CLOSED_NOW, mocks(),
     "You are Elena Russo calling late on a Monday evening. You want to speak to someone about a wedding party booking for five people. "
     "Your number is the one you're calling from. Don't book anything.",
     ["The agent said the salon is currently closed.",
      "The agent collected the caller's name, confirmed the callback number, and got the reason.",
      "The agent called save_message.",
      "The agent said the salon team will follow up within one business day."]),
    ("DEMO 11 after hours: still books", CLOSED_NOW, mocks(),
     "You are Taylor Brooks calling on a Monday night. You want a deep conditioning treatment this Saturday. Take the first time. Email taylor.brooks@example.com, mobile 631-555-0166. Confirm.",
     ["The agent mentioned the salon is closed but still offered to book.",
      "The agent called check_deep_conditioning and then book_deep_conditioning after confirmation."]),
    ("DEMO 12 stylist: Emma for highlights", OPEN_NOW, mocks(),
     "You are Lauren Kim, a new client. Ask to book full highlights with Emma. When the agent explains who does highlights, happily accept that stylist. "
     "If a consultation is suggested, say no thanks. Take the first time offered. Email lauren.kim@example.com, mobile 631-555-0111. Confirm once, then end the call politely.",
     ["The agent explained kindly that Olivia does colour and highlights.",
      "The agent recommended the free colour consultation for a new colour client.",
      "The agent booked with book_full_highlights after confirmation."]),
    ("DEMO 13 reaction after service: urgent message", OPEN_NOW, mocks(),
     "You are Nina Gold. You had colour done two days ago and your scalp is itchy and red. You want the owner to call you. Number 631-555-0155.",
     ["The agent suggested seeing a pharmacist or doctor and did not diagnose.",
      "The agent took a message and called save_message with urgency urgent.",
      "The agent did not promise a refund or a free fix."]),
]


def main():
    engine = {"type": "retell-llm", "llm_id": ids["llm_id"]}
    st, existing = api("GET", "/v2/list-test-case-definitions?type=retell-llm&llm_id=" + ids["llm_id"])
    by_name = {}
    if st == 200:
        items = existing if isinstance(existing, list) else existing.get("items", [])
        by_name = {t.get("name"): t for t in items}
    saved, out_ids = [], []
    for name, dv, mk, prompt, metrics in CASES:
        body = {"name": name, "response_engine": engine, "user_prompt": prompt, "metrics": metrics,
                "dynamic_variables": dv, "tool_mocks": mk}
        if name in by_name:
            tid = by_name[name]["test_case_definition_id"]
            st, r = api("PUT", f"/update-test-case-definition/{tid}", body)
        else:
            st, r = api("POST", "/create-test-case-definition", body)
            tid = r.get("test_case_definition_id")
        print(st, name, tid, "" if st < 300 else r)
        if st < 300:
            out_ids.append(tid)
            saved.append({"id": tid, **{k: v for k, v in body.items() if k != "tool_mocks"}, "tool_mocks": f"{len(mk)} mocks (all Cal.com tools)"})
    json.dump(saved, open(os.path.join(HERE, "retell", "tests.json"), "w"), indent=2)
    ids["test_case_definition_ids"] = out_ids
    json.dump(ids, open(IDS, "w"), indent=2)
    print(f"{len(out_ids)}/{len(CASES)} test cases saved")


if __name__ == "__main__":
    main()
