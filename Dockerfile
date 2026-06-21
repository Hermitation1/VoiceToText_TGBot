FROM python:3.14.4-slim

RUN apt update && apt install -y ffmpeg
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN useradd -m botuser
USER botuser
WORKDIR /home/botuser/tgbot

ENV LD_LIBRARY_PATH="/home/botuser/tgbot/.venv/lib/python3.14/site-packages/nvidia/cublas/lib/:\
                     /home/botuser/tgbot/.venv/lib/python3.14/site-packages/nvidia/cuda_runtime/lib/:\
                     /home/botuser/tgbot/.venv/lib/python3.14/site-packages/nvidia/cudnn/lib/"

COPY --chown=botuser:botuser ./pyproject.toml .
COPY --chown=botuser:botuser ./uv.lock .

RUN uv sync

COPY --chown=botuser:botuser . .

CMD [".venv/bin/python", "bot.py"]