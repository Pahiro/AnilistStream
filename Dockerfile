FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY . .

RUN uv sync

CMD ["uv", "run", "main.py"]

EXPOSE 8000
