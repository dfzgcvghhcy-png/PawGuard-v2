import asyncio
import os
from datetime import timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions


BOT_NAME = "PawGuard"
CREATOR = "Evan"
WEBSITE_URL = "https://google.com"

# память
user_warns = {}
user_cache = {}


# =======================
# 🔍 Получение user_id
# =======================
async def get_target_user(message: types.Message):
    # reply
    if message.reply_to_message:
        return message.reply_to_message.from_user.id

    args = message.text.split()

    if len(args) < 2:
        return None

    target = args[1]

    # @username
    if target.startswith("@"):
        username = target[1:].lower()

        if username in user_cache:
            return user_cache[username]

        return None

    # user_id
    if target.isdigit():
        return int(target)

    return None


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # =======================
    # 📦 КЭШ ПОЛЬЗОВАТЕЛЕЙ
    # =======================
    @dp.message()
    async def cache_users(message: types.Message):
        if message.from_user.username:
            user_cache[message.from_user.username.lower()] = message.from_user.id

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
            "/ban @user | reply | id\n"
            "/mute @user | reply | id\n"
            "/unmute @user | reply | id\n\n"
            "⚠️ Предупреждения:\n"
            "/warn @user | reply | id\n"
        )

        await message.answer(text, parse_mode="HTML")

    # =======================
    # 🔨 BAN
    # =======================
    @dp.message(Command("ban"))
    async def cmd_ban(message: types.Message):
        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден (пусть напишет сообщение)")
            return

        try:
            await bot.ban_chat_member(message.chat.id, user_id)
            await message.answer("🔨 Пользователь забанен")
        except Exception as e:
            await message.answer("❌ Ошибка бана")
            print(e)

    # =======================
    # 🔇 MUTE
    # =======================
    @dp.message(Command("mute"))
    async def cmd_mute(message: types.Message):
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
            await message.answer("🔇 Пользователь замучен на 10 минут")
        except Exception as e:
            await message.answer("❌ Ошибка мута")
            print(e)

    # =======================
    # 🔊 UNMUTE
    # =======================
    @dp.message(Command("unmute"))
    async def cmd_unmute(message: types.Message):
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
            await message.answer("🔊 Пользователь размучен")
        except Exception as e:
            await message.answer("❌ Ошибка размута")
            print(e)

    # =======================
    # ⚠️ WARN
    # =======================
    @dp.message(Command("warn"))
    async def cmd_warn(message: types.Message):
        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден")
            return

        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        warns = user_warns[user_id]

        await message.answer(f"⚠️ Предупреждение ({warns}/3)")

        if warns >= 3:
            try:
                await bot.restrict_chat_member(
                    message.chat.id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=timedelta(minutes=10)
                )
                user_warns[user_id] = 0
                await message.answer("🔇 3 варна → мут на 10 минут")
            except Exception as e:
                print(e)

    print("🐾 PawGuard запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
