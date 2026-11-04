# -*- coding: utf-8 -*-
import csv
import os
import sys
import time
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

# UTF-8 console support on Windows
if os.name == "nt":
    os.system("chcp 65001 > nul")

for stream in (sys.stdin, sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    import isodate
except ImportError:
    print("pip install isodate")
    sys.exit(1)

# Папка программы: рядом с EXE (PyInstaller) или рядом с main.py
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    filename=str(BASE_DIR / "youtube_trend_analyzer.log"),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)

DEVELOPER = "Pavel Muv"
CONTACTS = [
    ("YouTube", "https://www.youtube.com/@Pavel_Muv_Lab"),
    ("X", "https://x.com/Pavel_muv"),
]

EXIT_WORDS = {"0", "exit", "quit", "q", "выход", "в"}
SEARCH_COST = 100  # единиц квоты за один вызов search().list

# Визуал и текстовые блоки с поддержкой языков (ru/en)
TEXT = {
    "ru": {
        "title": "YOUTUBE TREND ANALYZER",
        "brand_line": "Ранний вход: молодое + быстрое + не гигант",
        "api_key": "Введите API-ключ YouTube Data API v3",
        "checking": "Проверка API-ключа...",
        "api_ok": "API-ключ работает.",
        "api_error": "Не удалось подключиться к YouTube API.",
        "bye": "Работа завершена. До встречи!",
        "count": "Количество результатов",
        "format_label": "Тип видео",
        "format_menu": (
            "Тип видео:\n"
            "1 — Все\n"
            "2 — Shorts\n"
            "3 — Обычные"
        ),
        "period_menu": (
            "Период публикации:\n"
            "1 — 24 часа\n"
            "2 — 2 дня\n"
            "3 — 3 дня\n"
            "4 — 7 дней\n"
            "5 — 1 месяц (~30 дней)\n"
            "6 — 3 месяца (~90 дней)\n"
            "7 — Полгода (~180 дней)\n"
            "8 — Без ограничений (все время)"
        ),
        "mode_menu": (
            "Режим:\n"
            "1 — Тренды по странам + похожие запросы\n"
            "2 — Ключевое слово (date + viewCount)\n"
            "3 — Оба: тренды и слово"
        ),
        "query": "Ключевое слово (можно на любом языке, 0 — выход)",
        "next_query": "Введите следующий запрос (0 — выход)",
        "sort": (
            "Сортировка:\n"
            "1 — Emerging — лучшее для входа\n"
            "2 — Просмотры в час\n"
            "3 — Views / подписчики (ролик сильнее канала)\n"
            "4 — Просто просмотры"
        ),
        "searching": "Сбор трендов и данных...",
        "search_query": "Поиск",
        "progress_videos": "Получение данных видео",
        "progress_channels": "Получение данных каналов",
        "done": "ГОТОВО! АНАЛИЗ ЗАВЕРШЁН",
        "follow": "Больше полезного — в моих соцсетях",
        "found": "Найдено уникальных видео",
        "selected": "Видео после фильтров",
        "saved_to": "Сохранено в папку",
        "preview": "ИТОГИ ПОИСКА (Emerging Score)",
        "empty": "Подходящих видео не найдено.",
        "unknown": "Неизвестно",
        "published": "Дата публикации",
        "duration": "Длительность",
        "views": "Просмотры",
        "likes": "Лайки",
        "comments": "Комментарии",
        "channel": "Канал",
        "subs": "Подписчики",
        "age": "Возраст, дн.",
        "vph": "Просмотров в час",
        "ratio": "Views / подписчики",
        "score": "Emerging score",
        "developer": "Разработчик",
        "contacts": "Контакты",
        "invalid": "Некорректный ввод.",
        "no_results": "Попробуйте изменить запрос или фильтры.",
        "quota_estimate": (
            "Расход квоты на этот запуск: около {cost} ед. "
            "(дефолтный лимит — 10 000 ед. в сутки)."
        ),
        "quota_exceeded": (
            "Квота YouTube Data API на сегодня исчерпана. "
            "Она обновляется раз в сутки (полночь по тихоокеанскому времени)."
        ),
        "key_rejected": "Ключ отклонён или доступ запрещён. Проверьте ключ и включён ли YouTube Data API v3.",
    },
    "en": {
        "title": "YOUTUBE TREND ANALYZER",
        "brand_line": "Early entry: young + fast + not a giant",
        "api_key": "Enter your YouTube Data API v3 key",
        "checking": "Checking API key...",
        "api_ok": "API key is working.",
        "api_error": "Could not connect to YouTube API.",
        "bye": "Finished. See you!",
        "count": "Number of results",
        "format_label": "Video type",
        "format_menu": (
            "Video type:\n"
            "1 — All\n"
            "2 — Shorts\n"
            "3 — Normal"
        ),
        "period_menu": (
            "Publication period:\n"
            "1 — 24 hours\n"
            "2 — 2 days\n"
            "3 — 3 days\n"
            "4 — 7 days\n"
            "5 — 1 month (~30 days)\n"
            "6 — 3 months (~90 days)\n"
            "7 — Half a year (~180 days)\n"
            "8 — All time"
        ),
        "mode_menu": (
            "Mode:\n"
            "1 — Regional trends + seed queries\n"
            "2 — Keyword search (date + viewCount)\n"
            "3 — Both: trends and keyword"
        ),
        "query": "Keyword (any language, 0 to exit)",
        "next_query": "Enter the next query (0 to exit)",
        "sort": (
            "Sort by:\n"
            "1 — Emerging — best for entry\n"
            "2 — Views per hour\n"
            "3 — Views / subscribers (outlier)\n"
            "4 — Just views"
        ),
        "searching": "Collecting trends and data...",
        "search_query": "Search",
        "progress_videos": "Fetching video data",
        "progress_channels": "Fetching channel data",
        "done": "ALL DONE! ANALYSIS COMPLETE",
        "follow": "More from me — follow my channels",
        "found": "Unique videos found",
        "selected": "Videos after filters",
        "saved_to": "Saved in folder",
        "preview": "SEARCH SUMMARY (Emerging Score)",
        "empty": "No matching videos found.",
        "unknown": "Unknown",
        "published": "Published",
        "duration": "Duration",
        "views": "Views",
        "likes": "Likes",
        "comments": "Comments",
        "channel": "Channel",
        "subs": "Subscribers",
        "age": "Age, days",
        "vph": "Views per hour",
        "ratio": "Views / subscribers",
        "score": "Emerging score",
        "developer": "Developer",
        "contacts": "Contacts",
        "invalid": "Invalid input.",
        "no_results": "Try changing your query or filters.",
        "quota_estimate": (
            "Estimated quota cost for this run: about {cost} units "
            "(default daily limit is 10,000 units)."
        ),
        "quota_exceeded": (
            "The YouTube Data API quota for today is exhausted. "
            "It resets once a day (midnight Pacific Time)."
        ),
        "key_rejected": "The key was rejected or access is denied. Check the key and that YouTube Data API v3 is enabled.",
    },
}

