"""
MINDSETHAPPYBOT - Callback query handlers
Handles inline button presses and navigation
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from aiogram.fsm.context import FSMContext

from src.bot.keyboards.inline import (
    get_settings_keyboard,
    get_moments_keyboard,
    get_main_menu_inline,
    get_hours_keyboard,
    get_interval_keyboard,
    get_address_form_keyboard,
    get_timezone_keyboard,
    get_social_profile_keyboard,
    get_social_remove_keyboard,
)
from src.bot.states.social_profile import SocialProfileStates
from src.services.user_service import UserService
from src.services.moment_service import MomentService
from src.services.gdpr_service import GDPRService
from src.services.social_profile_service import SocialProfileService
from src.utils.localization import get_onboarding_text

logger = logging.getLogger(__name__)
router = Router(name="callbacks")


async def get_user_language(telegram_id: int) -> str:
    """Helper to get user's language code"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(telegram_id)
    return user.language_code if user else "ru"


# Onboarding callbacks
@router.callback_query(F.data == "address_informal")
async def callback_address_informal(callback: CallbackQuery) -> None:
    """Set informal address (ты)"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        formal_address=False
    )

    # Get user's language for localized response
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    confirm_text = get_onboarding_text("address_informal_confirm", language_code)

    await callback.message.edit_text(
        confirm_text,
        reply_markup=get_main_menu_inline(language_code)
    )

    await user_service.complete_onboarding(callback.from_user.id)

    # Send first question immediately after onboarding
    from src.services.scheduler import NotificationScheduler
    scheduler = NotificationScheduler.get_instance()
    logger.info(f"Attempting to send first question after onboarding for user {callback.from_user.id}, scheduler instance: {scheduler is not None}")
    if scheduler:
        try:
            result = await scheduler.send_first_question_after_onboarding(callback.from_user.id)
            logger.info(f"First question sent result for user {callback.from_user.id}: {result}")
        except Exception as e:
            logger.error(f"Failed to send first question after onboarding for user {callback.from_user.id}: {e}")
    else:
        # Fallback: create temporary scheduler with bot from callback
        logger.warning(f"No scheduler instance available for user {callback.from_user.id}, using fallback")
        try:
            temp_scheduler = NotificationScheduler(callback.bot)
            result = await temp_scheduler.send_first_question_after_onboarding(callback.from_user.id)
            logger.info(f"First question sent via fallback for user {callback.from_user.id}: {result}")
        except Exception as e:
            logger.error(f"Fallback failed to send first question for user {callback.from_user.id}: {e}")
    await callback.answer()


@router.callback_query(F.data == "address_formal")
async def callback_address_formal(callback: CallbackQuery) -> None:
    """Set formal address (вы)"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        formal_address=True
    )

    # Get user's language for localized response
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    confirm_text = get_onboarding_text("address_formal_confirm", language_code)

    await callback.message.edit_text(
        confirm_text,
        reply_markup=get_main_menu_inline(language_code)
    )

    await user_service.complete_onboarding(callback.from_user.id)

    # Send first question immediately after onboarding
    from src.services.scheduler import NotificationScheduler
    scheduler = NotificationScheduler.get_instance()
    logger.info(f"Attempting to send first question after onboarding for user {callback.from_user.id}, scheduler instance: {scheduler is not None}")
    if scheduler:
        try:
            result = await scheduler.send_first_question_after_onboarding(callback.from_user.id)
            logger.info(f"First question sent result for user {callback.from_user.id}: {result}")
        except Exception as e:
            logger.error(f"Failed to send first question after onboarding for user {callback.from_user.id}: {e}")
    else:
        # Fallback: create temporary scheduler with bot from callback
        logger.warning(f"No scheduler instance available for user {callback.from_user.id}, using fallback")
        try:
            temp_scheduler = NotificationScheduler(callback.bot)
            result = await temp_scheduler.send_first_question_after_onboarding(callback.from_user.id)
            logger.info(f"First question sent via fallback for user {callback.from_user.id}: {result}")
        except Exception as e:
            logger.error(f"Fallback failed to send first question for user {callback.from_user.id}: {e}")
    await callback.answer()


