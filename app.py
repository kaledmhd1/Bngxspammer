from flask import Flask, request, Response
import asyncio
import httpx
import json
import os
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
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
    data = bytes.fromhex(encrypt_api(f'08a7c4839f1e10{Encrypt_ID(target_id)}1801'))
    async with httpx.AsyncClient(verify=False, timeout=60) as client:
        try:
            response = await client.post(url, data=data)
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
        return "Please provide ?id=UID"
    def generate():
        yield f"📨 Sending friend requests to {target_id}...\n"
        for r in spam_task(target_id):
            yield r + "\n"
    return Response(generate(), content_type="text/plain")


# <<<--- التغيير المهم هنا --->
print("[INFO] Initial token refresh (app load)...")
refresh_tokens()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8398))
    app.run(host="0.0.0.0", port=port, debug=True)