SCAN_REGIONS = ["US", "GB", "ES", "MX", "AR", "CO", "BR", "DE", "FR", "JP", "KR", "RU"]

COUNTRY_NAMES = {
    "US": "США", "RU": "Россия", "GB": "Великобритания", "KZ": "Казахстан",
    "CN": "Китай", "JP": "Япония", "KR": "Южная Корея", "DE": "Германия",
    "FR": "Франция", "ES": "Испания", "IT": "Италия", "CA": "Канада",
    "AU": "Австралия", "BR": "Бразилия", "IN": "Индия", "MX": "Мексика",
    "AR": "Аргентина", "CL": "Чили", "CO": "Колумбия", "TR": "Турция",
    "UA": "Украина", "PL": "Польша", "NL": "Нидерланды", "SE": "Швеция",
    "PT": "Португалия", "ID": "Индонезия", "PH": "Филиппины", "TH": "Таиланд",
    "VN": "Вьетнам", "PK": "Пакистан", "BD": "Бангладеш", "NG": "Нигерия",
    "EG": "Египет", "SA": "Саудовская Аравия", "AE": "ОАЭ", "IL": "Израиль",
}

DEFAULT_BLOCKLIST = [
    "huggy", "huggy wuggy", "poppy playtime", "skibidi",
    "full movie", "pelicula completa", "película completa",
    "watch online free",
]

# Категории тем для быстрой фильтрации
TOPIC_CATEGORIES = [
    ("Детский контент / Мультики", [
        "kids", "nursery", "rhymes", "cocomelon", "peppa", "paw patrol", 
        "skibidi", "toilet", "huggy", "wuggy", "poppy playtime", "roblox kids",
        "мультик", "для детей", "сказки", "детский"
    ]),
    ("Гейминг / Стримы", [
        "gameplay", "walkthrough", "gaming", "stream", "twitch", "fortnite",
        "minecraft", "roblox", "gta", "pubg", "valorant", "league of legends",
        "прохождение", "летсплей", "игра"
    ]),
    ("Фильмы / Сериалы / Шоу", [
        "full movie", "full film", "pelicula completa", "película completa", 
        "movie", "trailer", "episode", "season", "episode 1", "фильм", "сериал",
        "трейлер", "серия", "шоу", "watch online free"
    ]),
    ("Музыка / Клипы / Ремиксы", [
        "official music video", "official audio", "lyric video", "lyrics",
        "remix", "song", "album", "cover", "concert", "live performance",
        "клип", "песня", "альбом", "концерт", "ремикс"
    ]),
    ("Политика / Новости / Война", [
        "news", "breaking news", "politics", "political", "war", "election",
        "president", "biden", "trump", "putin", "ukraine", "новости", "политика",
        "война", "выборы", "президент"
    ]),
    ("ИИ Сгенерированный контент / Озвучка", [
        "ai voice", "elevenlabs", "text to speech", "ai generated", "ai animation",
        "sora", "veo", "midjourney", "chatgpt", "ии", "нейросеть"
    ]),
]


