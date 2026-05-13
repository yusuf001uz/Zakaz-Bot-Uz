# 🤖 PinokioAI Telegram Bot

**Guruh Topik Boshqaruv Tizimi** — aiogram 3.x asosida yozilgan professional bot

---

## 📁 Loyiha Tuzilmasi

```
telegram_bot/
├── main.py                    # Bot ishga tushirish nuqtasi
├── config.py                  # Barcha sozlamalar
├── requirements.txt           # Kutubxonalar
├── .env.example               # .env namunasi
├── handlers/
│   ├── order_handler.py       # Buyurtma FSM jarayoni
│   ├── admin_handler.py       # Admin amallar
│   └── review_handler.py      # Fikr qoldirish FSM
├── keyboards/
│   └── __init__.py            # Barcha Inline klaviaturalar
├── states/
│   └── __init__.py            # FSM holatlari
├── middlewares/
│   └── topic_filter.py        # Topik filtri
└── utils/
    └── __init__.py            # MarkdownV2, formatlashtirish
```

---

## ⚙️ O'rnatish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. .env faylini yaratish
```bash
cp .env.example .env
```

### 3. .env faylini to'ldirish

```env
BOT_TOKEN=your_bot_token_here
GROUP_ID=-1001234567890
BUYURTMA_BERISH_ID=1
ZAKAZ_BERILGAN_BOTLAR_ID=2
MIJOZLAR_FIKRI_ID=3
ADMIN_IDS=123456789,987654321
BOT_USERNAME=@YourBotUsername
```

---

## 🔍 Topik ID-larini Aniqlash

**Topik ID-lari har bir guruhda turlicha!** Quyidagi tartibda aniqlang:

1. Botni guruhga admin sifatida qo'shing
2. Har bir topikka bir narsa yozing
3. O'sha topikda `/get_id` buyrug'ini yuboring
4. Bot sizga `thread_id` ni ko'rsatadi
5. Shu qiymatni `.env` ga kiriting

---

## 🚀 Ishga Tushirish

```bash
python main.py
```

---

## 📋 Bot Buyruqlari

| Buyruq | Izoh | Kim uchun |
|--------|------|-----------|
| `/start` | Botni boshlash | Hamma |
| `/buyurtma` | Buyurtma berish | Hamma |
| `/get_id` | Topik ID ni ko'rsatish | Faqat Adminlar |
| `/orders` | Barcha buyurtmalar | Faqat Adminlar |

---

## 🔄 Buyurtma Jarayoni (FSM)

```
/start
  └─► [Buyurtma Berish tugmasi]
        └─► 1. Loyiha nomi (matn)
              └─► 2. Loyiha turi (Inline tugma)
                    └─► 3. Tavsif (matn)
                          └─► 4. Byudjet (Inline tugma)
                                └─► 5. Muddat (Inline tugma)
                                      └─► 6. Aloqa (matn)
                                            └─► 7. Screenshot (rasm/o'tkazib yuborish)
                                                  └─► 8. Tasdiqlash
                                                        └─► ✅ Guruhga yuborildi
```

---

## ⭐ Fikr Qoldirish Jarayoni

```
[Buyurtma bajarildi] → Mijozga xabar
  └─► 1. Yulduzcha tanlash (1-5)
        └─► 2. Matnli sharh yozish
              └─► 3. Tasdiqlash
                    └─► MIJOZLAR_FIKRI topigiga yuborildi
```

---

## 🛡️ Xavfsizlik

- Faqat `ADMIN_IDS` dagi foydalanuvchilar buyurtma holatini o'zgartira oladi
- `message_thread_id` filter orqali xabarlar kerakli topikka yo'naltiriladi
- FSM orqali har bir foydalanuvchining holati alohida saqlanadi

---

## 📊 Topik Vazifalari

| Topik | Vazifa | Kim yozadi |
|-------|--------|------------|
| `BUYURTMA_BERISH_ID` | Yangi buyurtmalar | Bot (avtomatik) |
| `ZAKAZ_BERILGAN_BOTLAR_ID` | Bajarilgan ishlar hisoboti | Bot (Admin "Bajarildi" bosganda) |
| `MIJOZLAR_FIKRI_ID` | Mijoz sharhlari | Bot (Mijoz fikr qoldirganda) |

---

## 🏗️ Kelajakda Qo'shish Mumkin

- [ ] PostgreSQL database (hozir xotirada saqlanadi)
- [ ] Admin panel (web yoki bot ichida)
- [ ] Buyurtma statistikasi
- [ ] Webhook rejimi (polling o'rniga)
- [ ] Redis FSM storage (ko'p serverlar uchun)

---

*Muallif: **PinokioAI** (Muhammadyusuf Abdug'afforov)*
