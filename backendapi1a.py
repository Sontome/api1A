import asyncio
import time
import random
import string
import json
import httpx
from createNewSession import createNewSession

# ================== SESSION HANDLER ==================
SESSIONS = {}
SESSION_TTL = 900  # 15 phút

def generate_jsession():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def create_new_session(jsession_id=None):
    if jsession_id is None:
        jsession_id = generate_jsession()
    SESSIONS[jsession_id] = {
        "cryptic": createNewSession(),
        "created_at": time.time()
    }
    return jsession_id

def get_session(jsession_id):
    if jsession_id is None:
        return None
    session = SESSIONS.get(jsession_id)
    if not session:
        return None
    if time.time() - session["created_at"] > SESSION_TTL:
        del SESSIONS[jsession_id]
        return None
    return session["cryptic"]

def cleanup_sessions():
    now = time.time()
    expired = [sid for sid, s in SESSIONS.items() if now - s["created_at"] > SESSION_TTL]
    for sid in expired:
        del SESSIONS[sid]
    if expired:
        print(f"🗑 Đã xóa {len(expired)} session hết hạn")

def loadJsession(jsession_id=None):
    session = get_session(jsession_id)
    if session is None:
        ssid = create_new_session(jsession_id)
        session = get_session(ssid)
        return [ssid, session]
    cleanup_sessions()
    return [jsession_id, session]


# ================== HTTPX CLIENT ==================
url = "https://tc345.resdesktop.altea.amadeus.com/cryptic/apfplus/modules/cryptic/cryptic?SITE=AVNPAIDL&LANGUAGE=GB&OCTX=ARDW_PROD_WBP"
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "referer": "https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/init/login?SITE=AVNPAIDL&LANGUAGE=GB&MARKETS=ARDW_PROD_WBP&ACTION=clpLogin",
}

with open("cookie1a.json", "r", encoding="utf-8") as f:
    cookies_raw = json.load(f)
COOKIES = {c["name"]: c["value"] for c in cookies_raw} if isinstance(cookies_raw, list) else cookies_raw


async def send_command(client: httpx.AsyncClient, command_str: str, ssid=None):
    ssid, cryp = loadJsession(ssid)
    jSessionId = cryp["jSessionId"]
    contextId = cryp["dcxid"]
    userId = cryp["officeId"]
    organization = cryp["organization"]

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
    resp = await client.post(url, headers=headers, cookies=COOKIES, data=data, timeout=30)
    return ssid, resp


# ================== BUSINESS LOGIC ==================
async def process_row(client: httpx.AsyncClient, row, ssid):
    """Xử lý 1 row combo (dùng lại ssid từ checkve1A)"""
    results = []

    for seg in row:
        print(f"👉 [Task] Đang check {seg}")
        ssid, res = await send_command(client, seg, ssid)
        #print("KQ seg:", res.text[:50])

        ssid, res = await send_command(client, "fxr/ky/rvfr,u", ssid)
        giachuyenbay = json.loads(res.text)
        giachuyenbay = giachuyenbay["model"]["output"]["crypticResponse"]["response"]
        print("KQ fxr:", giachuyenbay[:200])

        results.append({
            "combo": seg,
            "giachuyenbay": giachuyenbay
        })

        ssid, res = await send_command(client, "XE1,2", ssid)
        
    ssid, res = await send_command(client, "IG", ssid)
    return results


async def checkve1A(code,ssid=None):
    start_time = time.time()
    all_results = []

    async with httpx.AsyncClient(http2=False) as client:
        # chỉ gọi send_command lần đầu ở đây
        ssid, res = await send_command(client, code)
        data = json.loads(res.text)

        segments = data["model"]["output"]["speedmode"]["structuredResponse"]["availabilityResponse"]
        all_segments = []
        for segment in segments:
            j_list = []
            for group in segment["core"]:
                for leg in group:
                    for line in leg["line"]:
                        display = line["display"]

                        if any(item.get("v") == "KE" and item.get("c") == 2 for item in display):
                            continue

                        stt = next(
                            (item["v"].strip() for item in display if item.get("c") == 1 and item.get("v").strip()),
                            None
                        )

                        if stt and any(item.get("v", "").startswith("J") for item in display):
                            j_list.append(f"J{stt}")
            all_segments.append(j_list)

        combos = []
        if len(all_segments) >= 2:
            chieu_di = all_segments[0]
            chieu_ve = all_segments[1]
            for d in chieu_di:
                row = []
                for v in chieu_ve:
                    row.append(f"SS1{d}*{v}")
                combos.append(row)

        print("Tổ hợp:", combos)

        for row in combos:
            res_row = await process_row(client, row, ssid)
            all_results.extend(res_row)

    with open("ketqua.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"⏱️ Tổng thời gian chạy: {time.time() - start_time:.2f} giây")
    return combos


if __name__ == "__main__":
    asyncio.run(checkve1A("ANVN19AUGICNHAN*22AUG","TEST"))
