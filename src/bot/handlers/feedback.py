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
from src.services.user_service import UserService
from src.utils.localization import get_all_menu_button_texts, get_system_message

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


async def get_user_language(telegram_id: int) -> str:
    """Helper to get user's language code"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(telegram_id)
    return user.language_code if user else "ru"


async def cmd_feedback(message: Message) -> None:
    """Start feedback flow - called from messages handler"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False

    feedback_title = get_system_message("feedback_title", language_code)
    feedback_intro = get_system_message("feedback_intro_formal" if formal else "feedback_intro", language_code, formal=formal)
    feedback_choose = get_system_message("feedback_choose_category_formal" if formal else "feedback_choose_category", language_code, formal=formal)
    
    feedback_text = f"{feedback_title}\n\n{feedback_intro}\n{feedback_choose}"
    await message.answer(
        feedback_text,
        reply_markup=get_feedback_category_keyboard(language_code)
    )


@router.callback_query(F.data == "feedback_new")
async def callback_feedback_new(callback: CallbackQuery) -> None:
    """Start new feedback from 'suggest more' button"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    clear_feedback_state(callback.from_user.id)

    feedback_title = get_system_message("feedback_title", language_code)
    feedback_intro = get_system_message("feedback_intro_formal" if formal else "feedback_intro", language_code, formal=formal)
    feedback_choose = get_system_message("feedback_choose_category_formal" if formal else "feedback_choose_category", language_code, formal=formal)
    
    feedback_text = f"{feedback_title}\n\n{feedback_intro}\n{feedback_choose}"
    await callback.message.edit_text(
        feedback_text,
        reply_markup=get_feedback_category_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_suggestion")
async def callback_feedback_suggestion(callback: CallbackQuery) -> None:
    """User selected 'suggestion' category"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    
    set_feedback_state(callback.from_user.id, FeedbackState(
        category="suggestion",
        awaiting_content=True
    ))

    title = get_system_message("feedback_suggestion_title", language_code)
    text = get_system_message("feedback_suggestion_text_formal" if formal else "feedback_suggestion_text", language_code, formal=formal)
    hint = get_system_message("feedback_input_hint", language_code)
    
    await callback.message.edit_text(
        f"{title}\n\n{text}\n\n{hint}"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_bug")
async def callback_feedback_bug(callback: CallbackQuery) -> None:
    """User selected 'bug' category"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    
    set_feedback_state(callback.from_user.id, FeedbackState(
        category="bug",
        awaiting_content=True
    ))

    title = get_system_message("feedback_bug_title", language_code)
    text = get_system_message("feedback_bug_text_formal" if formal else "feedback_bug_text", language_code, formal=formal)
    hint = get_system_message("feedback_input_hint", language_code)
    
    await callback.message.edit_text(
        f"{title}\n\n{text}\n\n{hint}"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_other")
async def callback_feedback_other(callback: CallbackQuery) -> None:
    """User selected 'other' category"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    
    set_feedback_state(callback.from_user.id, FeedbackState(
        category="other",
        awaiting_content=True
    ))

    title = get_system_message("feedback_other_title", language_code)
    text = get_system_message("feedback_other_text_formal" if formal else "feedback_other_text", language_code, formal=formal)
    hint = get_system_message("feedback_input_hint", language_code)
    
    await callback.message.edit_text(
        f"{title}\n\n{text}\n\n{hint}"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_cancel")
async def callback_feedback_cancel(callback: CallbackQuery) -> None:
    """User cancelled feedback"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    clear_feedback_state(callback.from_user.id)

    cancelled = get_system_message("feedback_cancelled", language_code)
    hint = get_system_message("feedback_cancelled_hint_formal" if formal else "feedback_cancelled_hint", language_code, formal=formal)
    
    await callback.message.edit_text(
        f"{cancelled}\n\n{hint}"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_submit")
async def callback_feedback_submit(callback: CallbackQuery) -> None:
    """User confirmed feedback submission"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    state = get_feedback_state(callback.from_user.id)

    if not state or not state.content:
        error_text = get_system_message("feedback_error_formal" if formal else "feedback_error", language_code, formal=formal)
        await callback.message.edit_text(
            error_text,
            reply_markup=get_feedback_category_keyboard(language_code)
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
        # Get localized category names
        category_keys = {
            "suggestion": "feedback_suggestion_title",
            "bug": "feedback_bug_title",
            "other": "feedback_other_title"
        }
        category_key = category_keys.get(state.category, "feedback_other_title")
        category_name = get_system_message(category_key, language_code)
        # Remove HTML tags for category name
        import re
        category_name = re.sub(r'<[^>]+>', '', category_name).strip()

        saved_title = get_system_message("feedback_saved", language_code)
        saved_details = get_system_message("feedback_saved_details", language_code, category=category_name, content=state.content[:100] + ('...' if len(state.content) > 100 else ''))
        saved_confirm = get_system_message("feedback_saved_confirm_formal" if formal else "feedback_saved_confirm", language_code, formal=formal)

        await callback.message.edit_text(
            f"{saved_title}\n\n{saved_details}\n\n{saved_confirm}",
            reply_markup=get_feedback_thanks_keyboard(language_code)
        )
    else:
        error_text = get_system_message("feedback_save_error_formal" if formal else "feedback_save_error", language_code, formal=formal)
        await callback.message.edit_text(
            error_text,
            reply_markup=get_feedback_thanks_keyboard(language_code)
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

    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False

    # Check if message contains text
    if not message.text:
        text_only = get_system_message("please_send_text", language_code)
        await message.answer(text_only)
        return True

    content = message.text.strip()
    if not content:
        empty_text = get_system_message("feedback_empty_formal" if formal else "feedback_empty", language_code, formal=formal)
        await message.answer(empty_text)
        return True

    # Save immediately (no confirmation) to avoid lost in-memory state on restarts
    feedback_service = FeedbackService()
    feedback = await feedback_service.submit_feedback(
        telegram_id=message.from_user.id,
        content=content,
        category=state.category or "other",
    )

    clear_feedback_state(message.from_user.id)

    # Get localized category names
    category_keys = {
        "suggestion": "feedback_suggestion_title",
        "bug": "feedback_bug_title",
        "other": "feedback_other_title",
    }
    category_key = category_keys.get(state.category, "feedback_other_title")
    category_name = get_system_message(category_key, language_code)
    # Remove HTML tags for category name
    import re
    category_name = re.sub(r'<[^>]+>', '', category_name).strip()

    if feedback:
        saved_title = get_system_message("feedback_saved", language_code)
        saved_details = get_system_message("feedback_saved_details", language_code, category=category_name, content=content[:100] + ('...' if len(content) > 100 else ''))
        saved_short = get_system_message("feedback_saved_short", language_code)
        
        await message.answer(
            f"{saved_title}\n\n{saved_details}\n\n{saved_short}",
            reply_markup=get_feedback_thanks_keyboard(language_code),
        )
    else:
        error_text = get_system_message("feedback_save_error_formal" if formal else "feedback_save_error", language_code, formal=formal)
        await message.answer(
            error_text,
            reply_markup=get_feedback_thanks_keyboard(language_code),
        )

    return True
