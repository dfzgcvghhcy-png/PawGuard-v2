import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select

# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# ================= DB =================

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    full_name = Column(String)

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ================= BOT =================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= DB FUNCTIONS =================

async def add_user(user: types.User):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.user_id == user.id)
        )
        existing = result.scalar()

        if not existing:
            new_user = User(
                user_id=user.id,
                username=user.username,
                full_name=user.full_name
            )
            session.add(new_user)
            await session.commit()

# ================= HANDLERS =================

@dp.message(Command("start"))
async def start(message: Message):
    await add_user(message.from_user)

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🌐 Открыть сайт",
                    url="https://google.com"
                )
            ]
        ]
    )

    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n\n"
        f"Я модератор-бот PawGuard 🐾\n"
        f"Используй /help чтобы увидеть команды",
        reply_markup=kb
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "📜 Команды:\n\n"
        "/ban @user\n"
        "/mute @user\n"
        "/unmute @user\n"
        "/warn @user\n"
    )

# ================= AUTO COLLECT =================

@dp.message()
async def auto_collect(message: Message):
    await add_user(message.from_user)

# ================= FIND USER =================

async def get_user_by_username(username: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar()

# ================= COMMANDS =================

@dp.message(Command("mute"))
async def mute_user(message: Message):
    if not message.text:
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❗ Укажи пользователя")
        return

    username = parts[1].replace("@", "")

    user = await get_user_by_username(username)

    if not user:
        await message.answer("❗ Пользователь не найден в базе")
        return

    await message.answer(f"🔇 Пользователь @{username} замьючен")

@dp.message(Command("ban"))
async def ban_user(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❗ Укажи пользователя")
        return

    username = parts[1].replace("@", "")

    user = await get_user_by_username(username)

    if not user:
        await message.answer("❗ Пользователь не найден в базе")
        return

    await message.answer(f"🔨 Пользователь @{username} забанен")

# ================= START =================

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