# Settings callbacks
@router.callback_query(F.data == "settings_hours")
async def callback_settings_hours(callback: CallbackQuery) -> None:
    """Show hours settings"""
    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "🕐 <b>Активные часы</b>\n\n"
        "Выбери время начала активного периода:",
        reply_markup=get_hours_keyboard("start", language_code=language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hour_start_"))
async def callback_hour_start(callback: CallbackQuery) -> None:
    """Set start hour"""
    hour = callback.data.split("_")[2]
    language_code = await get_user_language(callback.from_user.id)
    # Store temporarily and show end hour selection
    await callback.message.edit_text(
        f"🕐 Начало: {hour}:00\n\n"
        "Теперь выбери время окончания:",
        reply_markup=get_hours_keyboard("end", start_hour=hour, language_code=language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hour_end_"))
async def callback_hour_end(callback: CallbackQuery) -> None:
    """Set end hour and save"""
    parts = callback.data.split("_")
    end_hour = parts[2]
    start_hour = parts[3] if len(parts) > 3 else "09"

    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        active_hours_start=f"{start_hour}:00",
        active_hours_end=f"{end_hour}:00"
    )

    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        f"✅ Активные часы установлены: {start_hour}:00 - {end_hour}:00",
        reply_markup=get_settings_keyboard(language_code)
    )
    await callback.answer("Сохранено!")


@router.callback_query(F.data == "settings_interval")
async def callback_settings_interval(callback: CallbackQuery) -> None:
    """Show interval settings"""
    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "⏰ <b>Интервал между вопросами</b>\n\n"
        "Как часто мне спрашивать о хорошем?",
        reply_markup=get_interval_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("interval_"))
async def callback_set_interval(callback: CallbackQuery) -> None:
    """Set notification interval"""
    hours = int(callback.data.split("_")[1])

    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        notification_interval_hours=hours
    )

    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        f"✅ Интервал установлен: каждые {hours} ч.",
        reply_markup=get_settings_keyboard(language_code)
    )
    await callback.answer("Сохранено!")


@router.callback_query(F.data == "settings_address")
async def callback_settings_address(callback: CallbackQuery) -> None:
    """Show address form settings"""
    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "🗣 <b>Форма обращения</b>\n\n"
        "Как тебе удобнее?",
        reply_markup=get_address_form_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data == "settings_notifications")
async def callback_settings_notifications(callback: CallbackQuery) -> None:
    """Toggle notifications"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    new_state = not user.notifications_enabled
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        notifications_enabled=new_state
    )

    status = "включены" if new_state else "выключены"
    await callback.message.edit_text(
        f"🔔 Уведомления {status}",
        reply_markup=get_settings_keyboard(language_code)
    )
    await callback.answer("Сохранено!")


@router.callback_query(F.data == "settings_timezone")
async def callback_settings_timezone(callback: CallbackQuery) -> None:
    """Show timezone settings"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    current_tz = user.timezone if user else "UTC"
    await callback.message.edit_text(
        f"🌍 <b>Часовой пояс</b>\n\n"
        f"Текущий: <code>{current_tz}</code>\n\n"
        "Выбери свой часовой пояс:",
        reply_markup=get_timezone_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("timezone_"))
