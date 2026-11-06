#!/usr/bin/env node
// Local voice-orb test page for a client's Retell agent.
//
// Usage: node .claude/skills/validate-receptionist/scripts/test-page/server.mjs <client-slug> [port]
//
// - Serves orb.html on http://localhost:<port> (default 5173).
// - The browser SDK sends its "create web call" request to this server, which forwards ONLY
//   POST /v3/create-web-call to Retell with the API key from .env and forces the agent_id to
//   the client's agent. The key never reaches the browser, and no public key is needed.
// - Audio then flows directly between the browser and Retell (WebRTC).
// No dependencies beyond Node 18+.
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const slug = process.argv[2];
const port = Number(process.argv[3] || 5173);
if (!slug) {
  console.error("usage: server.mjs <client-slug> [port]");
  process.exit(2);
}
const root = execSync("git rev-parse --show-toplevel").toString().trim();
const here = dirname(fileURLToPath(import.meta.url));

const env = Object.fromEntries(
  (existsSync(join(root, ".env")) ? readFileSync(join(root, ".env"), "utf8") : "")
    .split("\n")
    .filter((l) => l.includes("=") && !l.trim().startsWith("#"))
    .map((l) => [l.slice(0, l.indexOf("=")).trim(), l.slice(l.indexOf("=") + 1).trim().replace(/^['"]|['"]$/g, "")])
);
const apiKey = env.RETELL_API_KEY || process.env.RETELL_API_KEY;
if (!apiKey) {
  console.error("RETELL_API_KEY missing from .env");
  process.exit(1);
}

const ids = JSON.parse(readFileSync(join(root, "clients", slug, "deploy", "retell", "ids.json"), "utf8"));
const agentId = ids.agent_id;
const clientName = ids.client_name || slug;
const page = readFileSync(join(here, "orb.html"), "utf8")
  .replaceAll("__CLIENT_NAME__", clientName.replace(/[<>&"]/g, ""))
  .replaceAll("__AGENT_ID__", agentId);
const sdk = readFileSync(join(here, "vendor", "retell-sdk.mjs"));

const server = createServer(async (req, res) => {
  try {
    if (req.method === "GET" && (req.url === "/" || req.url.startsWith("/?"))) {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
      return res.end(page);
    }
    if (req.method === "GET" && req.url === "/vendor/retell-sdk.mjs") {
      res.writeHead(200, { "Content-Type": "text/javascript; charset=utf-8", "Cache-Control": "max-age=3600" });
      return res.end(sdk);
    }
    if (req.method === "POST" && req.url === "/retell/v3/create-web-call") {
      let raw = "";
      for await (const chunk of req) raw += chunk;
      let body = {};
      try { body = JSON.parse(raw || "{}"); } catch {}
      const upstream = await fetch("https://api.retellai.com/v3/create-web-call", {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_id: agentId, // always this client's agent, whatever the page sent
          retell_llm_dynamic_variables: body.retell_llm_dynamic_variables,
          metadata: { source: "local-test-page", client: slug },
        }),
      });
      const text = await upstream.text();
      const headers = { "Content-Type": "application/json" };
      for (const h of ["x-retell-client-js-sdk-min-version", "x-retell-client-js-sdk-recommended-version"]) {
        const v = upstream.headers.get(h);
        if (v) headers[h] = v;
      }
      res.writeHead(upstream.status, headers);
      if (upstream.ok) console.log(`web call started: ${JSON.parse(text).call_id}`);
      else console.error(`create-web-call failed: HTTP ${upstream.status} ${text.slice(0, 200)}`);
      return res.end(text);
    }
    res.writeHead(404).end("not found");
  } catch (e) {
    console.error(e);
    res.writeHead(500).end("server error");
  }
});
server.listen(port, () => console.log(`Voice test page for ${clientName}: http://localhost:${port}`));
