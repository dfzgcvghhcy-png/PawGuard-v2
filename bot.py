import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


BOT_NAME = "PawGuard"
CREATOR = "Evan"
WEBSITE_URL = "https://google.com"  # потом поменяешь


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # ✅ START
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

    # ✅ HELP
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        text = (
            "📖 <b>Команды бота:</b>\n\n"
            "👮‍♂️ Модерация:\n"
            "/ban — забанить пользователя\n"
            "/mute — замутить пользователя\n"
            "/unban — разбан\n"
            "/unmute — размут\n\n"
            "⚠️ Предупреждения:\n"
            "/warn — выдать предупреждение\n"
            "/unwarn — снять предупреждение\n\n"
            "📊 Прочее:\n"
            "/stats — статистика пользователя\n"
            "/help — список команд\n\n"
            "🚀 Больше функций скоро..."
        )

        await message.answer(text, parse_mode="HTML")

    print("🐾 PawGuard запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
