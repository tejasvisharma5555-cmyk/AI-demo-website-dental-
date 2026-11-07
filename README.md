# DialPilot AI — demo website

Static one-page site (`index.html`, no build step) for DialPilot AI. It embeds the
existing Retell AI voice agent **"Luxe Hair Salon DEMO - Sophia"**
(`agent_7dd2e9e07fd10fc34d66dd5efb`) with Retell's official widget
(`retell-widget-v2.js`) in **voice-only** mode, so visitors can talk to it from their browser.

## Run locally

```bash
python3 -m http.server 8080
```

Open http://localhost:8080. `localhost` counts as a secure context, so the microphone works there.
In production, serve the site over **HTTPS**.

## Retell widget

The widget `<script id="retell-widget">` tag sits in the `<head>` of `index.html`.
It uses only the voice attributes (`data-voice-public-key` and `data-voice-agent-id`), so chat mode stays off.
The key in that tag is a Retell **public** key. Never commit a private Retell API key.

If you restrict the public key to certain domains (Retell Dashboard → Settings → Public Keys),
add every domain that hosts this page, including `localhost` for local testing.
