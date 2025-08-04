from flask import Flask, request
import asyncio
import httpx
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

ACCS_FILE = "accs.txt"  # ملف الحسابات


async def fetch_jwt(session, uid, password):
    url = f"https://bngx-jwt-pgwb.onrender.com/api/oauth_guest?uid={uid}&password={password}"
    try:
        resp = await session.get(url, timeout=30, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token") or data.get("BearerAuth") or data.get("jwt")  # حسب شكل الاستجابة
            if not token and "BearerAuth" in data:
                token = data["BearerAuth"]
            return uid, token
        else:
            print(f"[ERROR] Failed to get JWT for {uid}, status: {resp.status_code}")
            return uid, None
    except Exception as e:
        print(f"[ERROR] Exception in fetch_jwt for {uid}: {e}")
        return uid, None


async def fetch_all_tokens(accounts):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_jwt(client, uid, pw) for uid, pw in accounts.items()]
        results = await asyncio.gather(*tasks)
        tokens = {uid: token for uid, token in results if token}
        return tokens


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


async def async_add_fr(uid, token, target_id):
    url = f'https://bngx-add-friend.onrender.com/add_friend?token={token}&uid={target_id}'
    async with httpx.AsyncClient(verify=False, timeout=60) as client:
        try:
            response = await client.get(url)
            text = response.text
            if "Invalid token" in text or response.status_code == 401:
                print(f"[REMOVED] {uid} (Invalid Token)")
                return f"{uid} ➤ Invalid token (REMOVED)"
            elif response.status_code == 200:
                return f"{uid} ➤ Success for {target_id}"
            return f"{uid} ➤ {text}"
        except Exception as e:
            return f"{uid} ➤ ERROR {e}"


async def spam_task_async(target_id, tokens):
    tasks = [async_add_fr(uid, token, target_id) for uid, token in tokens.items()]
    results = await asyncio.gather(*tasks)
    return results


@app.route("/spam")
def spam_endpoint():
    target_id = request.args.get("id")
    if not target_id:
        return "الرجاء إدخال ?id=UID", 400

    accounts = load_accounts()
    if not accounts:
        return "لا توجد حسابات متاحة", 500

    tokens = asyncio.run(fetch_all_tokens(accounts))
    if not tokens:
        return "فشل في جلب التوكنات الصالحة", 500

    results = asyncio.run(spam_task_async(target_id, tokens))

    success_count = sum(1 for res in results if "Success" in res)
    fail_count = len(results) - success_count

    return f"تم إرسال {success_count} طلب بنجاح، وفشل {fail_count} طلب."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8398))
    app.run(host="0.0.0.0", port=port, debug=True)
