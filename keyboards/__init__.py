"""
Inline klaviaturalar - barcha tugmalar shu yerda
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ORDER_TYPES, BUDGET_OPTIONS, DEADLINE_OPTIONS


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Boshlash menyu klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📋 Buyurtma Berish",
            callback_data="start_order"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="💬 Fikr Qoldirish",
            callback_data="start_review"
        ),
        InlineKeyboardButton(
            text="ℹ️ Xizmatlar",
            callback_data="show_services"
        )
    )
    return builder.as_markup()


def get_order_type_keyboard() -> InlineKeyboardMarkup:
    """Buyurtma turi tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for key, label in ORDER_TYPES.items():
        builder.button(
            text=label,
            callback_data=f"type_{key}"
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_order")
    )
    return builder.as_markup()


def get_budget_keyboard() -> InlineKeyboardMarkup:
    """Byudjet tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for key, label in BUDGET_OPTIONS.items():
        builder.button(
            text=label,
            callback_data=f"budget_{key}"
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_description"),
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_order")
    )
    return builder.as_markup()


def get_deadline_keyboard() -> InlineKeyboardMarkup:
    """Muddat tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for key, label in DEADLINE_OPTIONS.items():
        builder.button(
            text=label,
            callback_data=f"deadline_{key}"
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_budget"),
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_order")
    )
    return builder.as_markup()


def get_screenshot_keyboard() -> InlineKeyboardMarkup:
    """Screenshot/ilova yuborish yoki o'tkazib yuborish."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭ O'tkazib Yuborish", callback_data="skip_screenshot")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_order")
    )
    return builder.as_markup()


def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_order"),
        InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit_order")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_order")
    )
    return builder.as_markup()


def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Yulduzcha reytingi tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    stars = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    for i, star in enumerate(stars, 1):
        builder.button(text=star, callback_data=f"rating_{i}")
    builder.adjust(5)
    builder.row(
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_review")
    )
    return builder.as_markup()


def get_confirm_review_keyboard() -> InlineKeyboardMarkup:
    """Sharhni tasdiqlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_review"),
        InlineKeyboardButton(text="✏️ Qayta Yozish", callback_data="rewrite_review")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_review")
    )
    return builder.as_markup()


def get_admin_order_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Admin uchun buyurtma boshqaruv klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Bajarildi",
            callback_data=f"admin_done_{order_id}"
        ),
        InlineKeyboardButton(
            text="🔄 Jarayonda",
            callback_data=f"admin_progress_{order_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Rad Etildi",
            callback_data=f"admin_reject_{order_id}"
        ),
        InlineKeyboardButton(
            text="💬 Mijozga Yoz",
            callback_data=f"admin_contact_{order_id}"
        )
    )
    return builder.as_markup()
