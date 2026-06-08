FROM python:3.14.4-slim

ENV LD_LIBRARY_PATH="/tgbot/.venv/lib/python3.14/site-packages/nvidia/cublas/lib/:\
                     /tgbot/.venv/lib/python3.14/site-packages/nvidia/cuda_runtime/lib/:\
                     /tgbot/.venv/lib/python3.14/site-packages/nvidia/cudnn/lib/"

RUN apt update && apt install -y ffmpeg
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR tgbot

COPY ./pyproject.toml .
COPY ./uv.lock .

RUN uv sync

COPY . .

CMD [".venv/bin/python", "bot.py"]