import asyncio
from aiogram import Bot, Dispatcher
import os

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    print("🐾 PawGuard стартанул")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
