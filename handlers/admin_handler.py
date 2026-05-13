"""
Admin handleri - buyurtma holatini boshqarish
Faqat ADMIN_IDS ro'yxatidagi foydalanuvchilar uchun
"""

import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from config import ADMIN_IDS, GROUP_ID, ZAKAZ_BERILGAN_BOTLAR_ID
from keyboards import get_rating_keyboard
from utils import escape_md, format_completed_order

logger = logging.getLogger(__name__)
admin_router = Router(name="admin_router")

# Order storage - order_handler.py dan import qilinadi
from handlers.order_handler import orders_storage


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish."""
    return user_id in ADMIN_IDS


# ============================================================
# Admin filter funksiyasi
# ============================================================

async def admin_check(callback: CallbackQuery) -> bool:
    """Admin emasliklarni filtrlash."""
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "❌ Siz admin emassiz! Faqat adminlar bu amalni bajarishi mumkin.",
            show_alert=True
        )
        return False
    return True


# ============================================================
# /get_id - topik ID larini aniqlash (faqat adminlar)
# ============================================================

@admin_router.message(Command("get_id"))
async def cmd_get_id(message: Message) -> None:
    """Thread ID va Chat ID ni ko'rsatish - konfiguratsiya uchun."""
    if not is_admin(message.from_user.id):
        return

    thread_id = message.message_thread_id or "Asosiy chat (topik yo'q)"
    chat_id = message.chat.id

    text = (
        f"🔍 *ID Ma'lumotlari*\n\n"
        f"💬 Chat ID: `{escape_md(str(chat_id))}`\n"
        f"🧵 Thread/Topik ID: `{escape_md(str(thread_id))}`\n\n"
        f"_Bu ma'lumotlarni config\\.py ga kiriting_"
    )
    await message.reply(text)


# ============================================================
# /orders - barcha buyurtmalarni ko'rish
# ============================================================

@admin_router.message(Command("orders"))
async def cmd_list_orders(message: Message) -> None:
    """Barcha faol buyurtmalarni ro'yxatini ko'rsatish."""
    if not is_admin(message.from_user.id):
        return

    if not orders_storage:
        await message.reply("📭 Hozircha buyurtmalar yo'q\\.")
        return

    lines = ["📋 *BARCHA BUYURTMALAR*\n━━━━━━━━━━━━━━━━"]
    for order_id, data in list(orders_storage.items())[-10:]:  # Oxirgi 10 ta
        status = data.get("status", "pending")
        status_emoji = {
            "pending": "🟡",
            "progress": "🔵",
            "done": "✅",
            "rejected": "❌"
        }.get(status, "🟡")

        lines.append(
            f"{status_emoji} `{escape_md(order_id)}` \\- "
            f"*{escape_md(data.get('project_name', 'N/A'))}*\n"
            f"   👤 @{escape_md(data.get('username', 'N/A'))}"
        )

    await message.reply("\n".join(lines))


# ============================================================
# Admin: "Bajarildi" tugmasi
# ============================================================

@admin_router.callback_query(F.data.startswith("admin_done_"))
async def admin_mark_done(callback: CallbackQuery, bot: Bot) -> None:
    """Buyurtmani bajarilgan deb belgilash va hisobotni yuborish."""
    if not await admin_check(callback):
        return

    await callback.answer("✅ Bajarildi deb belgilanmoqda...")
    order_id = callback.data.replace("admin_done_", "")
    order_data = orders_storage.get(order_id)

    if not order_data:
        await callback.answer("⚠️ Buyurtma topilmadi!", show_alert=True)
        return

    # Statusni yangilash
    orders_storage[order_id]["status"] = "done"

    try:
        # 1. ZAKAZ_BERILGAN_BOTLAR topigiga hisobot yuborish
        completed_text = format_completed_order(
            order_data,
            admin_note=f"Admin: @{callback.from_user.username or 'N/A'}"
        )

        report_msg = await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=ZAKAZ_BERILGAN_BOTLAR_ID,
            text=completed_text
        )

        # Screenshot ham mavjud bo'lsa yuborish
        if order_data.get("has_screenshot") and order_data.get("screenshot_file_id"):
            await bot.send_photo(
                chat_id=GROUP_ID,
                message_thread_id=ZAKAZ_BERILGAN_BOTLAR_ID,
                photo=order_data["screenshot_file_id"],
                caption=f"🖼 *{escape_md(order_data.get('project_name', 'N/A'))}* \\- loyiha screenshoti"
            )

        # 2. Asosiy xabarni yangilash (tugmalarni o'chirish)
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.reply(
                f"✅ *Buyurtma bajarildi\\!*\n"
                f"Admin: @{escape_md(callback.from_user.username or 'admin')}"
            )
        except TelegramBadRequest:
            pass

        # 3. Mijozga xabar yuborish (agar user_id ma'lum bo'lsa)
        user_id = order_data.get("user_id")
        if user_id:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"🎉 *Buyurtmangiz bajarildi\\!*\n\n"
                        f"🆔 ID: `{escape_md(order_id)}`\n"
                        f"📌 Loyiha: *{escape_md(order_data.get('project_name', 'N/A'))}*\n\n"
                        f"Fikr qoldirishni unutmang\\! 👇"
                    ),
                    reply_markup=get_rating_keyboard()
                )
                # Review uchun state belgilash (review_handler da qabul qilinadi)
                logger.info(f"Mijoz {user_id} ga bajarildi xabari yuborildi")
            except Exception as e:
                logger.warning(f"Mijozga xabar yuborib bo'lmadi {user_id}: {e}")

        logger.info(f"Buyurtma {order_id} bajarildi. Admin: {callback.from_user.id}")

    except Exception as e:
        logger.error(f"admin_done xatosi: {e}")
        await callback.answer("⚠️ Xato yuz berdi!", show_alert=True)


