"""
Fikr qoldirish handleri - FSM asosidagi sharh tizimi
"""

import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import GROUP_ID, MIJOZLAR_FIKRI_ID
from states import ReviewStates
from keyboards import get_rating_keyboard, get_confirm_review_keyboard, get_start_keyboard
from utils import escape_md, get_stars, format_review_for_topic

logger = logging.getLogger(__name__)
review_router = Router(name="review_router")


# ============================================================
# Fikr qoldirish tugmasi (start menyudan)
# ============================================================

@review_router.callback_query(F.data == "start_review")
async def cb_start_review(callback: CallbackQuery, state: FSMContext) -> None:
    """Fikr qoldirish jarayonini boshlash."""
    await callback.answer()
    await state.set_state(ReviewStates.waiting_rating)

    text = (
        "💬 *FIKR QOLDIRISH*\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        "Xizmatimizni qanday baholaysiz?\n"
        "*Yulduzcha tanlang:*"
    )
    await callback.message.edit_text(text, reply_markup=get_rating_keyboard())


# ============================================================
# 1-qadam: Reyting tanlash (Callback)
# ============================================================

@review_router.callback_query(F.data.startswith("rating_"))
async def get_rating(callback: CallbackQuery, state: FSMContext) -> None:
    """Yulduzcha reytingini qabul qilish."""
    await callback.answer()

    rating = int(callback.data.replace("rating_", ""))
    stars = get_stars(rating)

    await state.update_data(
        rating=rating,
        user_id=callback.from_user.id,
        username=callback.from_user.username or callback.from_user.full_name
    )
    await state.set_state(ReviewStates.waiting_review_text)

    text = (
        f"*Sizning reytingingiz:* {escape_md(stars)}\n\n"
        f"✍️ *Endi fikirlaringizni yozing:*\n"
        f"\\(Xizmat, sifat, tezlik haqida batafsil\\)"
    )
    await callback.message.edit_text(text)


# ============================================================
# 2-qadam: Sharh matni
# ============================================================

@review_router.message(ReviewStates.waiting_review_text, F.text)
async def get_review_text(message: Message, state: FSMContext) -> None:
    """Sharh matnini qabul qilish."""
    text = message.text.strip()

    if len(text) < 10:
        await message.answer(
            "⚠️ Sharh kamida 10 ta belgidan iborat bo'lsin\\.\n"
            "Iltimos, batafsil yozing\\."
        )
        return

    if len(text) > 1000:
        await message.answer(
            "⚠️ Sharh 1000 ta belgidan oshmasin\\.\n"
            "Qisqaroq yozing\\."
        )
        return

    await state.update_data(review_text=text)
    await state.set_state(ReviewStates.confirming_review)

    # Oldindan ko'rsatish
    data = await state.get_data()
    rating = data.get("rating", 5)
    stars = get_stars(rating)

    preview_text = (
        f"*📋 SHARHINGIZ OLDINDAN KO'RINISHI:*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ Reyting: {escape_md(stars)}\n\n"
        f"💭 Fikr:\n_{escape_md(text)}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Sharhni yuborasizmi?*"
    )
    await message.answer(preview_text, reply_markup=get_confirm_review_keyboard())


# ============================================================
# 3-qadam: Tasdiqlash
# ============================================================

