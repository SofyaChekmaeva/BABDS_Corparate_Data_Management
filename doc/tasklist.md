## Итерационный план реализации RAG-проекта

**Проект:** SupportRAG — умная система поиска и генерации ответов на основе обращений в службу поддержки  
**Датасет:** Customer Support Tickets (200 000 записей)  
**Цель:** Реализовать полный RAG-пайплайн с оценкой качества

---

## Таблица прогресса по итерациям

| Итерация | Название | Статус | Дата завершения | Проверка |
|----------|----------|--------|-----------------|----------|
| 0 | Настройка окружения и знакомство | ⬜ Не начата | — | `uv run pytest tests/ -v` |
| 1 | Загрузка и подготовка датасета | ⬜ Не начата | — | `data/raw/datasets.json` содержит 1000+ записей |
| 2 | Чанкинг и индексация (TF-IDF) | ⬜ Не начата | — | `data/index/matrix.npz` и `vectorizer.pkl` созданы |
| 3 | Поиск (retrieval) и тестирование | ⬜ Не начата | — | `scripts/check_retrieval.py` выдаёт scores |
| 4 | Генератор (demo-ответ с контекстом) | ⬜ Не начата | — | `scripts/check_generator.py` выдаёт ответ |
| 5 | Оценка качества поиска (метрики) | ⬜ Не начата | — | Реализованы recall@k, MRR, precision@k |
| 6 | Улучшение генератора (контекст + отказы) | ⬜ Не начата | — | Отказ на off-topic запросы |
| 7 | Ноутбук-отчёт (report.ipynb) | ⬜ Не начата | — | Все визуализации и выводы |
| 8 | Финальная интеграция и деплой | ⬜ Не начата | — | Streamlit UI работает |

**Легенда:**
- ⬜ Не начата
- 🔄 В процессе
- ✅ Завершена
- ❌ Проблема/переделка

---

## Итерация 0: Настройка окружения и знакомство

**Цель:** Развернуть проект, установить зависимости, убедиться, что исходная версия работает.

**Задачи:**
1. Клонировать репозиторий `rag-tutorial`
2. Установить `uv` (если не установлен)
3. Создать виртуальное окружение: `uv venv`
4. Установить зависимости: `uv sync`
5. Запустить тесты: `uv run pytest tests/ -v`
6. Запустить демо-версию с исходными данными: `uv run python scripts/build_index.py`
7. Запустить Streamlit UI: `uv run streamlit run app/main.py`
8. Проверить demo-вопросы из README

**Проверка:**
```bash
uv run pytest tests/ -v  # все тесты проходят
uv run streamlit run app/main.py  # UI открывается без ошибок
```

## Итерация 1: Загрузка и подготовка датасета

**Цель:** Заменить исходный датасет на выбранный (Customer Support Tickets, 5,000 записей).

### Задачи

1. Скачать `customer_support_tickets_200k.csv` с Kaggle (73 MB)
2. Создать скрипт `scripts/prepare_dataset.py` (или сделать в Colab):
   - Прочитать CSV через pandas
   - Взять первые N=5000 записей
   - Отобрать колонки: `Ticket ID`, `Ticket Category`, `issue_description`, `resolution_notes`
   - Преобразовать в формат: `{"id": Ticket ID, "title": Ticket Category, "text": issue_description + "\n\n" + resolution_notes}`
3. Сохранить как `data/raw/datasets.json`
4. Проверить, что в файле 5000 записей
5. Удалить временные файлы (CSV, если не нужен)

### Проверка

```bash
# Проверка количества записей
python -c "import json; print(len(json.load(open('data/raw/datasets.json'))))"  # → 5000

# Проверка структуры
python -c "import json; d=json.load(open('data/raw/datasets.json')); print(d[0].keys())"  # → dict_keys(['id', 'title', 'text'])
```

## Итерация 2: Чанкинг и индексация (TF-IDF)

**Цель:** Настроить чанкинг под специфику тикетов поддержки и построить TF-IDF индекс.

### Задачи

1. Проанализировать длину текстов в `datasets.json` (распределение символов)
2. Настроить параметры чанкинга в `app/config.py`:
   - `CHUNK_SIZE = 500` (символов)
   - `CHUNK_OVERLAP = 50` (перекрытие)
3. Доопределить `app/chunker.py` (если нужно):
   - Сохранить существующую логику (по параграфам, затем по символам)
   - Добавить опциональную привязку к `title` документа
4. Запустить сборку индекса: `uv run python scripts/build_index.py`
5. Проверить созданные файлы:
   - `data/processed/chunks.jsonl` — количество строк (ожидается ~10,000-15,000)
   - `data/index/vectorizer.pkl` — существует
   - `data/index/matrix.npz` — существует

### Проверка

```bash
# Количество чанков
wc -l data/processed/chunks.jsonl  # → ~10-15k

# Индекс не пустой
python -c "import pickle; import scipy.sparse; v=pickle.load(open('data/index/vectorizer.pkl','rb')); m=scipy.sparse.load_npz('data/index/matrix.npz'); print(m.shape)"  # → (N_chunks, N_features)
```

## Итерация 3: Поиск (retrieval) и тестирование

**Цель:** Убедиться, что поиск работает на реальных запросах.

### Задачи

1. Запустить `uv run python scripts/check_retrieval.py` с тестовым запросом
2. Протестировать поиск на нескольких категориях:
   - `"Не могу войти в аккаунт"` → ожидаем `Login Issue` или `Account Suspension`
   - `"Как изменить способ оплаты"` → ожидаем `Payment Problem`
   - `"Отменить подписку"` → ожидаем `Subscription Cancellation`
