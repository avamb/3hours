# MINDSETHAPPYBOT Knowledge Base для RAG-системы

## 📋 Обзор

Эта база знаний предназначена для векторной RAG (Retrieval-Augmented Generation) системы бота MINDSETHAPPYBOT - AI-друга для поддержки ментального здоровья через практику благодарности.

**Версия:** 1.0  
**Языки:** RU, EN, UK, ES, FR, DE, HE, IT, PL, CS, HU  
**Последнее обновление:** January 2026

---

## 🗂️ Структура базы знаний

```
knowledge_base/
├── core/                          # Основные принципы и философия
│   ├── 01_bot_philosophy.md       # Философия бота, научное обоснование
│   └── 02_personalization_rules.md # Правила персонализации и адаптации
│
├── support/                       # Эмоциональная поддержка
│   └── 01_anxiety_support.md      # Поддержка при тревоге и депрессии
│
├── techniques/                    # Практические техники
│   └── 01_anxiety_techniques.md   # Техники борьбы с тревогой (5-4-3-2-1, дыхание, когнитивная переоценка)
│
├── questions/                     # Вопросы для пользователей
│   ├── 01_diverse_questions.md    # Разнообразные вопросы (по времени суток, дню недели)
│   └── 02_seasonal_contextual.md  # Сезонные и праздничные вопросы
│
├── audience_specific/             # Контент для специфических аудиторий
│   ├── 01_elderly_support.md      # Поддержка пожилых (45-70+)
│   ├── 02_new_mothers_ppd.md      # Поддержка молодых мам (послеродовая депрессия)
│   └── 03_professionals_burnout.md # Поддержка профессионалов с выгоранием
│
└── crisis/                        # Кризисная поддержка
    └── 01_crisis_protocols.md     # Протоколы при кризисе, горячие линии по странам
```

---

## 🏷️ Метаданные в заголовках файлов

Каждый markdown файл содержит YAML front matter с метаданными для эффективного поиска:

```yaml
---
category: core | support | techniques | questions | audience_specific | crisis
type: philosophy | emotional_support | anxiety_management | prompts | etc.
languages: [ru, en, uk, es, fr, de, he, it, pl, cs, hu]
audience: all | anxiety_sufferers | elderly_45plus | new_mothers_ppd | professionals_burnout
tone: warm | gentle | practical | directive | etc.
use_case: foundational_understanding | responding_to_distress | daily_check_ins | crisis_detection_referral
chunk_size: small | medium | large
priority: normal | critical  # Только для crisis контента
tags: [список, релевантных, тегов]
---
```

### Как использовать метаданные:

**Векторный поиск + фильтрация:**
```python
# Пример поиска с фильтрацией
results = vector_search(
    query=user_message,
    filter={
        "audience": user.segment,  # "anxiety_sufferers"
        "languages": user.language,  # "ru"
        "category": {"$nin": ["crisis"]}  # Exclude unless triggered
    },
    top_k=5
)

# Для кризиса - приоритет
if detect_crisis_keywords(user_message):
    crisis_results = vector_search(
        query=user_message,
        filter={"category": "crisis", "priority": "critical"},
        top_k=1  # Только один самый релевантный протокол
    )
```

---

## 🎯 Использование RAG-системы

### Архитектура потока

```
User Message
    ↓
1. Crisis Detection (keywords: "суицид", "умереть", etc.)
    ↓
    YES → crisis/01_crisis_protocols.md (HIGHEST PRIORITY)
    NO ↓
2. Context Analysis
    - Time of day
    - Day of week
    - User segment
    - Mood history
    - Language
    ↓
3. Vector Search
    - Query: user message + context
    - Filters: audience, language, category
    - Top K: 3-5 chunks
    ↓
4. Personalization Layer
    - Load: core/02_personalization_rules.md
    - User history from vector DB
    - Past joys if mood negative
    ↓
5. Response Generation
    - Combine: support + questions + techniques + personalization
    - Adapt: tone, complexity, formality
    - Add: relevant past joy reminder if applicable
    ↓
6. Store Interaction
    - Metadata: sentiment, themes, time, etc.
    - Vector embedding for future retrieval
```

