import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMINS = [
    int(admin_id.strip())
    for admin_id in os.getenv("ADMINS", "").split(",")
    if admin_id.strip().isdigit()
]

# Файл зі станом чатів, щоб він переживав перезапуск бота
STATE_FILE = os.getenv("STATE_FILE", "data/chat_state.json")
