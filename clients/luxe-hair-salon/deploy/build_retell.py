#!/usr/bin/env python3
"""Build (or update) the Luxe Hair Salon DEMO receptionist in Retell via the REST API.

Usage: python3 -I clients/luxe-hair-salon/deploy/build_retell.py
- Reads the prompt from receptionist/prompt.md and Cal.com event types from deploy/calcom/event-types.json.
- Creates the Retell LLM + agent on first run; on later runs PATCHes them (IDs in deploy/retell/ids.json).
- Writes every request body and response to deploy/retell/. Never writes secrets.
"""
import json
import os
import re
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(CLIENT))
OUT = os.path.join(HERE, "retell")
APP_ID = "app_e7c5b5d3ef6dc166798af57f"  # Cal.com connection (deploy/retell/calcom-app.json)
TZ = "America/New_York"

for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)
KEY = os.environ["RETELL_API_KEY"]


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
            return e.code, {"raw": t[:500].decode(errors="replace")}


def save(name, request, response):
    json.dump({"request": request, "response": response}, open(os.path.join(OUT, name), "w"), indent=2)


def desc(text):
    return {"type": "string", "description": text}


def tools():
    # One Cal.com event type per stylist, with several lengths (deploy/calcom/event-types-per-stylist.json)
    stylists = json.load(open(os.path.join(HERE, "calcom", "event-types-per-stylist.json")))
    out = []
    for s in stylists:
        key = s["stylist"].lower()
        etid = str(s["event_type_id"])
        menu = "; ".join(f"{name} = {mins}" for name, mins in s["services"].items())
        lengths = sorted(set(s["services"].values()))
        dur = {"type": "number", "enum": lengths,
               "description": f"Length in minutes of the service the caller wants: {menu}. Use the same value when checking and booking."}
        out.append({
            "type": "integration_app", "name": f"check_{key}", "app_id": APP_ID, "provider": "calcom",
            "app_tool_template_name": "check_calcom_availability",
            "description": f"Check {s['stylist']}'s open start times for one of her services ({', '.join(s['services'])}). Call before offering any time.",
            "parameters": [
                {"type": "object", "required": ["event_type_id", "start_time", "end_time", "timezone"],
                 "properties": {
                     "event_type_id": {"type": "string", "const": etid},
                     "start_time": desc("Start of the window to search, local New York time, ISO 8601 YYYY-MM-DDTHH:MM:SS. Use the caller's preferred day."),
                     "end_time": desc("End of the window, local New York time, ISO 8601 YYYY-MM-DDTHH:MM:SS. At most a few days after start_time."),
                     "timezone": {"type": "string", "const": TZ}}},
                {"type": "object", "required": [], "properties": {"duration_minutes": dur}},
            ],
            "speak_during_execution": True, "execution_message_type": "static_text",
            "execution_message_description": "One sec.",
        })
        out.append({
            "type": "integration_app", "name": f"book_{key}", "app_id": APP_ID, "provider": "calcom",
            "app_tool_template_name": "book_calcom_appointment",
            "description": f"Book a service with {s['stylist']} at a time returned by check_{key} (same duration), only after the caller said yes to the confirmation.",
            "parameters": [
                {"type": "object", "required": ["event_type_id"],
                 "properties": {"event_type_id": {"type": "string", "const": etid}}},
                {"type": "object", "required": ["time", "timezone", "name", "email", "attendeePhoneNumber"],
                 "properties": {
                     "time": desc("The confirmed start time, local New York time, ISO 8601 YYYY-MM-DDTHH:MM:SS, exactly as returned by the availability check."),
                     "timezone": {"type": "string", "const": TZ},
                     "duration_minutes": dur,
                     "name": desc("The client's first and last name."),
                     "email": desc("The client's email address."),
                     "attendeePhoneNumber": desc("The client's mobile number in E.164 format, e.g. +16315550123."),
                     "notes": desc("Start with 'DEMO booking via AI receptionist.' then the service name (e.g. 'Service: Balayage'), new or returning, and anything the stylist should know."),
                 }},
            ],
            "speak_during_execution": True, "execution_message_type": "static_text",
            "execution_message_description": "One sec.",
        })
    out += [
        {"type": "integration_app", "name": "find_booking", "app_id": APP_ID, "provider": "calcom",
         "app_tool_template_name": "list_calcom_bookings",
         "description": "Find the caller's upcoming Luxe bookings by the email they booked with. Call before rescheduling or cancelling.",
         "parameters": [{"type": "object", "required": ["attendee_email", "start_time", "end_time", "timezone"],
                         "properties": {
                             "attendee_email": desc("The email the caller booked with, as confirmed letter by letter."),
                             "start_time": desc("Now, in local New York time, ISO 8601 YYYY-MM-DDTHH:MM:SS."),
                             "end_time": desc("Three months from now, local New York time, ISO 8601 YYYY-MM-DDTHH:MM:SS."),
                             "timezone": {"type": "string", "const": TZ}}}],
         "speak_during_execution": True, "execution_message_type": "static_text",
         "execution_message_description": "One sec."},
        {"type": "integration_app", "name": "reschedule_booking", "app_id": APP_ID, "provider": "calcom",
         "app_tool_template_name": "reschedule_calcom_booking",
         "description": "Move the caller's confirmed booking to a new time that the service's check tool returned and the caller agreed to.",
         "parameters": [{"type": "object", "required": ["booking_uid", "start", "timezone"],
                         "properties": {
                             "booking_uid": desc("The booking_uid of the booking the caller confirmed, from the find_booking result."),
                             "start": desc("The new start time the caller agreed to, local New York time, ISO 8601 YYYY-MM-DDTHH:MM:SS."),
                             "timezone": {"type": "string", "const": TZ},
                             "reschedule_reason": desc("A short reason from the conversation.")}}],
         "speak_during_execution": True, "execution_message_type": "static_text",
         "execution_message_description": "One sec."},
        {"type": "integration_app", "name": "cancel_booking", "app_id": APP_ID, "provider": "calcom",
         "app_tool_template_name": "cancel_calcom_booking",
         "description": "Cancel the caller's confirmed booking, only after offering to reschedule and getting a clear yes to cancel.",
         "parameters": [{"type": "object", "required": ["booking_uid", "cancellation_reason"],
                         "properties": {
                             "booking_uid": desc("The booking_uid of the booking the caller confirmed, from the find_booking result."),
                             "cancellation_reason": desc("A short reason from the conversation.")}}],
         "speak_during_execution": True, "execution_message_type": "static_text",
         "execution_message_description": "One moment."},
        {"type": "extract_dynamic_variable", "name": "save_message",
         "description": "Save a message for the salon team once you have the caller's name, best number, and reason.",
         "variables": [
             {"type": "string", "name": "message_caller_name", "description": "Caller's name."},
             {"type": "string", "name": "message_callback_number", "description": "Best callback number, E.164 if possible."},
             {"type": "string", "name": "message_reason", "description": "What the message is about, in one or two sentences."},
             {"type": "enum", "name": "message_urgency", "description": "urgent only for a skin or scalp reaction or a same-day problem.", "choices": ["normal", "urgent"]},
         ]},
        {"type": "end_call", "name": "end_call", "description": "End the call after the caller has nothing else and you've said goodbye."},
    ]
    return out


