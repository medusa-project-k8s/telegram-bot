import os
from dotenv import load_dotenv, find_dotenv
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.menu import send_start_menu, end_chat_button_user
from aiogram.filters import Command
from utils.chat_router import *
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

ADMINS = [
    int(admin_id.strip())
    for admin_id in os.getenv("ADMINS", "").split(",")
    if admin_id.strip().isdigit()
]

user_router = Router()

@user_router.message(F.text == "/start")
async def start_handler(message: Message):
    await send_start_menu(message.bot, message)


@user_router.callback_query(F.data == "contact_admin")
async def contact_admin(callback: CallbackQuery):
    user = callback.from_user
    if is_user_busy(user.id):
        await callback.message.answer("🟢 Ви вже перебуваєте в активному чаті.")
    elif get_admin_for_user(user.id):
        await callback.message.answer("🕓 Ваш запит вже надіслано. Очікуйте відповіді.")
    else:
        request_chat(user.id)

        if not ADMINS:
            await callback.message.answer("⚠️ Наразі жоден адміністратор не активний. Спробуйте пізніше.")
            return

        for admin_id in ADMINS:
            await callback.bot.send_message(
                admin_id,
                f"📥 Користувач @{user.username or user.first_name} (ID: {user.id}) хоче поспілкуватися.\n"
                f"Щоб розпочати чат: /chat_{user.id}"
            )

        await callback.message.answer("✅ Запит надіслано. Очікуйте відповіді адміністратора.")
    await callback.answer()


@user_router.message(Command("stop"))
async def stop_chat_command(message: Message):
    user_id = message.from_user.id
    admin_id = end_chat_by_user(user_id)

    if admin_id:
        await message.answer("🔕 Ви завершили чат.")
        await message.bot.send_message(admin_id, f"❌ Користувач {user_id} завершив чат.")
    else:
        await message.answer("У вас немає активного чату.")


@user_router.callback_query(F.data == "user_end_chat")
async def user_ends_chat(callback: CallbackQuery):
    user_id = callback.from_user.id
    admin_id = end_chat_by_user(user_id)
    if admin_id:
        await callback.message.answer("🔕 Ви завершили чат.")
        await callback.bot.send_message(admin_id, f"❌ Користувач {user_id} завершив чат.")
    else:
        await callback.message.answer("У вас немає активного чату.")
    await callback.answer()


@user_router.message(F.text & ~F.from_user.id.in_(ADMINS))
async def forward_to_admin(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    admin_id = get_admin_for_user(user_id)
    if admin_id:
        await message.bot.send_message(admin_id, f"👤 {username}:\n{message.text}")


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
