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
    """Get welcome text in user's language"""
    if language_code and language_code.startswith("en"):
        return (
            f"Hello, {first_name}! 👋\n\n"
            "I'm your assistant for developing positive thinking. "
            "Every day I will ask you about good things, "
            "so that we can notice the joyful moments of life together. ✨\n\n"
            "Let's begin! How would you prefer to communicate?"
        )
    elif language_code and language_code.startswith("uk"):
        return (
            f"Привіт, {first_name}! 👋\n\n"
            "Я — твій помічник для розвитку позитивного мислення. "
            "Щодня я буду запитувати тебе про хороше, "
            "щоб разом помічати радісні моменти життя. ✨\n\n"
            "Давай почнемо! Як тобі зручніше спілкуватися?"
        )
    else:  # Default to Russian
        return (
            f"Привет, {first_name}! 👋\n\n"
            "Я — твой помощник для развития позитивного мышления. "
            "Каждый день я буду спрашивать тебя о хорошем, "
            "чтобы вместе замечать радостные моменты жизни. ✨\n\n"
            "Давай начнём! Как тебе удобнее общаться?"
        )


def get_localized_welcome_back_text(first_name: str, language_code: str) -> str:
    """Get welcome back text in user's language"""
    if language_code and language_code.startswith("en"):
        return (
            f"Welcome back, {first_name}! 💝\n\n"
            "Good to see you again. How can I help?"
        )
    elif language_code and language_code.startswith("uk"):
        return (
            f"З поверненням, {first_name}! 💝\n\n"
            "Радий знову тебе бачити. Чим можу допомогти?"
        )
    else:  # Default to Russian
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

    if not user.onboarding_completed:
        # New user - send welcome image first
        await send_welcome_image(message)

        # Get localized welcome text based on user's language
        welcome_text = get_localized_welcome_text(user.first_name, user.language_code)

        await message.answer(
            welcome_text,
            reply_markup=get_onboarding_keyboard()
        )
    else:
        # Existing user - welcome back
        welcome_back_text = get_localized_welcome_back_text(user.first_name, user.language_code)

        await message.answer(
            welcome_back_text,
            reply_markup=get_main_menu_keyboard()
        )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command - show available commands and usage"""
    help_text = (
        "📚 <b>Команды бота</b>\n\n"
        "/start - Начать заново\n"
        "/help - Показать эту справку\n"
        "/moments - Просмотреть историю моментов\n"
        "/stats - Посмотреть статистику\n"
        "/settings - Настройки\n"
        "/talk - Начать свободный диалог\n"
        "/privacy - Политика конфиденциальности\n"
        "/export_data - Экспортировать свои данные\n"
        "/delete_data - Удалить все свои данные\n\n"
        "💡 <b>Как это работает</b>\n"
        "Каждые несколько часов я спрошу тебя: «Что хорошего произошло?» "
        "Ты можешь ответить текстом или голосовым сообщением. "
        "Я сохраню твои радостные моменты и напомню о них, "
        "когда будет нужна поддержка. 🌟"
    )
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())


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

    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"🕐 Активные часы: {user.active_hours_start} - {user.active_hours_end}\n"
        f"⏰ Интервал: каждые {user.notification_interval_hours} ч.\n"
        f"🌍 Часовой пояс: {user.timezone}\n"
        f"🗣 Обращение: {'на «вы»' if user.formal_address else 'на «ты»'}\n"
        f"🔔 Уведомления: {'включены' if user.notifications_enabled else 'выключены'}\n"
    )
    await message.answer(settings_text, reply_markup=get_settings_keyboard())


@router.message(Command("moments"))
async def cmd_moments(message: Message) -> None:
    """Handle /moments command - show user's moment history"""
    from src.services.moment_service import MomentService
    from src.bot.keyboards.inline import get_moments_keyboard

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

    await message.answer(moments_text, reply_markup=get_moments_keyboard())


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

    dialog_intro = (
        "💬 <b>Режим диалога</b>\n\n"
        "Я готов выслушать тебя. Расскажи, что у тебя на душе. "
        "Я постараюсь помочь взглядом со стороны, "
        "но помни — все решения принимаешь ты сам. 💝\n\n"
        "Чтобы выйти из режима диалога, нажми кнопку ниже."
    )
    DialogService.get_instance().start_dialog(message.from_user.id)
    await message.answer(dialog_intro, reply_markup=get_dialog_keyboard())


@router.message(Command("privacy"))
async def cmd_privacy(message: Message) -> None:
    """Handle /privacy command - show privacy policy"""
    privacy_text = (
        "🔒 <b>Политика конфиденциальности</b>\n\n"
        "Я храню твои данные только для того, чтобы делать наше общение "
        "более персональным и полезным для тебя.\n\n"
        "<b>Что я сохраняю:</b>\n"
        "• Твои ответы о хороших моментах\n"
        "• Историю наших диалогов\n"
        "• Настройки (часы, интервал, язык)\n\n"
        "<b>Как использую:</b>\n"
        "• Только для персонализации нашего общения\n"
        "• Чтобы напоминать тебе о прошлых радостях\n"
        "• Данные НЕ передаются третьим лицам\n\n"
        "<b>Твои права:</b>\n"
        "• /export_data — скачать все свои данные\n"
        "• /delete_data — полностью удалить всё\n\n"
        "Вопросы? Напиши мне в свободном диалоге! 💝"
    )
    await message.answer(privacy_text)


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

    confirm_text = (
        "⚠️ <b>Удаление данных</b>\n\n"
        "Ты уверен, что хочешь удалить ВСЕ свои данные?\n\n"
        "Это действие:\n"
        "• Удалит все твои моменты\n"
        "• Удалит историю диалогов\n"
        "• Удалит статистику\n"
        "• Сбросит настройки\n\n"
        "⚠️ <b>Это действие необратимо!</b>"
    )
    await message.answer(confirm_text, reply_markup=get_delete_confirmation_keyboard())


@router.message(Command("summary"))
async def cmd_summary(message: Message) -> None:
    """Handle /summary command - get weekly or monthly summary of moments"""
    from src.bot.keyboards.inline import get_summary_keyboard

    summary_intro = (
        "📊 <b>Саммари моментов</b>\n\n"
        "Выбери тип саммари, который хочешь получить:\n\n"
        "📅 <b>Еженедельное</b> — обзор хороших моментов за последнюю неделю\n"
        "🗓 <b>Месячное</b> — итоги за последний месяц"
    )
    await message.answer(summary_intro, reply_markup=get_summary_keyboard())
