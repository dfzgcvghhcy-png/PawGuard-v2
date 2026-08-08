import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("🐾 PawGuard работает!")

    print("🐾 PawGuard стартанул")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
