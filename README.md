# 🚀 Telegram Poller with Python + Docker + n8n
---
This guide walks you through setting up a local Telegram polling script that works seamlessly with n8n's Webhook Trigger-without needing to expose your instance publicly or configure a reverse proxy.

✅ No publishing or public endpoints required
🖥️ Perfect for local or self-hosted n8n setups
🆓 Free and self-contained
🐳 Requires only Docker - no ngrok, no third-party tunnels

With this setup, Telegram messages are fetched via polling and forwarded directly to your local n8n workflows using a webhook.
---

## 📁 Create Project Directory

```bash
mkdir telegram-poller && cd telegram-poller
touch .env Dockerfile poller.py
```

**OR GIT CLONE THIS REPO:**
```bash
git clone https://github.com/rodoviario/n8n-telegram-no-expose.git telegram-poller && cd telegram-poller
touch .env
```

---

## ⚙️ .env

```env
BOT_TOKEN=telegram_bot_token_here
N8N_URL=http://n8n:5678/webhook/ # IMPORTANT: both URLs must have a trailing '/'
N8N_TEST_URL=http://n8n:5678/webhook-test/ # IMPORTANT: both URLs must have a trailing '/'
WEBHOOK_PATH=telegram-local
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
docker build --network=host -t telegram-poller .

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
