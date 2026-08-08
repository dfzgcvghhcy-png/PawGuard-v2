import asyncio
import os
from datetime import timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions


BOT_NAME = "PawGuard"
CREATOR = "Evan"
WEBSITE_URL = "https://google.com"

# ⚠️ ХРАНИЛИЩЕ WARN (временно)
user_warns = {}


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # =======================
    # 🟢 START
    # =======================
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

    # =======================
    # 📖 HELP
    # =======================
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        text = (
            "📖 <b>Команды бота:</b>\n\n"
            "👮‍♂️ Модерация:\n"
            "/ban — бан\n"
            "/mute — мут (10 минут)\n"
            "/unmute — размут\n\n"
            "⚠️ Предупреждения:\n"
            "/warn — предупреждение\n\n"
            "📊 Прочее:\n"
            "/help — список команд"
        )

        await message.answer(text, parse_mode="HTML")

    # =======================
    # 🔨 BAN
    # =======================
    @dp.message(Command("ban"))
    async def cmd_ban(message: types.Message):
        if not message.reply_to_message:
            await message.answer("❗ Ответь на сообщение пользователя")
            return

        user_id = message.reply_to_message.from_user.id

        try:
            await bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=user_id
            )
            await message.answer("🔨 Пользователь забанен")
        except Exception as e:
            await message.answer("❌ Ошибка бана")
            print(e)

    # =======================
    # 🔇 MUTE
    # =======================
    @dp.message(Command("mute"))
    async def cmd_mute(message: types.Message):
        if not message.reply_to_message:
            await message.answer("❗ Ответь на сообщение пользователя")
            return

        user_id = message.reply_to_message.from_user.id

        try:
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=timedelta(minutes=10)
            )
            await message.answer("🔇 Пользователь замучен на 10 минут")
        except Exception as e:
            await message.answer("❌ Ошибка мута")
            print(e)

    # =======================
    # 🔊 UNMUTE
    # =======================
    @dp.message(Command("unmute"))
    async def cmd_unmute(message: types.Message):
        if not message.reply_to_message:
            await message.answer("❗ Ответь на сообщение пользователя")
            return

        user_id = message.reply_to_message.from_user.id

        try:
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=True)
            )
            await message.answer("🔊 Пользователь размучен")
        except Exception as e:
            await message.answer("❌ Ошибка размута")
            print(e)

    # =======================
    # ⚠️ WARN
    # =======================
    @dp.message(Command("warn"))
    async def cmd_warn(message: types.Message):
        if not message.reply_to_message:
            await message.answer("❗ Ответь на сообщение пользователя")
            return

        user_id = message.reply_to_message.from_user.id

        # увеличиваем варны
        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        warns = user_warns[user_id]

        await message.answer(f"⚠️ Пользователь получил предупреждение ({warns}/3)")

        # авто-мут на 3 варна
        if warns >= 3:
            try:
                await bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=timedelta(minutes=10)
                )

                user_warns[user_id] = 0  # сброс
                await message.answer("🔇 3 варна → пользователь замучен на 10 минут")

            except Exception as e:
                print(e)

    print("🐾 PawGuard запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