@review_router.callback_query(ReviewStates.confirming_review, F.data == "confirm_review")
async def confirm_review(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Sharhni tasdiqlash va topikka yuborish."""
    await callback.answer("⏳ Sharh yuborilmoqda...")
    data = await state.get_data()

    username = data.get("username", "Noma'lum")
    user_id = data.get("user_id", 0)
    rating = data.get("rating", 5)
    review_text = data.get("review_text", "")
    order_id = data.get("order_id", "")  # Agar buyurtma bilan bog'liq bo'lsa

    try:
        # MIJOZLAR_FIKRI topigiga yuborish
        review_msg = format_review_for_topic(
            username=username,
            user_id=user_id,
            rating=rating,
            review_text=review_text,
            order_id=order_id
        )

        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=MIJOZLAR_FIKRI_ID,
            text=review_msg
        )

        stars = get_stars(rating)
        await callback.message.edit_text(
            f"✅ *Sharhingiz uchun rahmat\\!* {escape_md(stars)}\n\n"
            f"Fikringiz bizga juda muhim\\. Yaxshi xizmat ko'rsatishda davom etamiz\\! 🙏"
        )
        logger.info(f"Yangi sharh qabul qilindi. User: {user_id}, Reyting: {rating}")

    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Sharhni yuborishda xato: {e}")

        if "chat not found" in error_msg:
            bot_info = await bot.get_me()
            logger.critical(
                f"[KONFIGURATSIYA XATOSI] Guruh topilmadi!\n"
                f"  GROUP_ID={GROUP_ID} | MIJOZLAR_FIKRI_ID={MIJOZLAR_FIKRI_ID}\n"
                f"  Tekshiring:\n"
                f"  1. Bot guruhga qoshilganmi? @{bot_info.username}\n"
                f"  2. GROUP_ID minus bilan: -100XXXXXXXXXX\n"
                f"  3. Bot guruhda admin huquqiga egami?\n"
                f"  4. MIJOZLAR_FIKRI_ID: topikda /get_id yuboring"
            )
            await callback.message.answer(
                "⚠️ *Texnik muammo yuz berdi\\.*\n\n"
                "Sharhingiz qabul qilindi, tez orada hal qilinadi\\. Uzr\\! 🙏"
            )
        elif "forbidden" in error_msg or "kicked" in error_msg:
            logger.critical("[RUXSAT XATOSI] Bot guruhdan chiqarib yuborilgan!")
            await callback.message.answer(
                "⚠️ *Bot guruhda faol emas\\.*\nAdmin bilan boglanin\\."
            )
        elif "thread not found" in error_msg:
            logger.critical(
                f"[TOPIK XATOSI] MIJOZLAR_FIKRI_ID={MIJOZLAR_FIKRI_ID} topilmadi!\n"
                f"  Topikda /get_id buyrug ini yuboring va ID ni yangilang"
            )
            await callback.message.answer(
                "⚠️ *Topik topilmadi\\.*\nAdmin sozlamalarni tekshirsin\\."
            )
        else:
            await callback.message.answer(
                "⚠️ Xato yuz berdi\\. Iltimos qayta urinib koring\\."
            )
    finally:
        await state.clear()


@review_router.callback_query(ReviewStates.confirming_review, F.data == "rewrite_review")
async def rewrite_review(callback: CallbackQuery, state: FSMContext) -> None:
    """Sharhni qayta yozish."""
    await callback.answer()
    await state.set_state(ReviewStates.waiting_review_text)
    await callback.message.edit_text(
        "✍️ *Sharhingizni qayta yozing:*"
    )


@review_router.callback_query(F.data == "cancel_review")
async def cancel_review(callback: CallbackQuery, state: FSMContext) -> None:
    """Sharhni bekor qilish."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "❌ *Sharh qoldirish bekor qilindi\\.*\n\n"
        "Istalgan vaqt qayta baholashingiz mumkin\\.",
        reply_markup=get_start_keyboard()
    )


# ============================================================
# Xizmatlar haqida ma'lumot
# ============================================================

@review_router.callback_query(F.data == "show_services")
async def show_services(callback: CallbackQuery) -> None:
    """Xizmatlar ro'yxatini ko'rsatish."""
    await callback.answer()
    text = (
        "🛠 *BIZNING XIZMATLARIMIZ*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🤖 *Telegram Botlar*\n"
        "_Buyurtma, savdo, avtomatlashtirish botlari_\n\n"
        "🌐 *Web Saytlar*\n"
        "_Landing page, korporativ, internet do'kon_\n\n"
        "📱 *Mobil Ilovalar*\n"
        "_iOS va Android uchun ilovalar_\n\n"
        "⚙️ *Avtomatlashtirish*\n"
        "_Biznes jarayonlarini avtomatlashtirish_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💬 Buyurtma berish uchun pastdagi tugmani bosing\\!"
    )
    await callback.message.edit_text(text, reply_markup=get_start_keyboard())
