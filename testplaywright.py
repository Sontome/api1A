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

        print("ID:", session_id)
        print("EncryptionKey:", encryption_key)
        return({
            "ID": session_id,
            "EncryptionKey" :encryption_key
        })
    except:
        return({
            "ID": None,
            "EncryptionKey" :None
        })
def extract_jsessionid(url):
    match = re.search(r';jsessionid=([^?]+)', url, re.IGNORECASE)
    return match.group(1) if match else None

found_session = False
def keepalive():
    pass
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    def on_response(res):
        global found_session  # dùng global thay vì nonlocal
        if found_session:
            return  # đã bắt được thì thôi

        url = res.url
        if "createSessionKey" in url and ";jsessionid=" in url.lower():
            jsid = extract_jsessionid(url)
            try:
                body = res.json()
            except:
                try:
                    body = res.text()
                except:
                    body = "<Không đọc được body>"

            log_data = f"""
[*] Found jsessionid: {jsid}
[*] Full URL: {url}
[*] Response body:
{body}
{"="*80}
"""
            print(log_data)
            jsession = getIDvsENC(body)
            print(jsession)
            # Ghi log vào file
            with open("session_log.json", "w", encoding="utf-8") as f:
                json.dump(jsession, f, indent=2, ensure_ascii=False)
            
            

            # Lưu cookies
            cookies = page.context.cookies()
            with open("cookie1a.json", "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            print("[*] Cookies saved to cookie1a.json")

            found_session = True

    # Bắt sự kiện response
    page.on("response", on_response)

    # Mở trang login
    page.goto("https://tc345.resdesktop.altea.amadeus.com/app_ard/apf/init/login?SITE=AVNPAIDL&LANGUAGE=GB&MARKETS=ARDW_PROD_WBP&ACTION=clpLogin")

    # Nhập username
    page.wait_for_selector("#userAliasInput")
    page.fill("#userAliasInput", USERNAME)
    page.click('button[type="submit"]')

    # Nhập password
    page.wait_for_selector("#passwordInput")
    page.fill("#passwordInput", PASSWORD)
    page.click('button[type="submit"]')

    # Accept nếu có popup
    try:
        page.wait_for_selector('#privateDataDiscOkButton', timeout=5000)
        page.click('#privateDataDiscOkButton')
    except:
        pass

    print("[*] Đang chờ request có jsessionid... Nhấn Ctrl+C để thoát")
    
    
    page.wait_for_timeout(60000000)  # chờ max 60s nhưng không đóng browser
