# 📋 План улучшений онбординга

**Дата:** 2026-01-21  
**Версия:** 1.0  
**Статус:** Планирование

---

## 🎯 Цели

1. Улучшить UX онбординга (5 пунктов из Customer Journey Map)
2. Добавить выбор пола в онбординг (мужчина/женщина/нейтрально)
3. Сделать онбординг более информативным и удобным

---

## 📊 Текущее состояние

### Онбординг сейчас:
1. `/start` → Приветствие + выбор формы обращения (ты/вы)
2. Выбор формы → Инструкция + завершение онбординга
3. Автоматическая отправка первого вопроса

### Что отсутствует:
- ❌ Выбор пола в онбординге (только в настройках)
- ❌ Анимация загрузки при отправке вопроса
- ❌ Подтверждение перед завершением
- ❌ Примеры ответов
- ❌ Быстрая настройка часового пояса
- ❌ Видео-демонстрация (опционально)

---

## 🚀 План реализации

### **Этап 1: Добавление выбора пола в онбординг**

#### 1.1. Обновить модель данных
**Файл:** `src/db/models/user.py`
- ✅ Пол уже есть: `gender: Mapped[Optional[str]]` (male, female, unknown)
- ✅ Значение по умолчанию: `"unknown"`

**Действия:**
- Проверить, что модель поддерживает "unknown" (уже поддерживает)

#### 1.2. Расширить клавиатуру выбора пола
**Файл:** `src/bot/keyboards/inline.py`

**Текущее состояние:**
```python
def get_gender_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("gender_male", language_code), callback_data="gender_male"),
                InlineKeyboardButton(text=get_menu_text("gender_female", language_code), callback_data="gender_female"),
            ],
        ]
    )
```

**Изменения:**
```python
def get_gender_keyboard(language_code: str = "ru", include_neutral: bool = False) -> InlineKeyboardMarkup:
    """Create keyboard for gender selection
    
    Args:
        language_code: User's language
        include_neutral: If True, adds "neutral/unknown" option (for onboarding)
    """
    buttons = [
        [
            InlineKeyboardButton(text=get_menu_text("gender_male", language_code), callback_data="gender_male"),
            InlineKeyboardButton(text=get_menu_text("gender_female", language_code), callback_data="gender_female"),
        ],
    ]
    
    if include_neutral:
        buttons.append([
            InlineKeyboardButton(text=get_menu_text("gender_neutral", language_code), callback_data="gender_neutral"),
        ])
    
    # Add back button only if not in onboarding
    if not include_neutral:
        buttons.append([
            InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back"),
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
```

#### 1.3. Добавить локализацию для "нейтрально"
**Файл:** `src/utils/localization.py`

**Добавить в MENU_TEXTS для всех языков:**
```python
"gender_neutral": "⚪ Нейтрально",  # RU
"gender_neutral": "⚪ Neutral",     # EN
"gender_neutral": "⚪ Нейтрально",  # UK
# ... для остальных языков
```

#### 1.4. Создать обработчик для "нейтрально"
**Файл:** `src/bot/handlers/callbacks.py`

**Добавить:**
```python
@router.callback_query(F.data == "gender_neutral")
async def callback_gender_neutral(callback: CallbackQuery) -> None:
    """Set gender to neutral/unknown"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        gender="unknown"
    )
    
    language_code = await get_user_language(callback.from_user.id)
    confirm_text = get_system_message("gender_set_neutral", language_code)
    await callback.message.edit_text(
        f"✅ {confirm_text}",
        reply_markup=get_settings_keyboard(language_code)  # или get_onboarding_next_keyboard
    )
    await callback.answer(get_system_message("saved", language_code))
```

#### 1.5. Изменить flow онбординга
**Файл:** `src/bot/handlers/callbacks.py`

**Новый flow:**
1. `/start` → Приветствие + выбор формы обращения (ты/вы)
2. Выбор формы → **НОВОЕ:** Выбор пола (мужчина/женщина/нейтрально)
3. Выбор пола → Подтверждение + инструкция + завершение онбординга
4. Автоматическая отправка первого вопроса

