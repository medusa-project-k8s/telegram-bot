import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError


async def safe_send(bot: Bot, chat_id: int, text: str, **kwargs) -> bool:
    """Надсилає повідомлення і не падає, якщо користувач заблокував бота тощо."""
    try:
        await bot.send_message(chat_id, text, **kwargs)
        return True
    except TelegramAPIError as e:
        logging.warning(f"Не вдалося надіслати повідомлення {chat_id}: {e}")
        return False
