# 📋 GIT WORKFLOW - Content Expansion Branch

## 🎯 Цель

Создать feature branch с расширением контента и многоязычной поддержкой, протестировать, затем слить с main.

---

## 📂 Шаг 1: Создание ветки

```bash
# Перейти в корень проекта
cd /path/to/3hours

# Убедиться что на актуальной main
git checkout main
git pull origin main

# Создать feature branch
git checkout -b feature/content-expansion-multilingual

# Проверить что на новой ветке
git branch
# Должно показать: * feature/content-expansion-multilingual
```

---

## 📥 Шаг 2: Копирование новых файлов

```bash
# Скопировать новые файлы из expansion пакета
# (Замени /path/to/expansion на реальный путь)

# Вопросы
cp /path/to/mindsethappybot-expansion/knowledge_base/questions/03_emotions_deep_dive.md \
   knowledge_base/questions/

cp /path/to/mindsethappybot-expansion/knowledge_base/questions/04_relationships_social.md \
   knowledge_base/questions/

cp /path/to/mindsethappybot-expansion/knowledge_base/questions/05_self_care_body.md \
   knowledge_base/questions/

cp /path/to/mindsethappybot-expansion/knowledge_base/questions/06_creativity_hobbies.md \
   knowledge_base/questions/

cp /path/to/mindsethappybot-expansion/knowledge_base/questions/07_nature_environment.md \
   knowledge_base/questions/

cp /path/to/mindsethappybot-expansion/knowledge_base/questions/08_gratitude_practice.md \
   knowledge_base/questions/

cp /path/to/mindsethappybot-expansion/knowledge_base/questions/09_reflection_growth.md \
   knowledge_base/questions/

# Техники
cp /path/to/mindsethappybot-expansion/knowledge_base/techniques/02_mindfulness_meditation.md \
   knowledge_base/techniques/

# Документация
cp /path/to/mindsethappybot-expansion/README.md \
   docs/CONTENT_EXPANSION_README.md
```

---

## ✅ Шаг 3: Проверка изменений

```bash
# Посмотреть какие файлы изменились
git status

# Должно показать:
# Untracked files:
#   knowledge_base/questions/03_emotions_deep_dive.md
#   knowledge_base/questions/04_relationships_social.md
#   ...
```

---

## 💾 Шаг 4: Staging и Commit

```bash
# Добавить все новые файлы
git add knowledge_base/questions/03_emotions_deep_dive.md
git add knowledge_base/questions/04_relationships_social.md
git add knowledge_base/questions/05_self_care_body.md
git add knowledge_base/questions/06_creativity_hobbies.md
git add knowledge_base/questions/07_nature_environment.md
git add knowledge_base/questions/08_gratitude_practice.md
git add knowledge_base/questions/09_reflection_growth.md
git add knowledge_base/techniques/02_mindfulness_meditation.md
git add docs/CONTENT_EXPANSION_README.md

# Проверить staging
git status

# Commit
git commit -m "feat: Add 330+ new questions and mindfulness techniques

- Add 7 new question categories (emotions, relationships, self-care, creativity, nature, gratitude, reflection)
- Add mindfulness and meditation techniques
- Support for RU, EN, UK (ready for multilingual expansion)
- Total: 330+ new questions across all categories

Closes #[issue-number] (if applicable)"
```

---

## 🔄 Шаг 5: Загрузка в БД и тестирование

```bash
# Загрузить новый контент
python scripts/load_knowledge_base_content.py --category questions
python scripts/load_knowledge_base_content.py --category techniques

# Индексация
python -m src.knowledge_indexer

# Запустить бота для тестирования
python -m src.main

# Тестировать в Telegram:
# - Отправить /start
# - Попросить вопрос: "Задай мне вопрос"
# - Проверить разнообразие (задать 10 раз, не должны повторяться)
```

---

## 📤 Шаг 6: Push и создание Pull Request

```bash
# Push ветки на remote
git push origin feature/content-expansion-multilingual

# Если это первый push этой ветки:
git push -u origin feature/content-expansion-multilingual
```

### На GitHub:

1. Перейти в репозиторий
2. Кликнуть "Pull Requests" → "New Pull Request"
3. Base: `main` ← Compare: `feature/content-expansion-multilingual`
4. Заполнить:

**Title:**
```
feat: Content Expansion - 330+ questions + Multilingual support
```

