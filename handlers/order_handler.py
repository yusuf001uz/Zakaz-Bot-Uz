"""
Buyurtma berish handleri - FSM asosidagi to'liq jarayon
"""

import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PhotoSize

from config import (
    GROUP_ID, BUYURTMA_BERISH_ID, ZAKAZ_BERILGAN_BOTLAR_ID,
    ORDER_TYPES, BUDGET_OPTIONS, DEADLINE_OPTIONS
)
from states import OrderStates
from keyboards import (
    get_start_keyboard, get_order_type_keyboard, get_budget_keyboard,
    get_deadline_keyboard, get_screenshot_keyboard, get_confirm_order_keyboard,
    get_admin_order_keyboard
)
from utils import (
    escape_md, generate_order_id, format_order_summary
)

logger = logging.getLogger(__name__)
order_router = Router(name="order_router")

# Xotirada saqlanadigan buyurtmalar (production'da DB ishlatilsin)
orders_storage: dict[str, dict] = {}


# ============================================================
# /start va /buyurtma komandalar
# ============================================================

@order_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Bot boshlanishi - private chatda."""
    await state.clear()

    user_name = message.from_user.full_name if message.from_user else "Mehmon"
    text = (
        f"Salom, *{escape_md(user_name)}*\\! 👋\n\n"
        f"Men *PinokioAI* botiman\\. Sizga quyidagilarda yordam bera olaman:\n\n"
        f"📋 *Buyurtma berish* \\- loyihangizni bizga toping\n"
        f"💬 *Fikr qoldirish* \\- xizmatimiz haqida baholang\n\n"
        f"Nima qilmoqchisiz?"
    )
    await message.answer(text, reply_markup=get_start_keyboard())


@order_router.message(
    Command("buyurtma"),
    F.chat.type == "private"
)
async def cmd_order_private(message: Message, state: FSMContext) -> None:
    """Private chatda buyurtma berish."""
    await start_order_flow(message, state)


@order_router.message(
    F.chat.type.in_({"group", "supergroup"}),
    F.message_thread_id == BUYURTMA_BERISH_ID
)
async def handle_buyurtma_topic(message: Message, state: FSMContext) -> None:
    """Buyurtma berish topigida yozilgan xabar."""
    if message.text and not message.text.startswith("/"):
        await message.reply(
            "Buyurtma berish uchun pastdagi tugmani bosing:",
            reply_markup=get_start_keyboard()
        )


# ============================================================
# Callback: "Buyurtma Berish" tugmasi bosilganda
# ============================================================

@order_router.callback_query(F.data == "start_order")
async def cb_start_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Buyurtma jarayonini boshlash."""
    await callback.answer()
    await start_order_flow(callback.message, state, callback.from_user)


async def start_order_flow(message: Message, state: FSMContext, user=None) -> None:
    """Buyurtma jarayonini boshlash - umumiy funksiya."""
    await state.set_state(OrderStates.waiting_project_name)

    if user:
        await state.update_data(
            user_id=user.id,
            username=user.username or user.full_name,
            order_id=generate_order_id()
        )
    elif message.from_user:
        await state.update_data(
            user_id=message.from_user.id,
            username=message.from_user.username or message.from_user.full_name,
            order_id=generate_order_id()
        )

    text = (
        "📋 *BUYURTMA BERISH*\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ *Loyiha nomini kiriting:*\n"
        "\\(Masalan: _\"Do'kon uchun Telegram Bot\"_\\)"
    )
    await message.answer(text)


# ============================================================
# 1-qadam: Loyiha nomi
# ============================================================

