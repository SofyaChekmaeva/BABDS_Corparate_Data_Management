# SupportRAG — Умная система поддержки клиентов

RAG-система для поиска и генерации ответов на основе обращений в службу поддержки.

## Датасет

- **Источник:** [Customer Support Tickets Dataset](https://www.kaggle.com/datasets/mirzayasirabdullah07/customer-support-tickets-dataset-200k-records)
- **Размер:** 200 000+ записей (используем 5 000)
- **Поля:** `issue_description`, `resolution_notes`, `Ticket Category`

## Архитектура
CSV → datasets.json → документы → чанки → TF-IDF индекс → поиск → генератор → UI

## Структура проекта:
rag-tutorial/
├── app/
│   ├── config.py          # Настройки
│   ├── chunker.py         # Нарезка текста
│   ├── retriever.py       # TF-IDF поиск
│   ├── generator.py       # Генерация ответов
│   ├── prompts.py         # Шаблоны ответов
│   └── main.py            # Streamlit UI
├── scripts/
│   ├── prepare_datasets.py
│   ├── build_index.py
│   └── check_*.py
├── data/
│   ├── raw/               # Исходные данные
│   ├── processed/         # Чанки
│   └── index/             # TF-IDF индекс
├── tests/                 # Тесты
├── doc/                   # Документация
└── homework/              # Отчёт