**Изменения в `callback_address_informal` и `callback_address_formal`:**
```python
@router.callback_query(F.data == "address_informal")
async def callback_address_informal(callback: CallbackQuery) -> None:
    """Set informal address (ты)"""
    user_service = UserService()
    await user_service.update_user_settings(
        telegram_id=callback.from_user.id,
        formal_address=False
    )
    
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    language_code = user.language_code if user else "ru"
    
    # НОВОЕ: Показываем выбор пола вместо завершения онбординга
    prompt = get_system_message("onboarding_select_gender", language_code)
    await callback.message.edit_text(
        prompt,
        reply_markup=get_gender_keyboard(language_code, include_neutral=True)
    )
    await callback.answer()
    # НЕ вызываем complete_onboarding() здесь!
```

**Новый обработчик для завершения онбординга после выбора пола:**
```python
async def _complete_onboarding_flow(callback: CallbackQuery, language_code: str) -> None:
    """Complete onboarding and send first question"""
    user_service = UserService()
    await user_service.complete_onboarding(callback.from_user.id)
    
    # Показываем финальное сообщение с инструкциями
    confirm_text = get_onboarding_text("onboarding_complete", language_code)
    await callback.message.edit_text(
        confirm_text,
        reply_markup=get_main_menu_inline(language_code)
    )
    
    # Отправляем первый вопрос
    from src.services.scheduler import NotificationScheduler
    scheduler = NotificationScheduler.get_instance()
    if scheduler:
        try:
            await scheduler.send_first_question_after_onboarding(callback.from_user.id)
        except Exception as e:
            logger.error(f"Failed to send first question: {e}")
    else:
        temp_scheduler = NotificationScheduler(callback.bot)
        try:
            await temp_scheduler.send_first_question_after_onboarding(callback.from_user.id)
        except Exception as e:
            logger.error(f"Fallback failed: {e}")
    
    await callback.answer()
```

**Обновить `callback_gender_male`, `callback_gender_female`, `callback_gender_neutral`:**
```python
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
    
    # Проверяем, идет ли онбординг
    if not user.onboarding_completed:
        # Завершаем онбординг
        await _complete_onboarding_flow(callback, language_code)
    else:
        # Обычная настройка
        confirm_text = get_system_message("gender_set_male", language_code)
        await callback.message.edit_text(
            f"✅ {confirm_text}",
            reply_markup=get_settings_keyboard(language_code)
        )
        await callback.answer(get_system_message("saved", language_code))
```

#### 1.6. Обновить приветственное сообщение (добавить информацию о голосовых)
**Файл:** `src/bot/handlers/commands.py`

**Изменения в `get_localized_welcome_text()`:**
```python
def get_localized_welcome_text(first_name: str, language_code: str) -> str:
    """Get welcome text in user's language"""
    if language_code and language_code.startswith("en"):
        return (
            f"Hello, {first_name}! 👋\n\n"
            "I'm your assistant for developing positive thinking. "
            "Every day I will ask you about good things, "
            "so that we can notice the joyful moments of life together. ✨\n\n"
            "💬 You can reply with text or voice messages - I'll understand both!\n\n"
            "Let's begin! How would you prefer to communicate?"
        )
    elif language_code and language_code.startswith("uk"):
        return (
            f"Привіт, {first_name}! 👋\n\n"
            "Я — твій помічник для розвитку позитивного мислення. "
            "Щодня я буду запитувати тебе про хороше, "
            "щоб разом помічати радісні моменти життя. ✨\n\n"
            "💬 Ти можеш відповідати текстом або голосовими повідомленнями - я зрозумію обидва!\n\n"
            "Давай почнемо! Як тобі зручніше спілкуватися?"
        )
    else:  # Default to Russian
        return (
            f"Привет, {first_name}! 👋\n\n"
            "Я — твой помощник для развития позитивного мышления. "
            "Каждый день я буду спрашивать тебя о хорошем, "
            "чтобы вместе замечать радостные моменты жизни. ✨\n\n"
            "💬 Ты можешь отвечать текстом или голосовыми сообщениями - я пойму оба варианта!\n\n"
            "Давай начнём! Как тебе удобнее общаться?"
        )
```

**ВАЖНО:** Все тексты должны быть в `localization.py`, а не хардкод в функции!

