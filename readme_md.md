# 🚀 YouTube Trend Analyzer v6

[Русский](#-russian) | [English](#-english)

---

## 🇷🇺 Русский

### 📌 Описание
**YouTube Trend Analyzer** — это инструмент бизнес-разведки и поиска начинающихся трендов на YouTube. В отличие от стандартных сервисов аналитики, которые показывают уже отшумевшие хиты («кладбище победителей»), этот скрипт находит **молодые ролики**, которые **быстро набирают просмотры** на **небольших каналах**. Это позволяет контент-мейкерам вовремя заметить зарождающийся мем, формат или тему и успеть снять свой ролик.

### ✨ Ключевые возможности
- **Поиск раннего входа (`Emerging Score`):** Уникальный алгоритм оценки вирусности, учитывающий скорость набора просмотров в час, вовлеченность, свежесть и размер канала.
- **Мульти-региональный сканер:** Сканирование трендов по 12 ключевым регионам (США, Великобритания, Германия, Япония, Южная Корея и др.).
- **Добор сид-запросов:** Автоматический поиск повторяющихся слов в заголовках трендов для отслеживания зарождающихся мемов.
- **Глубокие фильтры:** 
  - Фильтрация по длительности (Shorts / Longs).
  - Настройка периода публикации (от 24 часов до 6 месяцев или за всё время).
  - Исключение выбранных стран (интерактивный выбор).
  - Исключение готовых тематических категорий (детский контент, гейминг, музыка, политика, ИИ-контент) и пользовательских стоп-слов.
  - Лимит подписчиков и просмотров.
- **Экспорт в 3 формата:** Автоматическое сохранение результатов в `.csv`, `.txt` и `.md` (адаптировано под **Obsidian** с YAML-тегами и вики-ссылками).
- **Двуязычный интерфейс:** Поддержка русского и английского языков прямо в консоли.

### 🛠 Требования
- Python 3.8+
- Ключ `YouTube Data API v3` (получить в Google Cloud Console)

### 📦 Установка
1. Клонируйте репозиторий или скачайте исходный код:
   ```bash
   git clone https://github.com/your-username/youtube-trend-analyzer.git
   cd youtube-trend-analyzer
   ```
2. Установите необходимые зависимости:
   ```bash
   pip install google-api-python-client isodate
   ```

### 🚀 Запуск
```bash
python main.py
```
После запуска скрипт предложит выбрать язык (Русский/English), ввести API-ключ и настроить параметры поиска через удобное интерактивное меню.

---

## 🇬🇧 English

### 📌 Overview
**YouTube Trend Analyzer** is a content intelligence and early-trend detection tool for YouTube. Unlike standard analytics platforms that highlight already saturated trends ("the graveyard of winners"), this script identifies **fresh videos** gaining **rapid views per hour** on **small to mid-sized channels**. This gives content creators a head start to catch emerging memes, topics, or formats before the niche becomes oversaturated.

### ✨ Key Features
- **Emerging Score Formula:** A custom algorithm ranking videos based on velocity (views/hour), engagement, freshness, and channel size relative to performance.
- **Multi-Region Scanner:** Scans regional trends across 12 primary countries (US, GB, DE, JP, KR, etc.).
- **Seed Keyword Harvesting:** Extracts repeating viral keywords from trend titles to uncover early-stage meme waves.
- **Advanced Filtering:**
  - Format separation (Shorts vs. Longform).
  - Custom publish date windows (24h, 7d, 30d, 90d, 180d, or All time).
  - Interactive country exclusion list.
  - Topic-based category blocklists (Kids content, Gaming, Music, Politics, AI generation) + custom stop-words.
  - Subscriber count cap & view thresholds.
- **Multi-Format Export:** Automatic export to `.csv`, `.txt`, and `.md` (pre-formatted for **Obsidian** with YAML frontmatter, tags, and internal links).
- **Bilingual Interface:** Full interactive support for English and Russian in the terminal.

### 🛠 Prerequisites
- Python 3.8+
- `YouTube Data API v3` key (obtainable via Google Cloud Console)

### 📦 Installation
1. Clone the repository or download the source code:
   ```bash
   git clone https://github.com/your-username/youtube-trend-analyzer.git
   cd youtube-trend-analyzer
   ```
2. Install required packages:
   ```bash
   pip install google-api-python-client isodate
   ```

### 🚀 Usage
```bash
python main.py
```
Follow the interactive prompts to choose language, enter your YouTube API key, and configure search filters.

---

### 👨‍💻 Developer / Разработчик
**Pavel Muv**
- YouTube: [@Pavel_Muv_Lab](https://www.youtube.com/@Pavel_Muv_Lab)
- X (Twitter): [@Pavel_muv](https://x.com/Pavel_muv)