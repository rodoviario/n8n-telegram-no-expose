import time
import os
import requests
import json
from urllib.parse import urljoin

BOT_TOKEN = os.environ.get("BOT_TOKEN")
N8N_URL = os.environ.get("N8N_URL", "http://n8n:5678/webhook/")
N8N_TEST_URL = os.environ.get("N8N_TEST_URL", "http://n8n:5678/webhook-test/")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "telegram-local")

offset = 0

WEBHOOK_URL = urljoin(N8N_URL, WEBHOOK_PATH)
WEBHOOK_TEST_URL = urljoin(N8N_TEST_URL, WEBHOOK_PATH)

print(f"🟢 Starting Telegram Poller")
print(f"📡 BOT_TOKEN set: {'Yes' if BOT_TOKEN else 'No'}")
print(f"🌐 n8n URL: {WEBHOOK_URL}\n")
print(f"🌐 n8n Test URL: {WEBHOOK_TEST_URL}\n")

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
            print(f"POST {WEBHOOK_URL}")
            print("Payload:")
            print(json.dumps(update, indent=2))

            try:
                webhook_response = requests.post(WEBHOOK_URL, json=update, verify=False)
                print(f"✅ Webhook response: {webhook_response.status_code} {webhook_response.text}")
            except Exception as we:
                print(f"❌ Error posting to webhook: {we}")

            print(f"POST {WEBHOOK_TEST_URL}")

            try:
                webhook_response = requests.post(WEBHOOK_TEST_URL, json=update, verify=False)
                print(f"✅ Test webhook response: {webhook_response.status_code} {webhook_response.text}")
            except Exception as we:
                print(f"⚠️ Error posting to test webhook: {we}. Maybe its disabled.")


        time.sleep(2)

    except Exception as e:
        print(f"❌ Polling error: {e}")
        time.sleep(5)