# ───────────────────────── helpers ─────────────────────────

def choose_language():
    print("\n1. Русский")
    print("2. English")

    while True:
        choice = input("> ").strip()
        if choice == "1":
            return "ru"
        if choice == "2":
            return "en"
        print("Введите 1 или 2 / Enter 1 or 2")


def format_number(number):
    try:
        return f"{int(number):,}".replace(",", " ")
    except Exception:
        return "0"


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def parse_duration(duration):
    try:
        return int(isodate.parse_duration(duration).total_seconds())
    except Exception:
        return 0


def format_duration(seconds):
    seconds = safe_int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def parse_youtube_date(date_string):
    try:
        return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def age_hours_of(published):
    now = datetime.now(timezone.utc)
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    return max((now - published).total_seconds() / 3600.0, 0.25)


def is_short(duration, title="", description=""):
    text = f"{title} {description}".lower()
    if duration <= 60:
        return True
    if duration <= 180 and ("#shorts" in text or "#short" in text or "/shorts" in text):
        return True
    return False


def blocked(title, description, blocklist):
    text = f"{title} {description}".lower()
    return any(word.lower() in text for word in blocklist if word.strip())


def emerging_score(views, likes, comments, age_hours, subscribers):
    views = max(safe_int(views), 0)
    likes = max(safe_int(likes), 0)
    comments = max(safe_int(comments), 0)
    age_hours = max(float(age_hours), 0.25)
    subscribers = max(safe_int(subscribers), 1)

    vph = views / age_hours
    engagement = (likes + comments * 4) / max(views, 1)
    freshness = 72.0 / (age_hours + 6.0)
    small_channel = 50_000.0 / (subscribers + 5_000.0)

    score = (vph * 1.0) + (views * engagement * 8.0)
    score *= freshness
    score *= (0.35 + small_channel)
    return round(score, 2)


def execute_with_retry(request, tries=5, pause=1.5):
    last = None
    for attempt in range(1, tries + 1):
        try:
            return request.execute()
        except HttpError as e:
            last = e
            status = getattr(getattr(e, "resp", None), "status", None)
            if status in (403, 400):
                raise
        except Exception as e:
            last = e
        time.sleep(pause * attempt)
    raise last


def is_quota_error(error):
    if not isinstance(error, HttpError):
        return False
    try:
        content = error.content.decode("utf-8", errors="ignore")
    except AttributeError:
        content = str(error)
    return "quotaExceeded" in content or "dailyLimitExceeded" in content


def is_key_error(error):
    if not isinstance(error, HttpError):
        return False
    status = getattr(error.resp, "status", None)
    return status in (400, 401, 403) and not is_quota_error(error)


def cell_text(value, empty="—"):
    return empty if value is None else str(value)


def connect_api(api_key):
    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key,
        cache_discovery=False,
        num_retries=5,
    )
    youtube.videos().list(part="snippet", id="dQw4w9WgXcQ", maxResults=1).execute()
    return youtube


# ───────────────────────── сбор данных ─────────────────────────

def paged_search(youtube, **kwargs):
    pages = kwargs.pop("pages", 1)
    items = []
    token = None
    for _ in range(max(1, pages)):
        body = dict(kwargs)
        if token:
            body["pageToken"] = token
        try:
            resp = execute_with_retry(youtube.search().list(**body))
        except Exception:
            break
        items.extend(resp.get("items", []))
        token = resp.get("nextPageToken")
        if not token:
            break
    return items


def get_trending_region(youtube, region, max_results=50):
    try:
        resp = execute_with_retry(youtube.videos().list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            regionCode=region,
            maxResults=min(max_results, 50),
        ))
        time.sleep(0.2)
        return resp.get("items", [])
    except Exception:
        return []


def get_video_details(youtube, video_ids):
    out = []
    ids = [v for v in video_ids if v]
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        try:
            resp = execute_with_retry(youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(batch),
                maxResults=50,
            ))
            out.extend(resp.get("items", []))
            time.sleep(0.25)
        except Exception:
            pass
    return out