**Правильный подход:**
1. Добавить ключи в `ONBOARDING_TEXTS`:
```python
"welcome_with_voice": (
    "Привет, {first_name}! 👋\n\n"
    "Я — твой помощник для развития позитивного мышления. "
    "Каждый день я буду спрашивать тебя о хорошем, "
    "чтобы вместе замечать радостные моменты жизни. ✨\n\n"
    "💬 Ты можешь отвечать текстом или голосовыми сообщениями - я пойму оба варианта!\n\n"
    "Давай начнём! Как тебе удобнее общаться?"
),  # RU
```

2. Использовать в функции:
```python
def get_localized_welcome_text(first_name: str, language_code: str) -> str:
    """Get welcome text in user's language"""
    return get_onboarding_text("welcome_with_voice", language_code, first_name=first_name)
```

#### 1.7. Добавить новые тексты локализации
**Файл:** `src/utils/localization.py`

**В ONBOARDING_TEXTS добавить:**
```python
"welcome_with_voice": (
    "Привет, {first_name}! 👋\n\n"
    "Я — твой помощник для развития позитивного мышления. "
    "Каждый день я буду спрашивать тебя о хорошем, "
    "чтобы вместе замечать радостные моменты жизни. ✨\n\n"
    "💬 Ты можешь отвечать текстом или голосовыми сообщениями - я пойму оба варианта!\n\n"
    "Давай начнём! Как тебе удобнее общаться?"
),  # RU

"onboarding_select_gender": (
    "Отлично! Буду обращаться на «ты» 😊\n\n"
    "Теперь выбери, как тебя лучше называть:\n\n"
    "Это поможет мне задавать более персонализированные вопросы."
),  # RU

"onboarding_complete": (
    "Отлично! Всё готово! 🎉\n\n"
    "Теперь немного о том, как это работает:\n\n"
    "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
    "• Ты можешь ответить текстом или голосовым сообщением\n"
    "• Я сохраню твои моменты и напомню о них, когда понадобится поддержка\n\n"
    "🔒 Твои данные в безопасности и используются только для нашего общения.\n"
    "Подробнее: /privacy"
),  # RU
```

**В SYSTEM_MESSAGES добавить:**
```python
"gender_set_neutral": "Пол установлен: нейтрально",  # RU
"gender_set_neutral": "Gender set to: neutral",      # EN
"gender_set_neutral": "Стать встановлено: нейтрально",  # UK
```

---

### **Этап 2: Анимация загрузки при отправке первого вопроса**

#### 2.1. Добавить индикатор "typing"
**Файл:** `src/services/scheduler.py`

**В `send_first_question_after_onboarding`:**
```python
async def send_first_question_after_onboarding(self, telegram_id: int) -> bool:
    """Send the first question immediately after onboarding completion."""
    try:
        async with get_session() as session:
            # ... получение пользователя ...
            
            # НОВОЕ: Показываем индикатор печати
            await self.bot.send_chat_action(
                chat_id=user.telegram_id,
                action=ChatAction.TYPING
            )
            
            # Небольшая задержка для UX (опционально)
            await asyncio.sleep(0.5)
            
            # Получаем вопрос
            question = self._get_question(user)
            
            # Отправляем сообщение
            sent_message = await self.bot.send_message(
                chat_id=user.telegram_id,
                text=question,
                reply_markup=get_question_keyboard(),
            )
            # ... остальной код ...
```

**Импорт:**
```python
from aiogram.enums import ChatAction
import asyncio
```

---

### **Этап 3: Подтверждение перед завершением онбординга**

#### 3.1. Добавить промежуточный шаг
**Файл:** `src/bot/handlers/callbacks.py`

**После выбора пола показывать:**
```python
async def _show_onboarding_confirmation(callback: CallbackQuery, language_code: str) -> None:
    """Show confirmation before completing onboarding"""
    confirm_text = get_onboarding_text("onboarding_ready_confirm", language_code)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_menu_text("yes_start", language_code),
                    callback_data="onboarding_confirm_yes"
                ),
                InlineKeyboardButton(
                    text=get_menu_text("no_settings", language_code),
                    callback_data="onboarding_confirm_settings"
                ),
            ],
        ]
    )
    await callback.message.edit_text(confirm_text, reply_markup=keyboard)
    await callback.answer()
```

**Новые тексты:**
```python
"onboarding_ready_confirm": (
    "Всё готово! 🎉\n\n"
    "Я буду задавать тебе вопросы о хороших моментах дня.\n\n"
    "Готов начать? Или хочешь сначала настроить часовой пояс и интервал?"
),  # RU
```

