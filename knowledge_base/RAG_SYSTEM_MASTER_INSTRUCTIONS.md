---
type: meta_instructions
category: system
priority: CRITICAL
audience: system
use_case: rag_orchestration
---

# RAG System Master Instructions для MINDSETHAPPYBOT

## Архитектура базы знаний

### Структура директорий:
```
/knowledge_base/
├── core/                    # Философия, культурные адаптации
├── support/                 # Эмоциональная поддержка
├── techniques/              # Практические техники (дыхание, заземление)
├── questions/               # Банк вопросов (разнообразие, сезонность)
├── crisis/                  # Кризисные протоколы
└── audience_specific/       # Контент для специфических аудиторий
```

### Приоритеты загрузки (от высшего к низшему):

**1. КРИТИЧЕСКИЙ (immediate action):**
- `/crisis/01_crisis_protocols.md` — суицидальные мысли, самоповреждение
- Priority: 100
- Trigger: суицидальные keywords
- Action: немедленное извлечение, прерывание обычного диалога

**2. ВЫСОКИЙ (urgent support):**
- `/techniques/01_anxiety_techniques.md` — паника, сильная тревога
- `/support/01_anxiety_support.md` — эмоциональная валидация
- Priority: 80
- Trigger: "паника", "не могу дышать", "сердце колотится"
- Action: быстрое извлечение техник

**3. СРЕДНИЙ (contextual support):**
- `/audience_specific/*` — специфика аудитории
- `/core/02_cultural_adaptation.md` — культурные нюансы
- Priority: 60
- Trigger: определенная аудитория (пожилые, мамы, профессионалы)
- Action: адаптация тона и содержания

**4. БАЗОВЫЙ (standard interaction):**
- `/core/01_bot_philosophy.md` — философия бота
- `/questions/*` — вопросы для пользователя
- Priority: 40
- Trigger: обычный диалог
- Action: стандартное извлечение

**5. ДОПОЛНИТЕЛЬНЫЙ (enhancement):**
- `/questions/02_seasonal_contextual.md` — сезонные адаптации
- Priority: 20
- Trigger: текущий сезон/праздник
- Action: subtle улучшение, не основа

---

## Workflow обработки сообщения пользователя

### Шаг 1: Анализ сообщения (Triage)

```python
def analyze_message(user_message, user_history):
    # 1. Детекция кризиса (HIGHEST priority)
    if detect_crisis_keywords(user_message):
        return {
            "priority": "CRITICAL",
            "chunks_needed": ["crisis/01_crisis_protocols.md"],
            "action": "immediate_intervention",
            "tone": "calm_direct"
        }
    
    # 2. Детекция острой тревоги
    if detect_anxiety_attack(user_message):
        return {
            "priority": "HIGH",
            "chunks_needed": [
                "techniques/01_anxiety_techniques.md",
                "support/01_anxiety_support.md"
            ],
            "action": "provide_techniques",
            "tone": "calm_supportive"
        }
    
    # 3. Детекция специфической аудитории
    audience = detect_audience(user_message, user_history)
    if audience:
        return {
            "priority": "MEDIUM",
            "chunks_needed": [
                f"audience_specific/{audience}.md",
                "core/02_cultural_adaptation.md"
            ],
            "action": "adapt_tone",
            "tone": audience_specific_tone(audience)
        }
    
    # 4. Стандартный диалог
    return {
        "priority": "BASIC",
        "chunks_needed": [
            "core/01_bot_philosophy.md",
            "questions/01_diverse_questions.md"
        ],
        "action": "ask_question",
        "tone": "warm_curious"
    }
```

### Шаг 2: Извлечение релевантных chunks

```python
def retrieve_chunks(query, priority, language):
    # Vector search с фильтрами
    results = vector_db.search(
        query=query,
        filters={
            "language": language,
            "priority": priority,
            "audience": detected_audience
        },
        top_k=5,
        threshold=0.7
    )
    
    # Reranking по приоритету
    results = rerank_by_priority(results)
    
    return results[:3]  # Top 3 chunks
```

### Шаг 3: Формирование контекста для LLM

```python
def build_context(chunks, user_history, user_metadata):
    context = {
        "system_role": "Empathetic gratitude bot",
        "knowledge": chunks,
        "user_history": user_history[-10:],  # Last 10 interactions
        "user_metadata": {
            "language": user_metadata["language"],
            "age_group": user_metadata.get("age_group"),
            "audience_type": user_metadata.get("audience_type"),
            "formality": user_metadata.get("formality", "informal")
        },
        "current_context": {
            "season": get_current_season(),
            "time_of_day": get_time_of_day(),
            "day_of_week": get_day_of_week()
        }
    }
    return context
```

### Шаг 4: Генерация ответа

