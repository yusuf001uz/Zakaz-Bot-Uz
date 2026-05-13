"""
Konfiguratsiya fayli
⚠️ MUHIM: Quyidagi ID-larni o'zingiznikiga almashtiring!
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# BOT TOKEN - @BotFather dan oling
# ============================================================
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8827659709:AAESRLYSCZ3siGUBgYuWqWbR0TtX0NmNrd8")

# ============================================================
# GURUH VA TOPIK ID-LARI
# ⚠️ QANDAY ANIQLASH: Har bir topikka biror narsa yozing,
#    keyin /get_id buyrug'ini yuboring - bot thread_id ni ko'rsatadi
# ============================================================
GROUP_ID: int = int(os.getenv("GROUP_ID", "-1003998340018"))

# Topik ID-lari
BUYURTMA_BERISH_ID: int = int(os.getenv("BUYURTMA_BERISH_ID", "4"))      # Buyurtmalar topigi
ZAKAZ_BERILGAN_BOTLAR_ID: int = int(os.getenv("ZAKAZ_BERILGAN_BOTLAR_ID", "3"))  # Bajarilgan ishlar
MIJOZLAR_FIKRI_ID: int = int(os.getenv("MIJOZLAR_FIKRI_ID", "8"))        # Sharhlar topigi

# ============================================================
# ADMIN ID-LARI
# @userinfobot orqali o'z ID-ingizni bilib oling
# ============================================================
ADMIN_IDS: list[int] = [
    int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")
    if x.strip().isdigit()
]

# ============================================================
# BOT SOZLAMALARI
# ============================================================
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "@ZakazBotUz_Bot")

# Buyurtma turlari
ORDER_TYPES: dict[str, str] = {
    "telegram_bot": "🤖 Telegram Bot",
    "web_site": "🌐 Web Sayt",
    "mobile_app": "📱 Mobil Ilova",
    "automation": "⚙️ Avtomatlashtirish",
    "other": "📦 Boshqa",
}

# Byudjet variantlari
BUDGET_OPTIONS: dict[str, str] = {
    "budget_50": "💵 $50 gacha",
    "budget_100": "💵 $50 - $100",
    "budget_200": "💰 $100 - $200",
    "budget_500": "💰 $200 - $500",
    "budget_500plus": "💎 $500+",
}

# Muddat variantlari
DEADLINE_OPTIONS: dict[str, str] = {
    "urgent": "⚡ 1-3 kun (shoshilinch)",
    "week": "📅 1 hafta",
    "two_weeks": "📅 2 hafta",
    "month": "🗓 1 oy",
    "flexible": "🤝 Moslashuvchan",
}
