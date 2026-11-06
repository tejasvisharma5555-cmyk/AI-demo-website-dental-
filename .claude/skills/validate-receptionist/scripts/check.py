#!/usr/bin/env python3
"""Validate a client's Retell receptionist after a build.

Usage:
  check.py <client-slug> [--simulate [--cases "DEMO 06,DEMO 12"]] [--timeout 600]

COST: --simulate spends the owner's Retell credits (CLAUDE.md rule 9). Run the full suite once per
build; after a fix, pass --cases with only the affected test names (substring match) or IDs.

Reads IDs from clients/<slug>/deploy/retell/ids.json and RETELL_API_KEY from .env, then checks:
  - the agent exists and is published
  - the response engine (Retell LLM / conversation flow) exists and every expected tool is registered
  - knowledge bases have finished ingesting
  - every integration app authenticates (POST /test-app-auth)
  - the phone number exists and routes inbound calls to this agent
  - custom function URLs (Vercel) are reachable and reject unsigned requests
With --simulate it also runs all of the client's simulation test cases as one batch and waits
for the result.

Writes clients/<slug>/deploy/validation.json. Exit code 0 = all passed, 1 = something failed.
Never prints the API key.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.retellai.com"


def load_env(root):
    env = {}
    path = os.path.join(root, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


class Retell:
    def __init__(self, key):
        self.key = key

    def call(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(API + path, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.key}")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                txt = r.read().decode()
                return r.status, (json.loads(txt) if txt else {})
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors="replace")
            try:
                return e.code, json.loads(txt)
            except ValueError:
                return e.code, {"raw": txt[:300]}


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        return 2
    slug = args[0]
    simulate = "--simulate" in args
    timeout = int(args[args.index("--timeout") + 1]) if "--timeout" in args else 600
    only = [c.strip() for c in args[args.index("--cases") + 1].split(",")] if "--cases" in args else None

    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    ids_path = os.path.join(root, "clients", slug, "deploy", "retell", "ids.json")
    if not os.path.exists(ids_path):
        print(f"FAIL  missing {ids_path} (build-receptionist must write it)")
        return 1
    ids = json.load(open(ids_path, encoding="utf-8"))
    key = load_env(root).get("RETELL_API_KEY") or os.environ.get("RETELL_API_KEY")
    if not key:
        print("FAIL  RETELL_API_KEY not found in .env")
        return 1
    rt = Retell(key)
    results = []

    def record(name, ok, detail=""):
        results.append({"check": name, "ok": bool(ok), "detail": detail})
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))

    # Agent
    agent_id = ids.get("agent_id")
    st, agent = rt.call("GET", f"/get-agent/{agent_id}") if agent_id else (0, {})
    record("agent exists", st == 200, f"{agent_id} '{agent.get('agent_name', '')}'" if st == 200 else f"HTTP {st}")
    if st == 200:
        st_v, versions = rt.call("GET", f"/list-agent-versions/{agent_id}")
        items = versions if isinstance(versions, list) else versions.get("items", versions.get("versions", []))
        published = [v for v in items if isinstance(v, dict) and v.get("is_published")] if st_v == 200 else []
        record("agent has a published version", bool(published) or agent.get("is_published"),
               f"published versions: {[v.get('version') for v in published]}" if published else "none published")

    # Response engine and tools
    expected = set(ids.get("expected_tools", []))
    if ids.get("llm_id"):
        st, llm = rt.call("GET", f"/get-retell-llm/{ids['llm_id']}")
        record("Retell LLM exists", st == 200, ids["llm_id"] if st == 200 else f"HTTP {st}")
        if st == 200:
            tools = list(llm.get("general_tools") or [])
            for state in llm.get("states") or []:
                tools += state.get("tools") or []
            names = {t.get("name") for t in tools}
            missing = sorted(expected - names)
            record("functions registered", not missing,
                   f"registered: {sorted(n for n in names if n)}" + (f"; MISSING: {missing}" if missing else ""))
            mc = llm.get("model_config") or {}
            record("model configured", bool(mc.get("primary")), json.dumps(mc.get("primary")))
    elif ids.get("conversation_flow_id"):
        st, flow = rt.call("GET", f"/get-conversation-flow/{ids['conversation_flow_id']}")
        record("conversation flow exists", st == 200, ids["conversation_flow_id"] if st == 200 else f"HTTP {st}")
        if st == 200:
            # tools + node names (transfer/end/SMS are nodes in a flow)
            names = {t.get("name") for t in (flow.get("tools") or [])}
            names |= {n.get("name") for n in (flow.get("nodes") or [])}
            missing = sorted(expected - names)
            record("functions registered", not missing,
                   f"registered: {sorted(n for n in names if n)}" + (f"; MISSING: {missing}" if missing else ""))
    else:
        record("response engine id recorded", False, "ids.json needs llm_id or conversation_flow_id")

    # Knowledge bases
    for kb in ids.get("knowledge_base_ids", []):
        st, k = rt.call("GET", f"/get-knowledge-base/{kb}")
        record(f"knowledge base {kb} ready", st == 200 and k.get("status") == "complete",
               k.get("status", f"HTTP {st}"))

    # Integrations
    for app in ids.get("app_ids", []):
        st, a = rt.call("POST", f"/test-app-auth/{app}", {})
        record(f"integration {app} authenticates", st == 200 and a.get("success") is True,
               "success" if a.get("success") else f"HTTP {st} {a}")

    # Phone number
    num = ids.get("phone_number")
    if num:
        st, p = rt.call("GET", f"/get-phone-number/{urllib.parse.quote(num)}")
        inbound = [a.get("agent_id") for a in (p.get("inbound_agents") or [])] if st == 200 else []
        record("phone number routes to agent", st == 200 and agent_id in inbound,
               f"{num} → {inbound}" if st == 200 else f"HTTP {st}")
    elif ids.get("phone_number_skipped_reason"):
        results.append({"check": "phone number attached", "ok": True, "skipped": True,
                        "detail": ids["phone_number_skipped_reason"]})
        print(f"SKIP  phone number attached — {ids['phone_number_skipped_reason']}")
    else:
        record("phone number attached", False, "no phone_number in ids.json")

    # Custom functions (must reject unsigned requests)
    for url in ids.get("custom_function_urls", []):
        req = urllib.request.Request(url, data=b'{"args":{}}', method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:  # unreachable
            code = f"unreachable: {e.__class__.__name__}"
        record(f"custom function {url} rejects unsigned", code in (401, 403), f"got {code}")

    # Simulation
    if simulate:
        tcs = ids.get("test_case_definition_ids", [])
        if only and tcs:
            st_l, lst = rt.call("GET", "/v2/list-test-case-definitions?type=" + ("retell-llm" if ids.get("llm_id") else "conversation-flow")
                                + ("&llm_id=" + ids["llm_id"] if ids.get("llm_id") else ""))
            names = {t.get("test_case_definition_id"): t.get("name", "") for t in
                     (lst if isinstance(lst, list) else lst.get("items", []))} if st_l == 200 else {}
            tcs = [t for t in tcs if t in only or any(o.lower() in names.get(t, "").lower() for o in only)]
            print(f"Running only {len(tcs)} selected test(s): {[names.get(t, t) for t in tcs]}")
        engine = ({"type": "retell-llm", "llm_id": ids["llm_id"]} if ids.get("llm_id")
                  else {"type": "conversation-flow", "conversation_flow_id": ids.get("conversation_flow_id")})
        if not tcs:
            record("simulation tests", False, "no test_case_definition_ids in ids.json")
        else:
            st, b = rt.call("POST", "/create-batch-test", {"test_case_definition_ids": tcs, "response_engine": engine})
            if st not in (200, 201):
                record("simulation batch started", False, f"HTTP {st} {b}")
            else:
                bid = b.get("test_case_batch_job_id")
                deadline = time.time() + timeout
                while time.time() < deadline:
                    st, b = rt.call("GET", f"/get-batch-test/{bid}")
                    if b.get("status") == "complete":
                        break
                    time.sleep(10)
                done = b.get("status") == "complete"
                detail = (f"pass {b.get('pass_count')}/{b.get('total_count')}, fail {b.get('fail_count')}, "
                          f"error {b.get('error_count')} (batch {bid})")
                if done and (b.get("fail_count") or b.get("error_count")):
                    st_r, runs = rt.call("GET", f"/v2/list-test-runs/{bid}")
                    items = runs if isinstance(runs, list) else runs.get("items", [])
                    for run in items:
                        if run.get("status") in ("fail", "error"):
                            name = (run.get("test_case_definition_snapshot") or {}).get("name", run.get("test_case_job_id"))
                            detail += f"\n      ✗ {name}: {run.get('result_explanation', '')[:200]}"
                record("simulation tests pass", done and b.get("pass_count") == b.get("total_count"),
                       detail if done else f"timed out after {timeout}s (batch {bid})")

    out = os.path.join(root, "clients", slug, "deploy", "validation.json")
    json.dump({"validated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "results": results},
              open(out, "w", encoding="utf-8"), indent=2)
    failed = [r for r in results if not r["ok"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed → {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
