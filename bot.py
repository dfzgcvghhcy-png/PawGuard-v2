import asyncio
import os
from datetime import timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions


BOT_NAME = "PawGuard"
CREATOR = "Evan"
WEBSITE_URL = "https://google.com"

user_warns = {}
user_cache = {}


# =======================
# 🔍 Получение user_id
# =======================
async def get_target_user(message: types.Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id

    args = message.text.split()

    if len(args) < 2:
        return None

    target = args[1]

    if target.startswith("@"):
        username = target[1:].lower()
        return user_cache.get(username)

    if target.isdigit():
        return int(target)

    return None


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # =======================
    # 🟢 START
    # =======================
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        if message.from_user.username:
            user_cache[message.from_user.username.lower()] = message.from_user.id

        text = (
            f"🐾 <b>{BOT_NAME}</b>\n\n"
            "Привет! Я бот для модерации чатов.\n\n"
            "⚡ Что я умею:\n"
            "• Бан / мут\n"
            "• Варны\n\n"
            f"👨‍💻 Создатель: {CREATOR}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🌐 Сайт",
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
        if message.from_user.username:
            user_cache[message.from_user.username.lower()] = message.from_user.id

        text = (
            "📖 <b>Команды:</b>\n\n"
            "/ban @user | reply | id\n"
            "/mute @user | reply | id\n"
            "/unmute @user | reply | id\n"
            "/warn @user | reply | id\n"
        )

        await message.answer(text, parse_mode="HTML")

    # =======================
    # 🔨 BAN
    # =======================
    @dp.message(Command("ban"))
    async def cmd_ban(message: types.Message):
        if message.from_user.username:
            user_cache[message.from_user.username.lower()] = message.from_user.id

        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден (пусть напишет сообщение)")
            return

        try:
            await bot.ban_chat_member(message.chat.id, user_id)
            await message.answer("🔨 Забанен")
        except Exception as e:
            await message.answer("❌ Ошибка")
            print(e)

    # =======================
    # 🔇 MUTE
    # =======================
    @dp.message(Command("mute"))
    async def cmd_mute(message: types.Message):
        if message.from_user.username:
            user_cache[message.from_user.username.lower()] = message.from_user.id

        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден")
            return

        try:
            await bot.restrict_chat_member(
                message.chat.id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=timedelta(minutes=10)
            )
            await message.answer("🔇 Замучен")
        except Exception as e:
            await message.answer("❌ Ошибка")
            print(e)

    # =======================
    # 🔊 UNMUTE
    # =======================
    @dp.message(Command("unmute"))
    async def cmd_unmute(message: types.Message):
        if message.from_user.username:
            user_cache[message.from_user.username.lower()] = message.from_user.id

        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден")
            return

        try:
            await bot.restrict_chat_member(
                message.chat.id,
                user_id,
                permissions=ChatPermissions(can_send_messages=True)
            )
            await message.answer("🔊 Размучен")
        except Exception as e:
            await message.answer("❌ Ошибка")
            print(e)

    # =======================
    # ⚠️ WARN
    # =======================
    @dp.message(Command("warn"))
    async def cmd_warn(message: types.Message):
        if message.from_user.username:
            user_cache[message.from_user.username.lower()] = message.from_user.id

        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден")
            return

        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        warns = user_warns[user_id]

        await message.answer(f"⚠️ Warn ({warns}/3)")

        if warns >= 3:
            try:
                await bot.restrict_chat_member(
                    message.chat.id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=timedelta(minutes=10)
                )
                user_warns[user_id] = 0
                await message.answer("🔇 3 варна → мут")
            except Exception as e:
                print(e)

    print("🐾 PawGuard запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