async def callback_set_timezone(callback: CallbackQuery) -> None:
    """Set user timezone"""
    timezone = callback.data.replace("timezone_", "")
    language_code = await get_user_language(callback.from_user.id)

    user_service = UserService()
    try:
        await user_service.update_user_settings(
            telegram_id=callback.from_user.id,
            timezone=timezone
        )

        await callback.message.edit_text(
            f"✅ Часовой пояс установлен: {timezone}",
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer("Сохранено!")
    except ValueError as e:
        await callback.message.edit_text(
            f"❌ Ошибка: неверный часовой пояс",
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer("Ошибка!")


# Social profile callbacks
@router.callback_query(F.data == "settings_social")
async def callback_settings_social(callback: CallbackQuery) -> None:
    """Show social profile settings"""
    language_code = await get_user_language(callback.from_user.id)
    social_service = SocialProfileService()
    summary = await social_service.get_profile_summary(callback.from_user.id)

    await callback.message.edit_text(
        f"👤 <b>Социальный профиль</b>\n\n{summary}",
        reply_markup=get_social_profile_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data == "social_add")
async def callback_social_add(callback: CallbackQuery, state: FSMContext) -> None:
    """Prompt to add a social network link"""
    await state.set_state(SocialProfileStates.waiting_for_social_link)
    await callback.message.edit_text(
        "🔗 <b>Добавить соцсеть</b>\n\n"
        "Отправь ссылку на свою страницу в соцсети.\n\n"
        "Поддерживаются:\n"
        "• Instagram\n"
        "• Facebook\n"
        "• Twitter/X\n"
        "• LinkedIn\n"
        "• ВКонтакте\n"
        "• Telegram канал\n"
        "• YouTube\n"
        "• TikTok\n\n"
        "Отправь /cancel чтобы отменить."
    )
    await callback.answer()


@router.callback_query(F.data == "social_bio")
async def callback_social_bio(callback: CallbackQuery, state: FSMContext) -> None:
    """Prompt to edit bio"""
    await state.set_state(SocialProfileStates.waiting_for_bio)
    await callback.message.edit_text(
        "📝 <b>Редактирование биографии</b>\n\n"
        "Напиши немного о себе, своих увлечениях и интересах.\n"
        "Это поможет мне лучше понять тебя и сделать наше общение более персональным.\n\n"
        "Отправь /cancel чтобы отменить."
    )
    await callback.answer()


@router.callback_query(F.data == "social_parse")
async def callback_social_parse(callback: CallbackQuery) -> None:
    """Parse interests from profile"""
    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text("🔍 Анализирую профиль...")

    social_service = SocialProfileService()
    success, interests = await social_service.parse_interests(callback.from_user.id)

    if success and interests:
        interests_text = ", ".join(interests)
        await callback.message.edit_text(
            f"✅ <b>Интересы определены!</b>\n\n"
            f"Твои интересы: {interests_text}\n\n"
            f"Эта информация будет использоваться для персонализации нашего общения.",
            reply_markup=get_social_profile_keyboard(language_code)
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось определить интересы.\n\n"
            "Добавь больше информации в свой профиль: ссылки на соцсети или биографию.",
            reply_markup=get_social_profile_keyboard(language_code)
        )
    await callback.answer()


@router.callback_query(F.data == "social_remove")
async def callback_social_remove(callback: CallbackQuery) -> None:
    """Show list of social links to remove"""
    language_code = await get_user_language(callback.from_user.id)
    social_service = SocialProfileService()
    profile = await social_service.get_profile(callback.from_user.id)

    if not profile:
        await callback.message.edit_text(
            "У тебя нет добавленных соцсетей.",
            reply_markup=get_social_profile_keyboard(language_code)
        )
    else:
        urls = profile.get_all_urls()
        await callback.message.edit_text(
            "🗑 <b>Удаление ссылки</b>\n\n"
            "Выбери соцсеть для удаления:",
            reply_markup=get_social_remove_keyboard(urls, language_code)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("social_del_"))
async def callback_social_delete(callback: CallbackQuery) -> None:
    """Delete a social network link"""
    language_code = await get_user_language(callback.from_user.id)
    network = callback.data.replace("social_del_", "")

    social_service = SocialProfileService()
    success, message = await social_service.remove_social_link(callback.from_user.id, network)

    if success:
        await callback.message.edit_text(
            f"✅ {message}",
            reply_markup=get_social_profile_keyboard(language_code)
        )
    else:
        await callback.message.edit_text(
            f"❌ {message}",
            reply_markup=get_social_profile_keyboard(language_code)
        )
    await callback.answer()


@router.callback_query(F.data == "social_back")
async def callback_social_back(callback: CallbackQuery) -> None:
    """Go back to social profile menu"""
    language_code = await get_user_language(callback.from_user.id)
    social_service = SocialProfileService()
    summary = await social_service.get_profile_summary(callback.from_user.id)

    await callback.message.edit_text(
        f"👤 <b>Социальный профиль</b>\n\n{summary}",
        reply_markup=get_social_profile_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data == "settings_back")
async def callback_settings_back(callback: CallbackQuery) -> None:
    """Go back to settings menu"""
    from src.bot.handlers.commands import cmd_settings
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"🕐 Активные часы: {user.active_hours_start} - {user.active_hours_end}\n"
        f"⏰ Интервал: каждые {user.notification_interval_hours} ч.\n"
        f"🌍 Часовой пояс: {user.timezone}\n"
        f"🗣 Обращение: {'на «вы»' if user.formal_address else 'на «ты»'}\n"
        f"🔔 Уведомления: {'включены' if user.notifications_enabled else 'выключены'}\n"
    )
    await callback.message.edit_text(settings_text, reply_markup=get_settings_keyboard(language_code))
    await callback.answer()


@router.callback_query(F.data == "settings_reset")
async def callback_settings_reset(callback: CallbackQuery) -> None:
    """Reset all settings to default values"""
    user_service = UserService()
    success = await user_service.reset_settings_to_defaults(callback.from_user.id)

    if success:
        # Fetch updated user to show new settings
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        language_code = user.language_code if user else "ru"
        settings_text = (
            "✅ <b>Настройки сброшены!</b>\n\n"
            f"🕐 Активные часы: {user.active_hours_start} - {user.active_hours_end}\n"
            f"⏰ Интервал: каждые {user.notification_interval_hours} ч.\n"
            f"🌍 Часовой пояс: {user.timezone}\n"
            f"🗣 Обращение: {'на «вы»' if user.formal_address else 'на «ты»'}\n"
            f"🔔 Уведомления: {'включены' if user.notifications_enabled else 'выключены'}\n"
        )
        await callback.message.edit_text(settings_text, reply_markup=get_settings_keyboard(language_code))
        await callback.answer("Настройки сброшены!")
    else:
        language_code = await get_user_language(callback.from_user.id)
        await callback.message.edit_text(
            "😔 Не удалось сбросить настройки. Попробуй позже.",
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer("Ошибка")


# Moments callbacks
@router.callback_query(F.data == "moments_next")
async def callback_moments_next(callback: CallbackQuery) -> None:
    """Show next page of moments"""
    # Pagination logic would go here
    await callback.answer("Следующая страница")


@router.callback_query(F.data == "moments_prev")
async def callback_moments_prev(callback: CallbackQuery) -> None:
    """Show previous page of moments"""
    await callback.answer("Предыдущая страница")


@router.callback_query(F.data == "moments_random")
async def callback_moments_random(callback: CallbackQuery) -> None:
    """Show random moment with delete option"""
    from src.bot.keyboards.inline import get_random_moment_keyboard

    language_code = await get_user_language(callback.from_user.id)
    moment_service = MomentService()
    moment = await moment_service.get_random_moment(callback.from_user.id)

    if moment:
        date_str = moment.created_at.strftime("%d.%m.%Y")
        await callback.message.answer(
            f"🎲 <b>Случайный хороший момент</b>\n\n"
            f"📅 {date_str}\n\n"
            f"«{moment.content}»",
            reply_markup=get_random_moment_keyboard(moment.id, language_code)
        )
    else:
        await callback.message.answer("У тебя пока нет сохранённых моментов.")

    await callback.answer()


# Delete confirmation callbacks
@router.callback_query(F.data == "delete_confirm")
async def callback_delete_confirm(callback: CallbackQuery) -> None:
    """Confirm and execute data deletion"""
    gdpr_service = GDPRService()

    try:
        await gdpr_service.delete_all_user_data(callback.from_user.id)
        await callback.message.edit_text(
            "✅ Все твои данные удалены.\n\n"
            "Если захочешь вернуться — просто напиши /start 💝"
        )
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        await callback.message.edit_text(
            "😔 Произошла ошибка при удалении. Попробуй позже."
        )

    await callback.answer()


@router.callback_query(F.data == "delete_cancel")
async def callback_delete_cancel(callback: CallbackQuery) -> None:
    """Cancel data deletion"""
    await callback.message.edit_text(
        "👍 Удаление отменено. Твои данные в безопасности!"
    )
    await callback.answer()


# Individual moment delete callbacks
@router.callback_query(F.data.startswith("moment_delete_confirm_"))
async def callback_moment_delete_confirm(callback: CallbackQuery) -> None:
    """Show confirmation dialog for deleting a moment"""
    from src.bot.keyboards.inline import get_moment_delete_confirm_keyboard

    language_code = await get_user_language(callback.from_user.id)
    moment_id = int(callback.data.replace("moment_delete_confirm_", ""))
    moment_service = MomentService()

    # Get the moment to show preview
    moments = await moment_service.get_user_moments(
        telegram_id=callback.from_user.id,
        limit=100  # Get all to find the specific one
    )

    target_moment = None
    for m in moments:
        if m.id == moment_id:
            target_moment = m
            break

    if not target_moment:
        await callback.message.edit_text(
            "😔 Момент не найден.",
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
        await callback.answer()
        return

    preview = target_moment.content[:50] + ("..." if len(target_moment.content) > 50 else "")

    await callback.message.edit_text(
        f"🗑️ <b>Удалить момент?</b>\n\n"
        f"«{preview}»\n\n"
        f"⚠️ Это действие необратимо!",
        reply_markup=get_moment_delete_confirm_keyboard(moment_id, language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("moment_delete_") & ~F.data.startswith("moment_delete_confirm_"))
async def callback_moment_delete(callback: CallbackQuery) -> None:
    """Actually delete a moment"""
    language_code = await get_user_language(callback.from_user.id)
    moment_id = int(callback.data.replace("moment_delete_", ""))
    moment_service = MomentService()

    success = await moment_service.delete_moment(
        telegram_id=callback.from_user.id,
        moment_id=moment_id
    )

    if success:
        await callback.message.edit_text(
            "✅ Момент удалён.",
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
    else:
        await callback.message.edit_text(
            "😔 Не удалось удалить момент.",
            reply_markup=get_moments_keyboard(language_code=language_code)
        )

    await callback.answer()


# Dialog mode callbacks
@router.callback_query(F.data == "dialog_exit")
async def callback_dialog_exit(callback: CallbackQuery) -> None:
    """Exit dialog mode"""
    from src.bot.keyboards.reply import get_main_menu_keyboard
    from src.services.dialog_service import DialogService

    language_code = await get_user_language(callback.from_user.id)
    DialogService.get_instance().end_dialog(callback.from_user.id)
    await callback.message.answer(
        "Вернулись в обычный режим. Чем могу помочь? 😊",
        reply_markup=get_main_menu_keyboard(language_code)
    )
    await callback.answer()


# Back to main menu
@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery) -> None:
    """Return to main menu"""
    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "Чем могу помочь? 😊",
        reply_markup=get_main_menu_inline(language_code)
    )
    await callback.answer()


# Menu callbacks - route to appropriate handlers
@router.callback_query(F.data == "menu_moments")
async def callback_menu_moments(callback: CallbackQuery) -> None:
    """Show moments list"""
    from src.bot.keyboards.inline import get_moments_keyboard

    language_code = await get_user_language(callback.from_user.id)
    moment_service = MomentService()
    moments = await moment_service.get_user_moments(
        telegram_id=callback.from_user.id,
        limit=5
    )

    if not moments:
        await callback.message.edit_text(
            "📖 У тебя пока нет сохранённых моментов.\n"
            "Когда придёт время вопроса, поделись чем-то хорошим! 🌟",
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        moments_text = "📖 <b>Твои хорошие моменты</b>\n\n"
        for moment in moments:
            date_str = moment.created_at.strftime("%d.%m.%Y")
            content_preview = moment.content[:100] + "..." if len(moment.content) > 100 else moment.content
            moments_text += f"🌟 <i>{date_str}</i>\n{content_preview}\n\n"
        await callback.message.edit_text(moments_text, reply_markup=get_moments_keyboard(language_code=language_code))

    await callback.answer()


@router.callback_query(F.data == "menu_stats")
async def callback_menu_stats(callback: CallbackQuery) -> None:
    """Show statistics"""
    from src.services.stats_service import StatsService

    language_code = await get_user_language(callback.from_user.id)
    stats_service = StatsService()
    stats = await stats_service.get_user_stats(callback.from_user.id)

    if not stats:
        await callback.message.edit_text(
            "📊 Статистика пока недоступна.\n"
            "Начни отвечать на вопросы, и здесь появится твой прогресс! ✨",
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
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
        await callback.message.edit_text(stats_text, reply_markup=get_main_menu_inline(language_code))

    await callback.answer()


@router.callback_query(F.data == "menu_settings")
async def callback_menu_settings(callback: CallbackQuery) -> None:
    """Show settings menu"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    if not user:
        await callback.message.edit_text(
            "Пожалуйста, сначала запусти бота командой /start",
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        settings_text = (
            "⚙️ <b>Настройки</b>\n\n"
            f"🕐 Активные часы: {user.active_hours_start} - {user.active_hours_end}\n"
            f"⏰ Интервал: каждые {user.notification_interval_hours} ч.\n"
            f"🌍 Часовой пояс: {user.timezone}\n"
            f"🗣 Обращение: {'на «вы»' if user.formal_address else 'на «ты»'}\n"
            f"🔔 Уведомления: {'включены' if user.notifications_enabled else 'выключены'}\n"
        )
        await callback.message.edit_text(settings_text, reply_markup=get_settings_keyboard(language_code))

    await callback.answer()


@router.callback_query(F.data == "menu_talk")
async def callback_menu_talk(callback: CallbackQuery) -> None:
    """Start free dialog mode"""
    from src.bot.keyboards.inline import get_dialog_keyboard
    from src.services.dialog_service import DialogService

    language_code = await get_user_language(callback.from_user.id)
    DialogService.get_instance().start_dialog(callback.from_user.id)
    dialog_intro = (
        "💬 <b>Режим диалога</b>\n\n"
        "Я готов выслушать тебя. Расскажи, что у тебя на душе. "
        "Я постараюсь помочь взглядом со стороны, "
        "но помни — все решения принимаешь ты сам. 💝\n\n"
        "Чтобы выйти из режима диалога, нажми кнопку ниже."
    )
    await callback.message.edit_text(dialog_intro, reply_markup=get_dialog_keyboard(language_code))
    await callback.answer()


# Filter callbacks for moments
@router.callback_query(F.data.startswith("filter_"))
async def callback_filter_moments(callback: CallbackQuery) -> None:
    """Filter moments by period"""
    language_code = await get_user_language(callback.from_user.id)
    period = callback.data.replace("filter_", "")
    moment_service = MomentService()
    moments = await moment_service.get_user_moments(
        telegram_id=callback.from_user.id,
        limit=5,
        period=period
    )

    period_names = {"today": "сегодня", "week": "за неделю", "month": "за месяц"}
    period_name = period_names.get(period, period)

    if not moments:
        await callback.message.edit_text(
            f"📖 Нет моментов {period_name}.",
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
    else:
        moments_text = f"📖 <b>Моменты {period_name}</b>\n\n"
        for moment in moments:
            date_str = moment.created_at.strftime("%d.%m.%Y")
            content_preview = moment.content[:100] + "..." if len(moment.content) > 100 else moment.content
            moments_text += f"🌟 <i>{date_str}</i>\n{content_preview}\n\n"
        await callback.message.edit_text(moments_text, reply_markup=get_moments_keyboard(language_code=language_code))

    await callback.answer()


# Skip question callback
@router.callback_query(F.data == "question_skip")
async def callback_question_skip(callback: CallbackQuery) -> None:
    """Skip the current scheduled question"""
    await callback.message.edit_text(
        "👍 Хорошо, пропустим этот вопрос. До скорой встречи! 😊"
    )
    await callback.answer()


# Noop callback for display-only buttons
@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery) -> None:
    """Do nothing - for display-only buttons like page numbers"""
    await callback.answer()


# Summary callbacks
@router.callback_query(F.data == "summary_weekly")
async def callback_summary_weekly(callback: CallbackQuery) -> None:
    """Generate and show weekly summary"""
    from src.services.summary_service import SummaryService

    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "⏳ Готовлю еженедельное саммари..."
    )

    summary_service = SummaryService()
    summary = await summary_service.generate_weekly_summary(callback.from_user.id)

    if summary:
        await callback.message.edit_text(
            summary,
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        await callback.message.edit_text(
            "📅 Недостаточно моментов для еженедельного саммари.\n\n"
            "Когда у тебя будет больше записей, я смогу создать красивый обзор! 🌟",
            reply_markup=get_main_menu_inline(language_code)
        )

    await callback.answer()


@router.callback_query(F.data == "summary_monthly")
async def callback_summary_monthly(callback: CallbackQuery) -> None:
    """Generate and show monthly summary"""
    from src.services.summary_service import SummaryService

    language_code = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "⏳ Готовлю месячное саммари..."
    )

    summary_service = SummaryService()
    summary = await summary_service.generate_monthly_summary(callback.from_user.id)

    if summary:
        await callback.message.edit_text(
            summary,
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        await callback.message.edit_text(
            "🗓 Недостаточно моментов для месячного саммари.\n\n"
            "Когда у тебя будет больше записей, я смогу создать красивый обзор! 🌟",
            reply_markup=get_main_menu_inline(language_code)
        )

    await callback.answer()