```python
def generate_response(context, user_message):
    prompt = f"""
You are MINDSETHAPPYBOT, an empathetic AI friend helping users find joy.

KNOWLEDGE BASE:
{format_chunks(context["knowledge"])}

USER HISTORY:
{format_history(context["user_history"])}

USER PROFILE:
- Language: {context["user_metadata"]["language"]}
- Audience: {context["user_metadata"].get("audience_type", "general")}
- Formality: {context["user_metadata"]["formality"]}

CURRENT CONTEXT:
- Season: {context["current_context"]["season"]}
- Time: {context["current_context"]["time_of_day"]}

USER MESSAGE: {user_message}

INSTRUCTIONS:
1. Use knowledge base to inform response
2. Adapt tone based on user profile
3. Apply cultural nuances from knowledge base
4. If crisis detected - follow crisis protocol EXACTLY
5. Never repeat same question twice in a row
6. Use seasonal context subtly

Generate response:
"""
    
    response = llm.generate(prompt)
    return response
```

---

## Детекция триггеров (Keywords)

### Кризисные (CRITICAL priority):

**Суицидальные (все языки):**
```python
SUICIDE_KEYWORDS = {
    "ru": ["хочу умереть", "покончить с собой", "суицид", "не хочу жить"],
    "en": ["want to die", "kill myself", "suicide", "end it all"],
    "es": ["quiero morir", "suicidarme", "acabar con todo"],
    "fr": ["veux mourir", "me suicider", "en finir"],
    "de": ["sterben", "Selbstmord", "umbringen"],
    "he": ["למות", "התאבדות"],
    "it": ["voglio morire", "suicidarmi"],
    "pl": ["chcę umrzeć", "samobójstwo"],
    "cs": ["chci zemřít", "sebevražda"],
    "hu": ["meg akarok halni", "öngyilkosság"]
}
```

**Самоповреждение:**
```python
SELF_HARM_KEYWORDS = {
    "ru": ["режу себя", "порезы", "самоповреждение"],
    "en": ["cutting myself", "self-harm", "hurting myself"],
    "es": ["me corto", "autolesión"],
    # etc
}
```

### Тревога (HIGH priority):

```python
ANXIETY_KEYWORDS = {
    "ru": ["паника", "не могу дышать", "сердце колотится", "задыхаюсь"],
    "en": ["panic", "can't breathe", "heart racing", "anxiety attack"],
    "es": ["pánico", "no puedo respirar", "corazón late"],
    # etc
}
```

### Аудитория (MEDIUM priority):

```python
AUDIENCE_KEYWORDS = {
    "elderly": {
        "ru": ["лет", "пенсия", "внуки", "одиночество"],
        "en": ["years old", "retirement", "grandchildren", "lonely"],
    },
    "postpartum": {
        "ru": ["ребенок", "младенец", "роды", "плохая мать"],
        "en": ["baby", "infant", "birth", "bad mother"],
    },
    "burnout": {
        "ru": ["работа", "выгорание", "дедлайн", "проект"],
        "en": ["work", "burnout", "deadline", "project"],
    }
}
```

---

## Языковая детекция и адаптация

### Language Detection:

```python
def detect_language(message):
    # Use fasttext or langdetect
    lang = langdetect.detect(message)
    
    # Map to supported languages
    supported = ["ru", "en", "uk", "es", "fr", "de", "he", "it", "pl", "cs", "hu"]
    
    if lang in supported:
        return lang
    else:
        return "en"  # Default to English
```

### Cultural Adaptation:

```python
def apply_cultural_adaptation(language, age, response):
    # Load cultural rules
    cultural_chunk = load_chunk("core/02_cultural_adaptation.md", language)
    
    # Apply formality
    if age and age > 50:
        if language == "ru":
            response = convert_to_formal_you(response)  # ты → Вы
        elif language == "de":
            response = convert_to_sie(response)  # du → Sie
    
    # Apply cultural tone
    response = apply_cultural_tone(response, language, cultural_chunk)
    
    return response
```

---

## Embedding стратегия

### Модель:
```python
model = "multilingual-e5-large"  # Supports 100+ languages
# Alternative: "paraphrase-multilingual-mpnet-base-v2"
```

### Chunk размеры:
- **Small chunks (150-300 tokens):** Crisis protocols, techniques
- **Medium chunks (300-500 tokens):** Support content, questions
- **Large chunks (500-800 tokens):** Philosophy, cultural guides

### Metadata для каждого chunk:

```python
chunk_metadata = {
    "category": "support|techniques|questions|crisis|core|audience_specific",
    "priority": 20-100,  # 100 = critical
    "languages": ["ru", "en", "uk", ...],
    "audience": ["all"|"elderly"|"postpartum"|"professionals"],
    "tone": "warm|calm|directive|validating",
    "use_case": "crisis|anxiety|daily_check_in|...",
    "tags": ["anxiety", "breathing", "grounding", ...],
    "file_path": "core/01_bot_philosophy.md",
    "chunk_id": "core_philosophy_ru_001"
}
```

### Indexing strategy:

```python
# Separate indexes by priority
indexes = {
    "crisis": [],      # CRITICAL priority chunks
    "high": [],        # HIGH priority chunks
    "medium": [],      # MEDIUM priority chunks
    "basic": []        # BASIC priority chunks
}

# Search order:
# 1. Check crisis index first (always)
# 2. If no crisis, check appropriate priority index
# 3. Combine results with basic index for context
```

