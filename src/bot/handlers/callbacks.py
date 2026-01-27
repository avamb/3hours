"""
MINDSETHAPPYBOT - Callback query handlers
Handles inline button presses and navigation
"""
import logging
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ChatAction

from aiogram.fsm.context import FSMContext

from src.bot.keyboards.inline import (
    get_settings_keyboard,
    get_moments_keyboard,
    get_main_menu_inline,
    get_hours_keyboard,
    get_interval_keyboard,
    get_address_form_keyboard,
    get_gender_keyboard,
    get_timezone_keyboard,
    get_timezone_regions_keyboard,
    get_language_keyboard,
    get_social_profile_keyboard,
    get_social_remove_keyboard,
    get_pause_period_keyboard,
)
from src.bot.states.social_profile import SocialProfileStates
from src.services.user_service import UserService
from src.services.moment_service import MomentService
from src.services.gdpr_service import GDPRService
from src.services.social_profile_service import SocialProfileService
from src.utils.localization import get_onboarding_text, get_system_message, get_menu_text, get_language_code

logger = logging.getLogger(__name__)
router = Router(name="callbacks")


async def get_user_language(telegram_id: int) -> str:
    """Helper to get user's normalized language code (for localization)."""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(telegram_id)
    return get_language_code(user.language_code) if user else "ru"


async def _complete_onboarding_flow(callback: CallbackQuery, language_code: str) -> None:
    """Complete onboarding and send first question"""
    user_service = UserService()
    await user_service.complete_onboarding(callback.from_user.id)
    
    # Show final message with instructions and examples
    confirm_text = get_onboarding_text("onboarding_complete", language_code)
    await callback.message.edit_text(
        confirm_text,
        reply_markup=get_main_menu_inline(language_code)
    )
    
    # Send first question (typing animation is handled in scheduler)
    from src.services.scheduler import NotificationScheduler
    
    scheduler = NotificationScheduler.get_instance()
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


async def _show_onboarding_timezone(callback: CallbackQuery, language_code: str) -> None:
    """Show timezone selection during onboarding with explanation"""
    explanation = get_onboarding_text("onboarding_timezone_important", language_code)
    
    await callback.message.edit_text(
        explanation,
        reply_markup=get_timezone_regions_keyboard(language_code)
    )
    await callback.answer()


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
    
    # Check if onboarding is in progress
    if user and not user.onboarding_completed:
        # Show gender selection during onboarding
        # Use appropriate text based on formality
        if user.formal_address:
            prompt = get_onboarding_text("onboarding_select_gender_formal", language_code)
        else:
            prompt = get_onboarding_text("onboarding_select_gender", language_code)
        await callback.message.edit_text(
            prompt,
            reply_markup=get_gender_keyboard(language_code, include_neutral=True)
        )
    else:
        # Existing user changing settings
        confirm_text = get_onboarding_text("address_informal_confirm", language_code)
        await callback.message.edit_text(
            confirm_text,
            reply_markup=get_main_menu_inline(language_code)
        )
    
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
    
    # Check if onboarding is in progress
    if user and not user.onboarding_completed:
        # Show gender selection during onboarding
        # Use appropriate text based on formality
        if user.formal_address:
            prompt = get_onboarding_text("onboarding_select_gender_formal", language_code)
        else:
            prompt = get_onboarding_text("onboarding_select_gender", language_code)
        await callback.message.edit_text(
            prompt,
            reply_markup=get_gender_keyboard(language_code, include_neutral=True)
        )
    else:
        # Existing user changing settings
        confirm_text = get_onboarding_text("address_formal_confirm", language_code)
        await callback.message.edit_text(
            confirm_text,
            reply_markup=get_main_menu_inline(language_code)
        )
    
    await callback.answer()