---

## 📊 Chunk Size Guide

### Small chunks (200-400 tokens)
- **Когда использовать:** Quick lookups, specific techniques, individual questions
- **Примеры:** 
  - Одна техника заземления 5-4-3-2-1
  - 5-7 вопросов для утра
  - Валидация одного чувства

### Medium chunks (400-800 tokens)
- **Когда использовать:** Context with examples, protocols, audience-specific approaches
- **Примеры:**
  - Полный протокол ответа на кризис
  - Раздел о работе с импостерским синдромом
  - Философия бота с научным обоснованием

### Large chunks (800-1500 tokens)
- **Когда использовать:** Comprehensive rules, personalization logic, multi-language content
- **Примеры:**
  - core/02_personalization_rules.md (весь файл)
  - Все языки для одной техники

### Рекомендация по chunking:
```python
# Стратегия разбивки
if file.chunk_size == "small":
    strategy = "по заголовкам ## (каждый раздел отдельно)"
elif file.chunk_size == "medium":
    strategy = "по заголовкам ### (группы разделов)"
else:  # large
    strategy = "по заголовкам # (топ-левел секции)"

# Сохраняй метаданные для каждого chunk
chunk_metadata = {
    "file": filename,
    "category": yaml_frontmatter.category,
    "section": header_path,  # "RU: Вопросы для молодых мам"
    "languages": languages_in_chunk,  # ["ru", "en"]
    "audience": yaml_frontmatter.audience
}
```

---

## 🔍 Примеры запросов и ответов RAG

### Пример 1: Утреннее приветствие

**Input:**
```
User: (молчит, утро 8:00, сегмент: anxiety_sufferers)
System: время задать вопрос
```

**RAG Query:**
```python
context = {
    "time": "morning",
    "user_segment": "anxiety_sufferers",
    "language": "ru",
    "mood_last_3_days": [4, 5, 4]  # Средне
}

results = vector_search(
    query="утренний вопрос для тревожного пользователя",
    filter={
        "category": "questions",
        "audience": {"$in": ["all", "anxiety_sufferers"]},
        "languages": "ru"
    },
    top_k=3
)
```

**Retrieved chunks:**
1. `questions/01_diverse_questions.md` → "Утренние вопросы (6:00-10:00)"
2. `support/01_anxiety_support.md` → "Когда день был обычным"
3. `core/02_personalization_rules.md` → "Утро (6:00-10:00): тон мягкий"

**Generated response:**
```
"Доброе утро! Что приятного было в твоем пробуждении сегодня?"
```

---

### Пример 2: Пользователь выражает тревогу

**Input:**
```
User: "Меня захлестывает паника, сердце колотится, не могу дышать"
Time: 15:30, сегмент: anxiety_sufferers
```

**RAG Query:**
```python
# Сначала проверка кризиса
crisis_detected = False  # паника != суицид

results = vector_search(
    query="паническая атака тревога сердцебиение техника помощи",
    filter={
        "category": {"$in": ["support", "techniques"]},
        "audience": {"$in": ["all", "anxiety_sufferers"]},
        "languages": "ru",
        "tags": {"$in": ["panic", "breathing", "grounding"]}
    },
    top_k=4
)
```

**Retrieved chunks:**
1. `techniques/01_anxiety_techniques.md` → "Техника 5-4-3-2-1 (Заземление)"
2. `techniques/01_anxiety_techniques.md` → "Дыхательная техника Квадрат"
3. `support/01_anxiety_support.md` → "Когда пользователь выражает сильную тревогу"
4. `core/02_personalization_rules.md` → "Адаптация под паттерны настроения"

**Generated response:**
```
"Твоя тревога реальна, и я понимаю, как это тяжело, когда она захлестывает. 

Прямо сейчас давай попробуем технику 5-4-3-2-1 вместе. Она помогает мозгу вернуться в настоящий момент:

Назови (можешь просто подумать):
- 5 вещей, которые ты видишь
- 4 вещи, которых ты касаешься
- 3 звука, которые ты слышишь
- 2 запаха вокруг тебя
- 1 вкус во рту

Это поможет успокоить амигдалу - центр страха в мозге.

Также попробуй дыхание квадратом:
Вдох 4 счета → Задержка 4 → Выдох 4 → Задержка 4

Ты здесь? Напиши мне когда попробуешь."
```

