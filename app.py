from flask import Flask, request, Response, jsonify
import requests
import asyncio
import httpx
import threading
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# توكنات UID : Password
SPAM_TOKENS = {
    "3703466495": "799FAF292960B85062BCD462FD8116871F99B4A0505C09FFC6985AA1C32F31EA",
    "3570958179": "C15AB416AB9FFF0D33F1C7950C75D950135A4DA42692D9433FF736BD5385F7B3",
    "3571002164": "3D253727E7D7D4EC5CCC188398EABB9A94539579D7F7A041FDE5B268362AFF67",
}

app = Flask(__name__)

PORT = int(os.environ.get('PORT', 8398))
SELF_URL = os.environ.get("SELF_URL", f"http://127.0.0.1:{PORT}")

# Cache للتوكنات
JWT_CACHE = {}

def get_jwt(uid, password):
    url = f"https://jwt-gen-api-v2.onrender.com/token?uid={uid}&password={password}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                return data["token"]
        print(f"[JWT-ERROR] {uid}: {response.text}")
        return None
    except Exception as e:
        print(f"[JWT-EXCEPTION] {uid}: {e}")
        return None

async def async_add_fr(player_id, token):
    try:
        # استخدم player_id للـ uid في الطلب، token خاص بالحساب المرسل
        proxy_url = f"https://panel-friend-bot.vercel.app/request?token={token}&uid={player_id}"
        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.get(proxy_url)
            return f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"Error: {e}"

def refresh_tokens_background():
    while True:
        print("[DEBUG] Refreshing all JWT tokens...")
        for uid, pw in SPAM_TOKENS.items():
            token = get_jwt(uid, pw)
            if token:
                JWT_CACHE[uid] = token
                print(f"[JWT] {uid} -> Token updated successfully")
            else:
                print(f"[JWT] {uid} -> Failed to get token")
        print(f"[DEBUG] Current JWT_CACHE keys: {list(JWT_CACHE.keys())}")
        time.sleep(3600)

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

def generate(player_id):
    yield f"📨 Sending friend requests to player {player_id}...\n\n"
    for uid, pw in SPAM_TOKENS.items():
        token = JWT_CACHE.get(uid)
        if not token:
            yield f"❌ No JWT for {uid}\n"
            continue
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_add_fr(player_id, token))
        yield f"{uid} ➤ {result}\n"

@app.route("/spam")
def spam():
    player_id = request.args.get("id")
    if not player_id:
        return "Please provide ?id=UID"
    return Response(generate(player_id), content_type="text/plain")

@app.route("/tokens")
def show_tokens():
    # عرض محتويات الـ JWT_CACHE للتحقق من التوكنات المحفوظة
    return jsonify({uid: (token[:20] + "...") for uid, token in JWT_CACHE.items()})

if __name__ == "__main__":
    threading.Thread(target=refresh_tokens_background, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)