# Settings callbacks
@router.callback_query(F.data == "settings_hours")
async def callback_settings_hours(callback: CallbackQuery) -> None:
    """Show hours settings"""
    language_code = await get_user_language(callback.from_user.id)
    title = get_system_message("active_hours_title", language_code)
    prompt = get_system_message("select_active_hours_start", language_code)
    await callback.message.edit_text(
        f"{title}\n\n{prompt}",
        reply_markup=get_hours_keyboard("start", language_code=language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hour_start_"))
async def callback_hour_start(callback: CallbackQuery) -> None:
    """Set start hour"""
    hour = callback.data.split("_")[2]
    language_code = await get_user_language(callback.from_user.id)
    start_text = get_system_message("start_hour_set", language_code, hour=hour)
    end_prompt = get_system_message("select_active_hours_end", language_code)
    # Store temporarily and show end hour selection
    await callback.message.edit_text(
        f"{start_text}\n\n{end_prompt}",
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
    confirm_text = get_system_message("active_hours_set", language_code, start=f"{start_hour}:00", end=f"{end_hour}:00")
    await callback.message.edit_text(
        f"✅ {confirm_text}",
        reply_markup=get_settings_keyboard(language_code)
    )
    await callback.answer(get_system_message("saved", language_code))


@router.callback_query(F.data == "settings_interval")
async def callback_settings_interval(callback: CallbackQuery) -> None:
    """Show interval settings"""
    language_code = await get_user_language(callback.from_user.id)
    title = get_system_message("interval_title", language_code)
    prompt = get_system_message("how_often_ask", language_code)
    await callback.message.edit_text(
        f"{title}\n\n{prompt}",
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
    confirm_text = get_system_message("interval_set_confirm", language_code, hours=hours)
    await callback.message.edit_text(
        confirm_text,
        reply_markup=get_settings_keyboard(language_code)
    )
    await callback.answer(get_system_message("saved", language_code))


@router.callback_query(F.data == "settings_address")
async def callback_settings_address(callback: CallbackQuery) -> None:
    """Show address form settings"""
    language_code = await get_user_language(callback.from_user.id)
    title = get_system_message("address_form_title", language_code)
    prompt = get_system_message("how_would_you_like", language_code)
    await callback.message.edit_text(
        f"{title}\n\n{prompt}",
        reply_markup=get_address_form_keyboard(language_code)
    )
    await callback.answer()




@router.callback_query(F.data == "gender_neutral")
async def callback_gender_neutral(callback: CallbackQuery) -> None:
    """Set gender to neutral/unknown"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        gender="unknown"
    )

    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    
    # Check if onboarding is in progress
    if user and not user.onboarding_completed:
        # Show timezone selection during onboarding
        await _show_onboarding_timezone(callback, language_code)
    else:
        # Existing user changing settings
        confirm_text = get_system_message("gender_set_neutral", language_code)
        await callback.message.edit_text(
            f"✅ {confirm_text}",
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer(get_system_message("saved", language_code))


@router.callback_query(F.data == "settings_gender")
async def callback_settings_gender(callback: CallbackQuery) -> None:
    """Show gender settings"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    current_gender = user.gender if user and user.gender else "unknown"
    gender_values = {
        "male": get_system_message("gender_male_value", language_code),
        "female": get_system_message("gender_female_value", language_code)
    }
    gender_text = gender_values.get(current_gender, get_system_message("gender_unknown", language_code))

    title = get_system_message("gender_title", language_code)
    current_label = get_system_message("current_value", language_code, value=gender_text)
    prompt = get_system_message("select_gender_prompt", language_code)

    await callback.message.edit_text(
        f"{title}\n\n{current_label}\n\n{prompt}",
        reply_markup=get_gender_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data == "gender_male")
async def callback_gender_male(callback: CallbackQuery) -> None:
    """Set gender to male"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        gender="male"
    )

    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    
    # Check if onboarding is in progress
    if user and not user.onboarding_completed:
        # Show timezone selection during onboarding
        await _show_onboarding_timezone(callback, language_code)
    else:
        # Existing user changing settings
        confirm_text = get_system_message("gender_set_male", language_code)
        await callback.message.edit_text(
            f"✅ {confirm_text}",
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer(get_system_message("saved", language_code))


@router.callback_query(F.data == "gender_female")
async def callback_gender_female(callback: CallbackQuery) -> None:
    """Set gender to female"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        gender="female"
    )

    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    
    # Check if onboarding is in progress
    if user and not user.onboarding_completed:
        # Show timezone selection during onboarding
        await _show_onboarding_timezone(callback, language_code)
    else:
        # Existing user changing settings
        confirm_text = get_system_message("gender_set_female", language_code)
        await callback.message.edit_text(
            f"✅ {confirm_text}",
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer(get_system_message("saved", language_code))


@router.callback_query(F.data == "settings_language")
async def callback_settings_language(callback: CallbackQuery) -> None:
    """Show language settings"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    # Language names in their native form
    lang_names = {
        "en": "English",
        "ru": "Русский",
        "uk": "Українська",
        "es": "Español",
        "de": "Deutsch",
        "fr": "Français",
        "pt": "Português",
        "it": "Italiano",
        "zh": "中文",
        "ja": "日本語",
        "he": "עברית",
    }
    current_lang_name = lang_names.get(language_code, language_code)

    await callback.message.edit_text(
        f"🌐 <b>Interface Language</b>\n\n"
        f"Current: {current_lang_name}\n\n"
        "Select your preferred language:",
        reply_markup=get_language_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("language_"))
async def callback_set_language(callback: CallbackQuery) -> None:
    """Set user interface language"""
    new_language = callback.data.replace("language_", "")

    # Language names for confirmation message
    lang_names = {
        "en": "English",
        "ru": "Русский",
        "uk": "Українська",
        "es": "Español",
        "de": "Deutsch",
        "fr": "Français",
        "pt": "Português",
        "it": "Italiano",
        "zh": "中文",
        "ja": "日本語",
        "he": "עברית",
    }

    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        language_code=new_language
    )

    lang_name = lang_names.get(new_language, new_language)

    # Confirmation messages in different languages
    confirmations = {
        "en": f"✅ Language set to {lang_name}",
        "ru": f"✅ Язык изменён: {lang_name}",
        "uk": f"✅ Мову змінено: {lang_name}",
        "es": f"✅ Idioma cambiado: {lang_name}",
        "de": f"✅ Sprache geändert: {lang_name}",
        "fr": f"✅ Langue changée: {lang_name}",
        "pt": f"✅ Idioma alterado: {lang_name}",
        "it": f"✅ Lingua cambiata: {lang_name}",
        "zh": f"✅ 语言已更改: {lang_name}",
        "ja": f"✅ 言語を変更しました: {lang_name}",
        "he": f"✅ השפה שונתה ל-{lang_name}",
    }
    confirm_msg = confirmations.get(new_language, f"✅ Language set to {lang_name}")

    await callback.message.edit_text(
        confirm_msg,
        reply_markup=get_settings_keyboard(new_language)
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

    status_key = "notifications_toggled_on" if new_state else "notifications_toggled_off"
    status_text = get_system_message(status_key, language_code)
    await callback.message.edit_text(
        status_text,
        reply_markup=get_settings_keyboard(language_code)
    )
    await callback.answer(get_system_message("saved", language_code))


@router.callback_query(F.data == "settings_timezone")
async def callback_settings_timezone(callback: CallbackQuery) -> None:
    """Show timezone settings - region selection first"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    current_tz = user.timezone if user else "UTC"
    title = get_system_message("timezone_title", language_code)
    current_label = get_system_message("current_value", language_code, value=current_tz)
    prompt = get_system_message("select_timezone_prompt", language_code)
    await callback.message.edit_text(
        f"{title}\n\n{current_label}\n\n{prompt}",
        reply_markup=get_timezone_regions_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tz_region_"))
async def callback_timezone_region(callback: CallbackQuery) -> None:
    """Show timezones for selected region"""
    region = callback.data.replace("tz_region_", "")
    language_code = await get_user_language(callback.from_user.id)

    region_names = {
        "europe": "Europe",
        "americas": "Americas",
        "asia": "Asia",
        "pacific": "Australia & Pacific",
        "africa": "Africa & Middle East",
    }
    region_name = region_names.get(region, region.title())
    prompt = get_system_message("select_timezone_city", language_code)

    await callback.message.edit_text(
        f"🌍 <b>{region_name}</b>\n\n{prompt}",
        reply_markup=get_timezone_keyboard(language_code, region=region)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("timezone_"))
async def callback_set_timezone(callback: CallbackQuery) -> None:
    """Set user timezone"""
    timezone = callback.data.replace("timezone_", "")
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    try:
        await user_service.update_user_settings(
            telegram_id=callback.from_user.id,
            timezone=timezone
        )

        # Check if onboarding is in progress
        if user and not user.onboarding_completed:
            # During onboarding - show confirmation and complete onboarding
            await _complete_onboarding_flow(callback, language_code)
        else:
            # Existing user changing settings
            confirm_text = get_system_message("timezone_set_confirm", language_code, timezone=timezone)
            await callback.message.edit_text(
                confirm_text,
                reply_markup=get_settings_keyboard(language_code)
            )
            await callback.answer(get_system_message("saved", language_code))
    except ValueError as e:
        error_text = get_system_message("timezone_invalid", language_code)
        await callback.message.edit_text(
            error_text,
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer(get_system_message("error", language_code))


# Social profile callbacks
@router.callback_query(F.data == "settings_social")
async def callback_settings_social(callback: CallbackQuery) -> None:
    """Show social profile settings"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    social_service = SocialProfileService()
    summary = await social_service.get_profile_summary(callback.from_user.id, language_code, formal)
    title = get_system_message("social_profile_title", language_code)

    await callback.message.edit_text(
        f"{title}\n\n{summary}",
        reply_markup=get_social_profile_keyboard(language_code)
    )
    await callback.answer()


@router.callback_query(F.data == "social_add")
async def callback_social_add(callback: CallbackQuery, state: FSMContext) -> None:
    """Prompt to add a social network link"""
    language_code = await get_user_language(callback.from_user.id)
    await state.set_state(SocialProfileStates.waiting_for_social_link)
    prompt = get_system_message("social_add_prompt", language_code)
    await callback.message.edit_text(prompt)
    await callback.answer()


@router.callback_query(F.data == "social_bio")
async def callback_social_bio(callback: CallbackQuery, state: FSMContext) -> None:
    """Prompt to edit bio"""
    language_code = await get_user_language(callback.from_user.id)
    await state.set_state(SocialProfileStates.waiting_for_bio)
    prompt = get_system_message("social_bio_prompt", language_code)
    await callback.message.edit_text(prompt)
    await callback.answer()


@router.callback_query(F.data == "social_parse")
async def callback_social_parse(callback: CallbackQuery) -> None:
    """Parse interests from profile"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    parsing_text = get_system_message("social_parsing", language_code)
    await callback.message.edit_text(parsing_text)

    social_service = SocialProfileService()
    success, interests = await social_service.parse_interests(callback.from_user.id, language_code)

    if success and interests:
        interests_text = ", ".join(interests)
        success_text = get_system_message("social_interests_found", language_code, interests=interests_text)
        await callback.message.edit_text(
            success_text,
            reply_markup=get_social_profile_keyboard(language_code)
        )
    else:
        error_text = get_system_message("social_interests_failed", language_code)
        await callback.message.edit_text(
            error_text,
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
        no_links_text = get_system_message("social_no_links", language_code)
        await callback.message.edit_text(
            no_links_text,
            reply_markup=get_social_profile_keyboard(language_code)
        )
    else:
        urls = profile.get_all_urls()
        remove_text = get_system_message("social_remove_title", language_code)
        await callback.message.edit_text(
            remove_text,
            reply_markup=get_social_remove_keyboard(urls, language_code)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("social_del_"))
async def callback_social_delete(callback: CallbackQuery) -> None:
    """Delete a social network link"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    network = callback.data.replace("social_del_", "")

    social_service = SocialProfileService()
    success, message = await social_service.remove_social_link(
        callback.from_user.id, network, language_code, formal
    )

    if success:
        from src.utils.localization import get_system_message
        summary = await social_service.get_profile_summary(callback.from_user.id, language_code, formal)
        profile_title = get_system_message("social_profile_title", language_code)
        await callback.message.edit_text(
            f"✅ {message}\n\n{profile_title}\n\n{summary}",
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
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    social_service = SocialProfileService()
    summary = await social_service.get_profile_summary(callback.from_user.id, language_code, formal)
    title = get_system_message("social_profile_title", language_code)

    await callback.message.edit_text(
        f"{title}\n\n{summary}",
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

    title = get_system_message("settings_title", language_code)
    address_value = get_system_message("address_formal_value" if user.formal_address else "address_informal_value", language_code)
    notifications_value = get_system_message("notifications_on" if user.notifications_enabled else "notifications_off", language_code)
    interval_value = get_system_message("every_n_hours", language_code, hours=user.notification_interval_hours)

    settings_text = (
        f"{title}\n\n"
        f"🕐 {get_menu_text('settings_hours', language_code).replace('🕐 ', '')}: {user.active_hours_start} - {user.active_hours_end}\n"
        f"⏰ {get_menu_text('settings_interval', language_code).replace('⏰ ', '')}: {interval_value}\n"
        f"🌍 {get_menu_text('settings_timezone', language_code).replace('🌍 ', '')}: {user.timezone}\n"
        f"🗣 {get_menu_text('settings_address', language_code).replace('🗣 ', '')}: {address_value}\n"
        f"🔔 {get_menu_text('settings_notifications', language_code).replace('🔔 ', '')}: {notifications_value}\n"
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

        title = get_system_message("settings_reset_title", language_code)
        address_value = get_system_message("address_formal_value" if user.formal_address else "address_informal_value", language_code)
        notifications_value = get_system_message("notifications_on" if user.notifications_enabled else "notifications_off", language_code)
        interval_value = get_system_message("every_n_hours", language_code, hours=user.notification_interval_hours)

        settings_text = (
            f"{title}\n\n"
            f"🕐 {get_menu_text('settings_hours', language_code).replace('🕐 ', '')}: {user.active_hours_start} - {user.active_hours_end}\n"
            f"⏰ {get_menu_text('settings_interval', language_code).replace('⏰ ', '')}: {interval_value}\n"
            f"🌍 {get_menu_text('settings_timezone', language_code).replace('🌍 ', '')}: {user.timezone}\n"
            f"🗣 {get_menu_text('settings_address', language_code).replace('🗣 ', '')}: {address_value}\n"
            f"🔔 {get_menu_text('settings_notifications', language_code).replace('🔔 ', '')}: {notifications_value}\n"
        )
        try:
            await callback.message.edit_text(settings_text, reply_markup=get_settings_keyboard(language_code))
        except Exception as e:
            # Ignore "message is not modified" error - it means settings were already at default values
            error_msg = str(e)
            if "message is not modified" not in error_msg.lower():
                raise
        await callback.answer(get_system_message("settings_reset", language_code))
    else:
        language_code = await get_user_language(callback.from_user.id)
        error_text = get_system_message("settings_reset_error", language_code)
        await callback.message.edit_text(
            error_text,
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer(get_system_message("error", language_code))


# Moments callbacks
@router.callback_query(F.data == "moments_next")
async def callback_moments_next(callback: CallbackQuery) -> None:
    """Show next page of moments"""
    language_code = await get_user_language(callback.from_user.id)
    # Pagination logic would go here
    await callback.answer(get_system_message("moments_pagination_next", language_code))


@router.callback_query(F.data == "moments_prev")
async def callback_moments_prev(callback: CallbackQuery) -> None:
    """Show previous page of moments"""
    language_code = await get_user_language(callback.from_user.id)
    await callback.answer(get_system_message("moments_pagination_prev", language_code))


@router.callback_query(F.data == "moments_random")
async def callback_moments_random(callback: CallbackQuery) -> None:
    """Show random moment with delete option"""
    from src.bot.keyboards.inline import get_random_moment_keyboard

    language_code = await get_user_language(callback.from_user.id)
    moment_service = MomentService()
    moment = await moment_service.get_random_moment(callback.from_user.id)

    if moment:
        date_str = moment.created_at.strftime("%d.%m.%Y")
        title = get_system_message("random_moment_header", language_code)
        await callback.message.answer(
            f"{title}\n\n📅 {date_str}\n\n«{moment.content}»",
            reply_markup=get_random_moment_keyboard(moment.id, language_code)
        )
    else:
        empty_text = get_system_message("moments_empty", language_code)
        await callback.message.answer(empty_text)

    await callback.answer()


# Delete confirmation callbacks
@router.callback_query(F.data == "delete_confirm")
async def callback_delete_confirm(callback: CallbackQuery) -> None:
    """Confirm and execute data deletion"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    gdpr_service = GDPRService()

    try:
        await gdpr_service.delete_all_user_data(callback.from_user.id)
        success_text = get_system_message("data_deleted_formal" if formal else "data_deleted", language_code, formal=formal)
        await callback.message.edit_text(success_text)
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        error_text = get_system_message("data_delete_error_formal" if formal else "data_delete_error", language_code, formal=formal)
        await callback.message.edit_text(error_text)

    await callback.answer()


@router.callback_query(F.data == "delete_cancel")
async def callback_delete_cancel(callback: CallbackQuery) -> None:
    """Cancel data deletion"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    cancelled_text = get_system_message("delete_cancelled_formal" if formal else "delete_cancelled", language_code, formal=formal)
    await callback.message.edit_text(cancelled_text)
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
        not_found_text = get_system_message("moment_not_found", language_code)
        await callback.message.edit_text(
            not_found_text,
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
        await callback.answer()
        return

    preview = target_moment.content[:50] + ("..." if len(target_moment.content) > 50 else "")
    title = get_system_message("moment_delete_title", language_code)
    warning = get_system_message("moment_delete_warning", language_code)

    await callback.message.edit_text(
        f"{title}\n\n«{preview}»\n\n{warning}",
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
        success_text = get_system_message("moment_deleted_confirm", language_code)
        await callback.message.edit_text(
            success_text,
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
    else:
        error_text = get_system_message("moment_delete_error", language_code)
        await callback.message.edit_text(
            error_text,
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
    exit_text = get_system_message("dialog_exit_confirm", language_code)
    await callback.message.answer(
        exit_text,
        reply_markup=get_main_menu_keyboard(language_code)
    )
    await callback.answer()


# Back to main menu
@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery) -> None:
    """Return to main menu"""
    language_code = await get_user_language(callback.from_user.id)
    menu_text = get_system_message("main_menu_prompt", language_code)
    await callback.message.edit_text(
        menu_text,
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
        empty_text = get_system_message("moments_empty", language_code)
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        title = get_system_message("moments_title", language_code)
        moments_text = f"{title}\n\n"
        for moment in moments:
            date_str = moment.created_at.strftime("%d.%m.%Y")
            content_preview = moment.content[:100] + "..." if len(moment.content) > 100 else moment.content
            moments_text += f"🌟 <i>{date_str}</i>\n{content_preview}\n\n"
        await callback.message.edit_text(moments_text, reply_markup=get_moments_keyboard(language_code=language_code))

    await callback.answer()


@router.callback_query(F.data == "filter_today")
async def callback_filter_today(callback: CallbackQuery) -> None:
    """Filter moments for today"""
    from datetime import datetime, timedelta
    from src.bot.keyboards.inline import get_moments_keyboard

    language_code = await get_user_language(callback.from_user.id)
    moment_service = MomentService()
    
    # Get today's moments (last 24 hours)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)
    
    moments = await moment_service.get_user_moments_by_date(
        telegram_id=callback.from_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=10
    )
    
    if not moments:
        empty_text = get_system_message("moments_empty_today", language_code) or "У тебя пока нет моментов за сегодня."
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
    else:
        title = "📖 <b>Моменты за сегодня</b>\n\n"
        moments_text = title
        for moment in moments:
            date_str = moment.created_at.strftime("%H:%M")
            content_preview = moment.content[:100] + "..." if len(moment.content) > 100 else moment.content
            moments_text += f"🌟 <i>{date_str}</i>\n{content_preview}\n\n"
        await callback.message.edit_text(moments_text, reply_markup=get_moments_keyboard(language_code=language_code))
    
    await callback.answer()


@router.callback_query(F.data == "filter_week")
async def callback_filter_week(callback: CallbackQuery) -> None:
    """Filter moments for last 7 days"""
    from datetime import datetime, timedelta
    from src.bot.keyboards.inline import get_moments_keyboard

    language_code = await get_user_language(callback.from_user.id)
    moment_service = MomentService()
    
    # Get week's moments (last 7 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    moments = await moment_service.get_user_moments_by_date(
        telegram_id=callback.from_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=15
    )
    
    if not moments:
        empty_text = get_system_message("moments_empty_week", language_code) or "У тебя пока нет моментов за неделю."
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
    else:
        title = "📖 <b>Моменты за неделю</b>\n\n"
        moments_text = title
        for moment in moments:
            date_str = moment.created_at.strftime("%d.%m %H:%M")
            content_preview = moment.content[:100] + "..." if len(moment.content) > 100 else moment.content
            moments_text += f"🌟 <i>{date_str}</i>\n{content_preview}\n\n"
        await callback.message.edit_text(moments_text, reply_markup=get_moments_keyboard(language_code=language_code))
    
    await callback.answer()


@router.callback_query(F.data == "filter_month")
async def callback_filter_month(callback: CallbackQuery) -> None:
    """Filter moments for last 30 days"""
    from datetime import datetime, timedelta
    from src.bot.keyboards.inline import get_moments_keyboard

    language_code = await get_user_language(callback.from_user.id)
    moment_service = MomentService()
    
    # Get month's moments (last 30 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    moments = await moment_service.get_user_moments_by_date(
        telegram_id=callback.from_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=20
    )
    
    if not moments:
        empty_text = get_system_message("moments_empty_month", language_code) or "У тебя пока нет моментов за месяц."
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
    else:
        title = "📖 <b>Моменты за месяц</b>\n\n"
        moments_text = title
        for moment in moments:
            date_str = moment.created_at.strftime("%d.%m")
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
        empty_text = get_system_message("stats_empty", language_code)
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        title = get_system_message("stats_title", language_code)
        total_text = get_system_message("stats_total_moments", language_code, count=stats.total_moments)
        current_streak = get_system_message("stats_current_streak", language_code, days=stats.current_streak)
        longest_streak = get_system_message("stats_longest_streak", language_code, days=stats.longest_streak)

        stats_text = (
            f"{title}\n\n"
            f"🌟 {total_text}\n"
            f"🔥 {current_streak}\n"
            f"🏆 {longest_streak}\n"
            f"✉️ {stats.total_questions_sent}\n"
            f"✅ {stats.total_questions_answered}\n"
        )
        if stats.total_questions_sent > 0:
            answer_rate = (stats.total_questions_answered / stats.total_questions_sent) * 100
            rate_text = get_system_message("stats_response_rate", language_code, rate=f"{answer_rate:.1f}")
            stats_text += f"📈 {rate_text}\n"
        await callback.message.edit_text(stats_text, reply_markup=get_main_menu_inline(language_code))

    await callback.answer()


@router.callback_query(F.data == "menu_settings")
async def callback_menu_settings(callback: CallbackQuery) -> None:
    """Show settings menu"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"

    if not user:
        start_text = get_system_message("please_start_first", language_code)
        await callback.message.edit_text(
            start_text,
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        title = get_system_message("settings_title", language_code)
        address_value = get_system_message("address_formal_value" if user.formal_address else "address_informal_value", language_code)
        notifications_value = get_system_message("notifications_on" if user.notifications_enabled else "notifications_off", language_code)
        interval_value = get_system_message("every_n_hours", language_code, hours=user.notification_interval_hours)

        settings_text = (
            f"{title}\n\n"
            f"🕐 {get_menu_text('settings_hours', language_code).replace('🕐 ', '')}: {user.active_hours_start} - {user.active_hours_end}\n"
            f"⏰ {get_menu_text('settings_interval', language_code).replace('⏰ ', '')}: {interval_value}\n"
            f"🌍 {get_menu_text('settings_timezone', language_code).replace('🌍 ', '')}: {user.timezone}\n"
            f"🗣 {get_menu_text('settings_address', language_code).replace('🗣 ', '')}: {address_value}\n"
            f"🔔 {get_menu_text('settings_notifications', language_code).replace('🔔 ', '')}: {notifications_value}\n"
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
    dialog_intro = get_system_message("dialog_intro", language_code)
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

    # Get localized period name
    period_key = f"period_{period}"
    period_name = get_system_message(period_key, language_code)

    if not moments:
        empty_text = get_system_message("no_moments_period", language_code, period=period_name)
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_moments_keyboard(language_code=language_code)
        )
    else:
        title = get_system_message("moments_period_title", language_code, period=period_name)
        moments_text = f"{title}\n\n"
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
    language_code = await get_user_language(callback.from_user.id)
    skip_text = get_system_message("question_skipped", language_code)
    await callback.message.edit_text(skip_text)
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
    loading_text = get_system_message("summary_generating_weekly", language_code)
    await callback.message.edit_text(loading_text)

    summary_service = SummaryService()
    summary = await summary_service.generate_weekly_summary(callback.from_user.id)

    if summary:
        await callback.message.edit_text(
            summary,
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        empty_text = get_system_message("summary_not_enough_weekly", language_code)
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_main_menu_inline(language_code)
        )

    await callback.answer()


@router.callback_query(F.data == "summary_monthly")
async def callback_summary_monthly(callback: CallbackQuery) -> None:
    """Generate and show monthly summary"""
    from src.services.summary_service import SummaryService

    language_code = await get_user_language(callback.from_user.id)
    loading_text = get_system_message("summary_generating_monthly", language_code)
    await callback.message.edit_text(loading_text)

    summary_service = SummaryService()
    summary = await summary_service.generate_monthly_summary(callback.from_user.id)

    if summary:
        await callback.message.edit_text(
            summary,
            reply_markup=get_main_menu_inline(language_code)
        )
    else:
        empty_text = get_system_message("summary_not_enough_monthly", language_code)
        await callback.message.edit_text(
            empty_text,
            reply_markup=get_main_menu_inline(language_code)
        )

    await callback.answer()


# Pause callbacks
@router.callback_query(F.data == "pause_day")
async def callback_pause_day(callback: CallbackQuery) -> None:
    """Pause notifications for 1 day"""
    await _set_pause(callback, days=1)


@router.callback_query(F.data == "pause_week")
async def callback_pause_week(callback: CallbackQuery) -> None:
    """Pause notifications for 1 week"""
    await _set_pause(callback, days=7)


@router.callback_query(F.data == "pause_two_weeks")
async def callback_pause_two_weeks(callback: CallbackQuery) -> None:
    """Pause notifications for 2 weeks"""
    await _set_pause(callback, days=14)


@router.callback_query(F.data == "pause_cancel")
async def callback_pause_cancel(callback: CallbackQuery) -> None:
    """Cancel pause selection"""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    
    # Use answer instead of edit_text because we need ReplyKeyboardMarkup for main menu
    from src.bot.keyboards.reply import get_main_menu_keyboard
    await callback.message.answer(
        get_system_message("cancelled", language_code),
        reply_markup=get_main_menu_keyboard(language_code)
    )
    # Delete the inline message with pause selection
    try:
        await callback.message.delete()
    except Exception:
        pass  # Ignore if message already deleted
    await callback.answer()


async def _set_pause(callback: CallbackQuery, days: int) -> None:
    """Set pause for notifications"""
    from datetime import datetime, timedelta, timezone as dt_timezone
    from sqlalchemy import select
    from src.db.database import get_session
    from src.db.models import User
    
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    formal = user.formal_address if user else False
    
    # Calculate pause until datetime
    pause_until = datetime.now(dt_timezone.utc) + timedelta(days=days)
    
    # Update user
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == user.id)
        )
        db_user = result.scalar_one_or_none()
        if db_user:
            db_user.notifications_paused_until = pause_until.replace(tzinfo=None)
            await session.commit()
    
    # Format date for display
    from src.utils.localization import get_language_code
    lang = get_language_code(language_code)
    
    # Format date based on language
    if lang == "ru":
        date_str = pause_until.strftime("%d.%m.%Y в %H:%M")
    elif lang == "uk":
        date_str = pause_until.strftime("%d.%m.%Y о %H:%M")
    elif lang in ["es", "pt", "it", "fr", "de"]:
        # European format: DD.MM.YYYY at HH:MM
        date_str = pause_until.strftime("%d.%m.%Y в %H:%M")
    elif lang == "he":
        # Hebrew: DD/MM/YYYY at HH:MM
        date_str = pause_until.strftime("%d/%m/%Y в %H:%M")
    elif lang in ["zh", "ja"]:
        # Asian format: YYYY年MM月DD日 HH:MM
        if lang == "zh":
            date_str = pause_until.strftime("%Y年%m月%d日 %H:%M")
        else:  # ja
            date_str = pause_until.strftime("%Y年%m月%d日 %H:%M")
    else:  # English and others
        date_str = pause_until.strftime("%B %d, %Y at %H:%M")
    
    # Get confirmation message
    confirm_key = "pause_confirmed_formal" if formal else "pause_confirmed"
    confirm_msg = get_system_message(confirm_key, language_code, date=date_str)
    
    # Use answer instead of edit_text because we need ReplyKeyboardMarkup for main menu
    from src.bot.keyboards.reply import get_main_menu_keyboard
    await callback.message.answer(
        confirm_msg,
        reply_markup=get_main_menu_keyboard(language_code)
    )
    # Delete the inline message with pause selection
    try:
        await callback.message.delete()
    except Exception:
        pass  # Ignore if message already deleted
    await callback.answer()
