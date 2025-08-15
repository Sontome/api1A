import time
import random
import string
from createNewSession import createNewSession

# Lưu session vào dict: {jsession_id: {"cryptic": "...", "created_at": ...}}
SESSIONS = {}
SESSION_TTL = 900  # 15 phút

def generate_jsession():
    """Tạo ID session ngẫu nhiên"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def create_new_session():
    """Tạo session mới"""
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
        ssid = create_new_session()
        session = get_session(ssid)
        return [ssid,session]
    

    # Dọn dẹp session hết hạn
    cleanup_sessions()
    return [jsession_id,session]
#print(loadJsession("jmJZrH2LuAtIuoFJ"))
