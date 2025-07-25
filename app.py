from flask import Flask, request, Response, jsonify
import requests
import asyncio
import httpx
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# هنا تحط التوكنات (uid: password)
SPAM_TOKENS = {
    "4064887738": "11ED400B94AC97D3CA736299F1C89D09FDF843FE7ACE372DB85E2F35EC2F7DCC",
    "4064903378": "372397C2910AB98D5C60FCE54B767945CC89D874CD94F56816F34ED9C5FC75E1",
    "4064912372": "BD879CE620A1630335B482F2D757DD20E831706EFAC06C242E9ED15419CFA4A5",
    "4064986315": "DF07BD8D249EC8C80D4D3235FC1ED00EEE46A9E03C80192A187EB8FA40D7A2F1",
    "4064994323": "231170C6A0ED62D9BA944D89CBC4D6A55CB3F2418E5DCEDE7033FA9C799066D9",
    "4065003464": "2D1C991FEBA993FA72D0CC72221DF7E6E62325666E3374D47860B141FC365872",
    "4065012898": "59B63789275C7714D2DC020585F8DAB05DCEBC67515646C04ECA0F4B1E0F1450",
    "4026743904": "ADA04243B15C2F0D789E63B919749CEB4ECCEEBF982CC4371B9FBEC5231FE556",
    "4065074223": "72091CDD3ACE17349E0AB0C10B39062691B3212BAFFA957CBE1BB1390CADD63D",
    "4065081566": "67F566A5B0EFB517459233BEDCDE4BB4FEAE306E28303EBE698F8C6AFE832DA3"
}

app = Flask(__name__)

retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=frozenset(["GET", "POST"]),
)

session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# سنحتاجه لاستدعاء البروكسي محلياً
PORT = int(os.environ.get('PORT', 8398))
SELF_URL = os.environ.get("SELF_URL", f"http://127.0.0.1:{PORT}")

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

def get_jwt(uid, password):
    api_url = f"https://jwt-gen-api-v2.onrender.com/token?uid={uid}&password={password}"
    try:
        response = session.get(api_url, verify=False, timeout=30)
        print(f"[DEBUG] UID {uid} -> {response.status_code}: {response.text}")
        if response.status_code == 200:
            data = response.json()
            # نقبل أي status ما دام فيه token
            if "token" in data:
                return data["token"]
            else:
                print(f"Failed to get JWT for {uid}: {data}")
                return None
        else:
            print(f"API request failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for {uid}: {e}")
        return None

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

# --------- البروكسي الذي يستدعي Vercel بشكل غير مباشر ----------
@app.route("/proxy_vercel")
def proxy_vercel():
    token = request.args.get("token")
    uid = request.args.get("uid")
    if not token or not uid:
        return jsonify({"error": "Missing token or uid"}), 400

    try:
        url = f'https://panel-friend-bot.vercel.app/request?token={token}&uid={uid}'
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB49',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Authorization': f'Bearer {token}',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'clientbp.ggblueshark.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        data = bytes.fromhex(encrypt_api(f'08a7c4839f1e10{Encrypt_ID(uid)}1801'))

        r = session.post(url, headers=headers, data=data, verify=False, timeout=60)
        return Response(r.text, status=r.status_code, content_type=r.headers.get("content-type", "text/plain"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ---------------------------------------------------------------

async def async_add_fr(id, token):
    # نستدعي البروكسي المحلي بدل Vercel مباشرة
    proxy_url = f'{SELF_URL}/proxy_vercel?token={token}&uid={id}'
    async with httpx.AsyncClient(verify=False, timeout=60) as client:
        response = await client.get(proxy_url)
        text = response.text
        status_code = response.status_code

        if status_code == 400 and 'BR_FRIEND_NOT_SAME_REGION' in text:
            return f'Id : {id} Not In Same Region !'
        elif status_code == 200:
            # ممكن هنا يكون 200 لكن فيه رسائل أخرى داخل text؛ عالجها حسب ما تريد
            if 'BR_FRIEND_MAX_REQUEST' in text:
                return f'Id : {id} Reached Max Requests !'
            elif 'BR_FRIEND_ALREADY_SENT_REQUEST' in text:
                return f'Token Already Sent Requests To Id : {id}!'
            else:
                return f'Good Response Done Send To Id : {id}!'
        else:
            # رجّع محتوى الريسبونس للديبغ
            return f'HTTP {status_code}: {text[:200]}'

def send_requests_in_background(id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [async_add_fr(id, get_jwt(uid, pw)) for uid, pw in SPAM_TOKENS.items()]
    responses = loop.run_until_complete(asyncio.gather(*tasks))
    print("All requests sent:", responses)

def generate(id):
    yield f"📨 Sending friend requests to player {id}...\n\n"
    for uid, pw in SPAM_TOKENS.items():
        token = get_jwt(uid, pw)
        if not token:
            yield f"❌ Failed to get JWT for {uid}\n"
            continue
        # تحذير: asyncio.run داخل جنريتور قد يعمل مشاكل في بيئات معينة
        result = asyncio.run(async_add_fr(id, token))
        yield f"{uid} ➤ {result}\n"

@app.route('/spam')
def index():
    id = request.args.get('id')
    if id:
        return Response(generate(id), content_type='text/plain')
    else:
        return "Please provide a valid ID."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)