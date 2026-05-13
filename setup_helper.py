"""
setup_helper.py — Guruh va topik ID-larini avtomatik aniqlash yordamchisi
Ishlatish:  python setup_helper.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

FOUND = {}


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ .env fayliga BOT_TOKEN ni kiriting!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("id"))
    @dp.message(F.text == "/get_id")
    async def get_id(message: Message):
        chat_id   = message.chat.id
        thread_id = message.message_thread_id or "topik_emas"
        username  = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

        print(f"\n{'='*45}")
        print(f"  Chat ID    : {chat_id}")
        print(f"  Thread ID  : {thread_id}")
        print(f"  Kim yozdi  : {username}")
        print(f"{'='*45}")

        await message.reply(
            f"📋 ID Ma'lumotlari:\n\n"
            f"💬 Chat ID: <code>{chat_id}</code>\n"
            f"🧵 Thread ID: <code>{thread_id}</code>\n\n"
            f"Bu qiymatlarni <b>.env</b> fayliga kiriting!",
            parse_mode="HTML"
        )

    print("\n" + "="*50)
    print("  SETUP YORDAMCHISI ISHGA TUSHDI")
    print("="*50)
    print("\nQuyidagi amallarni bajaring:")
    print("  1. Botni guruhga admin sifatida qo'shing")
    print("  2. Har bir topikka /id yozing")
    print("  3. Bot javobidagi Chat ID va Thread ID ni .env ga kiriting")
    print("  4. Bosing Ctrl+C — keyin  python main.py\n")

    bot_info = await bot.get_me()
    print(f"  Bot: @{bot_info.username}\n")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n✅ Setup tugadi. Endi python main.py ni ishga tushiring.\n")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