**Description:**
```markdown
## 📋 Summary
This PR adds significant content expansion to the knowledge base:
- 7 new question categories (330+ questions)
- New mindfulness techniques
- Ready for multilingual expansion (9-26 languages)

## 📊 Changes
- **Questions:** 50 → 380+ (+660%)
- **Categories:** 2 → 9 (+350%)
- **Languages:** RU, EN, UK (ready for DE, FR, ES, IT, PT, NL, etc.)

## ✅ Testing
- [x] All new questions loaded into DB
- [x] Indexing successful
- [x] Bot runs without errors
- [x] Questions don't repeat frequently
- [x] RAG retrieves relevant content

## 📝 Files Changed
- `knowledge_base/questions/03_emotions_deep_dive.md`
- `knowledge_base/questions/04_relationships_social.md`
- `knowledge_base/questions/05_self_care_body.md`
- `knowledge_base/questions/06_creativity_hobbies.md`
- `knowledge_base/questions/07_nature_environment.md`
- `knowledge_base/questions/08_gratitude_practice.md`
- `knowledge_base/questions/09_reflection_growth.md`
- `knowledge_base/techniques/02_mindfulness_meditation.md`
- `docs/CONTENT_EXPANSION_README.md`

## 🔄 Next Steps (Optional - Фаза 2)
- [ ] Multilingual integration (Tier 1-2: 9 languages)
- [ ] Full multilingual (26 languages)

## 📸 Screenshots
(Add screenshots from admin panel showing new questions count)
```

---

## 🧪 Шаг 7: Code Review и Testing

После создания PR:

1. **Self-review:** Просмотри изменения на GitHub
2. **Request review:** Попроси кого-то проверить (если есть команда)
3. **CI/CD:** Дождись прохождения тестов (если настроены)
4. **Manual testing:** Попроси других протестировать ветку

```bash
# Коллеги могут checkout твою ветку:
git fetch origin
git checkout feature/content-expansion-multilingual

# И протестировать локально
python -m src.main
```

---

## ✅ Шаг 8: Merge в main

После approval:

### Опция A: Через GitHub UI
1. На странице PR кликнуть "Merge pull request"
2. Выбрать "Squash and merge" или "Create a merge commit"
3. Confirm merge

### Опция B: Через командную строку
```bash
# Вернуться на main
git checkout main

# Pull последние изменения
git pull origin main

# Merge feature branch
git merge feature/content-expansion-multilingual

# Push в main
git push origin main
```

---

## 🧹 Шаг 9: Cleanup

```bash
# Удалить локальную ветку (опционально)
git branch -d feature/content-expansion-multilingual

# Удалить remote ветку (опционально)
git push origin --delete feature/content-expansion-multilingual
```

---

## 🔄 Шаг 10: Деплой

```bash
# На продакшн сервере:
git pull origin main

# Загрузить новый контент в прод БД
python scripts/load_knowledge_base_content.py --category questions
python scripts/load_knowledge_base_content.py --category techniques

# Переиндексировать
python -m src.knowledge_indexer

# Restart бота
systemctl restart 3hours-bot  # или как у тебя настроено
```

---

## 📊 Проверка после деплоя

```sql
-- Подключиться к прод БД
psql -U your_user -d 3hours_db

-- Проверить количество вопросов
SELECT 
    SUBSTRING(title FROM '(\d+)_') as file_num,
    title,
    COUNT(*) as chunks
FROM knowledge_base
WHERE category = 'questions'
GROUP BY title
ORDER BY file_num;

-- Должно показать файлы 01-09 (9 файлов вопросов)
```

---

## 🎉 Done!

Поздравляю! Ты успешно:
- ✅ Создал feature branch
- ✅ Добавил 330+ новых вопросов
- ✅ Протестировал изменения
- ✅ Смержил в main
- ✅ Задеплоил на прод

**Результат:** Бот теперь в 7 раз разнообразнее! 🚀

---

## 🆘 Troubleshooting

### Merge conflict
```bash
# Обновить ветку от main
git checkout feature/content-expansion-multilingual
git pull origin main

# Разрешить конфликты вручную
# После разрешения:
git add .
git commit -m "fix: Resolve merge conflicts"
git push origin feature/content-expansion-multilingual
```

### Accidentally committed to main
```bash
# Откатить последний commit (не потеряв изменения)
git reset --soft HEAD~1

# Создать правильную ветку
git checkout -b feature/content-expansion-multilingual

# Commit снова
git add .
git commit -m "feat: Add content expansion"
git push -u origin feature/content-expansion-multilingual
```

### Хочу добавить еще что-то в существующий PR
```bash
# Убедись что на правильной ветке
git checkout feature/content-expansion-multilingual

# Сделай изменения
# ... edit files ...

# Commit
git add .
git commit -m "feat: Add additional questions"

# Push (обновит существующий PR автоматически)
git push origin feature/content-expansion-multilingual
```
