# Стан чату

active_user_chats = {}   # user_id → admin_id
active_admin_chats = {}  # admin_id → user_id
waiting_users = set()    # список user_id, які очікують

def request_chat(user_id: int):
    waiting_users.add(user_id)

def list_waiting_users():
    return list(waiting_users)

def start_chat(admin_id: int, user_id: int):
    print(f"[LOG] Старт чату: admin={admin_id} <-> user={user_id}")
    if user_id in waiting_users:
        waiting_users.remove(user_id)
    active_user_chats[user_id] = admin_id
    active_admin_chats[admin_id] = user_id

def end_chat_by_admin(admin_id: int):
    user_id = active_admin_chats.pop(admin_id, None)
    if user_id:
        active_user_chats.pop(user_id, None)
    return user_id

def end_chat_by_user(user_id: int):
    admin_id = active_user_chats.pop(user_id, None)
    if admin_id:
        active_admin_chats.pop(admin_id, None)
    return admin_id

def get_user_for_admin(admin_id: int):
    return active_admin_chats.get(admin_id)

def get_admin_for_user(user_id: int):
    return active_user_chats.get(user_id)

def is_user_busy(user_id: int):
    return user_id in active_user_chats