---

### Пример 3: Пользователь грустит, ничего хорошего

**Input:**
```
User: "Ничего хорошего сегодня не было. Все плохо."
Time: 19:00, настроение последние 4 дня: [3, 2, 3, 2] (депрессивный эпизод)
История: 2 недели назад радовался закату
```

**RAG Query:**
```python
# Основной поиск
results = vector_search(
    query="ничего хорошего депрессия поддержка",
    filter={
        "category": "support",
        "audience": {"$in": ["all", "anxiety_sufferers"]},
        "languages": "ru"
    },
    top_k=3
)

# Дополнительный поиск прошлых радостей
past_joys = vector_search(
    user_history,
    query="радость счастье красиво",
    filter={"sentiment": "positive"},
    top_k=3
)
```

**Retrieved chunks:**
1. `support/01_anxiety_support.md` → "Когда пользователь говорит что ничего хорошего не было → Вариант 3: Напоминание о прошлом"
2. `core/02_personalization_rules.md` → "Когда пользователь грустит → использование векторного поиска"
3. Past joy: "2 weeks ago: 'Видел красивейший закат, все небо было в оранжевых красках'"

**Generated response:**
```
"Я слышу тебя. Сегодня был тяжелый день, и это нормально — не каждый день легкий. Твои чувства важны и имеют право быть.

Я помню, что две недели назад ты рассказывал о красивейшем закате, как все небо было в оранжевых красках. Тогда это тебя по-настоящему тронуло.

Сейчас темно, но я знаю — свет вернется. Он всегда возвращается. Хорошие моменты не исчезают навсегда, они просто иногда прячутся за тучами.

А пока я с тобой."
```

---

## 🌍 Мультиязычность

### Структура мультиязычного контента

Каждый файл содержит контент на **всех поддерживаемых языках** в следующем формате:

```markdown
## RU: Заголовок раздела
[Контент на русском]

---

## EN: Section Header
[Content in English]

---

## ES: Encabezado de sección
[Contenido en español]

[etc.]
```

### Стратегия извлечения языка

```python
def extract_language_section(chunk_text, target_language):
    """
    Извлекает нужный язык из chunk с мультиязычным контентом
    """
    lang_markers = {
        "ru": "## RU:",
        "en": "## EN:",
        "uk": "## UK:",
        "es": "## ES:",
        "fr": "## FR:",
        "de": "## DE:",
        "he": "## HE:",
        "it": "## IT:",
        "pl": "## PL:",
        "cs": "## CS:",
        "hu": "## HU:"
    }
    
    marker = lang_markers.get(target_language, "## EN:")
    
    # Найти секцию для целевого языка
    if marker in chunk_text:
        start = chunk_text.find(marker)
        # Найти следующий language marker или конец
        next_markers = [chunk_text.find(m, start + 1) 
                       for m in lang_markers.values() 
                       if chunk_text.find(m, start + 1) != -1]
        end = min(next_markers) if next_markers else len(chunk_text)
        
        return chunk_text[start:end].replace(marker, "").strip()
    
    # Fallback на английский
    return extract_language_section(chunk_text, "en")
```

### Смешение языков (code-switching)

Если пользователь использует Ruglish или смешивает языки:

```python
if user.language_pattern == "code_switching":
    # Разреши английские вставки в русском ответе
    response_lang = user.primary_language  # "ru"
    allow_code_switching = True
    
    # Пример: "Какой moment сегодня был wow?"
```

---

## 🎨 Tone и Style адаптация

### Tone Guidelines по категориям

| Category | Default Tone | Adaptations |
|----------|-------------|-------------|
| core | warm, empathetic | - |
| support | gentle, validating | Depression: extra gentle / Positive mood: encouraging |
| techniques | practical, step-by-step | Crisis: calm, directive |
| questions | curious, warm | Morning: soft / Evening: reflective |
| audience_specific | varies | Elderly: respectful, patient / Mothers: non-judgmental |
| crisis | calm, directive, compassionate | ALWAYS priority |

