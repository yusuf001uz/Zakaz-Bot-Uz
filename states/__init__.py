"""
FSM (Finite State Machine) holatlari
Buyurtma va fikr qoldirish uchun alohida state guruhlar
"""

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """Buyurtma berish jarayoni holatlari."""
    waiting_project_name = State()      # 1. Loyiha nomi
    waiting_project_type = State()      # 2. Loyiha turi (inline tugmalar)
    waiting_description = State()       # 3. Batafsil tavsif
    waiting_budget = State()            # 4. Byudjet (inline tugmalar)
    waiting_deadline = State()          # 5. Muddat (inline tugmalar)
    waiting_contact = State()           # 6. Aloqa ma'lumotlari
    waiting_screenshot = State()        # 7. Ilova yoki rasm (ixtiyoriy)
    confirming_order = State()          # 8. Tasdiqlash


class ReviewStates(StatesGroup):
    """Fikr qoldirish jarayoni holatlari."""
    waiting_rating = State()            # 1. Yulduzcha reytingi (1-5)
    waiting_review_text = State()       # 2. Matnli sharh
    confirming_review = State()         # 3. Tasdiqlash