**Новые кнопки:**
```python
"yes_start": "✅ Да, начать",
"no_settings": "⚙️ Сначала настройки",
```

**Обработчики:**
```python
@router.callback_query(F.data == "onboarding_confirm_yes")
async def callback_onboarding_confirm_yes(callback: CallbackQuery) -> None:
    """User confirmed - complete onboarding"""
    language_code = await get_user_language(callback.from_user.id)
    await _complete_onboarding_flow(callback, language_code)

@router.callback_query(F.data == "onboarding_confirm_settings")
async def callback_onboarding_confirm_settings(callback: CallbackQuery) -> None:
    """User wants to configure settings first"""
    language_code = await get_user_language(callback.from_user.id)
    # Показываем быструю настройку часового пояса (см. Этап 5)
    # После настройки возвращаемся к подтверждению
```

---

### **Этап 4: Примеры ответов в инструкции**

#### 4.1. Обновить текст завершения онбординга
**Файл:** `src/utils/localization.py`

**В `ONBOARDING_TEXTS["onboarding_complete"]` добавить:**
```python
"onboarding_complete": (
    "Отлично! Всё готово! 🎉\n\n"
    "Теперь немного о том, как это работает:\n\n"
    "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
    "• Ты можешь ответить текстом или голосовым сообщением\n"
    "• Я сохраню твои моменты и напомню о них, когда понадобится поддержка\n\n"
    "📝 <b>Примеры ответов:</b>\n"
    "• «Сегодня прогулялся в парке, было очень красиво!»\n"
    "• «Встретился с друзьями, хорошо пообщались»\n"
    "• «Закончил важный проект, чувствую гордость»\n"
    "• «Выпил вкусный кофе и почитал книгу»\n\n"
    "⚙️ <b>Важно:</b> Пожалуйста, настрой свой <b>часовой пояс</b> и <b>частоту сообщений</b> "
    "в разделе ⚙️ Настройки, чтобы я писал тебе в удобное время!\n\n"
    "🔒 Твои данные в безопасности и используются только для нашего общения.\n"
    "Подробнее: /privacy"
),  # RU
```

---

### **Этап 5: Обязательная настройка часового пояса в онбординге**

#### 5.1. Использовать существующий виджет выбора часового пояса
**Файл:** `src/bot/handlers/callbacks.py`

**Существующие функции (используем как есть):**
- `callback_settings_timezone()` - показывает выбор региона
- `callback_timezone_region()` - показывает города в регионе
- `callback_set_timezone()` - сохраняет часовой пояс

**Изменения:**
- Модифицировать `callback_set_timezone()` чтобы проверять, идет ли онбординг
- Если онбординг → переходить к следующему шагу (подтверждение)
- Если настройки → возвращаться в настройки

#### 5.2. Добавить объяснение важности часового пояса
**Файл:** `src/utils/localization.py`

**В ONBOARDING_TEXTS добавить:**
```python
"onboarding_timezone_important": (
    "🌍 <b>Важно: Выбор часового пояса</b>\n\n"
    "Это очень важно! Без правильного часового пояса я могу начать отправлять "
    "сообщения ночью, когда ты не хочешь получать уведомления. 😴\n\n"
    "Я буду писать тебе только в активные часы (по умолчанию с 9:00 до 21:00), "
    "но для этого мне нужно знать твой часовой пояс.\n\n"
    "Пожалуйста, выбери свой часовой пояс:"
),  # RU

"onboarding_timezone_important": (
    "🌍 <b>Important: Timezone Selection</b>\n\n"
    "This is very important! Without the correct timezone, I might start sending "
    "messages at night when you don't want to receive notifications. 😴\n\n"
    "I will only message you during active hours (default 9:00 AM to 9:00 PM), "
    "but I need to know your timezone for that.\n\n"
    "Please select your timezone:"
),  # EN
```

#### 5.3. Создать обработчик для показа часового пояса в онбординге
**Файл:** `src/bot/handlers/callbacks.py`