3. Посмотреть scores: они должны быть в диапазоне 0.3-0.9 для релевантных
4. Если scores систематически низкие (<0.3) — проверить:
   - Достаточно ли длинные тексты в `datasets.json`
   - Нет ли пустых `issue_description`
   - Размер чанка (возможно, нужен 300 или 800)

### Проверка

```bash
uv run python scripts/check_retrieval.py --query "Не могу войти в аккаунт"
# Должны увидеть top-3 чанка со scores > 0.3
```

## Итерация 4: Генератор (demo-ответ с контекстом)

**Цель:** Настроить генератор, чтобы он выдавал осмысленный ответ из найденных чанков.

### Задачи

1. Изучить `app/generator.py` и `app/prompts.py`
2. Убедиться, что генератор:
   - Формирует ответ, склеивая найденные чанки
   - Добавляет источники (`doc_id`, `score`)
   - Использует threshold (по умолчанию 0.3)
3. Настроить threshold в `app/config.py` (если нужно)
4. Запустить `uv run python scripts/check_generator.py`
5. Проверить, что ответ содержит фрагменты из чанков

### Проверка

```bash
uv run python scripts/check_generator.py --query "Как изменить способ оплаты"
# Ответ должен содержать что-то из resolution_notes
```

## Итерация 5: Оценка качества поиска (метрики)

**Цель:** Реализовать метрики оценки retrieval: recall@k, MRR, precision@k.

### Задачи

1. Создать тестовый набор запросов (минимум 10-20 штук) с разметкой релевантных `doc_id` или `chunk_id`
2. Реализовать функции в `app/retriever.py` или отдельном модуле `scripts/evaluate.py`:
   - `recall_at_k(retrieved_chunks, relevant_ids, k)`
   - `precision_at_k(retrieved_chunks, relevant_ids, k)`
   - `mrr(retrieved_chunks, relevant_ids)`
3. Вычислить метрики для k=1,3,5
4. Сохранить результаты в `data/metrics.json`
5. Добавить визуализацию в ноутбук (позже)

### Проверка

```bash
uv run python scripts/evaluate.py
# Должны увидеть:
# recall@3: 0.65
# precision@3: 0.70
# MRR: 0.72
```

## Итерация 6: Улучшение генератора (контекст + отказы)

**Цель:** Добиться корректных отказов на запросы не по теме и улучшить качество ответов.

### Задачи

1. Дополнить `app/prompts.py` правилами отказа:
   - Кулинария, спорт, политика → "Я могу отвечать только на вопросы о поддержке клиентов"
   - Пустой запрос → "Пожалуйста, задайте вопрос"
   - Нецензурная лексика → "Пожалуйста, задайте вопрос корректно"
2. Добавить проверку домена в `app/generator.py`:
   - Список стоп-слов/тем (опционально)
   - Если чанки не найдены (empty) → отказ
   - Если max_score < threshold → отказ
3. Протестировать на off-topic запросах:
   - `"Как приготовить борщ?"` → отказ
   - `"Кто выиграл чемпионат мира по футболу?"` → отказ

### Проверка

```bash
uv run python scripts/check_generator.py --query "Как приготовить борщ"
# Ответ: "Извините, я не могу найти информацию по вашему вопросу в базе знаний."
```

## Итерация 7: Ноутбук-отчёт (report.ipynb)

**Цель:** Подготовить итоговый отчёт с визуализациями и выводами.

### Задачи

1. Создать `homework/report.ipynb` (Jupyter Notebook)
2. Включить в него:
   - **Раздел 1:** Описание датасета (откуда, сколько записей, примеры)
   - **Раздел 2:** Визуализация распределения категорий тикетов (bar chart)
   - **Раздел 3:** Распределение длины текстов (гистограмма)
   - **Раздел 4:** Визуализация scores поиска (boxplot по категориям)
   - **Раздел 5:** Таблица метрик (recall@k, MRR, precision@k)
   - **Раздел 6:** Примеры работы системы (2-3 успешных + 1 отказ)
   - **Раздел 7:** Выводы и возможные улучшения
3. Убедиться, что ноутбук воспроизводим (очистить вывод перед коммитом)

### Проверка

```bash
# Запустить ноутбук в headless-режиме
jupyter nbconvert --to notebook --execute homework/report.ipynb --output report_executed.ipynb
# Не должно быть ошибок
```

## Итерация 8: Финальная интеграция и деплой

**Цель:** Собрать всё воедино, проверить end-to-end и подготовить к сдаче.

### Задачи

1. Запустить полный пайплайн от начала до конца:
   - `uv run python scripts/prepare_dataset.py` (если есть)
   - `uv run python scripts/build_index.py`
   - `uv run python scripts/check_retrieval.py`
   - `uv run python scripts/check_generator.py`
   - `uv run streamlit run app/main.py`
2. Убедиться, что UI отвечает на вопросы из README
3. Закоммитить все изменения с понятными сообщениями (Conventional Commits)
4. Обновить `README.md` проекта:
   - Указать, что используется датасет Customer Support Tickets
   - Добавить инструкцию по запуску
   - Добавить примеры запросов
5. Проверить, что файлы `doc/00_project_idea.md`, `doc/vision.md`, `doc/conventions.md`, `doc/tasklist.md` присутствуют и заполнены

### Проверка

```bash
# Полная проверка
uv run pytest tests/ -v && \
uv run python scripts/build_index.py && \
uv run python scripts/check_retrieval.py && \
uv run python scripts/check_generator.py
# Всё зелёное
```






