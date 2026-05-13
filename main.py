"""
Telegram Bot - Buyurtma va Fikr boshqaruv tizimi
Muallif: PinokioAI (Muhammadyusuf Abdug'afforov)
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import (
    BOT_TOKEN, GROUP_ID,
    BUYURTMA_BERISH_ID, ZAKAZ_BERILGAN_BOTLAR_ID, MIJOZLAR_FIKRI_ID
)
from handlers import order_router, review_router, admin_router
from middlewares.topic_filter import TopicMiddleware

# Logging sozlamasi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def validate_config(bot: Bot) -> None:
    """Bot ishga tushganda GROUP_ID va topik ID-larini tekshirish."""
    logger.info("Konfiguratsiya tekshirilmoqda...")

    try:
        chat = await bot.get_chat(GROUP_ID)
        logger.info(f"✅ Guruh topildi: {chat.title} (id={GROUP_ID})")
    except Exception as e:
        logger.critical(
            f"❌ [GURUH XATOSI] GROUP_ID={GROUP_ID} topilmadi: {e}\n"
            f"   1. .env dagi GROUP_ID togri? (minus bilan: -100XXXXXXXXXX)\n"
            f"   2. Bot guruhga qoshilganmi?\n"
            f"   3. Bot guruhda admin huquqiga egami?"
        )
        return

    try:
        bot_info = await bot.get_me()
        member = await bot.get_chat_member(GROUP_ID, bot_info.id)
        logger.info(
            f"✅ Bot holati guruhda: {member.status}\n"
            f"   GROUP_ID              = {GROUP_ID}\n"
            f"   BUYURTMA_BERISH_ID    = {BUYURTMA_BERISH_ID}\n"
            f"   ZAKAZ_BERILGAN_BOTLAR = {ZAKAZ_BERILGAN_BOTLAR_ID}\n"
            f"   MIJOZLAR_FIKRI_ID     = {MIJOZLAR_FIKRI_ID}"
        )
    except Exception as e:
        logger.warning(f"⚠️ Bot huquqini tekshirishda xato: {e}")


async def main() -> None:
    """Bot ishga tushirish funksiyasi."""
    logger.info("Bot ishga tushmoqda...")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Middleware qo'shish
    dp.message.middleware(TopicMiddleware())

    # Router'larni qo'shish
    dp.include_router(admin_router)
    dp.include_router(order_router)
    dp.include_router(review_router)

    bot_info = await bot.get_me()
    logger.info(f"Bot ishga tushdi: @{bot_info.username}")

    # Konfiguratsiyani tekshirish
    await validate_config(bot)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())