### Formality levels

```python
formality = {
    "elderly_ru": "Вы",  # Всегда формально
    "elderly_other": "formal_pronouns",
    "professional": "respectful",
    "young_mothers": "supportive_informal",
    "default": "friendly_informal"
}

user.formality = detect_formality(user.messages)
if user.explicitly_requests("ты"):
    user.formality = "informal"
```

---

## 🚨 Кризисная детекция

### Trigger keywords (по языкам)

```python
CRISIS_KEYWORDS = {
    "ru": ["суицид", "самоубийство", "хочу умереть", "покончить с собой", 
           "лучше бы меня не было", "не хочу жить", "порезать себя"],
    "en": ["suicide", "kill myself", "want to die", "end it all", 
           "better off dead", "cut myself", "self harm"],
    "es": ["suicidio", "matarme", "quiero morir", "terminar todo"],
    "de": ["Selbstmord", "umbringen", "sterben wollen"],
    "he": ["התאבדות", "להתאבד", "למות"],
    # etc.
}

def detect_crisis(user_message):
    for keyword in CRISIS_KEYWORDS[user.language]:
        if keyword in user_message.lower():
            return True
    return False

if detect_crisis(message):
    # HIGHEST PRIORITY
    protocol = load_content("crisis/01_crisis_protocols.md")
    response = generate_crisis_response(protocol, user.language, user.country)
    log_crisis_event(user_id, message, response)
```

### Приоритет кризиса

```
CRISIS (priority: critical) > все остальное
```

Если детектирован кризис:
1. Немедленно загрузить `crisis/01_crisis_protocols.md`
2. Извлечь протокол для языка и страны пользователя
3. Предоставить ресурсы (горячие линии)
4. Логировать событие для возможного human review

---

## 📈 Метрики качества RAG

### Что измерять

```python
rag_metrics = {
    "relevance_score": 0.0,  # Насколько релевантен retrieved chunk
    "diversity_score": 0.0,  # Разнообразие источников
    "personalization_score": 0.0,  # Использованы ли данные пользователя
    "crisis_detection_accuracy": 0.0,  # False positives/negatives
    "language_accuracy": 0.0,  # Правильный язык в ответе
    "tone_appropriateness": 0.0,  # Соответствие тона ситуации
}
```

### A/B тестирование

```python
# Вариант A: только vector search
# Вариант B: vector search + user history
# Вариант C: vector search + user history + personalization rules

# Измерить:
# - User engagement (отвечает ли)
# - Sentiment improvement (настроение улучшается?)
# - Retention (возвращается ли)
```

---

## 🔧 Техническая интеграция

### Рекомендуемый стек

**Vector Database:**
- Pinecone / Weaviate / Qdrant
- Embedding model: `multilingual-e5-large` или `OpenAI text-embedding-3-large`

**LLM для генерации:**
- GPT-4 / Claude 3.5 Sonnet / Gemini 1.5 Pro
- Системный промпт должен включать персонализацию

**Хранение истории:**
- PostgreSQL для structured data (user profiles, metadata)
- Vector DB для embeddings диалогов

### Пример pipeline

```python
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import ChatOpenAI

# 1. Инициализация
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = Pinecone(index_name="mindsethappybot-kb", embeddings=embeddings)

# 2. User message
user_msg = "Мне тревожно сегодня"
context = get_user_context(user_id)  # time, segment, mood_history

# 3. Crisis check
if detect_crisis(user_msg):
    return handle_crisis(user_msg, context)

# 4. Vector search
filter_dict = {
    "category": {"$in": ["support", "techniques", "questions"]},
    "audience": {"$in": ["all", context["segment"]]},
    "languages": context["language"]
}
docs = vectorstore.similarity_search(
    user_msg, 
    k=5,
    filter=filter_dict
)

# 5. Personalization
personalization_rules = load_personalization_rules()
user_history = get_user_history(user_id, days=14)

if context["mood_trend"] == "declining":
    past_joys = vector_search(user_history, "радость счастье", k=3)
else:
    past_joys = None

# 6. Combine context
combined_context = f"""
Релевантный контент из базы знаний:
{format_docs(docs)}

Правила персонализации:
{personalization_rules}

История пользователя (если релевантно):
{past_joys if past_joys else "N/A"}

Контекст:
- Время: {context['time']}
- Сегмент: {context['segment']}
- Настроение последние 3 дня: {context['mood_last_3_days']}
- Язык: {context['language']}
"""

# 7. Generate
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
response = llm(combined_context + f"\n\nСообщение пользователя: {user_msg}")

# 8. Store interaction
store_interaction(user_id, user_msg, response, metadata=context)
```