def main():
    ids_path = os.path.join(OUT, "ids.json")
    ids = json.load(open(ids_path)) if os.path.exists(ids_path) else {}
    prompt = re.search(r"```prompt\n(.*?)```", open(os.path.join(CLIENT, "receptionist", "prompt.md")).read(), re.S).group(1).strip()
    kb = json.load(open(os.path.join(OUT, "knowledge-base.json")))["response"]["knowledge_base_id"]
    tl = tools()
    llm_body = {
        "general_prompt": prompt,
        "begin_message": "Hi, Luxe Hair Salon, this is Sophia, the virtual assistant. This call may be recorded. How can I help?",  # fixed text: a generated greeting leaked the agent's reasoning
        "start_speaker": "agent",
        "model_config": {"type": "cascading",
                         "primary": {"model": "claude-5.5-haiku", "tier": "standard"},
                         "backup": {"model": "gemini-3.8-flash", "tier": "standard"},
                         "temperature": 0.3},
        "knowledge_base_ids": [],  # removed: all facts are in the prompt; KB chunks were being read as caller speech
        "general_tools": tl,
    }
    draft_version, llm_version = None, None
    if ids.get("agent_id"):
        # Published versions are frozen: edit a draft. Reuse the newest draft, or create one from the newest version.
        st, vers = api("GET", f"/list-agent-versions/{ids['agent_id']}")
        items = sorted(vers.get("items", []), key=lambda v: v["version"])
        latest = items[-1]
        if latest.get("is_published"):
            st, draft = api("POST", f"/create-agent-version/{ids['agent_id']}", {"base_version": latest["version"]})
            print("new draft version", st, draft.get("version"), "" if st < 300 else draft)
            if st >= 300:
                return 1
        else:
            st, draft = api("GET", f"/get-agent/{ids['agent_id']}?version={latest['version']}")
        draft_version = draft["version"]
        llm_version = (draft.get("response_engine") or {}).get("version")
        ids["draft_version"] = draft_version
    if ids.get("llm_id"):
        q = f"?version={llm_version}" if llm_version is not None else ""
        st, llm = api("PATCH", f"/update-retell-llm/{ids['llm_id']}{q}", llm_body)
    else:
        st, llm = api("POST", "/create-retell-llm", llm_body)
    print("llm", st, llm.get("llm_id"), "" if st < 300 else llm)
    if st >= 300:
        return 1
    save("llm.json", llm_body, llm)
    ids["llm_id"] = llm["llm_id"]

    analysis = [
        {"type": "enum", "name": "call_reason", "description": "Main reason for the call.", "choices": ["book", "reschedule", "cancel", "question", "message", "spam", "other"]},
        {"type": "boolean", "name": "appointment_booked", "description": "A new appointment was successfully booked."},
        {"type": "string", "name": "service", "description": "Service discussed or booked."},
        {"type": "string", "name": "appointment_time", "description": "Booked or new appointment time, if any."},
        {"type": "enum", "name": "booking_change", "description": "Whether an existing booking was changed.", "choices": ["rescheduled", "cancelled", "none"]},
        {"type": "string", "name": "caller_name", "description": "Caller's name, if given."},
        {"type": "string", "name": "callback_number", "description": "Callback number, if given."},
        {"type": "string", "name": "message", "description": "Message for the salon team, if one was taken."},
        {"type": "enum", "name": "urgency", "description": "urgent only for a reaction after a service or a same-day problem.", "choices": ["normal", "urgent"]},
        {"type": "boolean", "name": "after_hours", "description": "The call happened while the salon was closed."},
        {"type": "string", "name": "unanswered_question", "description": "Any question Sophia could not answer."},
    ]
    agent_body = {
        "agent_name": "Luxe Hair Salon DEMO - Sophia",
        "response_engine": {"type": "retell-llm", "llm_id": ids["llm_id"]},
        "voice_id": "retell-Marissa",
        "language": "en-US",
        "timezone": TZ,
        "boosted_keywords": ["Luxe", "balayage", "blowout", "highlights", "Emma", "Olivia", "Sophia", "Huntington", "root touch-up", "deep conditioning"],
        "post_call_analysis_data": analysis,
        "data_storage_setting": "everything",
        "data_storage_retention_days": 90,
        "end_call_after_silence_ms": 30000,
        "max_call_duration_ms": 900000,
        "interruption_sensitivity": 0.6,
        "version_title": "DEMO build",
        "version_description": "Luxe Hair Salon fictional demo receptionist",
    }
    if ids.get("agent_id"):
        agent_body.pop("response_engine")
        q = f"?version={draft_version}" if draft_version is not None else ""
        st, agent = api("PATCH", f"/update-agent/{ids['agent_id']}{q}", agent_body)
    else:
        st, agent = api("POST", "/create-agent", agent_body)
    print("agent", st, agent.get("agent_id"), "" if st < 300 else agent)
    if st >= 300:
        return 1
    save("agent.json", agent_body, agent)

    ids.update({
        "client_name": "Luxe Hair Salon (DEMO)",
        "demo": True,
        "agent_id": agent["agent_id"],
        "knowledge_base_ids": [],
        "app_ids": [APP_ID],
        "phone_number": None,
        "phone_number_skipped_reason": "Demo build: owner asked not to purchase a paid phone number.",
        "expected_tools": [t["name"] for t in tl],
        "custom_function_urls": [],
    })
    ids.setdefault("test_case_definition_ids", [])
    json.dump(ids, open(ids_path, "w"), indent=2)
    print("saved", ids_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
