"""
MINDSETHAPPYBOT - Callback query handlers
Handles inline button presses and navigation
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.bot.keyboards.inline import (
    get_settings_keyboard,
    get_moments_keyboard,
    get_main_menu_inline,
    get_hours_keyboard,
    get_interval_keyboard,
    get_address_form_keyboard,
)
from src.services.user_service import UserService
from src.services.moment_service import MomentService
from src.services.gdpr_service import GDPRService

logger = logging.getLogger(__name__)
router = Router(name="callbacks")


# Onboarding callbacks
@router.callback_query(F.data == "address_informal")
async def callback_address_informal(callback: CallbackQuery) -> None:
    """Set informal address (ты)"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        formal_address=False
    )

    await callback.message.edit_text(
        "Отлично! Буду обращаться на «ты» 😊\n\n"
        "Теперь немного о том, как это работает:\n\n"
        "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
        "• Ты можешь ответить текстом или голосовым сообщением\n"
        "• Я сохраню твои моменты и напомню о них, когда понадобится поддержка\n\n"
        "🔒 Твои данные в безопасности и используются только для нашего общения.\n"
        "Подробнее: /privacy",
        reply_markup=get_main_menu_inline()
    )

    await user_service.complete_onboarding(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "address_formal")
async def callback_address_formal(callback: CallbackQuery) -> None:
    """Set formal address (вы)"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        formal_address=True
    )

    await callback.message.edit_text(
        "Хорошо! Буду обращаться на «вы» 😊\n\n"
        "Теперь немного о том, как это работает:\n\n"
        "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
        "• Вы можете ответить текстом или голосовым сообщением\n"
        "• Я сохраню Ваши моменты и напомню о них, когда понадобится поддержка\n\n"
        "🔒 Ваши данные в безопасности и используются только для нашего общения.\n"
        "Подробнее: /privacy",
        reply_markup=get_main_menu_inline()
    )

    await user_service.complete_onboarding(callback.from_user.id)
    await callback.answer()


# Settings callbacks
@router.callback_query(F.data == "settings_hours")
async def callback_settings_hours(callback: CallbackQuery) -> None:
    """Show hours settings"""
    await callback.message.edit_text(
        "🕐 <b>Активные часы</b>\n\n"
        "Выбери время начала активного периода:",
        reply_markup=get_hours_keyboard("start")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hour_start_"))
async def callback_hour_start(callback: CallbackQuery) -> None:
    """Set start hour"""
    hour = callback.data.split("_")[2]
    # Store temporarily and show end hour selection
    await callback.message.edit_text(
        f"🕐 Начало: {hour}:00\n\n"
        "Теперь выбери время окончания:",
        reply_markup=get_hours_keyboard("end", start_hour=hour)
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

    await callback.message.edit_text(
        f"✅ Активные часы установлены: {start_hour}:00 - {end_hour}:00",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer("Сохранено!")


@router.callback_query(F.data == "settings_interval")
async def callback_settings_interval(callback: CallbackQuery) -> None:
    """Show interval settings"""
    await callback.message.edit_text(
        "⏰ <b>Интервал между вопросами</b>\n\n"
        "Как часто мне спрашивать о хорошем?",
        reply_markup=get_interval_keyboard()
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

    await callback.message.edit_text(
        f"✅ Интервал установлен: каждые {hours} ч.",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer("Сохранено!")


@router.callback_query(F.data == "settings_address")
async def callback_settings_address(callback: CallbackQuery) -> None:
    """Show address form settings"""
    await callback.message.edit_text(
        "🗣 <b>Форма обращения</b>\n\n"
        "Как тебе удобнее?",
        reply_markup=get_address_form_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings_notifications")
async def callback_settings_notifications(callback: CallbackQuery) -> None:
    """Toggle notifications"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)

    new_state = not user.notifications_enabled
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        notifications_enabled=new_state
    )

    status = "включены" if new_state else "выключены"
    await callback.message.edit_text(
        f"🔔 Уведомления {status}",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer("Сохранено!")


@router.callback_query(F.data == "settings_back")
async def callback_settings_back(callback: CallbackQuery) -> None:
    """Go back to settings menu"""
    from src.bot.handlers.commands import cmd_settings
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)

    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"🕐 Активные часы: {user.active_hours_start} - {user.active_hours_end}\n"
        f"⏰ Интервал: каждые {user.notification_interval_hours} ч.\n"
        f"🗣 Обращение: {'на «вы»' if user.formal_address else 'на «ты»'}\n"
        f"🔔 Уведомления: {'включены' if user.notifications_enabled else 'выключены'}\n"
    )
    await callback.message.edit_text(settings_text, reply_markup=get_settings_keyboard())
    await callback.answer()


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

    moment_service = MomentService()
    moment = await moment_service.get_random_moment(callback.from_user.id)

    if moment:
        date_str = moment.created_at.strftime("%d.%m.%Y")
        await callback.message.answer(
            f"🎲 <b>Случайный хороший момент</b>\n\n"
            f"📅 {date_str}\n\n"
            f"«{moment.content}»",
            reply_markup=get_random_moment_keyboard(moment.id)
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
            reply_markup=get_moments_keyboard()
        )
        await callback.answer()
        return

    preview = target_moment.content[:50] + ("..." if len(target_moment.content) > 50 else "")

    await callback.message.edit_text(
        f"🗑️ <b>Удалить момент?</b>\n\n"
        f"«{preview}»\n\n"
        f"⚠️ Это действие необратимо!",
        reply_markup=get_moment_delete_confirm_keyboard(moment_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("moment_delete_") & ~F.data.startswith("moment_delete_confirm_"))
async def callback_moment_delete(callback: CallbackQuery) -> None:
    """Actually delete a moment"""
    moment_id = int(callback.data.replace("moment_delete_", ""))
    moment_service = MomentService()

    success = await moment_service.delete_moment(
        telegram_id=callback.from_user.id,
        moment_id=moment_id
    )

    if success:
        await callback.message.edit_text(
            "✅ Момент удалён.",
            reply_markup=get_moments_keyboard()
        )
    else:
        await callback.message.edit_text(
            "😔 Не удалось удалить момент.",
            reply_markup=get_moments_keyboard()
        )

    await callback.answer()


# Dialog mode callbacks
@router.callback_query(F.data == "dialog_exit")
async def callback_dialog_exit(callback: CallbackQuery) -> None:
    """Exit dialog mode"""
    from src.bot.keyboards.reply import get_main_menu_keyboard

    await callback.message.answer(
        "Вернулись в обычный режим. Чем могу помочь? 😊",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


# Back to main menu
@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery) -> None:
    """Return to main menu"""
    await callback.message.edit_text(
        "Чем могу помочь? 😊",
        reply_markup=get_main_menu_inline()
    )
    await callback.answer()
