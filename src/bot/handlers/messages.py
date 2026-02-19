"""
MINDSETHAPPYBOT - Message handlers
Handles text messages and voice messages from users
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
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
from src.utils.localization import detect_and_update_language, get_all_menu_button_texts, get_language_code, get_menu_text

logger = logging.getLogger(__name__)
router = Router(name="messages")

dialog_service = DialogService.get_instance()
conversation_log = ConversationLogService()


@router.message(F.text.in_(get_all_menu_button_texts("menu_moments")))
async def handle_moments_button(message: Message) -> None:
    """Handle 'My moments' button press"""
    from src.bot.handlers.commands import cmd_moments
    await cmd_moments(message)


@router.message(F.text.in_(get_all_menu_button_texts("menu_stats")))
async def handle_stats_button(message: Message) -> None:
    """Handle 'Statistics' button press"""
    from src.bot.handlers.commands import cmd_stats
    await cmd_stats(message)


@router.message(F.text.in_(get_all_menu_button_texts("menu_settings")))
async def handle_settings_button(message: Message) -> None:
    """Handle 'Settings' button press"""
    from src.bot.handlers.commands import cmd_settings
    await cmd_settings(message)


@router.message(F.text.in_(get_all_menu_button_texts("menu_talk")))
async def handle_talk_button(message: Message) -> None:
    """Handle 'Talk' button press"""
    from src.bot.handlers.commands import cmd_talk
    await cmd_talk(message)


@router.message(F.text.in_(get_all_menu_button_texts("menu_feedback")))
async def handle_feedback_button(message: Message) -> None:
    """Handle 'Feedback' button press"""
    from src.bot.handlers.feedback import cmd_feedback
    await cmd_feedback(message)


@router.message(F.text.in_(get_all_menu_button_texts("menu_pause")))
async def handle_pause_button(message: Message) -> None:
    """Handle 'Pause' button press"""
    from src.services.user_service import UserService
    from src.bot.keyboards.inline import get_pause_period_keyboard
    from src.utils.localization import get_system_message
    
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    
    title_key = "pause_title_formal" if formal else "pause_title"
    prompt_key = "pause_select_period_formal" if formal else "pause_select_period"
    
    title = get_system_message(title_key, language_code)
    prompt = get_system_message(prompt_key, language_code)
    
    await message.answer(
        f"{title}\n\n{prompt}",
        reply_markup=get_pause_period_keyboard(language_code)
    )


# Cancel command for FSM states
@router.message(Command("cancel"), StateFilter(SocialProfileStates))
async def cancel_social_profile_state(message: Message, state: FSMContext) -> None:
    """Cancel social profile input"""
    from src.services.user_service import UserService
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = get_language_code(user.language_code) if user else "ru"

    await state.clear()
    social_service = SocialProfileService()
    formal = user.formal_address if user else False
    from src.utils.localization import get_system_message
    cancelled = get_system_message("cancelled", language_code)
    profile_title = get_system_message("social_profile_title", language_code)
    summary = await social_service.get_profile_summary(message.from_user.id, language_code, formal)
    await message.answer(
        f"❌ {cancelled}\n\n{profile_title}\n\n{summary}",
        reply_markup=get_social_profile_keyboard(language_code)
    )


# Social profile FSM handlers
@router.message(StateFilter(SocialProfileStates.waiting_for_social_link))
async def handle_social_link_input(message: Message, state: FSMContext) -> None:
    """Handle social network link input"""
    from src.services.user_service import UserService

    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False

    # Check if message contains text
    if not message.text:
        from src.utils.localization import get_system_message
        text_only_message = get_system_message("please_send_text", language_code)
        await message.answer(text_only_message)
        return

    url = message.text.strip()

    social_service = SocialProfileService()
    success, result_message, profile_parse_failed = await social_service.add_social_link(
        message.from_user.id, url, language_code, formal
    )

    await state.clear()

    if success:
        from src.utils.localization import get_system_message
        profile_title = get_system_message("social_profile_title", language_code)
        summary = await social_service.get_profile_summary(message.from_user.id, language_code, formal)

        # Build response message
        response_parts = [f"✅ {result_message}"]

        # If profile parsing failed, show the warning message
        if profile_parse_failed:
            parse_failed_msg = get_menu_text("social_parse_failed", language_code)
            response_parts.append(f"\n⚠️ {parse_failed_msg}")

        response_parts.append(f"\n\n{profile_title}\n\n{summary}")

        await message.answer(
            "".join(response_parts),
            reply_markup=get_social_profile_keyboard(language_code)
        )
    else:
        await message.answer(
            f"❌ {result_message}",
            reply_markup=get_social_profile_keyboard(language_code)
        )


@router.message(StateFilter(SocialProfileStates.waiting_for_bio))
async def handle_bio_input(message: Message, state: FSMContext) -> None:
    """Handle bio text input"""
    from src.services.user_service import UserService
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = get_language_code(user.language_code) if user else "ru"
    formal = user.formal_address if user else False

    # Check if message contains text
    if not message.text:
        from src.utils.localization import get_system_message
        text_only_message = get_system_message("please_send_text", language_code)
        await message.answer(text_only_message)
        return

    bio_text = message.text.strip()

    if len(bio_text) > 1000:
        from src.utils.localization import get_system_message
        bio_too_long = get_system_message("bio_too_long", language_code)
        bio_hint = get_system_message("bio_too_long_hint_formal" if formal else "bio_too_long_hint", language_code, formal=formal)
        await message.answer(
            f"{bio_too_long}\n{bio_hint}"
        )
        return

    social_service = SocialProfileService()
    success, result_message = await social_service.update_bio(
        message.from_user.id, bio_text, language_code, formal
    )

    await state.clear()

    if success:
        from src.utils.localization import get_system_message
        profile_title = get_system_message("social_profile_title", language_code)
        summary = await social_service.get_profile_summary(message.from_user.id, language_code, formal)
        await message.answer(
            f"✅ {result_message}\n\n{profile_title}\n\n{summary}",
            reply_markup=get_social_profile_keyboard(language_code)
        )
    else:
        await message.answer(
            f"❌ {result_message}",
            reply_markup=get_social_profile_keyboard(language_code)
        )


@router.message(F.voice)
async def handle_voice_message(message: Message) -> None:
    """
    Handle voice messages
    - Download voice file
    - Transcribe using Whisper API with auto language detection
    - Respond in the same language as the voice message
    - UI (status, menu) always in user's interface language; reply in voice language
    """
    from src.services.user_service import UserService
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    ui_lang = get_language_code(user.language_code) if user else "ru"

    # Clear pending prompt when user replies via voice
    if user and getattr(user, 'last_pending_prompt_message_id', None):
        await user_service.clear_pending_prompt(message.from_user.id)
        logger.debug(f"Cleared pending prompt for user {message.from_user.id} (voice)")

    # Processing message — always in user's UI language
    processing_messages = {
        "ru": "🎙 Распознаю голосовое сообщение...",
        "en": "🎙 Recognizing voice message...",
        "uk": "🎙 Розпізнаю голосове повідомлення...",
        "he": "🎙 מזהה הודעת קול...",
        "ja": "🎙 音声メッセージを認識しています...",
        "zh": "🎙 正在识别语音消息...",
        "it": "🎙 Riconoscimento messaggio vocale...",
        "pt": "🎙 Reconhecendo mensagem de voz...",
        "fr": "🎙 Reconnaissance du message vocal...",
        "de": "🎙 Sprachnachricht wird erkannt...",
        "es": "🎙 Reconociendo mensaje de voz...",
    }
    await message.answer(processing_messages.get(ui_lang, processing_messages["ru"]))

    speech_service = SpeechToTextService()

    try:
        # Download voice file
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        file_path = file.file_path

        # Download and transcribe - now returns (text, detected_language)
        transcribed_text, detected_language = await speech_service.transcribe_voice(
            bot=message.bot,
            file_path=file_path,
            telegram_id=message.from_user.id,
        )

        if not transcribed_text or transcribed_text.strip() == "":
            error_messages = {
                "ru": "😔 Не удалось распознать голос. Попробуй ещё раз или напиши текстом.",
                "en": "😔 Couldn't recognize voice. Please try again or type your message.",
                "uk": "😔 Не вдалося розпізнати голос. Спробуй ще раз або напиши текстом.",
                "he": "😔 לא הצלחתי לזהות את הקול. נסה שוב או כתוב הודעה.",
                "ja": "😔 音声を認識できませんでした。もう一度お試しか、文字で送ってください。",
                "zh": "😔 无法识别语音。请重试或输入文字。",
                "it": "😔 Impossibile riconoscere la voce. Riprova o scrivi il messaggio.",
                "pt": "😔 Não foi possível reconhecer a voz. Tente de novo ou escreva sua mensagem.",
                "fr": "😔 Impossible de reconnaître la voix. Réessaie ou écris ton message.",
                "de": "😔 Spracherkennung fehlgeschlagen. Bitte versuche es erneut oder schreibe.",
                "es": "😔 No se pudo reconocer la voz. Intenta de nuevo o escribe tu mensaje.",
            }
            await message.answer(error_messages.get(ui_lang, error_messages["ru"]))
            return

        # Reply in detected voice language; do NOT overwrite user's UI language
        response_language = get_language_code(detected_language) if detected_language else ui_lang

        # Process as moment
        moment_service = MomentService()
        personalization_service = PersonalizationService()

        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="user_response",
            content=transcribed_text,
            metadata={"source": "voice", "voice_file_id": voice.file_id, "detected_language": detected_language},
        )

        await moment_service.create_moment(
            telegram_id=message.from_user.id,
            content=transcribed_text,
            source_type="voice",
            voice_file_id=voice.file_id
        )

        # Show typing indicator while generating response
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Generate personalized response in the detected language
        response = await personalization_service.generate_response(
            telegram_id=message.from_user.id,
            moment_content=transcribed_text,
            override_language=response_language  # Force response in voice message language
        )

        # "Recognized" prefix — UI language (user's interface), not voice language
        recognized_prefix = {
            "ru": "✅ Распознано",
            "en": "✅ Recognized",
            "uk": "✅ Розпізнано",
            "he": "✅ זוהה",
            "ja": "✅ 認識しました",
            "zh": "✅ 已识别",
            "it": "✅ Riconosciuto",
            "pt": "✅ Reconhecido",
            "fr": "✅ Reconnu",
            "de": "✅ Erkannt",
            "es": "✅ Reconocido",
        }
        prefix = recognized_prefix.get(ui_lang, recognized_prefix["ru"])

        await message.answer(
            f"{prefix}: «{transcribed_text}»\n\n{response}",
            reply_markup=get_main_menu_keyboard(ui_lang)
        )

        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="bot_reply",
            content=response,
            metadata={"source": "voice", "response_language": response_language},
        )

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        error_messages = {
            "ru": "😔 Произошла ошибка при обработке голосового сообщения. Попробуй ещё раз или напиши текстом.",
            "en": "😔 An error occurred while processing the voice message. Please try again or type your message.",
            "uk": "😔 Сталася помилка при обробці голосового повідомлення. Спробуй ще раз або напиши текстом.",
            "he": "😔 אירעה שגיאה בעת עיבוד ההודעה הקולית. נסה שוב או כתוב הודעה.",
            "ja": "😔 音声メッセージの処理中にエラーが発生しました。もう一度お試しか、文字で送ってください。",
            "zh": "😔 处理语音消息时出错。请重试或输入文字。",
            "it": "😔 Errore durante l'elaborazione del messaggio vocale. Riprova o scrivi il messaggio.",
            "pt": "😔 Ocorreu um erro ao processar a mensagem de voz. Tente de novo ou escreva sua mensagem.",
            "fr": "😔 Erreur lors du traitement du message vocal. Réessaie ou écris ton message.",
            "de": "😔 Bei der Verarbeitung der Sprachnachricht ist ein Fehler aufgetreten. Bitte versuche es erneut oder schreibe.",
            "es": "😔 Ocurrió un error al procesar el mensaje de voz. Intenta de nuevo o escribe tu mensaje.",
        }
        await message.answer(error_messages.get(ui_lang, error_messages["ru"]))


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """
    Handle text messages
    - Could be a response to a question
    - Could be free dialog
    - Could be feedback input
    - Could be any other text input
    """
    # Safety check for text, although F.text filter should ensure it exists
    if not message.text:
        logger.warning(f"Received non-text message in text handler from user {message.from_user.id}")
        return

    logger.info(
        f"Received text message from user {message.from_user.id} "
        f"in chat {message.chat.id} ({message.chat.type}): {message.text[:100]}"
    )
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

    # Clear pending prompt when user replies (to prevent deletion of answered prompts)
    if user and getattr(user, 'last_pending_prompt_message_id', None):
        await user_service.clear_pending_prompt(message.from_user.id)
        logger.debug(f"Cleared pending prompt for user {message.from_user.id}")

    language_code = user.language_code if user else "ru"

    # Detect and update language based on user's message
    detected_lang = await detect_and_update_language(message.from_user.id, text)
    if detected_lang:
        language_code = detected_lang

    def _looks_like_question_or_request(t: str) -> bool:
        """
        Lightweight intent routing:
        if user asks a question / requests help, answer it (dialog-style) instead of saving as a "moment".
        """
        s = (t or "").strip()
        low = s.lower()
        if not s:
            return False
        if "?" in s:
            return True
        # mid-sentence intents like "я хочу вспомнить..." should still route as a request
        if any(k in low for k in ("вспомн", "помни", "напомни", "покажи", "найди", "расскажи", "объясни")):
            return True
        request_starts = (
            "как ",
            "почему ",
            "зачем ",
            "что ",
            "когда ",
            "где ",
            "какой ",
            "какая ",
            "какие ",
            "сколько ",
            "расскажи",
            "объясни",
            "помоги",
            "подскажи",
            "посоветуй",
            "составь",
            "сделай",
            "дай",
            "найди",
            "вспомни",
        )
        if low.startswith(request_starts):
            return True
        return False

    async def _should_continue_request_flow(telegram_id: int) -> bool:
        """
        If the last bot_reply was produced by dialog pipeline (has rag metadata),
        treat the next user message as continuation even if it doesn't look like a request.
        """
        try:
            from datetime import datetime, timedelta, timezone
            from sqlalchemy import select, and_
            from src.db.database import get_session
            from src.db.models import User, Conversation

            async with get_session() as session:
                res_u = await session.execute(select(User).where(User.telegram_id == telegram_id))
                u = res_u.scalar_one_or_none()
                if not u:
                    return False

                since = datetime.now(timezone.utc) - timedelta(minutes=10)
                res = await session.execute(
                    select(Conversation)
                    .where(
                        and_(
                            Conversation.user_id == u.id,
                            Conversation.created_at >= since,
                            Conversation.message_type == "bot_reply",
                        )
                    )
                    .order_by(Conversation.created_at.desc())
                    .limit(1)
                )
                last = res.scalar_one_or_none()
                if not last or not last.message_metadata:
                    return False
                meta = last.message_metadata or {}
                # dialog_service stores rag_metadata; normal mode uses {"source":"text",...}
                return "rag_mode" in meta or "retrieval_used" in meta
        except Exception:
            return False

    # Safety: auto-close stale Talk mode so users don't get stuck in dialog flow.
    await dialog_service.expire_stale_dialog(message.from_user.id)

    # Dialog mode: route to DialogService only when dialog mode is explicitly active.
    # To avoid losing user moments, still persist clearly "moment-like" texts.
    if await dialog_service.is_in_dialog(message.from_user.id):
        from src.bot.keyboards.inline import get_dialog_keyboard
        moment_service = MomentService()

        if not _looks_like_question_or_request(text):
            await moment_service.create_moment(
                telegram_id=message.from_user.id,
                content=text,
                source_type="text",
            )
            logger.info(
                "Saved moment in dialog mode for user %s: %s",
                message.from_user.id,
                text[:100],
            )

        # Show typing indicator while generating AI response
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        response = await dialog_service.process_dialog_message(
            telegram_id=message.from_user.id,
            message=text,
        )
        await message.answer(response, reply_markup=get_dialog_keyboard(language_code))
        return

    # Normal mode: if user asks a question/request, answer it directly (RAG dialog pipeline).
    if _looks_like_question_or_request(text) or await _should_continue_request_flow(message.from_user.id):
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        response = await dialog_service.process_dialog_message(
            telegram_id=message.from_user.id,
            message=text,
        )
        await message.answer(response, reply_markup=get_main_menu_keyboard(language_code))
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
                past_moments=similar_moments,
                override_language=language_code  # Pass detected language
            )
        else:
            # Refresh typing indicator before generating response
            await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            response = await personalization_service.generate_empathetic_response(
                telegram_id=message.from_user.id,
                text=text,
                override_language=language_code  # Pass detected language
            )

        await message.answer(response, reply_markup=get_main_menu_keyboard(language_code))
        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="bot_reply",
            content=response,
            metadata={"source": "text", "kind": "supportive" if is_negative else "other"},
        )
    else:
        # Save as positive moment
        await moment_service.create_moment(
            telegram_id=message.from_user.id,
            content=text,
            source_type="text"
        )

        # Refresh typing indicator before generating response
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Generate personalized positive response
        response = await personalization_service.generate_response(
            telegram_id=message.from_user.id,
            moment_content=text,
            override_language=language_code  # Pass detected language
        )

        await message.answer(response, reply_markup=get_main_menu_keyboard(language_code))
        await conversation_log.log(
            telegram_id=message.from_user.id,
            message_type="bot_reply",
            content=response,
            metadata={"source": "text", "kind": "positive"},
        )