def get_channels(youtube, channel_ids, progress_callback=None):
    info = {}
    ids = list({x for x in channel_ids if x})
    total_batches = max(1, (len(ids) + 49) // 50)
    
    for batch_index, i in enumerate(range(0, len(ids), 50), 1):
        batch = ids[i:i + 50]
        try:
            resp = execute_with_retry(youtube.channels().list(
                part="snippet,statistics",
                id=",".join(batch),
                maxResults=50,
            ))
            time.sleep(0.2)
        except Exception:
            continue
        for item in resp.get("items", []):
            cid = item.get("id", "")
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            cc = (snippet.get("country") or "").upper().strip()
            info[cid] = {
                "region": COUNTRY_NAMES.get(cc, cc or "—"),
                "region_code": cc or "—",
                "subscribers": safe_int(stats.get("subscriberCount", 0)),
                "hidden_subs": stats.get("hiddenSubscriberCount", False),
                "channel_videos": safe_int(stats.get("videoCount", 0)),
            }
        if progress_callback:
            progress_callback(batch_index, total_batches, batch_index == total_batches)
    return info


def prepare_video(item):
    snippet = item.get("snippet", {})
    content = item.get("contentDetails", {})
    statistics = item.get("statistics", {})

    video_id = item.get("id", "")
    if isinstance(video_id, dict):
        video_id = video_id.get("videoId", "")

    title = snippet.get("title", "Без названия")
    description = snippet.get("description", "") or ""
    published = parse_youtube_date(snippet.get("publishedAt", ""))
    duration = parse_duration(content.get("duration", "PT0S"))
    views = safe_int(statistics.get("viewCount", 0))
    likes = safe_int(statistics.get("likeCount", 0))
    comments = safe_int(statistics.get("commentCount", 0))
    age_hours = age_hours_of(published)
    age_days = age_hours / 24.0

    return {
        "id": video_id,
        "video_id": video_id,
        "title": title,
        "description": description,
        "channel": snippet.get("channelTitle", "—"),
        "channel_id": snippet.get("channelId", ""),
        "language": snippet.get("defaultAudioLanguage") or snippet.get("defaultLanguage") or "—",
        "published": published.strftime("%Y-%m-%d %H:%M UTC"),
        "published_str": published.strftime("%Y-%m-%d %H:%M"),
        "duration": format_duration(duration),
        "duration_sec": duration,
        "views": views,
        "likes": likes,
        "comments": comments,
        "age_hours": round(age_hours, 2),
        "age_days": round(age_days, 2),
        "views_per_hour": round(views / max(age_hours, 0.25), 2),
        "views_per_day": round(views / max(age_days, 1 / 24), 2),
        "is_short": is_short(duration, title, description),
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "region": "—",
        "region_code": "—",
        "subscribers": 0,
        "views_per_sub": 0.0,
        "emerging_score": 0.0,
        "why": "",
    }


def enrich_channels(youtube, videos, progress_callback=None):
    ids = [v.get("channel_id") for v in videos if v.get("channel_id")]
    meta = get_channels(youtube, ids, progress_callback=progress_callback)
    for v in videos:
        m = meta.get(v.get("channel_id"), {})
        v["region"] = m.get("region", "—")
        v["region_code"] = m.get("region_code", "—")
        v["subscribers"] = m.get("subscribers", 0)
        subs = max(v["subscribers"], 1)
        v["views_per_sub"] = round(v["views"] / subs, 3)
        v["emerging_score"] = emerging_score(
            v["views"], v["likes"], v["comments"], v["age_hours"], v["subscribers"]
        )
        reasons = []
        if v["age_hours"] <= 36:
            reasons.append("свежее")
        if v["subscribers"] and v["subscribers"] < 20000 and v["views"] > 20000:
            reasons.append("маленький канал / много просмотров")
        if v["views_per_hour"] >= 2000:
            reasons.append("высокая скорость")
        if v["views_per_sub"] >= 5:
            reasons.append("ролик сильнее канала")
        v["why"] = ", ".join(reasons) or "слабый сигнал раннего входа"


def dedupe(videos):
    seen, out = set(), []
    for v in videos:
        vid = v.get("id") or v.get("video_id")
        if vid and vid not in seen:
            seen.add(vid)
            out.append(v)
    return out


def apply_filters(videos, video_type, max_age_days, min_views, max_subs, excluded_regions, blocklist):
    out = []
    for v in videos:
        if max_age_days and v["age_days"] > max_age_days:
            continue
        if video_type == "shorts" and not v["is_short"]:
            continue
        if video_type == "normal" and v["is_short"]:
            continue
        if v["views"] < min_views:
            continue
        if max_subs and v["subscribers"] > max_subs:
            continue
        if v["region_code"] in excluded_regions or v["region"] in excluded_regions:
            continue
        if blocked(v["title"], v["description"], blocklist):
            continue
        out.append(v)
    return out


def collect_trending(youtube, max_age_days, regions, progress_callback=None):
    items = []
    total = len(regions)
    for idx, region in enumerate(regions, 1):
        items.extend(get_trending_region(youtube, region, 50))
        if progress_callback:
            progress_callback(idx, total, idx == total)
    videos = [prepare_video(x) for x in items]
    return dedupe(videos)


def collect_keyword(youtube, keyword, max_age_days, pages, progress_callback=None):
    published_after = None
    if max_age_days:
        published_after = (
            datetime.now(timezone.utc) - timedelta(days=max_age_days)
        ).isoformat().replace("+00:00", "Z")

    raw = []
    orders = ("date", "viewCount")
    total_steps = len(orders) * pages
    current_step = 0

    for order in orders:
        for p in range(pages):
            current_step += 1
            body = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": order,
                "maxResults": 50,
            }
            if published_after:
                body["publishedAfter"] = published_after

            resp_items = paged_search(youtube, **body, pages=1)
            raw.extend(resp_items)
            if progress_callback:
                progress_callback(current_step, total_steps, current_step == total_steps)

    ids = []
    for item in raw:
        vid = (item.get("id") or {}).get("videoId")
        if vid:
            ids.append(vid)
    detailed = get_video_details(youtube, ids)
    return dedupe([prepare_video(x) for x in detailed])


