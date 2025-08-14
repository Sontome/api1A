import requests
import json
import re
import xml.etree.ElementTree as ET

def createNewSession(
    session_log_file="session_log.json",
    cookie_file="cookie1a.json"
):
    try:
        # ===== Load LOG_PARENT_JSESSIONID & ENC từ sessionlog.json =====
        with open(session_log_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)

        LOG_PARENT_JSESSIONID = session_data.get("ID")
        ENC_PARENT = session_data.get("EncryptionKey")

        # ===== Load cookie =====
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookies_raw = json.load(f)
        if isinstance(cookies_raw, list):
            cookies = {c["name"]: c["value"] for c in cookies_raw}
        else:
            cookies = cookies_raw

        session = requests.Session()
        session.cookies.update(cookies)

        # ===== Tạo session key =====
        url_create = f"https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/do/home.taskmgr/UMCreateSessionKey;jsessionid={LOG_PARENT_JSESSIONID}"
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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

        resp = session.post(url_create, headers=headers, data=data)
        if resp.status_code != 200:
            return {"status": "ERROR", "message": "Tạo session key thất bại", "code": resp.status_code}

        # ===== Lấy ENC mới =====
        match = re.search(r'<!\[CDATA\[(.*?)\]\]>', resp.text, re.S)
        if not match:
            return {"status": "ERROR", "message": "Không tìm thấy CDATA trong phản hồi createSessionKey"}
        json_text = match.group(1).strip()
        enc_match = re.search(r'"ENC":"([A-F0-9]+)"', json_text)
        if not enc_match:
            return {"status": "ERROR", "message": "Không tìm thấy ENC trong CDATA"}
        ENC = enc_match.group(1)[:-9]  # cắt 9 ký tự cuối như code cũ

        # ===== Login new session =====
        url_login = "https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/do/loginNewSession.UM/login"
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

        resp_login = session.post(url_login, headers=headers, data=payload)
        if resp_login.status_code != 200:
            print(resp_login.text)
            return {"status": "ERROR", "message": "Login new session thất bại", "code": resp_login.status_code}
            
        # ===== Tìm cryptic session data =====
        pattern = re.compile(
            r'<templates-init[^>]*moduleId="cryptic"[^>]*><!\[CDATA\[(.*?)\]\]></templates-init>',
            re.DOTALL
        )
        match_cryptic = pattern.search(resp_login.text)
        cryptic_data = None
        if match_cryptic:
            cdata_content = match_cryptic.group(1)
            try:
                cryptic_data = json.loads(cdata_content)
                print(cryptic_data)
                with open("crypticjsession.json", "w", encoding="utf-8") as f:
                    json.dump(cryptic_data, f, indent=2, ensure_ascii=False)
                jSessionId = cryptic_data["model"]["jSessionId"]
                language = cryptic_data["model"]["language"]
                defaultActivePluginType = cryptic_data["model"]["defaultActivePluginType"]
                dcxid = cryptic_data["model"]["dcxid"]
                siteCode = cryptic_data["model"]["siteCode"]
                octx = cryptic_data["model"]["octx"]
                organization = cryptic_data["model"]["organization"]
            
            except:
                cryptic_data = None

        return {
            "status": "OK",
            "ENC": ENC,
            "jSessionId": jSessionId,
            "language": language,
            "defaultActivePluginType": defaultActivePluginType,
            "dcxid": dcxid,
            "siteCode": siteCode,
            "octx": octx,
            "organization": organization

        }

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


if __name__ == "__main__":
    result = createNewSession()
    print(result)