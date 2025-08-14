from playwright.sync_api import sync_playwright
import re
import json
import xml.etree.ElementTree as ET

USERNAME = "SEL28AA8"
PASSWORD = "Bkdfasdv@203414"

def getIDvsENC(xml_data):
    try:
        root = ET.fromstring(xml_data)
        # Lấy CDATA trong <framework>
        framework_json_str = root.find("framework").text.strip()
        framework_data = json.loads(framework_json_str)
        session_id = framework_data["session"]["id"]

        # Lấy CDATA trong <data>
        data_json_str = root.find("data").text.strip()
        data_data = json.loads(data_json_str)
        encryption_key = data_data["model"]["output"]["encryptionKey"]

        return {
            "ID": session_id,
            "EncryptionKey": encryption_key
        }
    except:
        return None

def extract_jsessionid(url):
    match = re.search(r';jsessionid=([^?]+)', url, re.IGNORECASE)
    return match.group(1) if match else None


def login(username=USERNAME, password=PASSWORD):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("[*] Đang chờ request có jsessionid...")

        # Bắt event response cho đúng request
        def is_target_response(res):
            return "createSessionKey" in res.url and ";jsessionid=" in res.url.lower()

        # Mở trang login
        page.goto("https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/init/login?SITE=AVNPAIDL&LANGUAGE=GB&MARKETS=ARDW_PROD_WBP&ACTION=clpLogin")

        # Nhập username
        page.wait_for_selector("#userAliasInput")
        page.fill("#userAliasInput", username)
        page.click('button[type="submit"]')

        # Nhập password
        page.wait_for_selector("#passwordInput")
        page.fill("#passwordInput", password)
        page.click('button[type="submit"]')

        # Accept popup nếu có
        try:
            page.wait_for_selector('#privateDataDiscOkButton', timeout=5000)
            page.click('#privateDataDiscOkButton')
        except:
            pass

        # Chờ response đúng điều kiện
        try:
            res = page.wait_for_event("response", timeout=60000, predicate=is_target_response)
        except:
            print("[❌] Không bắt được createSessionKey trong 60s")
            browser.close()
            return None

        # Lấy dữ liệu
        try:
            body = res.json()
        except:
            try:
                body = res.text()
            except:
                body = "<Không đọc được body>"

        jsession_data = getIDvsENC(body)
        if jsession_data:
            # Lưu session_log.json
            with open("session_log.json", "w", encoding="utf-8") as f:
                json.dump(jsession_data, f, indent=2, ensure_ascii=False)

            # Lưu cookies
            cookies = page.context.cookies()
            with open("cookie1a.json", "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)

            #print("[✅] Login thành công:", jsession_data)
            
            return {"status": "OK", "session": jsession_data}
        else:
            print("[❌] Không lấy được ID/EncryptionKey")
            
            return None


if __name__ == "__main__":
    result = login()
    if result:
        print(result)
    else:
        print("Login lỗi")