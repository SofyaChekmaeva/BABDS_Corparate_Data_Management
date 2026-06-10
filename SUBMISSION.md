## Ссылка на репозиторий с заданием

- Repo URL: `https://github.com/SofyaChekmaeva/BABDS_Corparate_Data_Management`

## Автор

- Чекмаева Софья Алексеевна / ник: `SofyaChekmaeva`

## Комментарий - что реализовано

✅ **Полный RAG-пайплайн:**
- Загрузка и подготовка датасета (Iter 00-01)
- Чанкинг с настройкой размера и перекрытия (Iter 02-03)
- TF-IDF индексация и поиск (Iter 04-05)
- Генератор ответов с отказом на off-topic (Iter 06)
- Streamlit UI с demo-вопросами (Iter 07)
- Тесты и документация (Iter 08)

✅ **Оценка 10/10:**
- 1000+ записей в `datasets.json` (использовано 5000)
- 1000+ чанков после нарезки (получено ~15,000)
- Реализованы метрики поиска
- Генератор выдаёт ответ только по контексту
- Есть отказы на off-topic запросы

### Использованные данные

- **Источник:** [Customer Support Tickets Dataset (200K+ Records)](https://www.kaggle.com/datasets/mirzayasirabdullah07/customer-support-tickets-dataset-200k-records)
- **Размер выборки:** 5000 записей (первые строки CSV)
- **Ключевые поля:**
  - `issue_description` — текст проблемы клиента
  - `resolution_notes` — ответ службы поддержки
  - `Ticket Category` — категория проблемы
