"""
MINDSETHAPPYBOT - Command handlers
Handles all bot commands: /start, /help, /settings, /moments, /stats, etc.
"""
import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, URLInputFile
from aiogram.filters import Command, CommandStart

from src.bot.keyboards.reply import get_main_menu_keyboard
from src.bot.keyboards.inline import get_settings_keyboard, get_onboarding_keyboard
from src.db.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.utils.localization import get_system_message, get_onboarding_text, get_language_code, t

logger = logging.getLogger(__name__)
router = Router(name="commands")

# Welcome image URL (using a placeholder positive/mindset image)
WELCOME_IMAGE_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop"

# Path to local welcome image (if exists)
ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"
WELCOME_IMAGE_PATH = ASSETS_DIR / "welcome.jpg"


async def send_welcome_image(message: Message) -> bool:
    """
    Send welcome image to user
    Returns True if image was sent successfully, False otherwise
    """
    try:
        # Try local file first
        if WELCOME_IMAGE_PATH.exists():
            photo = FSInputFile(str(WELCOME_IMAGE_PATH))
            await message.answer_photo(photo)
            return True

        # Fall back to URL image
        photo = URLInputFile(WELCOME_IMAGE_URL)
        await message.answer_photo(photo)
        return True
    except Exception as e:
        logger.warning(f"Could not send welcome image: {e}")
        return False


def get_localized_welcome_text(first_name: str, language_code: str) -> str:
    """Get welcome text in user's language with voice message info"""
    return get_onboarding_text("welcome_with_voice", language_code, first_name=first_name)