**Новая функция:**
```python
async def _show_onboarding_timezone(callback: CallbackQuery, language_code: str) -> None:
    """Show timezone selection during onboarding with explanation"""
    explanation = get_onboarding_text("onboarding_timezone_important", language_code)
    
    await callback.message.edit_text(
        explanation,
        reply_markup=get_timezone_regions_keyboard(language_code)
    )
    await callback.answer()
```

#### 5.4. Модифицировать существующий обработчик
**Файл:** `src/bot/handlers/callbacks.py`

**Изменения в `callback_set_timezone()`:**
```python
@router.callback_query(F.data.startswith("timezone_"))
async def callback_set_timezone(callback: CallbackQuery) -> None:
    """Set user timezone"""
    timezone = callback.data.replace("timezone_", "")
    language_code = await get_user_language(callback.from_user.id)

    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    try:
        await user_service.update_user_settings(
            telegram_id=callback.from_user.id,
            timezone=timezone
        )

        confirm_text = get_system_message("timezone_set_confirm", language_code, timezone=timezone)
        
        # Проверяем, идет ли онбординг
        if user and not user.onboarding_completed:
            # В онбординге - переходим к подтверждению готовности
            await _show_onboarding_confirmation(callback, language_code)
        else:
            # В настройках - возвращаемся в настройки
            await callback.message.edit_text(
                confirm_text,
                reply_markup=get_settings_keyboard(language_code)
            )
        
        await callback.answer(get_system_message("saved", language_code))
    except Exception as e:
        logger.error(f"Failed to set timezone: {e}")
        error_text = get_system_message("error", language_code)
        await callback.answer(error_text)
```

#### 5.5. Интегрировать в flow онбординга
**Порядок шагов:**
1. `/start` → Приветствие (с информацией о голосовых сообщениях)
2. Выбор формы обращения (ты/вы)
3. Выбор пола (мужчина/женщина/нейтрально)
4. **ОБЯЗАТЕЛЬНО:** Настройка часового пояса (с объяснением важности) ← **БЕЗ ПРОПУСКА**
5. Подтверждение готовности
6. Завершение онбординга + первый вопрос

---

### **Этап 6: Видео-демонстрация (опционально, низкий приоритет)**

#### 6.1. Подготовка видео
- Создать короткое видео (30-60 сек) о том, как работает бот
- Загрузить на YouTube или другой хостинг
- Получить ссылку

#### 6.2. Добавить кнопку в приветствие
**Файл:** `src/bot/keyboards/inline.py`

```python
def get_onboarding_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=informal_text, callback_data="address_informal"),
                InlineKeyboardButton(text=formal_text, callback_data="address_formal"),
            ],
            [
                InlineKeyboardButton(
                    text=get_menu_text("watch_demo", language_code),
                    url="https://youtube.com/watch?v=..."  # Ссылка на видео
                ),
            ],
        ]
    )
    return keyboard
```

**Новый текст:**
```python
"watch_demo": "📹 Посмотреть демо (1 мин)",
```

---

## 📅 План выполнения

### Приоритет 1 (Критично):
- ✅ **Этап 1:** Добавление выбора пола в онбординг
- ✅ **Этап 2:** Анимация загрузки

**Время:** 2-3 часа

### Приоритет 2 (Важно):
- ✅ **Этап 3:** Подтверждение перед завершением
- ✅ **Этап 4:** Примеры ответов

**Время:** 1-2 часа

### Приоритет 3 (Критично - обязательно):
- ✅ **Этап 5:** Обязательная настройка часового пояса (используем существующий виджет)

**Время:** 1-2 часа

### Приоритет 4 (Опционально):
- ✅ **Этап 6:** Видео-демонстрация

**Время:** 1-2 часа (только если видео готово)

---

## 🧪 Тестирование

### Чек-лист для каждого этапа:

#### Этап 1 (Пол):
- [ ] Кнопка "Нейтрально" появляется в онбординге
- [ ] Выбор "мужчина" завершает онбординг
- [ ] Выбор "женщина" завершает онбординг
- [ ] Выбор "нейтрально" завершает онбординг
- [ ] Пол сохраняется в БД
- [ ] Вопросы адаптируются под пол

#### Этап 2 (Анимация):
- [ ] Индикатор "typing" показывается перед вопросом
- [ ] Задержка не слишком долгая (< 1 сек)