---

## 📝 Как добавлять новый контент

### Шаг 1: Создать файл

```bash
touch knowledge_base/[category]/[number]_[name].md
```

### Шаг 2: Добавить YAML front matter

```yaml
---
category: [выбрать из существующих]
type: [описательный тип]
languages: [список языков]
audience: [all или специфический сегмент]
tone: [описание тона]
use_case: [когда использовать]
chunk_size: [small | medium | large]
tags: [релевантные, теги]
---
```

### Шаг 3: Структурировать контент

```markdown
# Заголовок файла

## RU: Раздел на русском
[контент]

---

## EN: Section in English
[content]

---

[остальные языки...]
```

### Шаг 4: Добавить в векторную БД

```python
# Chunking
chunks = chunk_markdown_file(filepath, strategy=chunk_size)

# Embedding
for chunk in chunks:
    embedding = embed_text(chunk["text"])
    metadata = {
        **chunk["metadata"],
        "file": filepath,
        "section": chunk["header_path"]
    }
    vectorstore.add(
        text=chunk["text"],
        embedding=embedding,
        metadata=metadata
    )
```

---

## ⚠️ Важные ограничения и предупреждения

### Что бот НЕ может

1. **Не заменяет терапию** - всегда напоминать пользователям
2. **Не диагностирует** - не использовать медицинские термины как диагнозы
3. **Не дает лекарственные советы** - только профессиональная помощь
4. **Не гарантирует безопасность** - при кризисе направлять к специалистам

### Этические границы

```python
NEVER_DO = [
    "Давать медицинские диагнозы",
    "Рекомендовать конкретные лекарства",
    "Заменять терапевта",
    "Обещать 'вылечить' депрессию/тревогу",
    "Минимизировать боль ('просто думай позитивно')",
    "Guilt-trip за отсутствие или негатив"
]

ALWAYS_DO = [
    "Валидировать чувства",
    "Предлагать профессиональную помощь при необходимости",
    "Уважать границы пользователя",
    "Признавать ограничения AI",
    "Защищать конфиденциальность"
]
```

---

## 🔄 Обновление базы знаний

### Версионирование

```
v1.0 - Initial release (January 2026)
- 11 languages
- 4 audience segments
- Crisis protocols for 15 countries
```

### Roadmap для v1.1

- [ ] Добавить поддержку арабского и португальского
- [ ] Расширить контент для хронических заболеваний
- [ ] Добавить LGBTQ+ специфический контент
- [ ] Интеграция с медитацией и майндфулнесс практиками

### Как контрибьютить

1. Создать Issue с предложением нового контента
2. Следовать структуре существующих файлов
3. Добавить ВСЕ поддерживаемые языки (минимум RU + EN)
4. Протестировать на релевантность через RAG
5. Submit Pull Request

---

## 📞 Поддержка и вопросы

**Разработчик:** aBH Team  
**Email:** [your-email]  
**Проект:** MINDSETHAPPYBOT  

**Документация:** [GitHub/Documentation]  
**Issues:** [GitHub/Issues]

---

## 📄 Лицензия

Эта база знаний создана для MINDSETHAPPYBOT проекта.  
Контент предназначен для поддержки ментального здоровья и не должен использоваться во вред.

**Важно:** Всегда консультируйтесь с профессиональными психологами и психиатрами при разработке ментального здоровья инструментов.

---

**Последнее обновление:** January 16, 2026  
**Версия:** 1.0