def get_localized_welcome_back_text(first_name: str, language_code: str) -> str:
    """Get welcome back text in user's language"""
    lang = get_language_code(language_code) if language_code else "ru"
    if lang == "en":
        return (
            f"Welcome back, {first_name}! 💝\n\n"
            "Good to see you again. How can I help?"
        )
    if lang == "uk":
        return (
            f"З поверненням, {first_name}! 💝\n\n"
            "Радий знову тебе бачити. Чим можу допомогти?"
        )
    if lang == "he":
        return (
            f"ברוך שובך, {first_name}! 💝\n\n"
            "טוב לראות אותך שוב. איך אני יכול לעזור?"
        )
    if lang == "es":
        return (
            f"¡Bienvenido de nuevo, {first_name}! 💝\n\n"
            "Me alegra verte otra vez. ¿En qué puedo ayudarte?"
        )
    if lang == "de":
        return (
            f"Willkommen zurück, {first_name}! 💝\n\n"
            "Schön, dich wiederzusehen. Womit kann ich helfen?"
        )
    if lang == "fr":
        return (
            f"Ravi de te revoir, {first_name}! 💝\n\n"
            "Comment puis-je t'aider?"
        )
    if lang == "pt":
        return (
            f"Bem-vindo de volta, {first_name}! 💝\n\n"
            "Que bom ver-te outra vez. Em que posso ajudar?"
        )
    if lang == "it":
        return (
            f"Bentornato, {first_name}! 💝\n\n"
            "Che piacere rivederti. Come posso aiutarti?"
        )
    if lang == "zh":
        return (
            f"欢迎回来，{first_name}！💝\n\n"
            "很高兴再见到你。需要什么帮助？"
        )
    if lang == "ja":
        return (
            f"おかえり、{first_name}！💝\n\n"
            "また会えてうれしい。何か手伝うことある？"
        )
    return (
        f"С возвращением, {first_name}! 💝\n\n"
        "Рад снова тебя видеть. Чем могу помочь?"
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Handle /start command
    - For new users: Start onboarding flow with welcome image
    - For existing users: Show welcome back message
    """
    user_service = UserService()
    user = await user_service.get_or_create_user(message.from_user)
    language_code = get_language_code(user.language_code) if user else "ru"

    if not user.onboarding_completed:
        # New user - send welcome image first
        await send_welcome_image(message)

        # Get localized welcome text based on user's language
        welcome_text = get_localized_welcome_text(user.first_name, language_code)

        await message.answer(
            welcome_text,
            reply_markup=get_onboarding_keyboard(language_code)
        )
    else:
        # Existing user - welcome back
        welcome_back_text = get_localized_welcome_back_text(user.first_name, language_code)

        await message.answer(
            welcome_back_text,
            reply_markup=get_main_menu_keyboard(language_code)
        )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command - show available commands and usage"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False

    # Build help text from localized messages
    help_title = get_system_message("help_title", language_code)
    help_start = get_system_message("help_start", language_code)
    help_help = get_system_message("help_help", language_code)
    help_settings = get_system_message("help_settings", language_code)
    help_stats = get_system_message("help_stats", language_code)
    help_privacy = get_system_message("help_privacy", language_code)
    help_export = get_system_message("help_export", language_code)
    help_delete = get_system_message("help_delete", language_code)

    # Additional commands (not in SYSTEM_MESSAGES yet, so use inline approach)
    if language_code.startswith("en"):
        help_moments = "/moments - View moment history"
        help_talk = "/talk - Start free dialog"
        how_it_works_title = "💡 <b>How it works</b>"
        how_it_works = (
            "Every few hours I'll ask: \"What good happened?\" "
            "You can reply with text or voice message. "
            "I'll save your happy moments and remind you of them "
            "when you need support. 🌟"
        )
    elif language_code.startswith("uk"):
        help_moments = "/moments - Переглянути історію моментів"
        help_talk = "/talk - Почати вільний діалог"
        how_it_works_title = "💡 <b>Як це працює</b>"
        how_it_works = (
            "Кожні кілька годин я запитаю: «Що хорошого сталося?» "
            "Ти можеш відповісти текстом або голосовим повідомленням. "
            "Я збережу твої радісні моменти і нагадаю про них, "
            "коли потрібна підтримка. 🌟"
        )
    else:
        help_moments = "/moments - Просмотреть историю моментов"
        help_talk = "/talk - Начать свободный диалог"
        how_it_works_title = "💡 <b>Как это работает</b>"
        how_it_works = (
            "Каждые несколько часов я спрошу тебя: «Что хорошего произошло?» "
            "Ты можешь ответить текстом или голосовым сообщением. "
            "Я сохраню твои радостные моменты и напомню о них, "
            "когда будет нужна поддержка. 🌟"
        )

    help_text = (
        f"📚 <b>{help_title}</b>\n\n"
        f"{help_start}\n"
        f"{help_help}\n"
        f"{help_moments}\n"
        f"{help_stats}\n"
        f"{help_settings}\n"
        f"{help_talk}\n"
        f"{help_privacy}\n"
        f"{help_export}\n"
        f"{help_delete}\n\n"
        f"{how_it_works_title}\n"
        f"{how_it_works}"
    )
    await message.answer(help_text, reply_markup=get_main_menu_keyboard(language_code))


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    """Handle /settings command - show settings menu"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    if not user:
        await message.answer(
            "Пожалуйста, сначала запусти бота командой /start"
        )
        return

    language_code = user.language_code if user else "ru"

    # Format settings with localization
    formality = t("address_formal_value" if user.formal_address else "address_informal_value", language_code)
    notifications_status = t("notifications_on" if user.notifications_enabled else "notifications_off", language_code)
    
    settings_text = (
        f"{t('settings_title', language_code)}\n\n"
        f"{t('settings.active_hours_value', language_code, start=user.active_hours_start, end=user.active_hours_end)}\n"
        f"{t('settings.interval_value', language_code, interval=user.notification_interval_hours)}\n"
        f"{t('settings.timezone_value', language_code, timezone=user.timezone)}\n"
        f"{t('settings.formality_value', language_code, formality=formality)}\n"
        f"{t('settings.notifications_value', language_code, status=notifications_status)}\n"
    )
    await message.answer(settings_text, reply_markup=get_settings_keyboard(language_code))


@router.message(Command("moments"))
async def cmd_moments(message: Message) -> None:
    """Handle /moments command - show user's moment history"""
    from src.services.moment_service import MomentService
    from src.bot.keyboards.inline import get_moments_keyboard

    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"

    moment_service = MomentService()
    moments = await moment_service.get_user_moments(
        telegram_id=message.from_user.id,
        limit=5
    )

    if not moments:
        await message.answer(
            "📖 У тебя пока нет сохранённых моментов.\n"
            "Когда придёт время вопроса, поделись чем-то хорошим! 🌟"
        )
        return

    moments_text = "📖 <b>Твои хорошие моменты</b>\n\n"
    for moment in moments:
        date_str = moment.created_at.strftime("%d.%m.%Y")
        content_preview = moment.content[:100] + "..." if len(moment.content) > 100 else moment.content
        moments_text += f"🌟 <i>{date_str}</i>\n{content_preview}\n\n"

    await message.answer(moments_text, reply_markup=get_moments_keyboard(language_code=language_code))


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """Handle /stats command - show user statistics"""
    from src.services.stats_service import StatsService

    stats_service = StatsService()
    stats = await stats_service.get_user_stats(message.from_user.id)

    if not stats:
        await message.answer(
            "📊 Статистика пока недоступна.\n"
            "Начни отвечать на вопросы, и здесь появится твой прогресс! ✨"
        )
        return

    stats_text = (
        "📊 <b>Твоя статистика</b>\n\n"
        f"🌟 Всего моментов: {stats.total_moments}\n"
        f"🔥 Текущий стрик: {stats.current_streak} дн.\n"
        f"🏆 Лучший стрик: {stats.longest_streak} дн.\n"
        f"✉️ Отправлено вопросов: {stats.total_questions_sent}\n"
        f"✅ Отвечено: {stats.total_questions_answered}\n"
    )

    if stats.total_questions_sent > 0:
        answer_rate = (stats.total_questions_answered / stats.total_questions_sent) * 100
        stats_text += f"📈 Процент ответов: {answer_rate:.1f}%\n"

    await message.answer(stats_text)


@router.message(Command("talk"))
async def cmd_talk(message: Message) -> None:
    """Handle /talk command - start free dialog mode"""
    from src.bot.keyboards.inline import get_dialog_keyboard
    from src.services.dialog_service import DialogService

    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"

    dialog_intro = (
        "💬 <b>Режим диалога</b>\n\n"
        "Я готов выслушать тебя. Расскажи, что у тебя на душе. "
        "Я постараюсь помочь взглядом со стороны, "
        "но помни — все решения принимаешь ты сам. 💝\n\n"
        "Чтобы выйти из режима диалога, нажми кнопку ниже."
    )
    DialogService.get_instance().start_dialog(message.from_user.id)
    await message.answer(dialog_intro, reply_markup=get_dialog_keyboard(language_code))


@router.message(Command("privacy"))
async def cmd_privacy(message: Message) -> None:
    """Handle /privacy command - show privacy policy"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"

    privacy_title = get_system_message("privacy_title", language_code)
    privacy_text = get_system_message("privacy_text", language_code)

    await message.answer(f"{privacy_title}\n\n{privacy_text}")


@router.message(Command("export_data"))
async def cmd_export_data(message: Message) -> None:
    """Handle /export_data command - export user data (GDPR)"""
    from src.services.gdpr_service import GDPRService

    await message.answer("📦 Готовлю твои данные для экспорта...")

    gdpr_service = GDPRService()
    try:
        file_data = await gdpr_service.export_user_data(message.from_user.id)
        await message.answer_document(
            file_data,
            caption="📦 Вот все твои данные в формате JSON."
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        await message.answer(
            "😔 Не удалось экспортировать данные. Попробуй позже."
        )


@router.message(Command("delete_data"))
async def cmd_delete_data(message: Message) -> None:
    """Handle /delete_data command - request data deletion (GDPR)"""
    from src.bot.keyboards.inline import get_delete_confirmation_keyboard

    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    if not user:
        lang = get_language_code(getattr(message.from_user, "language_code", None) or "ru")
        await message.answer(get_system_message("please_start_first", lang))
        return
    language_code = get_language_code(user.language_code)
    formal = user.formal_address

    # Build localized confirmation message
    title = get_system_message("delete_data_title", language_code)
    confirm = get_system_message("delete_data_confirm_formal" if formal else "delete_data_confirm", language_code, formal=formal)
    warning = get_system_message("delete_data_warning_formal" if formal else "delete_data_warning", language_code, formal=formal)
    moments = get_system_message("delete_data_moments_formal" if formal else "delete_data_moments", language_code, formal=formal)
    conversations = get_system_message("delete_data_conversations", language_code)
    stats = get_system_message("delete_data_stats", language_code)
    settings = get_system_message("delete_data_settings", language_code)
    irreversible = get_system_message("delete_data_irreversible", language_code)
    chat_note = get_system_message("delete_data_chat_note_formal" if formal else "delete_data_chat_note", language_code, formal=formal)

    confirm_text = (
        f"{title}\n\n"
        f"{confirm}\n\n"
        f"{warning}\n"
        f"{moments}\n"
        f"{conversations}\n"
        f"{stats}\n"
        f"{settings}\n\n"
        f"{irreversible}\n\n"
        f"{chat_note}"
    )
    await message.answer(confirm_text, reply_markup=get_delete_confirmation_keyboard(language_code))


@router.message(Command("summary"))
async def cmd_summary(message: Message) -> None:
    """Handle /summary command - get weekly or monthly summary of moments"""
    from src.bot.keyboards.inline import get_summary_keyboard

    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    language_code = user.language_code if user else "ru"

    summary_intro = (
        "📊 <b>Саммари моментов</b>\n\n"
        "Выбери тип саммари, который хочешь получить:\n\n"
        "📅 <b>Еженедельное</b> — обзор хороших моментов за последнюю неделю\n"
        "🗓 <b>Месячное</b> — итоги за последний месяц"
    )
    await message.answer(summary_intro, reply_markup=get_summary_keyboard(language_code))
