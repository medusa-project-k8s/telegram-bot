import re, os
from dotenv import load_dotenv, find_dotenv
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.menu import end_chat_button_admin, end_chat_button_user
from filters.admin_filter import IsAdmin, ChatTypeFilter
from utils.chat_router import waiting_users, start_chat, is_user_busy, get_user_for_admin, end_chat_by_admin

load_dotenv()

ADMINS = [
    int(admin_id.strip())
    for admin_id in os.getenv("ADMINS", "").split(",")
    if admin_id.strip().isdigit()
]

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

pattern = re.compile(r"^/chat_(\d+)$")

@admin_router.message(Command("list_waiting"))
async def list_waiting(message: Message):
    if not waiting_users:
        await message.answer("📭 Немає користувачів, що очікують.")
        return

    text = "📋 Користувачі, що очікують на відповідь:\n"
    for user_id in waiting_users:
        text += f"🔹 /chat_{user_id}\n"

    await message.answer(text)


@admin_router.message(Command("end_chat"))
async def end_chat_command(message: Message):
    admin_id = message.from_user.id
    user_id = end_chat_by_admin(admin_id)

    if user_id:
        print(f"🔕 [LOG] {admin_id} завершив чат з {user_id}")
        await message.answer("🔕 Ви завершили чат.")
        await message.bot.send_message(user_id, "🛑 Адміністратор завершив чат.")
    else:
        await message.answer("❌ У вас немає активного чату.")


@admin_router.callback_query(F.data == "admin_end_chat")
async def admin_end_chat(callback: CallbackQuery):
    admin_id = callback.from_user.id
    user_id = end_chat_by_admin(admin_id)

    if user_id:
        print(f"🔕 [LOG] {admin_id} завершив чат з {user_id}")
        await callback.answer("🔕 Ви завершили чат.")
        await callback.bot.send_message(user_id, "🛑 Адміністратор завершив чат.")
    else:
        await callback.answer("❌ У вас немає активного чату.")


@admin_router.message(lambda message: message.text and pattern.match(message.text))
async def start_chat_cmd(message: Message):
    if message.from_user.id not in ADMINS:
        print(f"⛔ [WARN] {message.from_user.id} не є адміном.")
        return

    try:
        user_id = int(message.text.split("_")[1])

        if is_user_busy(user_id):
            await message.answer("⛔ Цей користувач вже спілкується з іншим адміністратором.")
            return

        start_chat(message.from_user.id, user_id)
        await message.answer(
            f"✅ Ви почали чат з користувачем {user_id}.",
            reply_markup=end_chat_button_admin
        )
        await message.bot.send_message(
            user_id,
            "💬 Адміністратор приєднався до чату.",
            reply_markup=end_chat_button_user
        )
    except Exception as e:
        print(f"❌ [ERROR] {e}")
        await message.answer("❌ Невірна команда.")

@admin_router.message(lambda msg: msg.text and msg.from_user.id in ADMINS and not msg.text.startswith("/"))
async def forward_to_user(message: Message):
    BOT_NAME = "Persephone-brand"
    admin_id = message.from_user.id
    user_id = get_user_for_admin(admin_id)
    if user_id:
        await message.bot.send_message(user_id, f" ✨{BOT_NAME}:\n{message.text}")




