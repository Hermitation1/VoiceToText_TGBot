# VoiceToText Telegram Bot

Telegram-бот для транскрибации голосовых сообщений, аудио, видео и видео-кружков в текст с помощью faster-whisper.

A Telegram bot that transcribes voice messages, audio, video, and video notes into text using faster-whisper.

---

## Возможности / Features

- Принимает голосовые, аудио, видео и видео-кружки
- Транскрибирует в текст в реальном времени
- Очередь сообщений — несколько файлов обрабатываются по порядку
- Система доступа — только одобренные пользователи
- Поддержка групп
- Русский и английский интерфейс
- Accepts voice messages, audio, video, and video notes
- Real-time transcription
- Message queue — multiple files processed in order
- Access control — approved users only
- Group chat support
- Bilingual UI (Russian / English)

## Стек / Stack

- Python 3.14
- aiogram 3.x
- faster-whisper (large-v3-turbo, CUDA)
- ffmpeg
- pydantic-settings
- uv (package manager)

## Установка / Setup

### Локально / Local

```bash
# Клонировать репозиторий / Clone the repo
git clone <repo-url>
cd VoiceToText_TGBot

# Установить зависимости / Install dependencies
uv sync

# Создать .env файл / Create .env file
cp .env.example .env
# Заполнить токены / Fill in tokens
```

### Docker

```bash
docker compose up -d
```

Требуется NVIDIA GPU с поддержкой CUDA.
Requires NVIDIA GPU with CUDA support.

## Конфигурация / Configuration

Создать `.env` файл / Create `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
OWNER_ID=your_telegram_user_id
PROXY_URL=http://proxy:port  # или / or пропустить / skip
HF_TOKEN=hf_your_huggingface_token
```

| Переменная / Variable | Описание / Description |
|---|---|
| `BOT_TOKEN` | Токен бота из @BotFather / Bot token from @BotFather |
| `OWNER_ID` | Telegram ID владельца (админа) / Owner's Telegram ID |
| `PROXY_URL` | Прокси для Telegram API (опционально) / Optional proxy |
| `HF_TOKEN` | Токен Hugging Face для скачивания модели / HF token for model download |

## Использование / Usage

1. `/start` — запросить доступ / request access
2. Владелец одобряет через inline-кнопки / Owner approves via inline buttons
3. Отправить голосовое, аудио, видео или видео-кружок / Send voice, audio, video or video note
4. Бот транскрибирует в текст / Bot transcribes to text

### Команды / Commands

| Команда / Command | Кто / Who | Описание / Description |
|---|---|---|
| `/start` | Все / All | Запросить доступ / Request access |
| `/help` | Все / All | Справка / Help |
| `/get_users` | Владелец / Owner | Список пользователей / User list |

## Структура проекта / Project Structure

```
.
├── bot.py              # Хендлеры и точка входа / Handlers & entry point
├── config.py           # Настройки / Settings (pydantic)
├── core.py             # Модель Whisper, Bot, Dispatcher
├── messages.py         # Тексты сообщений / Message texts (RU/EN)
├── middleware.py        # UserAccess + ProcessingMiddleware + очередь / queue
├── services.py         # Бизнес-логика / Business logic
├── pyproject.toml      # Зависимости и конфиг линтеров / Dependencies & linter config
├── Dockerfile
├── docker-compose.yml
├── allowed_users.json  # Данные пользователей / User data
├── hf_cache/           # Кеш моделей / Model cache
└── voice_files/        # Временные файлы / Temp files (tmpfs в Docker)
```

## Разработка / Development

```bash
# Линтинг и типизация / Lint & type check
ruff check .
mypy .

# Форматирование / Format
ruff format .
```

## Лицензия / License

MIT
