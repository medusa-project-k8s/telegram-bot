import re
import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.menu import end_chat_button_admin, end_chat_button_user
from filters.admin_filter import IsAdmin, ChatTypeFilter
from utils.chat_router import waiting_users, start_chat, is_user_busy, get_user_for_admin, end_chat_by_admin
from utils.notify import safe_send

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
        logging.info(f"{admin_id} завершив чат з {user_id}")
        await message.answer("🔕 Ви завершили чат.")
        await safe_send(message.bot, user_id, "🛑 Адміністратор завершив чат.")
    else:
        await message.answer("❌ У вас немає активного чату.")


@admin_router.callback_query(F.data == "admin_end_chat")
async def admin_end_chat(callback: CallbackQuery):
    admin_id = callback.from_user.id
    user_id = end_chat_by_admin(admin_id)

    if user_id:
        logging.info(f"{admin_id} завершив чат з {user_id}")
        await callback.answer("🔕 Ви завершили чат.")
        await safe_send(callback.bot, user_id, "🛑 Адміністратор завершив чат.")
    else:
        await callback.answer("❌ У вас немає активного чату.")


@admin_router.message(F.text.regexp(pattern).as_("match"))
async def start_chat_cmd(message: Message, match: re.Match):
    admin_id = message.from_user.id
    user_id = int(match.group(1))

    current_user_id = get_user_for_admin(admin_id)
    if current_user_id:
        await message.answer(
            f"⛔ У вас вже є активний чат з користувачем {current_user_id}. "
            "Спочатку завершіть його: /end_chat"
        )
        return

    if is_user_busy(user_id):
        await message.answer("⛔ Цей користувач вже спілкується з іншим адміністратором.")
        return

    joined = await safe_send(
        message.bot,
        user_id,
        "💬 Адміністратор приєднався до чату.",
        reply_markup=end_chat_button_user
    )
    if not joined:
        await message.answer("❌ Не вдалося зв'язатися з користувачем (можливо, він заблокував бота).")
        return

    pending = start_chat(admin_id, user_id)
    await message.answer(
        f"✅ Ви почали чат з користувачем <a href=\"tg://user?id={user_id}\">{user_id}</a>.",
        reply_markup=end_chat_button_admin
    )

    # Передаємо повідомлення, які користувач надіслав до підключення адміна
    for message_id in pending:
        try:
            await message.bot.copy_message(admin_id, from_chat_id=user_id, message_id=message_id)
        except TelegramAPIError as e:
            logging.warning(f"Не вдалося переслати збережене повідомлення {message_id} від {user_id}: {e}")


# Пересилає користувачу будь-які повідомлення адміна, крім команд
@admin_router.message(lambda msg: not (msg.text or "").startswith("/"))
async def forward_to_user(message: Message):
    user_id = get_user_for_admin(message.from_user.id)
    if not user_id:
        await message.answer("❌ У вас немає активного чату. Список очікуючих: /list_waiting")
        return

    try:
        await message.copy_to(user_id)
    except TelegramAPIError as e:
        logging.warning(f"Не вдалося переслати повідомлення користувачу {user_id}: {e}")
        await message.answer("⚠️ Не вдалося доставити повідомлення (можливо, користувач заблокував бота).")
