"""
MINDSETHAPPYBOT - Feedback handlers
Handles user feedback submission flow
"""
import logging
from typing import Dict, Optional
from dataclasses import dataclass

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.bot.keyboards.reply import get_main_menu_keyboard
from src.bot.keyboards.inline import (
    get_feedback_category_keyboard,
    get_feedback_confirm_keyboard,
    get_feedback_thanks_keyboard,
)
from src.services.feedback_service import FeedbackService

logger = logging.getLogger(__name__)
router = Router(name="feedback")


@dataclass
class FeedbackState:
    """Temporary state for feedback submission"""
    category: Optional[str] = None
    content: Optional[str] = None
    awaiting_content: bool = False


# In-memory feedback states (telegram_id -> FeedbackState)
# In production, consider using Redis or database for persistence
_feedback_states: Dict[int, FeedbackState] = {}


def get_feedback_state(telegram_id: int) -> Optional[FeedbackState]:
    """Get feedback state for user"""
    return _feedback_states.get(telegram_id)


def set_feedback_state(telegram_id: int, state: FeedbackState) -> None:
    """Set feedback state for user"""
    _feedback_states[telegram_id] = state


def clear_feedback_state(telegram_id: int) -> None:
    """Clear feedback state for user"""
    _feedback_states.pop(telegram_id, None)


def is_awaiting_feedback(telegram_id: int) -> bool:
    """Check if user is in feedback input mode"""
    state = get_feedback_state(telegram_id)
    return state is not None and state.awaiting_content


@router.message(F.text == "💡 Предложить идею")
async def handle_feedback_button(message: Message) -> None:
    """Handle 'Suggest idea' button press - start feedback flow"""
    feedback_text = (
        "💡 <b>Предложить идею</b>\n\n"
        "Я буду рад услышать твои идеи и предложения!\n"
        "Выбери категорию:"
    )
    await message.answer(
        feedback_text,
        reply_markup=get_feedback_category_keyboard()
    )


@router.callback_query(F.data == "feedback_new")
async def callback_feedback_new(callback: CallbackQuery) -> None:
    """Start new feedback from 'suggest more' button"""
    clear_feedback_state(callback.from_user.id)

    feedback_text = (
        "💡 <b>Предложить идею</b>\n\n"
        "Я буду рад услышать твои идеи и предложения!\n"
        "Выбери категорию:"
    )
    await callback.message.edit_text(
        feedback_text,
        reply_markup=get_feedback_category_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_suggestion")
async def callback_feedback_suggestion(callback: CallbackQuery) -> None:
    """User selected 'suggestion' category"""
    set_feedback_state(callback.from_user.id, FeedbackState(
        category="suggestion",
        awaiting_content=True
    ))

    await callback.message.edit_text(
        "💡 <b>Идея/предложение</b>\n\n"
        "Напиши свою идею или предложение. "
        "Я передам её разработчикам! 📝\n\n"
        "<i>Просто отправь текстовое сообщение:</i>"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_bug")
async def callback_feedback_bug(callback: CallbackQuery) -> None:
    """User selected 'bug' category"""
    set_feedback_state(callback.from_user.id, FeedbackState(
        category="bug",
        awaiting_content=True
    ))

    await callback.message.edit_text(
        "🐛 <b>Сообщение об ошибке</b>\n\n"
        "Опиши, что пошло не так. "
        "Укажи, что ты делал и что произошло. 📝\n\n"
        "<i>Просто отправь текстовое сообщение:</i>"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_other")
async def callback_feedback_other(callback: CallbackQuery) -> None:
    """User selected 'other' category"""
    set_feedback_state(callback.from_user.id, FeedbackState(
        category="other",
        awaiting_content=True
    ))

    await callback.message.edit_text(
        "💬 <b>Другое</b>\n\n"
        "Напиши своё сообщение. 📝\n\n"
        "<i>Просто отправь текстовое сообщение:</i>"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_cancel")
async def callback_feedback_cancel(callback: CallbackQuery) -> None:
    """User cancelled feedback"""
    clear_feedback_state(callback.from_user.id)

    await callback.message.edit_text(
        "❌ Отменено.\n\n"
        "Если захочешь предложить идею позже, "
        "нажми кнопку «💡 Предложить идею» в меню."
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_submit")
async def callback_feedback_submit(callback: CallbackQuery) -> None:
    """User confirmed feedback submission"""
    state = get_feedback_state(callback.from_user.id)

    if not state or not state.content:
        await callback.message.edit_text(
            "😔 Что-то пошло не так. Попробуй ещё раз.",
            reply_markup=get_feedback_category_keyboard()
        )
        await callback.answer()
        return

    # Save feedback to database
    feedback_service = FeedbackService()
    feedback = await feedback_service.submit_feedback(
        telegram_id=callback.from_user.id,
        content=state.content,
        category=state.category or "other"
    )

    clear_feedback_state(callback.from_user.id)

    if feedback:
        category_names = {
            "suggestion": "Идея/предложение",
            "bug": "Ошибка",
            "other": "Другое"
        }
        category_name = category_names.get(state.category, "Другое")

        await callback.message.edit_text(
            f"✅ <b>Спасибо за отзыв!</b>\n\n"
            f"📂 Категория: {category_name}\n"
            f"📝 Сообщение: {state.content[:100]}{'...' if len(state.content) > 100 else ''}\n\n"
            f"Твоё сообщение сохранено и будет рассмотрено. 💝",
            reply_markup=get_feedback_thanks_keyboard()
        )
    else:
        await callback.message.edit_text(
            "😔 Не удалось сохранить отзыв. Попробуй позже.",
            reply_markup=get_feedback_thanks_keyboard()
        )

    await callback.answer()


async def handle_feedback_text(message: Message) -> bool:
    """
    Handle text message when user is in feedback input mode.
    Returns True if message was handled, False otherwise.

    This should be called from messages.py before processing regular text.
    """
    state = get_feedback_state(message.from_user.id)

    if not state or not state.awaiting_content:
        return False

    # User is submitting feedback content
    state.content = message.text.strip()
    state.awaiting_content = False
    set_feedback_state(message.from_user.id, state)

    # Ask for confirmation
    category_names = {
        "suggestion": "💡 Идея/предложение",
        "bug": "🐛 Ошибка",
        "other": "💬 Другое"
    }
    category_name = category_names.get(state.category, "💬 Другое")

    preview = state.content[:200] + "..." if len(state.content) > 200 else state.content

    await message.answer(
        f"<b>Подтверди отправку:</b>\n\n"
        f"📂 Категория: {category_name}\n"
        f"📝 Сообщение:\n{preview}\n\n"
        f"Отправить?",
        reply_markup=get_feedback_confirm_keyboard()
    )

    return True
