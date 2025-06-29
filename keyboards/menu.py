from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot

# Основное меню кнопок
def get_user_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    buttons = {
        "💬 Зв’язатися з адміністратором": "contact_admin",
        "ℹ️ О нас": "faq",
        "🩷 Ми у соціальних мережах": "social",
        "👗Як робити виміри": "measurements",

    }

    for text, callback in buttons.items():
        keyboard.button(text=text, callback_data=callback)

    return keyboard.adjust(1).as_markup()


# Функция отправки стартового меню с изображением
async def send_start_menu(bot: Bot, message: Message):
    photo_url = "https://i.pinimg.com/736x/e3/3e/3a/e33e3a343454df8481f3f8c39ee7a536.jpg"
    caption = "👋 Вітаємо у ✨Persephone-brand!✨\nОберіть дію нижче:"
    keyboard = get_user_main_keyboard()

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_url,
        caption=caption,
        reply_markup=keyboard
    )


# Кнопка завершить чат — пользователь
end_chat_button_user = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔚 Завершити чат", callback_data="user_end_chat")]
    ]
)

# Кнопка завершить чат — адмін
end_chat_button_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔚 Завершити чат", callback_data="admin_end_chat")]
    ]
)
