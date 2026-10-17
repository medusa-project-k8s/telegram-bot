# Стан чату

import json
import logging
import os

from config import STATE_FILE

MAX_PENDING_MESSAGES = 50

active_user_chats = {}   # user_id → admin_id
active_admin_chats = {}  # admin_id → user_id
waiting_users = {}       # user_id → message_id повідомлень, надісланих до підключення адміна


def _save():
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    tmp_path = f"{STATE_FILE}.tmp"
    with open(tmp_path, "w") as f:
        json.dump({"active_user_chats": active_user_chats, "waiting_users": waiting_users}, f)
    os.replace(tmp_path, STATE_FILE)


def _load():
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except FileNotFoundError:
        return
    except (OSError, ValueError) as e:
        logging.error(f"Не вдалося прочитати стан чатів з {STATE_FILE}: {e}")
        return

    for user_id, admin_id in state.get("active_user_chats", {}).items():
        active_user_chats[int(user_id)] = admin_id
        active_admin_chats[admin_id] = int(user_id)
    for user_id, message_ids in state.get("waiting_users", {}).items():
        waiting_users[int(user_id)] = message_ids


def request_chat(user_id: int):
    waiting_users.setdefault(user_id, [])
    _save()

def list_waiting_users():
    return list(waiting_users)

def is_waiting(user_id: int):
    return user_id in waiting_users

def buffer_message(user_id: int, message_id: int):
    """Запам'ятовує повідомлення очікуючого користувача. Повертає кількість збережених."""
    pending = waiting_users[user_id]
    if len(pending) < MAX_PENDING_MESSAGES:
        pending.append(message_id)
        _save()
    return len(pending)

def cancel_request(user_id: int):
    removed = waiting_users.pop(user_id, None) is not None
    if removed:
        _save()
    return removed

def start_chat(admin_id: int, user_id: int):
    """Починає чат і повертає message_id повідомлень, що чекали на адміна."""
    logging.info(f"Старт чату: admin={admin_id} <-> user={user_id}")
    pending = waiting_users.pop(user_id, [])
    active_user_chats[user_id] = admin_id
    active_admin_chats[admin_id] = user_id
    _save()
    return pending

def end_chat_by_admin(admin_id: int):
    user_id = active_admin_chats.pop(admin_id, None)
    if user_id:
        active_user_chats.pop(user_id, None)
        _save()
    return user_id

def end_chat_by_user(user_id: int):
    admin_id = active_user_chats.pop(user_id, None)
    if admin_id:
        active_admin_chats.pop(admin_id, None)
        _save()
    return admin_id

def get_user_for_admin(admin_id: int):
    return active_admin_chats.get(admin_id)

def get_admin_for_user(user_id: int):
    return active_user_chats.get(user_id)

def is_user_busy(user_id: int):
    return user_id in active_user_chats


_load()