def collect_seed_from_trending(youtube, videos, max_age_days, pages, progress_callback=None):
    words = {}
    stop = set(
        "the a an el la los las de un una y en vs video shorts short official "
        "trailer official trailer teaser hd 4k 2024 2025 2026".split()
    )
    for v in videos:
        for w in v["title"].replace("|", " ").replace("-", " ").split():
            w = "".join(ch for ch in w.lower() if ch.isalnum())
            if len(w) < 4 or w in stop:
                continue
            words[w] = words.get(w, 0) + 1
    seeds = [w for w, n in sorted(words.items(), key=lambda x: -x[1]) if n >= 3][:6]
    extra = []
    total = len(seeds) if seeds else 1
    for idx, seed in enumerate(seeds, 1):
        try:
            extra.extend(collect_keyword(youtube, seed, max_age_days, pages=1))
        except Exception:
            pass
        if progress_callback:
            progress_callback(idx, total, idx == total)
        time.sleep(0.6)
    if not seeds and progress_callback:
        progress_callback(1, 1, True)
    return extra


def sort_videos(videos, sort_by):
    key_map = {
        "emerging": lambda v: v["emerging_score"],
        "velocity": lambda v: v["views_per_hour"],
        "views": lambda v: v["views"],
        "outlier": lambda v: v["views_per_sub"],
        "likes": lambda v: v["likes"],
    }
    key = key_map.get(sort_by, key_map["emerging"])
    videos.sort(key=key, reverse=True)
    return videos


# ───────────────────────── визуальное оформление ─────────────────────────

def print_header(lang):
    t = TEXT[lang]
    line = "=" * 68
    print("\n" + line)
    print(f"  {t['title']}  |  {t['brand_line']}")
    print(line)
    print("  YouTube Data API v3  •  Инструмент поиска ранних трендов" if lang == "ru" else "  YouTube Data API v3  •  Trend hunting toolkit")
    print(f"  {t['developer']}: {DEVELOPER}")
    print("-" * 68)


def show_progress(label, current, total, finish=False):
    total = max(int(total), 1)
    current = min(max(int(current), 0), total)
    width = 28
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(100 * current / total)
    line = f"  {label:<28} [{bar}] {percent:3d}%  {current}/{total}"
    print("\r" + line + ("\n" if finish else ""), end="", flush=True)


def print_section(title):
    print(f"\n{'─' * 68}\n  {title}\n{'─' * 68}")


def print_summary(videos, lang):
    t = TEXT[lang]
    print_section(t["preview"])
    print(
        f"  {'#':>2}  "
        f"{'SCORE':>8}  "
        f"{'VIEWS':>9}  "
        f"{'CHANNEL':<18}  "
        f"{'TITLE'}"
    )
    print("  " + "─" * 64)

    for index, video in enumerate(videos[:15], 1):
        channel = video["channel"].replace("\n", " ")[:18]
        title = video["title"].replace("\n", " ")
        if len(title) > 38:
            title = title[:35] + "..."

        print(
            f"  {index:>2}  "
            f"{int(video['emerging_score']):>8,}  "
            f"{video['views']:>9,}  "
            f"{channel:<18}  "
            f"{title}"
        )


# ───────────────────────── экспорт результатов ─────────────────────────