@order_router.message(OrderStates.waiting_project_name, F.text)
async def get_project_name(message: Message, state: FSMContext) -> None:
    """Loyiha nomini qabul qilish."""
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("⚠️ Loyiha nomi kamida 3 ta harfdan iborat bo'lsin\\.")
        return
    if len(name) > 100:
        await message.answer("⚠️ Loyiha nomi 100 ta belgidan oshmasin\\.")
        return

    await state.update_data(project_name=name)
    await state.set_state(OrderStates.waiting_project_type)

    text = (
        "2️⃣ *Loyiha turini tanlang:*"
    )
    await message.answer(text, reply_markup=get_order_type_keyboard())


# ============================================================
# 2-qadam: Loyiha turi (Callback)
# ============================================================

@order_router.callback_query(OrderStates.waiting_project_type, F.data.startswith("type_"))
async def get_project_type(callback: CallbackQuery, state: FSMContext) -> None:
    """Loyiha turini tanlash."""
    await callback.answer()
    project_type = callback.data.replace("type_", "")

    await state.update_data(type=project_type)
    await state.set_state(OrderStates.waiting_description)

    selected = ORDER_TYPES.get(project_type, "Noma'lum")
    text = (
        f"✅ *{escape_md(selected)}* tanlandi\\.\n\n"
        f"3️⃣ *Loyihangizni batafsil tasvirlab bering:*\n"
        f"\\(Nima qilishi kerak, qanday funksiyalar bo'lsin va h\\.k\\.\\)"
    )
    await callback.message.edit_text(text)


# ============================================================
# 3-qadam: Tavsif
# ============================================================

@order_router.message(OrderStates.waiting_description, F.text)
async def get_description(message: Message, state: FSMContext) -> None:
    """Loyiha tavsifini qabul qilish."""
    desc = message.text.strip()
    if len(desc) < 20:
        await message.answer("⚠️ Tavsif kamida 20 ta belgidan iborat bo'lsin\\. Batafsil yozing\\.")
        return

    await state.update_data(description=desc)
    await state.set_state(OrderStates.waiting_budget)

    text = "4️⃣ *Taxminiy byudjetingizni tanlang:*"
    await message.answer(text, reply_markup=get_budget_keyboard())


