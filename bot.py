import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

BOT_NAME = "PawGuard"
CREATOR = "Evan"  # потом поменяем если хочешь
WEBSITE_URL = "https://your-site.com"  # потом вставим твой сайт

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):

        text = (
            f"🐾 <b>{BOT_NAME}</b>\n\n"
            "Привет! Я бот для модерации чатов.\n\n"
            "⚡ Что я умею:\n"
            "• Бан / мут пользователей\n"
            "• Предупреждения (warn)\n"
            "• Анти-спам защита\n"
            "• Система ролей\n\n"
            f"👨‍💻 Создатель: {CREATOR}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🌐 Открыть сайт",
                        url=WEBSITE_URL
                    )
                ]
            ]
        )

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

    print("🐾 PawGuard стартанул")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
