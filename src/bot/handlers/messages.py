"""
MINDSETHAPPYBOT - Message handlers
Handles text messages and voice messages from users
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.enums import ChatAction

from src.bot.keyboards.reply import get_main_menu_keyboard
from src.bot.keyboards.inline import get_social_profile_keyboard
from src.bot.states.social_profile import SocialProfileStates
from src.services.moment_service import MomentService
from src.services.dialog_service import DialogService
from src.services.speech_service import SpeechToTextService
from src.services.personalization_service import PersonalizationService
from src.services.conversation_log_service import ConversationLogService
from src.services.social_profile_service import SocialProfileService
from src.utils.localization import detect_and_update_language

logger = logging.getLogger(__name__)
router = Router(name="messages")

dialog_service = DialogService.get_instance()
conversation_log = ConversationLogService()


@router.message(F.text == "📖 Мои моменты")
async def handle_moments_button(message: Message) -> None:
    """Handle 'My moments' button press"""
    from src.bot.handlers.commands import cmd_moments
    await cmd_moments(message)


@router.message(F.text == "📊 Статистика")
async def handle_stats_button(message: Message) -> None:
    """Handle 'Statistics' button press"""
    from src.bot.handlers.commands import cmd_stats
    await cmd_stats(message)


@router.message(F.text == "⚙️ Настройки")
async def handle_settings_button(message: Message) -> None:
    """Handle 'Settings' button press"""
    from src.bot.handlers.commands import cmd_settings
    await cmd_settings(message)


@router.message(F.text == "💬 Поговорить")
async def handle_talk_button(message: Message) -> None:
    """Handle 'Talk' button press"""
    from src.bot.handlers.commands import cmd_talk
    await cmd_talk(message)


# Cancel command for FSM states
@router.message(Command("cancel"), StateFilter(SocialProfileStates))
async def cancel_social_profile_state(message: Message, state: FSMContext) -> None:
    """Cancel social profile input"""
    await state.clear()
    social_service = SocialProfileService()
    summary = await social_service.get_profile_summary(message.from_user.id)
    await message.answer(
        f"❌ Отменено.\n\n👤 <b>Социальный профиль</b>\n\n{summary}",
        reply_markup=get_social_profile_keyboard()
    )


# Social profile FSM handlers
@router.message(StateFilter(SocialProfileStates.waiting_for_social_link))
async def handle_social_link_input(message: Message, state: FSMContext) -> None:
    """Handle social network link input"""
    url = message.text.strip()

    social_service = SocialProfileService()
    success, result_message = await social_service.add_social_link(message.from_user.id, url)

    await state.clear()

    if success:
        summary = await social_service.get_profile_summary(message.from_user.id)
        await message.answer(
            f"✅ {result_message}\n\n👤 <b>Социальный профиль</b>\n\n{summary}",
            reply_markup=get_social_profile_keyboard()
        )
    else:
        await message.answer(
            f"❌ {result_message}",
            reply_markup=get_social_profile_keyboard()
        )


@router.message(StateFilter(SocialProfileStates.waiting_for_bio))
async def handle_bio_input(message: Message, state: FSMContext) -> None:
    """Handle bio text input"""
    bio_text = message.text.strip()

    if len(bio_text) > 1000:
        await message.answer(
            "❌ Биография слишком длинная. Максимум 1000 символов.\n"
            "Попробуй сократить текст или отправь /cancel для отмены."
        )
        return

    social_service = SocialProfileService()
    success, result_message = await social_service.update_bio(message.from_user.id, bio_text)

    await state.clear()

    if success:
        summary = await social_service.get_profile_summary(message.from_user.id)
        await message.answer(
            f"✅ {result_message}\n\n👤 <b>Социальный профиль</b>\n\n{summary}",
            reply_markup=get_social_profile_keyboard()
        )
    else:
        await message.answer(
            f"❌ {result_message}",
            reply_markup=get_social_profile_keyboard()
        )


@router.message(F.voice)
async def handle_voice_message(message: Message) -> None:
    """
    Handle voice messages
    - Download voice file
    - Transcribe using Whisper API
    - Process as text response
    """
    await message.answer("🎙 Распознаю голосовое сообщение...")

    speech_service = SpeechToTextService()

    try:
        # Download voice file
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        file_path = file.file_path

        # Download and transcribe
        transcribed_text = await speech_service.transcribe_voice(
            bot=message.bot,
            file_path=file_path
        )

        if not transcribed_text or transcribed_text.strip() == "":
            await message.answer(
                "😔 Не удалось распознать голос. Попробуй ещё раз или напиши текстом."
            )
            return

        # Process as moment
        moment_service = MomentService()
        personalization_service = PersonalizationService()

        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="user_response",
            content=transcribed_text,
            metadata={"source": "voice", "voice_file_id": voice.file_id},
        )

        moment = await moment_service.create_moment(
            telegram_id=message.from_user.id,
            content=transcribed_text,
            source_type="voice",
            voice_file_id=voice.file_id
        )

        # Show typing indicator while generating response
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Generate personalized response
        response = await personalization_service.generate_response(
            telegram_id=message.from_user.id,
            moment_content=transcribed_text
        )

        await message.answer(
            f"✅ Распознано: «{transcribed_text}»\n\n{response}",
            reply_markup=get_main_menu_keyboard()
        )

        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="bot_reply",
            content=response,
            metadata={"source": "voice"},
        )

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await message.answer(
            "😔 Произошла ошибка при обработке голосового сообщения. "
            "Попробуй ещё раз или напиши текстом."
        )


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """
    Handle text messages
    - Could be a response to a question
    - Could be free dialog
    - Could be feedback input
    - Could be any other text input
    """
    text = message.text.strip()

    # Check if text is empty or whitespace only
    if not text:
        await message.answer(
            "🤔 Кажется, сообщение пустое. Расскажи что-нибудь хорошее!"
        )
        return

    # Check if user is in feedback input mode
    from src.bot.handlers.feedback import handle_feedback_text
    if await handle_feedback_text(message):
        return  # Feedback handled

    # Get user state to determine context
    from src.services.user_service import UserService
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer(
            "Пожалуйста, начни с команды /start"
        )
        return

    # Detect and update language based on user's message
    await detect_and_update_language(message.from_user.id, text)

    # Dialog mode: route to DialogService (persists to conversations)
    if dialog_service.is_in_dialog(message.from_user.id):
        from src.bot.keyboards.inline import get_dialog_keyboard
        # Show typing indicator while generating AI response
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        response = await dialog_service.process_dialog_message(
            telegram_id=message.from_user.id,
            message=text,
        )
        await message.answer(response, reply_markup=get_dialog_keyboard())
        return

    # Normal mode: log to conversations for admin visibility
    await conversation_log.log(
        telegram_id=message.from_user.id,
        message_type="user_response",
        content=text,
        metadata={"source": "text"},
    )

    moment_service = MomentService()
    personalization_service = PersonalizationService()

    # Show typing indicator while processing AI tasks
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # Check for negative mood
    is_negative = await personalization_service.detect_negative_mood(text)

    if is_negative:
        # Find relevant past positive moments
        similar_moments = await moment_service.find_similar_moments(
            telegram_id=message.from_user.id,
            query_text=text,
            limit=3
        )

        if similar_moments:
            # Remind about past positive moments - refresh typing indicator
            await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            response = await personalization_service.generate_supportive_response(
                telegram_id=message.from_user.id,
                current_text=text,
                past_moments=similar_moments
            )
        else:
            # Refresh typing indicator before generating response
            await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            response = await personalization_service.generate_empathetic_response(
                telegram_id=message.from_user.id,
                text=text
            )

        await message.answer(response, reply_markup=get_main_menu_keyboard())
        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="bot_reply",
            content=response,
            metadata={"source": "text", "kind": "supportive" if is_negative else "other"},
        )
    else:
        # Save as positive moment
        moment = await moment_service.create_moment(
            telegram_id=message.from_user.id,
            content=text,
            source_type="text"
        )

        # Refresh typing indicator before generating response
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Generate personalized positive response
        response = await personalization_service.generate_response(
            telegram_id=message.from_user.id,
            moment_content=text
        )

        await message.answer(response, reply_markup=get_main_menu_keyboard())
        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="bot_reply",
            content=response,
            metadata={"source": "text", "kind": "positive"},
        )