@order_router.callback_query(OrderStates.waiting_description, F.data == "back_to_description")
async def back_to_description(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(OrderStates.waiting_description)
    await callback.message.edit_text(
        "3️⃣ *Loyihangizni batafsil tasvirlab bering:*"
    )


# ============================================================
# 4-qadam: Byudjet (Callback)
# ============================================================

@order_router.callback_query(OrderStates.waiting_budget, F.data.startswith("budget_"))
async def get_budget(callback: CallbackQuery, state: FSMContext) -> None:
    """Byudjetni tanlash."""
    await callback.answer()
    # "budget_budget_50" => "budget_50" (double prefix correction)
    budget_key = callback.data.replace("budget_budget_", "budget_")
    budget_key = budget_key.replace("budget_", "", 1)

    await state.update_data(budget=f"budget_{budget_key}")
    await state.set_state(OrderStates.waiting_deadline)

    selected = BUDGET_OPTIONS.get(f"budget_{budget_key}", "Noma'lum")
    text = (
        f"✅ *{escape_md(selected)}* tanlandi\\.\n\n"
        f"5️⃣ *Qachongacha tayyorlanishi kerak?*"
    )
    await callback.message.edit_text(text, reply_markup=get_deadline_keyboard())


@order_router.callback_query(OrderStates.waiting_budget, F.data == "back_to_budget")
async def back_to_budget(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(OrderStates.waiting_budget)
    await callback.message.edit_text(
        "4️⃣ *Taxminiy byudjetingizni tanlang:*",
        reply_markup=get_budget_keyboard()
    )


# ============================================================
# 5-qadam: Muddat (Callback)
# ============================================================

@order_router.callback_query(OrderStates.waiting_deadline, F.data.startswith("deadline_"))
async def get_deadline(callback: CallbackQuery, state: FSMContext) -> None:
    """Muddatni tanlash."""
    await callback.answer()
    deadline_key = callback.data.replace("deadline_", "")

    await state.update_data(deadline=deadline_key)
    await state.set_state(OrderStates.waiting_contact)

    selected = DEADLINE_OPTIONS.get(deadline_key, "Noma'lum")
    text = (
        f"✅ *{escape_md(selected)}* tanlandi\\.\n\n"
        f"6️⃣ *Aloqa ma'lumotlaringizni kiriting:*\n"
        f"\\(Telefon raqam yoki Telegram @username\\)"
    )
    await callback.message.edit_text(text)


# ============================================================
# 6-qadam: Aloqa
# ============================================================

@order_router.message(OrderStates.waiting_contact, F.text)
async def get_contact(message: Message, state: FSMContext) -> None:
    """Aloqa ma'lumotlarini qabul qilish."""
    contact = message.text.strip()
    if len(contact) < 5:
        await message.answer("⚠️ Aloqa ma'lumotlari juda qisqa\\. Qayta kiriting\\.")
        return

    await state.update_data(contact=contact)
    await state.set_state(OrderStates.waiting_screenshot)

    text = (
        "7️⃣ *Ilova yoki eskiz rasm \\(ixtiyoriy\\):*\n\n"
        "Loyihangizga oid rasm, mockup yoki eskiz bo'lsa yuboring\\.\n"
        "Agar yo'q bo'lsa \\- *O'tkazib Yuborish* tugmasini bosing\\."
    )
    await message.answer(text, reply_markup=get_screenshot_keyboard())


# ============================================================
# 7-qadam: Screenshot (ixtiyoriy)
# ============================================================

@order_router.message(OrderStates.waiting_screenshot, F.photo)
async def get_screenshot(message: Message, state: FSMContext) -> None:
    """Screenshot qabul qilish."""
    photo: PhotoSize = message.photo[-1]  # Eng yuqori sifatli rasm
    await state.update_data(
        screenshot_file_id=photo.file_id,
        has_screenshot=True
    )
    await show_order_confirmation(message, state)


@order_router.callback_query(OrderStates.waiting_screenshot, F.data == "skip_screenshot")
async def skip_screenshot(callback: CallbackQuery, state: FSMContext) -> None:
    """Screenshot o'tkazib yuborish."""
    await callback.answer()
    await state.update_data(has_screenshot=False, screenshot_file_id=None)
    await show_order_confirmation(callback.message, state)


async def show_order_confirmation(message: Message, state: FSMContext) -> None:
    """Buyurtma tasdiqlash sahifasini ko'rsatish."""
    await state.set_state(OrderStates.confirming_order)
    data = await state.get_data()

    summary = format_order_summary(data)
    screenshot_info = "✅ Rasm yuklandi" if data.get("has_screenshot") else "❌ Rasm yo'q"

    text = (
        f"{summary}\n"
        f"🖼 Screenshot: {escape_md(screenshot_info)}\n\n"
        f"*Buyurtmani tasdiqlaysizmi?*"
    )
    await message.answer(text, reply_markup=get_confirm_order_keyboard())


# ============================================================
# 8-qadam: Tasdiqlash
# ============================================================

@order_router.callback_query(OrderStates.confirming_order, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Buyurtmani tasdiqlash va guruhga yuborish."""
    await callback.answer("⏳ Buyurtma yuborilmoqda...")
    data = await state.get_data()

    order_id = data.get("order_id", generate_order_id())
    orders_storage[order_id] = data  # Xotirada saqlash

    try:
        # Guruhga buyurtmani yuborish
        await send_order_to_group(bot, data, order_id)

        await callback.message.edit_text(
            f"✅ *Buyurtmangiz qabul qilindi\\!*\n\n"
            f"🆔 ID: `{escape_md(order_id)}`\n\n"
            f"Tez orada adminlar siz bilan bog'lanadi\\. "
            f"Buyurtma holatini kuzatib boring\\!"
        )
        logger.info(f"Yangi buyurtma qabul qilindi: {order_id} - user: {data.get('user_id')}")

    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Buyurtmani guruhga yuborishda xato: {e}")

        if "chat not found" in error_msg:
            bot_info = await bot.get_me()
            logger.critical(
                f"[KONFIGURATSIYA XATOSI] Guruh topilmadi!\n"
                f"  GROUP_ID={GROUP_ID} | BUYURTMA_BERISH_ID={BUYURTMA_BERISH_ID}\n"
                f"  1. Bot guruhga qoshilganmi? @{bot_info.username}\n"
                f"  2. GROUP_ID minus bilan: -100XXXXXXXXXX\n"
                f"  3. Bot guruhda admin huquqiga egami?\n"
                f"  4. BUYURTMA_BERISH_ID: topikda /get_id yuboring"
            )
            await callback.message.answer(
                "⚠️ *Sozlamada xato bor\\.*\n\n"
                "Buyurtmangiz saqlandi, admin tez orada hal qiladi\\. Uzr\\! 🙏"
            )
        elif "thread not found" in error_msg:
            logger.critical(
                f"[TOPIK XATOSI] BUYURTMA_BERISH_ID={BUYURTMA_BERISH_ID} topilmadi!\n"
                f"  Topikda /get_id buyrug ini yuboring va .env ni yangilang"
            )
            await callback.message.answer(
                "⚠️ *Topik topilmadi\\.*\nAdmin /get_id bilan ID ni tekshirsin\\."
            )
        elif "forbidden" in error_msg or "kicked" in error_msg:
            logger.critical("[RUXSAT XATOSI] Bot guruhdan chiqarib yuborilgan!")
            await callback.message.answer(
                "⚠️ *Bot guruhda faol emas\\.*\nAdmin bilan boglanin\\."
            )
        else:
            await callback.message.answer(
                "⚠️ Xato yuz berdi\\. Iltimos qayta urinib koring yoki admin bilan boglanin\\."
            )
    finally:
        await state.clear()


async def send_order_to_group(bot: Bot, data: dict, order_id: str) -> None:
    """Buyurtmani BUYURTMA_BERISH_ID topigiga yuborish."""
    from utils import format_order_summary, escape_md
    from config import ZAKAZ_BERILGAN_BOTLAR_ID

    summary = format_order_summary(data)
    text = (
        f"🆕 *YANGI BUYURTMA KELDI\\!*\n\n"
        f"{summary}\n"
        f"🖼 Screenshot: " + ("✅ Bor" if data.get("has_screenshot") else "❌ Yo'q")
    )

    # Screenshot bormi - uni ham yuborish
    if data.get("has_screenshot") and data.get("screenshot_file_id"):
        sent = await bot.send_photo(
            chat_id=GROUP_ID,
            message_thread_id=BUYURTMA_BERISH_ID,
            photo=data["screenshot_file_id"],
            caption=text,
            reply_markup=get_admin_order_keyboard(order_id)
        )
    else:
        sent = await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=BUYURTMA_BERISH_ID,
            text=text,
            reply_markup=get_admin_order_keyboard(order_id)
        )

    # Guruh xabar ID sini saqlash (keyin tahrirlash uchun)
    if order_id in orders_storage:
        orders_storage[order_id]["group_message_id"] = sent.message_id


# ============================================================
# Bekor qilish
# ============================================================

@order_router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Buyurtmani bekor qilish."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "❌ *Buyurtma bekor qilindi\\.*\n\n"
        "Qayta boshlash uchun /start ni bosing\\."
    )


@order_router.callback_query(F.data == "edit_order")
async def edit_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Buyurtmani tahrirlash - boshidan boshlash."""
    await callback.answer()
    await state.set_state(OrderStates.waiting_project_name)
    await callback.message.edit_text(
        "✏️ *Buyurtmani tahrirlash*\n\n"
        "1️⃣ *Loyiha nomini qayta kiriting:*"
    )
