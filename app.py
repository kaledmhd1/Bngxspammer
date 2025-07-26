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

# ----------- ENCRYPTION ------------
def Encrypt_ID(x):
    x = int(x)
    dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                m = (n - int(strn)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
            else:
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()
# -----------------------------------

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
        proxy_url = f"https://panel-friend-bot.vercel.app/request?token={token}&uid={uid}"
        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.get(proxy_url)
            return f"{player_id} -> HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"Error for {player_id}: {e}"

def refresh_tokens_background():
    while True:
        print("[DEBUG] Refreshing all JWT tokens...")
        for uid, pw in SPAM_TOKENS.items():
            token = get_jwt(uid, pw)
            if token:
                JWT_CACHE[uid] = token
                print(f"[JWT] {uid} -> Token OK")
            else:
                print(f"[JWT] {uid} -> Failed")
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

if __name__ == "__main__":
    threading.Thread(target=refresh_tokens_background, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)