def export_results(videos, lang, query_desc):
    t = TEXT[lang]
    output_dir = BASE_DIR / "youtube_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = output_dir / f"emerging_{timestamp}"

    columns = [
        ("title", "Title"),
        ("url", "URL"),
        ("channel", t["channel"]),
        ("subscribers", t["subs"]),
        ("region", "Region"),
        ("language", "Language"),
        ("published_str", t["published"]),
        ("duration", t["duration"]),
        ("views", t["views"]),
        ("likes", t["likes"]),
        ("comments", t["comments"]),
        ("age_days", t["age"]),
        ("views_per_hour", t["vph"]),
        ("views_per_sub", t["ratio"]),
        ("emerging_score", t["score"]),
        ("why", "Why"),
    ]

    # ── CSV ──
    with open(str(base) + ".csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow([t["title"]])
        writer.writerow([t["developer"], DEVELOPER])
        for name, link in CONTACTS:
            writer.writerow([name, link])
        writer.writerow(["Query / Mode", query_desc])
        writer.writerow(["Exported", timestamp])
        writer.writerow([])
        writer.writerow([label for _, label in columns])
        for row in videos:
            writer.writerow([cell_text(row.get(key), empty="") for key, _ in columns])

    # ── TXT ──
    with open(str(base) + ".txt", "w", encoding="utf-8") as file:
        file.write("YOUTUBE TREND ANALYZER\n")
        file.write("Ранний вход: молодое + быстрое + не гигант\n")
        file.write("=" * 80 + "\n")
        file.write(f"Всего видео: {len(videos)}\n")
        file.write(f"Дата выгрузки: {timestamp}\n\n")

        for i, video in enumerate(videos, 1):
            kind = "Shorts" if video.get("is_short") else "Обычное видео"
            file.write("=" * 80 + "\n")
            file.write(f"ВИДЕО #{i}\n")
            file.write("=" * 80 + "\n\n")
            file.write(f"Название: {video.get('title', '—')}\n")
            file.write(f"Канал: {video.get('channel', '—')}\n")
            file.write(f"Подписчики: {format_number(video.get('subscribers', 0))}\n")
            file.write(f"Страна канала: {video.get('region', '—')}\n")
            file.write(f"Язык: {video.get('language', '—')}\n")
            file.write(f"Дата публикации: {video.get('published_str', '—')}\n")
            file.write(f"Тип: {kind}\n")
            file.write(f"Длительность: {video.get('duration', '—')}\n")
            file.write(f"Просмотры: {format_number(video.get('views', 0))}\n")
            file.write(f"Лайки: {format_number(video.get('likes', 0))}\n")
            file.write(f"Комментарии: {format_number(video.get('comments', 0))}\n")
            file.write(f"Возраст: {video.get('age_days', 0):.1f} дн.\n")
            file.write(f"Просмотров в час: {format_number(int(video.get('views_per_hour', 0)))}\n")
            file.write(f"Просмотры / подписчики: {video.get('views_per_sub', 0):.2f}\n")
            file.write(f"Emerging score: {format_number(int(video.get('emerging_score', 0)))}\n")
            file.write(f"Почему это ранний вход: {video.get('why', '—')}\n")
            file.write(f"Ссылка: {video.get('url', '—')}\n\n")

    # ── OBSIDIAN MARKDOWN (.md) ──
    with open(str(base) + ".md", "w", encoding="utf-8") as file:
        file.write("---\n")
        file.write("type: youtube-trend-analysis\n")
        file.write(f"created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        file.write(f"query: \"{query_desc}\"\n")
        file.write(f"total_videos: {len(videos)}\n")
        file.write("tags:\n")
        file.write("  - youtube/analysis\n")
        file.write("  - youtube/trends\n")
        file.write("---\n\n")

        file.write(f"# 🚀 YouTube Trend Analyzer: `{query_desc}`\n\n")
        file.write(f"> **Дата сбора:** `{timestamp}` | **Всего находок:** `{len(videos)}` | **Разработчик:** [[Pavel Muv]]\n\n")

        file.write("## 📊 Сводная таблица (Obsidian View)\n\n")
        file.write("| # | Название | Канал | Просмотры | Возраст (дн.) | Score | Ссылка |\n")
        file.write("|---|---|---|---|---|---|---|\n")

        for i, v in enumerate(videos, 1):
            clean_title = v['title'].replace('|', '\\|').replace('\n', ' ')
            clean_channel = v['channel'].replace('|', '\\|').replace('\n', ' ')
            file.write(
                f"| {i} | {clean_title} | [[{clean_channel}]] | {format_number(v['views'])} | "
                f"{v['age_days']:.1f} | **{int(v['emerging_score'])}** | [Смотреть]({v['url']}) |\n"
            )

        file.write("\n\n---\n\n")
        file.write("## 🎯 Детальные карточки видео\n\n")

        for i, v in enumerate(videos, 1):
            file.write(f"### {i}. {v['title']}\n")
            file.write(f"- **Канал:** [[{v['channel']}]] ({format_number(v['subscribers'])} сабов, Страна: `{v['region']}`)\n")
            file.write(f"- **Метрики:** `{format_number(v['views'])}` просмотров | `{format_number(int(v['views_per_hour']))}` просм/час\n")
            file.write(f"- **Давность:** `{v['published_str']}` (`{v['age_days']:.1f}` дней)\n")
            file.write(f"- **Сигнал:** *{v['why']}*\n")
            file.write(f"- **Ссылка:** [Открыть на YouTube]({v['url']})\n\n")

    return base


# ───────────────────────── интерактивный выбор фильтров ─────────────────────────

def ask_excluded_regions():
    print("\n  Выберите страны для ИСКЛЮЧЕНИЯ из выдачи:")
    print("  (Введите номера через запятую, например: 1, 5, 12, либо '0' чтобы никого не исключать)")
    print("  " + "─" * 50)
    
    sorted_countries = sorted(COUNTRY_NAMES.items(), key=lambda x: x[1])
    for idx, (code, name) in enumerate(sorted_countries, 1):
        print(f"  {idx:>2}. {name} ({code})")
    print("  " + "─" * 50)
    
    raw = input("  Ваш выбор [0]: ").strip()
    if not raw or raw == "0":
        return set()
    
    excluded = set()
    parts = raw.replace(";", ",").split(",")
    for p in parts:
        p = p.strip()
        if p.isdigit():
            num = int(p)
            if 1 <= num <= len(sorted_countries):
                code, name = sorted_countries[num - 1]
                excluded.add(code)
                excluded.add(name)
    return excluded


def ask_topic_blocklist():
    print("\n  Выберите ТЕМАТИЧЕСКИЕ КАТЕГОРИИ для исключения:")
    print("  (Введите номера через запятую, например: 1, 3, либо '0' чтобы пропустить)")
    print("  " + "─" * 50)
    
    for idx, (title, _) in enumerate(TOPIC_CATEGORIES, 1):
        print(f"  {idx}. {title}")
    print("  " + "─" * 50)
    
    raw = input("  Ваш выбор [0]: ").strip()
    added_words = []
    
    if raw and raw != "0":
        parts = raw.replace(";", ",").split(",")
        for p in parts:
            p = p.strip()
            if p.isdigit():
                num = int(p)
                if 1 <= num <= len(TOPIC_CATEGORIES):
                    _, words = TOPIC_CATEGORIES[num - 1]
                    added_words.extend(words)
                    
    extra_block = input("\n  Доп. свои стоп-слова через запятую (Enter = пропустить): ").strip()
    if extra_block:
        added_words.extend([x.strip() for x in extra_block.split(",") if x.strip()])
        
    return added_words


# ───────────────────────── цикл работы ─────────────────────────

def ask_choice(prompt_text, allowed, invalid_text):
    print(f"\n  {prompt_text}")
    value = input("  > ").strip()
    if value not in allowed:
        print("  ! " + invalid_text)
        return None
    return value


def run_search(youtube, lang, first_run):
    t = TEXT[lang]

    print_section("НАСТРОЙКА ПОИСКА" if lang == "ru" else "SEARCH SETUP")

    video_type_choice = ask_choice(t["format_menu"], ("1", "2", "3"), t["invalid"])
    if video_type_choice is None:
        return True
    video_type = {"1": "all", "2": "shorts", "3": "normal"}[video_type_choice]

    period_choice = ask_choice(t["period_menu"], ("1", "2", "3", "4", "5", "6", "7", "8"), t["invalid"])
    if period_choice is None:
        return True
    
    max_age_days_map = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 7,
        "5": 30,
        "6": 90,
        "7": 180,
        "8": None
    }
    max_age_days = max_age_days_map[period_choice]

    mode = ask_choice(t["mode_menu"], ("1", "2", "3"), t["invalid"])
    if mode is None:
        return True

    keyword = ""
    if mode in ("2", "3"):
        prompt = t["query"] if first_run else t["next_query"]
        keyword = input(f"\n  {prompt}: ").strip()
        if keyword.casefold() in EXIT_WORDS:
            return False
        if mode == "2" and not keyword:
            print("  ! Пустой запрос.")
            return True

    try:
        raw_subs = input("  Макс. подписчиков канала [500000, 0 = без лимита]: ").strip()
        max_subs = int(raw_subs) if raw_subs else 500000
    except ValueError:
        max_subs = 500000

    try:
        raw_views = input("  Мин. просмотров [3000]: ").strip()
        min_views = int(raw_views) if raw_views else 3000
    except ValueError:
        min_views = 3000

    excluded_regions = ask_excluded_regions()

    # Сбор стоп-слов по темам и вручную
    blocklist = list(DEFAULT_BLOCKLIST)
    blocklist.extend(ask_topic_blocklist())

    pages = 1
    if mode in ("2", "3"):
        try:
            raw_p = input("  Страниц поиска по 50 [1, максимум 3]: ").strip()
            pages = max(1, min(int(raw_p or 1), 3))
        except ValueError:
            pages = 1

    try:
        count = int(input(f"  {t['count']} [макс. для вывода] [50]: ").strip() or "50")
    except ValueError:
        count = 50

    sort_choice = ask_choice(t["sort"], ("1", "2", "3", "4"), t["invalid"])
    if sort_choice is None:
        return True
    sort_by = {"1": "emerging", "2": "velocity", "3": "outlier", "4": "views"}[sort_choice]

    print_section(t["searching"])

    try:
        videos = []
        if mode in ("1", "3"):
            show_progress("Сбор трендов по регионам", 0, len(SCAN_REGIONS))
            videos.extend(collect_trending(
                youtube, max_age_days, SCAN_REGIONS,
                progress_callback=lambda c, tot, fin: show_progress("Сбор трендов по регионам", c, tot, fin)
            ))
            
            show_progress("Поиск по сидам заголовков", 0, 1)
            videos.extend(collect_seed_from_trending(
                youtube, videos, max_age_days, pages=1,
                progress_callback=lambda c, tot, fin: show_progress("Поиск по сидам заголовков", c, tot, fin)
            ))
            
        if mode in ("2", "3") and keyword:
            total_steps = 2 * pages
            show_progress(f"Поиск: {keyword}", 0, total_steps)
            videos.extend(collect_keyword(
                youtube, keyword, max_age_days, pages,
                progress_callback=lambda c, tot, fin: show_progress(f"Поиск: {keyword}", c, tot, fin)
            ))

        videos = dedupe(videos)
        if not videos:
            print("\n  ! Пусто. Смени период или слово.")
            return True

        show_progress("Обогащение каналов", 0, 1)
        enrich_channels(
            youtube, videos,
            progress_callback=lambda c, tot, fin: show_progress("Обогащение каналов", c, tot, fin)
        )

        videos = apply_filters(
            videos, video_type, max_age_days, min_views, max_subs, excluded_regions, blocklist
        )
        if not videos:
            print("\n  ! После фильтров пусто. Подними период или опусти мин. просмотры.")
            return True

        videos = sort_videos(videos, sort_by)
        videos = videos[:count]

        print_summary(videos, lang)

        query_desc = keyword if keyword else "Global Trends"
        base = export_results(videos, lang, query_desc)

        print_section(t["done"])
        print(f"  ✓ {t['selected']}: {len(videos)}")
        print(f"  ✓ {t['saved_to']}: {base.parent.resolve()}")
        print("\n  FILES / ФАЙЛЫ")
        for extension in (".csv", ".txt", ".md"):
            path = Path(str(base) + extension).resolve()
            print(f"  ✓ {path.name}")
            print(f"    {path}")

        print("\n" + "=" * 68)
        print(f"  {t['follow']}")
        print(f"  {t['developer']}: {DEVELOPER}")
        for name, link in CONTACTS:
            print(f"  {name:<8} ·  {link}")
        print("=" * 68)

    except HttpError as error:
        logging.exception("Data collection failed")
        if is_quota_error(error):
            print("\n  ✗ " + t["quota_exceeded"])
        elif is_key_error(error):
            print("\n  ✗ " + t["key_rejected"])
        else:
            print("\n  ✗ " + t["api_error"])
            print("  " + t["no_results"])

    except Exception:
        logging.exception("Search failed")
        print("\n  ✗ " + t["api_error"])
        print("  " + t["no_results"])

    return True


# ───────────────────────── точка входа ─────────────────────────

def main():
    try:
        lang = choose_language()
        t = TEXT[lang]
        print_header(lang)

        api_key = input(f"\n  {t['api_key']}: ").strip()
        if not api_key:
            print(f"\n  ! {t['api_error']}")
            return

        print(f"\n  [1/4] {t['checking']}")

        try:
            youtube = connect_api(api_key)
            print("  ✓ " + t["api_ok"])
        except Exception as error:
            logging.exception("API connection failed")
            if is_quota_error(error):
                print("  ✗ " + t["quota_exceeded"])
            else:
                print("  ✗ " + t["api_error"])
                print("  Проверьте API-ключ, доступ к API и интернет-соединение.")
            return

        first_run = True
        while run_search(youtube, lang, first_run):
            first_run = False

        print(f"\n  {t['bye']}\n")

    except (KeyboardInterrupt, EOFError):
        print("\n\n  Bye!\n")


if __name__ == "__main__":
    main()