# ============================================================
# Admin: "Jarayonda" tugmasi
# ============================================================

@admin_router.callback_query(F.data.startswith("admin_progress_"))
async def admin_mark_progress(callback: CallbackQuery, bot: Bot) -> None:
    """Buyurtmani jarayonda deb belgilash."""
    if not await admin_check(callback):
        return

    order_id = callback.data.replace("admin_progress_", "")
    order_data = orders_storage.get(order_id)

    if not order_data:
        await callback.answer("⚠️ Buyurtma topilmadi!", show_alert=True)
        return

    orders_storage[order_id]["status"] = "progress"
    await callback.answer("🔵 Jarayonda deb belgilandi!")

    try:
        await callback.message.reply(
            f"🔵 *Buyurtma jarayonda\\!*\n"
            f"🆔 `{escape_md(order_id)}`\n"
            f"Admin: @{escape_md(callback.from_user.username or 'admin')}"
        )

        # Mijozga xabar
        user_id = order_data.get("user_id")
        if user_id:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"🔵 *Buyurtmangiz qabul qilindi\\!*\n\n"
                        f"🆔 ID: `{escape_md(order_id)}`\n"
                        f"📌 Loyiha: *{escape_md(order_data.get('project_name', 'N/A'))}*\n\n"
                        f"Ishlanmoqda\\. Tez orada tayyor bo'ladi\\! 💪"
                    )
                )
            except Exception as e:
                logger.warning(f"Mijozga xabar yuborib bo'lmadi: {e}")

    except Exception as e:
        logger.error(f"admin_progress xatosi: {e}")


# ============================================================
# Admin: "Rad Etildi" tugmasi
# ============================================================

@admin_router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_order(callback: CallbackQuery, bot: Bot) -> None:
    """Buyurtmani rad etish."""
    if not await admin_check(callback):
        return

    order_id = callback.data.replace("admin_reject_", "")
    order_data = orders_storage.get(order_id)

    if not order_data:
        await callback.answer("⚠️ Buyurtma topilmadi!", show_alert=True)
        return

    orders_storage[order_id]["status"] = "rejected"
    await callback.answer("❌ Rad etildi!")

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(
            f"❌ *Buyurtma rad etildi\\.*\n"
            f"🆔 `{escape_md(order_id)}`\n"
            f"Admin: @{escape_md(callback.from_user.username or 'admin')}"
        )

        # Mijozga xabar
        user_id = order_data.get("user_id")
        if user_id:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"❌ *Buyurtmangiz rad etildi\\.*\n\n"
                        f"🆔 ID: `{escape_md(order_id)}`\n\n"
                        f"Batafsil ma'lumot uchun admin bilan bog'laning\\."
                    )
                )
            except Exception as e:
                logger.warning(f"Mijozga xabar yuborib bo'lmadi: {e}")

    except Exception as e:
        logger.error(f"admin_reject xatosi: {e}")


# ============================================================
# Admin: Mijoz bilan bog'lanish
# ============================================================

@admin_router.callback_query(F.data.startswith("admin_contact_"))
async def admin_contact_user(callback: CallbackQuery) -> None:
    """Mijoz bilan bog'lanish ma'lumotlarini ko'rsatish."""
    if not await admin_check(callback):
        return

    order_id = callback.data.replace("admin_contact_", "")
    order_data = orders_storage.get(order_id)

    if not order_data:
        await callback.answer("⚠️ Buyurtma topilmadi!", show_alert=True)
        return

    user_id = order_data.get("user_id", "N/A")
    username = order_data.get("username", "N/A")
    contact = order_data.get("contact", "N/A")

    await callback.answer(
        f"Mijoz: @{username}\n"
        f"ID: {user_id}\n"
        f"Aloqa: {contact}",
        show_alert=True
    )
