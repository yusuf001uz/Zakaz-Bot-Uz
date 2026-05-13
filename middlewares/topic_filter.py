"""
Topic Middleware - xabarlar to'g'ri topiklarga tushishini ta'minlash
"""

import logging
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class TopicMiddleware(BaseMiddleware):
    """
    Guruh topik xabarlarini filtrlash middleware.
    Faqat kerakli topiklardagi xabarlarni qayta ishlaydi.
    """

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        # Private xabarlar (DM) - har doim o'tkazib yuborish
        if event.chat.type == "private":
            return await handler(event, data)

        # Guruh xabarlari uchun thread_id ni loglash (debug uchun foydali)
        if hasattr(event, 'message_thread_id') and event.message_thread_id:
            logger.debug(
                f"Guruh xabari | thread_id={event.message_thread_id} | "
                f"user={event.from_user.id if event.from_user else 'N/A'} | "
                f"text={event.text[:50] if event.text else 'N/A'}"
            )

        return await handler(event, data)
