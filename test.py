import requests
from bs4 import BeautifulSoup
import json
import os

def save_request_response(name, req, resp, cookies):
    os.makedirs("debug", exist_ok=True)

    # Lưu request
    with open(f"debug/{name}.req.txt", "w", encoding="utf-8") as f:
        f.write(f"URL: {req.url}\n")
        f.write(f"Method: {req.method}\n")
        f.write("Headers:\n")
        for k, v in req.headers.items():
            f.write(f"  {k}: {v}\n")
        if req.body:
            f.write("\nBody:\n")
            if isinstance(req.body, bytes):
                f.write(req.body.decode(errors="ignore"))
            else:
                f.write(str(req.body))

    # Lưu response
    with open(f"debug/{name}.resp.txt", "w", encoding="utf-8") as f:
        f.write(f"Status: {resp.status_code}\n")
        f.write("Headers:\n")
        for k, v in resp.headers.items():
            f.write(f"  {k}: {v}\n")
        f.write("\nBody:\n")
        f.write(resp.text)

    # Lưu cookie
    with open(f"debug/{name}.cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)


# ----------------- STEP 1 -----------------
url1 = "https://www.accounts.amadeus.com/LoginService/authorizeAngular?service=ARD_VN_DC"
session = requests.Session()

resp1 = session.get(url1, headers={
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "vi-VN,vi;q=0.9",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
})

save_request_response("step1", resp1.request, resp1, session.cookies.get_dict())

# Parse LID
soup = BeautifulSoup(resp1.text, "html.parser")
lid_tag = soup.find("meta", attrs={"lid": True})
lid_value = lid_tag["lid"] if lid_tag else None
clp_tag = soup.find("meta", attrs={"clp-version": True})
clp_value = clp_tag["clp-version"] if clp_tag else None
if not lid_value:
    raise Exception("Không tìm thấy LID trong HTML step1")
print("[*] LID:", lid_value)
print("[*] CLP:", clp_value)

# ----------------- STEP 2 -----------------
url2 = "https://www.accounts.amadeus.com/LoginService/ng/localization/locale_en_GB.json?v="+clp_value+"&origin=https://www.accounts.amadeus.com"
headers2 = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9",
    "lid": lid_value,
    "referer": url1,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}
resp2 = session.get(url2, headers=headers2)

save_request_response("step2", resp2.request, resp2, session.cookies.get_dict())

print("[*] Done, đã lưu request/response + cookies vào thư mục debug/")

# ----------------- STEP 3 -----------------
url3 = "https://www.accounts.amadeus.com/LoginService/services/rs/auth2.0/init?service=ARD_VN_DC"

headers3 = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9",
    "lid": lid_value,
    "referer": url1,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}
resp3 = session.post(url3, headers=headers3)

save_request_response("step3", resp3.request, resp3, session.cookies.get_dict())

print("[*] Done, đã lưu request/response + cookies vào thư mục debug/")
# ----------------- STEP 4 -----------------

url4 = "https://www.accounts.amadeus.com/LoginService/ng/localization/locale_de_DE.json?v="+clp_value+"&origin=https://www.accounts.amadeus.com"

headers4 = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9",
    "lid": lid_value,
    "referer": url1,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}
resp4 = session.get(url4, headers=headers4)

save_request_response("step4", resp4.request, resp4, session.cookies.get_dict())

print("[*] Done, đã lưu request/response + cookies vào thư mục debug/")