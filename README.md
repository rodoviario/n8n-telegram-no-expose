# 🚀 Telegram Poller with Python + Docker + n8n
---
This guide walks you through setting up a local Telegram polling script that works seamlessly with n8n's Webhook Trigger-without needing to expose your instance publicly or configure a reverse proxy.

✅ No publishing or public endpoints required
🖥️ Perfect for local or self-hosted n8n setups
🆓 Free and self-contained
🐳 Requires only Docker-no ngrok, no third-party tunnels

With this setup, Telegram messages are fetched via polling and forwarded directly to your local n8n workflows using a webhook.
---

## 📁 Create Project Directory

```bash
mkdir telegram-poller && cd telegram-poller
touch .env Dockerfile poller.py
```

---

## ⚙️ .env

```env
BOT_TOKEN=telegram_bot_token_here
N8N_URL=http://n8n:5678/webhook/telegram-local
```

---

## 🐳 Dockerfile

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY poller.py .

RUN pip install requests

CMD ["python", "poller.py"]
```

---

## 🐍 poller.py

```python
import time
import os
import requests
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN")
N8N_URL = os.environ.get("N8N_URL", "http://n8n:5678/webhook/telegram-local")
offset = 0

print(f"🟢 Starting Telegram Poller")
print(f"📡 BOT_TOKEN set: {'Yes' if BOT_TOKEN else 'No'}")
print(f"🌐 n8n URL: {N8N_URL}\n")

while True:
    try:
        res = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params={"offset": offset + 1, "timeout": 10}
        )
        res.raise_for_status()
        updates = res.json()

        if updates.get("result"):
            print(f"📥 Received {len(updates['result'])} update(s)")

        for update in updates.get("result", []):
            offset = update["update_id"]
            print(f"\n➡️ Sending update to n8n:")
            print(f"POST {N8N_URL}")
            print("Payload:")
            print(json.dumps(update, indent=2))

            try:
                webhook_response = requests.post(N8N_URL, json=update)
                print(f"✅ Webhook response: {webhook_response.status_code} {webhook_response.text}")
            except Exception as we:
                print(f"❌ Error posting to webhook: {we}")

        time.sleep(2)

    except Exception as e:
        print(f"❌ Polling error: {e}")
        time.sleep(5)
```

---

---
## Create shared network
```bash
docker network create n8n-net
```
---

## 🐋 Run the Docker Containers

**n8n container:**

```bash
docker run -it --rm --name n8n \
  --network n8n-net \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

**Telegram Poller container:**

```bash
docker run -it --rm --name telegram-poller \
  --network n8n-net \
  --env-file .env \
  telegram-poller
```

---

## 🌐 n8n Webhook Setup

1. **Create a Webhook Trigger node**
2. Set:
   - **HTTP Method**: `POST`
   - **Path**: `telegram-local`
   - **Authentication**: `None`
   - **Respond**: `Immediately`
3. Use the following **Production URL**:

```
http://localhost:5678/webhook/telegram-local
```

---

✅ Done! Your Telegram bot updates are now piped directly into your n8n workflows.
