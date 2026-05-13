"""
Yordamchi funksiyalar - matn formatlash, MarkdownV2 escape va boshqalar
"""

import re
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def escape_md(text: str) -> str:
    """
    MarkdownV2 uchun maxsus belgilarni escape qilish.
    Telegram MarkdownV2 quyidagi belgilarni talab qiladi: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if not text:
        return ""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))


def generate_order_id() -> str:
    """Unikal buyurtma ID yaratish."""
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


def get_stars(rating: int) -> str:
    """Reyting uchun yulduzcha string qaytarish."""
    return "⭐" * rating + "☆" * (5 - rating)


def format_order_summary(order_data: dict) -> str:
    """
    Buyurtma ma'lumotlarini chiroyli MarkdownV2 formatida ko'rsatish.
    Mijozga ko'rsatish uchun.
    """
    from config import ORDER_TYPES, BUDGET_OPTIONS, DEADLINE_OPTIONS

    order_type = ORDER_TYPES.get(order_data.get("type", ""), "Noma'lum")
    budget = BUDGET_OPTIONS.get(order_data.get("budget", ""), "Noma'lum")
    deadline = DEADLINE_OPTIONS.get(order_data.get("deadline", ""), "Noma'lum")

    lines = [
        "📋 *BUYURTMA MA'LUMOTLARI*",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🆔 ID: `{escape_md(order_data.get('order_id', 'N/A'))}`",
        f"📌 Loyiha nomi: *{escape_md(order_data.get('project_name', 'N/A'))}*",
        f"🔧 Turi: {escape_md(order_type)}",
        f"📝 Tavsif:",
        f"_{escape_md(order_data.get('description', 'N/A'))}_",
        f"💰 Byudjet: {escape_md(budget)}",
        f"⏱ Muddat: {escape_md(deadline)}",
        f"📞 Aloqa: {escape_md(order_data.get('contact', 'N/A'))}",
        "━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)


def format_completed_order(order_data: dict, admin_note: str = "") -> str:
    """
    Bajarilgan buyurtma uchun ZAKAZ_BERILGAN_BOTLAR topigiga yuboriladigan format.
    """
    from config import ORDER_TYPES, BUDGET_OPTIONS

    order_type = ORDER_TYPES.get(order_data.get("type", ""), "Noma'lum")
    budget = BUDGET_OPTIONS.get(order_data.get("budget", ""), "Noma'lum")
    completed_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    username = order_data.get("username", "Noma'lum")
    user_id = order_data.get("user_id", "")

    lines = [
        "✅ *BAJARILGAN LOYIHA HISOBOTI*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🆔 Buyurtma ID: `{escape_md(order_data.get('order_id', 'N/A'))}`",
        f"📌 *Loyiha Nomi:* {escape_md(order_data.get('project_name', 'N/A'))}",
        f"🔧 *Turi:* {escape_md(order_type)}",
        "",
        f"📝 *Funksiyalari:*",
        f"_{escape_md(order_data.get('description', 'N/A'))}_",
        "",
        f"💰 *Byudjet:* {escape_md(budget)}",
        f"👤 *Mijoz:* @{escape_md(username)} \\(`{escape_md(str(user_id))}`\\)",
        f"🕐 *Bajarilgan vaqt:* {escape_md(completed_time)}",
    ]

    if admin_note:
        lines.append(f"📎 *Admin izohi:* {escape_md(admin_note)}")

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "💬 _Mijozdan sharh kutilmoqda\\.\\.\\._"
    ])

    return "\n".join(lines)


def format_review_for_topic(
    username: str,
    user_id: int,
    rating: int,
    review_text: str,
    order_id: str = ""
) -> str:
    """
    Mijoz sharhini MIJOZLAR_FIKRI topigiga yuboriladigan format.
    """
    stars = get_stars(rating)
    review_time = datetime.now().strftime("%d.%m.%Y %H:%M")

    lines = [
        "💬 *YANGI MIJOZ SHARHI*",
        "━━━━━━━━━━━━━━━━━━━━",
        f"👤 Mijoz: @{escape_md(username)} \\(`{escape_md(str(user_id))}`\\)",
        f"⭐ Reyting: {escape_md(stars)} \\({rating}/5\\)",
    ]

    if order_id:
        lines.append(f"🆔 Buyurtma: `{escape_md(order_id)}`")

    lines.extend([
        "",
        f"💭 *Fikr:*",
        f"_{escape_md(review_text)}_",
        "",
        f"🕐 {escape_md(review_time)}",
        "━━━━━━━━━━━━━━━━━━━━",
    ])

    return "\n".join(lines)
