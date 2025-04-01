import asyncio
from bot import bot, dp
from handlers import start, categories   # Yangi faylni import qildik
from database import init_db

async def main():
    await init_db()  # 🔹 Bazani yaratish
    print("Baza yaratildi yoki mavjud!")
    dp.include_router(start.router)
    dp.include_router(categories.router)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
