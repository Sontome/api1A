import time
import random
import string
import json
import requests
from createNewSession import createNewSession

# Lưu session vào dict: {jsession_id: {"cryptic": "...", "created_at": ...}}
SESSIONS = {}
SESSION_TTL = 900  # 15 phút

def generate_jsession():
    """Tạo ID session ngẫu nhiên"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def create_new_session(jsession_id=None):
    """Tạo session mới"""
    if jsession_id == None:
        jsession_id = generate_jsession()
    SESSIONS[jsession_id] = {
        "cryptic": createNewSession(),
        "created_at": time.time()
    }
    return jsession_id

def get_session(jsession_id):
    if jsession_id== None:
        return None
    """Lấy session nếu tồn tại và chưa hết hạn"""
    session = SESSIONS.get(jsession_id)
    if not session:
        return None
    if time.time() - session["created_at"] > SESSION_TTL:
        del SESSIONS[jsession_id]
        return None
    return session["cryptic"]

def cleanup_sessions():
    """Xóa session hết hạn"""
    now = time.time()
    expired = [sid for sid, s in SESSIONS.items() if now - s["created_at"] > SESSION_TTL]
    for sid in expired:
        del SESSIONS[sid]
    if expired:
        print(f"🗑 Đã xóa {len(expired)} session hết hạn")

# ===== Ví dụ chạy thử =====
def loadJsession(jsession_id=None):
    session = get_session(jsession_id)

    if session ==None:
        ssid = create_new_session(jsession_id)
        session = get_session(ssid)
        return [ssid,session]
    

    # Dọn dẹp session hết hạn
    cleanup_sessions()
    return [jsession_id,session]
#print(loadJsession("jmJZrH2LuAtIuoFJ"))

url = "https://tc345.resdesktop.altea.amadeus.com/cryptic/apfplus/modules/cryptic/cryptic?SITE=AVNPAIDL&LANGUAGE=GB&OCTX=ARDW_PROD_WBP"

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
    "referer": "https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/init/login?SITE=AVNPAIDL&LANGUAGE=GB&MARKETS=ARDW_PROD_WBP&ACTION=clpLogin",
}
def send_command(command_str: str,ssid=None):
     # ===== Load cookie =====
    with open("cookie1a.json", "r", encoding="utf-8") as f:
        cookies_raw = json.load(f)
    if isinstance(cookies_raw, list):
        cookies = {c["name"]: c["value"] for c in cookies_raw}
    else:
        cookies = cookies_raw

    session = requests.Session()
    session.cookies.update(cookies)
    ssid,cryp = loadJsession(ssid)
    jSessionId= cryp["jSessionId"]
    contextId=cryp["dcxid"]
    userId=cryp["officeId"]
    organization=cryp["organization"]
    payload = {
        "jSessionId": jSessionId,
        "contextId": contextId,
        "userId": userId,
        "organization": organization,
        "officeId": userId,
        "gds": "AMADEUS",
        "tasks": [
            {
                "type": "CRY",
                "command": {
                    "command": command_str,
                    "prohibitedList": "SITE_JCPCRYPTIC_PROHIBITED_COMMANDS_LIST_1"
                }
            },
            {
                "type": "ACT",
                "actionType": "speedmode.SpeedModeAction",
                "args": {
                    "argsType": "speedmode.SpeedModeActionArgs",
                    "obj": {}
                }
            }
        ]
    }

    data = {"data": json.dumps(payload, separators=(",", ":"))}

    resp = session.post(url, headers=headers, data=data)
    return resp

# ví dụ gọi thử
if __name__ == "__main__":
    
    r = send_command("AN25JULICNHAN","test0")
    print(r.status_code)
    print(r.text)