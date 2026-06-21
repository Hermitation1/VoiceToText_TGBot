# VoiceToText Telegram Bot

Telegram-бот для транскрибации голосовых сообщений, аудио, видео и видео-кружков в текст с помощью faster-whisper.

A Telegram bot that transcribes voice messages, audio, video, and video notes into text using faster-whisper.

---

## Возможности / Features

- Принимает голосовые, аудио, видео и видео-кружки
- Транскрибирует в текст в реальном времени
- Очередь сообщений — несколько файлов обрабатываются по порядку
- Система доступа — только одобренные пользователи

- Accepts voice messages, audio, video, and video notes
- Real-time transcription
- Message queue — multiple files processed in order
- Access control — approved users only


## Стек / Stack

- Python 3.14
- aiogram 3.x
- faster-whisper (large-v3-turbo, CUDA — можно переключить на CPU, см. `core.py`)
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
### Windows

При локальном запуске на Windows faster-whisper может не найти
CUDA-библиотеки. Добавьте в `PATH`:

```
.venv\Lib\site-packages\nvidia\cublas\bin
.venv\Lib\site-packages\nvidia\cudnn\bin
.venv\Lib\site-packages\nvidia\cuda_runtime\bin
```

Или пропишите пути к локальной установке CUDA Toolkit и cuDNN.

When running locally on Windows, faster-whisper may fail to locate
CUDA libraries. Add to `PATH`:

```
.venv\Lib\site-packages\nvidia\cublas\bin
.venv\Lib\site-packages\nvidia\cudnn\bin
.venv\Lib\site-packages\nvidia\cuda_runtime\bin
```

Or set paths to your local CUDA Toolkit and cuDNN installation.

### Docker

```bash
docker compose up -d
```

Для полной и быстрой работы требуется NVIDIA GPU с CUDA.
Можно запустить на CPU (медленнее), изменив модель в `core.py`:
`WhisperModel("small", device="cpu", compute_type="int8")`

For best performance, NVIDIA GPU with CUDA is required.
Can run on CPU (slower) by switching the model in `core.py`:
`WhisperModel("small", device="cpu", compute_type="int8")`


## Конфигурация / Configuration

Создать `.env` файл / Create `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
OWNER_ID=your_telegram_user_id
PROXY_URL=http://proxy:port  # опционально / optional
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

Удалить пользователя можно кнопкой в списке `/get_users`.
Remove a user with the button in the `/get_users` list.

## Структура проекта / Project Structure

```
.
├── bot.py              # Хендлеры и точка входа / Handlers & entry point
├── config.py           # Настройки / Settings (pydantic)
├── core.py             # Модель Whisper, Bot, Dispatcher
├── messages.py         # Тексты сообщений / Message texts (RU/EN)
├── middleware.py        # UserAccess + ProcessingMiddleware + очередь / queue
├── services.py         # Бизнес-логика / Business logic
├── pyproject.toml      # Зависимости / Dependencies
├── Dockerfile
├── docker-compose.yml
├── allowed_users.json  # Данные пользователей / User data
├── hf_cache/           # Кеш моделей / Model cache
└── voice_files/        # Временные файлы / Temp files (tmpfs в Docker)
```

## Лицензия / License

MIT