#### Этап 3 (Подтверждение):
- [ ] Кнопка "Да, начать" завершает онбординг
- [ ] Кнопка "Сначала настройки" открывает настройки
- [ ] После настройки можно вернуться к подтверждению

#### Этап 4 (Примеры):
- [ ] Примеры отображаются в финальном сообщении
- [ ] Примеры локализованы для всех языков

#### Этап 5 (Часовой пояс):
- [ ] Объяснение важности часового пояса показывается
- [ ] Существующий виджет выбора региона работает
- [ ] Выбор города сохраняет часовой пояс
- [ ] Часовой пояс сохраняется в БД
- [ ] **НЕТ кнопки "Пропустить"** (обязательный шаг)
- [ ] После выбора часового пояса переходим к подтверждению

---

## 📝 Файлы для изменения

### Новые файлы:
- Нет

### Изменяемые файлы:
1. `src/bot/keyboards/inline.py` - Расширение клавиатуры пола (добавить "нейтрально")
2. `src/bot/handlers/callbacks.py` - Новые обработчики, изменение flow, модификация `callback_set_timezone()`
3. `src/bot/handlers/commands.py` - Обновление приветственного сообщения (использовать локализацию)
4. `src/utils/localization.py` - Новые тексты (20+ ключей для всех языков)
5. `src/services/scheduler.py` - Анимация загрузки

### Миграции БД:
- ❌ Не требуется (все поля уже есть)

---

## 🎯 Ожидаемый результат

### Новый flow онбординга:
1. `/start` → Приветствие (с информацией о голосовых сообщениях) + выбор формы обращения
2. Выбор формы → Выбор пола (мужчина/женщина/нейтрально)
3. Выбор пола → **ОБЯЗАТЕЛЬНАЯ** настройка часового пояса (с объяснением важности)
4. Выбор часового пояса → Подтверждение готовности
5. Подтверждение → Завершение + анимация загрузки
6. Первый вопрос с примерами ответов

**Время прохождения:** ~90-120 секунд (было 30-60)

**Улучшения:**
- ✅ Пользователь знает о голосовых сообщениях с самого начала
- ✅ Пользователь выбирает пол сразу
- ✅ **ОБЯЗАТЕЛЬНО** настраивает часовой пояс (предотвращает ночные сообщения)
- ✅ Видит объяснение важности часового пояса
- ✅ Видит примеры ответов
- ✅ Видит анимацию загрузки (лучший UX)
- ✅ Подтверждает готовность
- ✅ Все тексты локализованы, без хардкода

---

---

## ⚠️ Критические требования

### 1. Часовой пояс - ОБЯЗАТЕЛЬНЫЙ
- ❌ **НЕТ кнопки "Пропустить"**
- ✅ Используется существующий виджет (`get_timezone_regions_keyboard` → `get_timezone_keyboard`)
- ✅ Объяснение важности показывается перед выбором
- ✅ Без выбора часового пояса онбординг не завершается

### 2. Мультиязычность
- ✅ Все тексты в `localization.py`
- ❌ **НЕТ хардкода** в коде
- ✅ Поддержка всех 11 языков (RU, EN, UK, ES, DE, FR, PT, IT, ZH, JA, HE)

### 3. Голосовые сообщения
- ✅ Информация о голосовых сообщениях в приветствии
- ✅ Локализовано для всех языков

---

---

## 📝 Дополнительные требования к локализации

### Все новые тексты должны быть добавлены для всех 11 языков:

**RU, EN, UK, ES, DE, FR, PT, IT, ZH, JA, HE**

**Список новых ключей:**
1. `welcome_with_voice` - Приветствие с информацией о голосовых
2. `onboarding_select_gender` - Запрос выбора пола
3. `onboarding_timezone_important` - Объяснение важности часового пояса
4. `onboarding_ready_confirm` - Подтверждение готовности
5. `onboarding_complete` - Финальное сообщение с примерами
6. `gender_neutral` - Кнопка "Нейтрально"
7. `gender_set_neutral` - Подтверждение выбора нейтрального пола
8. `yes_start` - Кнопка "Да, начать"
9. `no_settings` - Кнопка "Сначала настройки"

**Всего:** ~9 новых ключей × 11 языков = **99 переводов**

---

**Документ создан:** 2026-01-21  
**Последнее обновление:** 2026-01-21 (версия 2.0 - с учетом замечаний)
