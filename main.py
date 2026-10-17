import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.client.default import DefaultBotProperties
from config import ADMINS, BOT_TOKEN
from handlers import user, admin

# Логирование
logging.basicConfig(level=logging.DEBUG)

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(admin.admin_router)
    dp.include_router(user.user_router)

    # Команды для всех пользователей
    await bot.set_my_commands(
        commands=[
            BotCommand(command="/start", description="Запустити бота"),
            BotCommand(command="/stop", description="Завершити чат"),
        ],
        scope=BotCommandScopeDefault()
    )

    # Команды только для адмінів
    for admin_id in ADMINS:
        await bot.set_my_commands(
            commands=[
                BotCommand(command="/start", description="Запустити бота"),
                BotCommand(command="/stop", description="Завершити чат"),
                BotCommand(command="/list_waiting", description="Очікуючі користувачі"),
                BotCommand(command="/end_chat", description="Завершити активний чат"),
            ],
            scope=BotCommandScopeChat(chat_id=admin_id)
        )

    print("[INFO] Роутери додано. Бот запускається.")
    await dp.start_polling(bot)
    print("[DEBUG] admin_router включено")

if __name__ == "__main__":
    asyncio.run(main())