---

## Vector Database Schema (ChromaDB / Pinecone / Qdrant)

```python
collection_schema = {
    "name": "mindsethappybot_knowledge",
    "embedding_function": "multilingual-e5-large",
    "metadata_schema": {
        "category": "string",
        "priority": "int",
        "language": "string",
        "audience": "string",
        "file_path": "string",
        "chunk_id": "string"
    },
    "distance_metric": "cosine"
}
```

---

## Персонализация на основе истории

### Данные пользователя для контекста:

```python
user_profile = {
    "user_id": "uuid",
    "language": "ru",
    "detected_audience": "professionals",  # elderly|postpartum|professionals|general
    "age_group": "30-40",  # optional
    "formality_preference": "informal",  # informal|formal
    "conversation_history": [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "user_message": "Сегодня был тяжелый день",
            "bot_response": "Я слышу тебя...",
            "mood_detected": "negative",
            "topic": "work_stress"
        }
    ],
    "past_joys": [
        {
            "timestamp": "2024-01-10T18:00:00Z",
            "joy": "Прогулка в парке с собакой",
            "embedding": [0.1, 0.2, ...]  # Vector for retrieval
        }
    ],
    "preferences": {
        "question_frequency": "every_3_hours",
        "preferred_topics": ["nature", "family", "work"],
        "avoided_topics": []
    }
}
```

### Использование past_joys:

```python
def retrieve_past_joy(user_id, current_mood):
    if current_mood == "negative":
        # Vector search в past_joys
        similar_joys = vector_search(
            user_profile["past_joys"],
            query="счастливый момент",
            top_k=1
        )
        return similar_joys[0]
    return None
```

---

## Пример полного workflow:

```
USER: "Не могу дышать, сердце бешено колотится"

↓

STEP 1: Analyze
- Language: RU
- Crisis: NO (not suicidal)
- Anxiety attack: YES
- Priority: HIGH

↓

STEP 2: Retrieve chunks
- techniques/01_anxiety_techniques.md (RU section)
- support/01_anxiety_support.md (RU section)
- Top k=3 chunks

↓

STEP 3: Build context
{
    "knowledge": [chunk1, chunk2, chunk3],
    "user_history": [...],
    "priority": "HIGH",
    "action": "provide_breathing_technique"
}

↓

STEP 4: Generate response
"Я понимаю, это страшно. Ты в безопасности, это паническая атака и она пройдет.
Давай попробуем вместе дыхательную технику:

Вдох 4 счета... 1...2...3...4...
Задержка 4 счета... 1...2...3...4...
Выдох 4 счета... 1...2...3...4...

Повтори со мной 4 раза. Я с тобой."

↓

STEP 5: Log interaction
- Save to user_history
- Update mood: "anxiety_attack"
- Check if follow-up needed in 30 min
```

---

## Обновление базы знаний

### Процесс добавления новых chunks:

1. **Создай .md файл** в соответствующей категории
2. **Добавь metadata** в header (YAML front matter)
3. **Структурируй контент** по языкам (RU, EN, ES, etc)
4. **Добавь технические инструкции** в конце файла
5. **Re-embed** файл в vector DB
6. **Тестируй** на примерах запросов

### Формат нового файла:

```markdown
---
category: support
type: new_topic
languages: [ru, en]
audience: all
tone: warm
use_case: specific_situation
chunk_size: medium
priority: 60
tags: [tag1, tag2]
---

# Название на русском

## RU: Раздел 1
Контент...

## EN: Section 1
Content...

## Технические инструкции для RAG
### Embedding стратегия:
...
```

---

## Мониторинг и улучшение

### Metrics для отслеживания:

```python
metrics = {
    "retrieval_accuracy": 0.0,  # Были ли извлечены правильные chunks?
    "response_quality": 0.0,    # User feedback (thumbs up/down)
    "crisis_detection_rate": 0.0,  # % правильно обнаруженных кризисов
    "average_chunks_used": 0.0,    # Сколько chunks в среднем
    "language_distribution": {},   # Какие языки используются
    "audience_distribution": {}    # Какие аудитории
}
```

### A/B testing chunks:

```python
# Test different versions of chunks
chunk_versions = {
    "support/01_anxiety_support.md": {
        "version_a": "empathetic_long",
        "version_b": "empathetic_concise"
    }
}

# Track which performs better based on user feedback
```

---

## Заключение

Эта RAG-система designed для:
✅ Мультиязычной поддержки (11 языков)
✅ Культурной адаптации
✅ Приоритизации кризисов
✅ Персонализации на основе истории
✅ Сезонной и контекстной релевантности

**Key principles:**
1. Safety first (кризисы = highest priority)
2. Cultural sensitivity (адаптация под культуру)
3. Personalization (история пользователя важна)
4. Variety (никогда не повторяй вопросы)
5. Empathy (всегда валидируй чувства)
