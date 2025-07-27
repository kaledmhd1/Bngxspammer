from flask import Flask, request, Response
import asyncio
import httpx
import json
import os
import threading
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

ACCS_FILE = "accs.txt"  # ملف الحسابات
TOKENS = {}             # تخزين التوكنات في الذاكرة
LOCK = threading.Lock()

retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
)
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)


def load_accounts():
    if not os.path.exists(ACCS_FILE):
        print(f"[ERROR] {ACCS_FILE} not found!")
        return {}
    with open(ACCS_FILE, "r") as f:
        content = f.read().strip()
        try:
            data = json.loads(content or "{}")
            print(f"[DEBUG] Loaded {len(data)} accounts")
            return data
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            return {}


def get_jwt(uid, password):
    api_url = f"https://jwt-gen-api-v2.onrender.com/token?uid={uid}&password={password}"
    try:
        response = session.get(api_url, verify=False, timeout=30)
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"[DEBUG] JWT for {uid}: {token}")
            return token
        else:
            print(f"[ERROR] Failed to get JWT for {uid}, status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception in get_jwt for {uid}: {e}")
    return None


def refresh_tokens():
    accounts = load_accounts()
    global TOKENS
    new_tokens = {}
    for uid, pw in accounts.items():
        token = get_jwt(uid, pw)
        if token:
            new_tokens[uid] = token
            print(f"[REFRESHED] {uid}")
        else:
            print(f"[FAILED] {uid}")
    with LOCK:
        TOKENS = new_tokens
    print(f"[INFO] Tokens refreshed: {len(TOKENS)} active.")
    threading.Timer(3600, refresh_tokens).start()


async def async_add_fr(uid, token, target_id):
    url = f'https://panel-friend-bot.vercel.app/request?token={token}&uid={target_id}'
    async with httpx.AsyncClient(verify=False, timeout=60) as client:
        try:
            response = await client.get(url)
            text = response.text
            if "Invalid token" in text or response.status_code == 401:
                with LOCK:
                    TOKENS.pop(uid, None)
                print(f"[REMOVED] {uid} (Invalid Token)")
                return f"{uid} ➤ Invalid token (REMOVED)"
            elif response.status_code == 200:
                return f"{uid} ➤ Success for {target_id}"
            return f"{uid} ➤ {text}"
        except Exception as e:
            return f"{uid} ➤ ERROR {e}"


def spam_task(target_id):
    with LOCK:
        tokens = TOKENS.copy()
    if not tokens:
        return ["No valid tokens available!"]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [async_add_fr(uid, token, target_id) for uid, token in tokens.items()]
    return loop.run_until_complete(asyncio.gather(*tasks))


@app.route("/spam")
def spam_endpoint():
    target_id = request.args.get("id")
    if not target_id:
        return "الرجاء إدخال ?id=UID", 400

    results = spam_task(target_id)  # تنفذ كل الطلبات وترجع قائمة النتائج

    success_count = 0
    fail_count = 0

    for res in results:
        if "Success" in res:
            success_count += 1
        elif "Invalid token" in res or "ERROR" in res:
            fail_count += 1
        else:
            fail_count += 1  # احتياطياً نعد أي شيء غير واضح كفشل

    return f"تم إرسال {success_count} طلب بنجاح، وفشل {fail_count} طلب."

print("[INFO] Initial token refresh (app load)...")
refresh_tokens()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8398))
    app.run(host="0.0.0.0", port=port, debug=True)
