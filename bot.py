import asyncio
import os
from datetime import timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select


BOT_NAME = "PawGuard"
CREATOR = "Evan"
WEBSITE_URL = "https://google.com"

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()


# =======================
# 📊 МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
# =======================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    username = Column(String)


# =======================
# 🔧 БАЗА
# =======================
engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# =======================
# 💾 СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ
# =======================
async def save_user(user: types.User):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.tg_id == user.id))
        db_user = result.scalar_one_or_none()

        if not db_user:
            new_user = User(
                tg_id=user.id,
                username=user.username
            )
            session.add(new_user)
        else:
            db_user.username = user.username

        await session.commit()


# =======================
# 🔍 ПОИСК USER_ID
# =======================
async def get_user_id(username: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if user:
            return user.tg_id

    return None


async def get_target_user(message: types.Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id

    args = message.text.split()

    if len(args) < 2:
        return None

    target = args[1]

    if target.startswith("@"):
        return await get_user_id(target[1:])

    if target.isdigit():
        return int(target)

    return None


# =======================
# 🚀 MAIN
# =======================
async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    await init_db()

    # =======================
    # 🟢 START
    # =======================
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await save_user(message.from_user)

        text = (
            f"🐾 <b>{BOT_NAME}</b>\n\n"
            "Привет! Я бот для модерации.\n\n"
            f"👨‍💻 Создатель: {CREATOR}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Сайт", url=WEBSITE_URL)]
            ]
        )

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

    # =======================
    # 📖 HELP
    # =======================
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await save_user(message.from_user)

        await message.answer(
            "/ban @user\n"
            "/mute @user\n"
            "/unmute @user\n"
            "/warn @user"
        )

    # =======================
    # 🔨 BAN
    # =======================
    @dp.message(Command("ban"))
    async def cmd_ban(message: types.Message):
        await save_user(message.from_user)

        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден в базе")
            return

        await bot.ban_chat_member(message.chat.id, user_id)
        await message.answer("🔨 Забанен")

    # =======================
    # 🔇 MUTE
    # =======================
    @dp.message(Command("mute"))
    async def cmd_mute(message: types.Message):
        await save_user(message.from_user)

        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден в базе")
            return

        await bot.restrict_chat_member(
            message.chat.id,
            user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=timedelta(minutes=10)
        )

        await message.answer("🔇 Замучен")

    # =======================
    # 🔊 UNMUTE
    # =======================
    @dp.message(Command("unmute"))
    async def cmd_unmute(message: types.Message):
        await save_user(message.from_user)

        user_id = await get_target_user(message)

        if not user_id:
            await message.answer("❗ Пользователь не найден")
            return

        await bot.restrict_chat_member(
            message.chat.id,
            user_id,
            permissions=ChatPermissions(can_send_messages=True)
        )

        await message.answer("🔊 Размучен")

    print("🐾 PawGuard с БД запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
