import logging

from aiogram import Router, F, Bot, html
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, CallbackQuery
from keyboards.menu import send_start_menu
from aiogram.filters import Command
from config import ADMINS
from utils.chat_router import *
from utils.notify import safe_send
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

user_router = Router()

@user_router.message(F.text == "/start")
async def start_handler(message: Message):
    await send_start_menu(message.bot, message)


@user_router.callback_query(F.data == "contact_admin")
async def contact_admin(callback: CallbackQuery):
    user = callback.from_user
    if is_user_busy(user.id):
        await callback.message.answer("🟢 Ви вже перебуваєте в активному чаті.")
    elif is_waiting(user.id):
        await callback.message.answer("🕓 Ваш запит вже надіслано. Очікуйте відповіді.")
    elif not ADMINS:
        await callback.message.answer("⚠️ Наразі жоден адміністратор не активний. Спробуйте пізніше.")
    else:
        request_chat(user.id)

        username = f" @{user.username}" if user.username else ""
        for admin_id in ADMINS:
            await safe_send(
                callback.bot,
                admin_id,
                f"📥 Користувач {html.quote(user.full_name)}{username} (ID: {user.id}) хоче поспілкуватися.\n"
                f"Щоб розпочати чат: /chat_{user.id}"
            )

        await callback.message.answer(
            "✅ Запит надіслано. Можете вже описати своє питання — "
            "повідомлення будуть передані адміністратору, щойно він підключиться."
        )
    await callback.answer()


async def end_user_chat(bot: Bot, user_id: int, reply):
    admin_id = end_chat_by_user(user_id)
    if admin_id:
        await reply("🔕 Ви завершили чат.")
        await safe_send(bot, admin_id, f"❌ Користувач {user_id} завершив чат.")
    elif cancel_request(user_id):
        await reply("🔕 Ваш запит до адміністратора скасовано.")
    else:
        await reply("У вас немає активного чату.")


@user_router.message(Command("stop"))
async def stop_chat_command(message: Message):
    await end_user_chat(message.bot, message.from_user.id, message.answer)


@user_router.callback_query(F.data == "user_end_chat")
async def user_ends_chat(callback: CallbackQuery):
    await end_user_chat(callback.bot, callback.from_user.id, callback.message.answer)
    await callback.answer()


# Пересилає адміну будь-які повідомлення: текст, фото, файли, голосові тощо
@user_router.message(~F.from_user.id.in_(ADMINS))
async def forward_to_admin(message: Message):
    user_id = message.from_user.id
    admin_id = get_admin_for_user(user_id)
    if admin_id:
        try:
            await message.copy_to(admin_id)
        except TelegramAPIError as e:
            logging.warning(f"Не вдалося переслати повідомлення від {user_id} адміну {admin_id}: {e}")
            await message.answer("⚠️ Не вдалося доставити повідомлення. Спробуйте ще раз.")
    elif is_waiting(user_id):
        if buffer_message(user_id, message.message_id) == 1:
            await message.answer("🕓 Адміністратор ще не підключився. Ваше повідомлення буде передано, щойно він приєднається.")
    else:
        await message.answer("Щоб написати адміністратору, натисніть «💬 Зв’язатися з адміністратором» у меню /start.")


@user_router.callback_query(F.data == "faq")
async def handle_faq(callback: CallbackQuery):
    text = (
        "❓ <b>Часті питання:</b>\n"
        "— Як оформити замовлення?\n"
        "— Скільки триває пошиття?\n"
        "— Які тканини ви використовуєте?\n\n"
        "Зв'яжіться з адміністратором для детальної консультації 💬"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написати адміну", callback_data="contact_admin")]
    ])

    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@user_router.callback_query(F.data == "measurements")
async def handle_measurements(callback: CallbackQuery):
    text = "📏 Як зробити виміри:\n👉 <a href='https://www.youtube.com/watch?v=LAM1mtphC-k'>Інструкція</a>"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@user_router.callback_query(F.data == "social")
async def handle_social(callback: CallbackQuery):
    text = (
        "📲 Ми в соцмережах:\n"
        "— Instagram: <a href='https://www.instagram.com/persephone.brand/'>@persephone.brand</a>\n"
        "— Etsy: <a href='https://www.etsy.com/shop/persephonebrand'>Перейти до магазину</a>"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
