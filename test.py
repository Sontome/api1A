import requests
import json
import re
import xml.etree.ElementTree as ET
# ===== Load LOG_PARENT_JSESSIONID & ENC từ sessionlog.json =====
with open("session_log.json", "r", encoding="utf-8") as f:
    session_data = json.load(f)

LOG_PARENT_JSESSIONID = session_data.get("ID")
ENC_PARENT = session_data.get("EncryptionKey")

# ===== Load cookie =====
with open("cookie1a.json", "r", encoding="utf-8") as f:
    cookies_raw = json.load(f)
if isinstance(cookies_raw, list):
    cookies = {c["name"]: c["value"] for c in cookies_raw}
else:
    cookies = cookies_raw
url = "https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/do/home.taskmgr/UMCreateSessionKey;jsessionid=" + LOG_PARENT_JSESSIONID

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/init/login?SITE=AVNPAIDL&LANGUAGE=GB&MARKETS=ARDW_PROD_WBP&ACTION=clpLogin",
}

data = {
    "flowExKey": "e14s1",
    "initialAction": "newCrypticSession",
    "recordLocator": "[object PointerEvent]",
    "ctiAcknowledge": "false",
    "LOG_PARENT_JSESSIONID": LOG_PARENT_JSESSIONID,
    "waiAria": "false",
    "SITE": "AVNPAIDL",
    "LANGUAGE": "GB",
    "aria.target": "body",
    "aria.panelId": "3"
}

session = requests.Session()
session.cookies.update(cookies)

resp = session.post(url, headers=headers, data=data)

print("Status code:", resp.status_code)

with open("createNewSession.txt", "w", encoding="utf-8") as f:
    f.write(resp.text)
match = re.search(r'<!\[CDATA\[(.*?)\]\]>', resp.text, re.S)
if match:
    json_text = match.group(1).strip()

    # Lọc bỏ khoảng trắng, xuống dòng thừa
    json_text = json_text.strip()

    # Trường hợp bên trong có nhiều dòng rác, chỉ lấy dòng có "ENC":
    enc_match = re.search(r'\"ENC\":\"([A-F0-9]+)\"', json_text)
    if enc_match:
        ENC = enc_match.group(1)
        print("ENC =", ENC[:-9])
    else:
        print("Không tìm thấy ENC")
else:
    print("Không tìm thấy CDATA")
url = "https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/do/loginNewSession.UM/login"

# Headers
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/init/login?SITE=AVNPAIDL&LANGUAGE=GB&MARKETS=ARDW_PROD_WBP&ACTION=clpLogin"
}

# Payload dạng dict cho dễ thay đổi
payload = {
    "LANGUAGE": "GB",
    "SITE": "AVNPAIDL",
    "MARKETS": "ARDW_PROD_WBP",
    "initialAction": "newCrypticSession",
    "waiAria": "false",
    "LOG_PARENT_JSESSIONID": LOG_PARENT_JSESSIONID,
    "recordLocator": "[object PointerEvent]",
    "ctiAcknowledge": "false",
    "aria.target": "body.main.s2",
    "aria.sprefix": "s2",
    "ENC": ENC,
    "ENCT": "1",
    "aria.panelId": "6"
}

# Nếu cần cookie phiên thì bỏ vô đây


# Gửi request
response = session.post(url, headers=headers, data=payload)

print(response.status_code)
with open("createNewSessionLogin.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
pattern = re.compile(
    r'<templates-init[^>]*moduleId="cryptic"[^>]*><!\[CDATA\[(.*?)\]\]></templates-init>',
    re.DOTALL
)

match = pattern.search(response.text)
if match:
    cdata_content = match.group(1)
    json_data = json.loads(cdata_content)
    with open("crypticjsession.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

    print("CDATA content:\n", cdata_content)
else:
    print("Không tìm thấy CDATA cho moduleId=cryptic")
