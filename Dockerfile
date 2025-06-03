FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt update && apt install -y wget unzip curl \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

COPY . ./app
WORKDIR /app

RUN mkdir -p data/font && \
    FONT_URL="https://mirrors.bfsu.edu.cn/pypi/web/packages/ad/97/03cd0a15291c6c193260d97586c4adf37a7277d8ae4507d68566c5757a6a/bbot_fonts-0.1.1-py3-none-any.whl" && \
    wget -O /tmp/bbot_fonts.whl $FONT_URL && \
    unzip /tmp/bbot_fonts.whl bbot_fonts/font/* -d data/font/ && \
    rm /tmp/bbot_fonts.whl && \
    mv data/font/bbot_fonts/font/* data/font/ && \
    rm -rf data/font/bbot_fonts && \
    printf "%s" "$FONT_URL" > data/font/.lock

RUN uv sync --no-dev --no-cache \
    && rm -rf /root/.uv

RUN uv run playwright install firefox --with-deps \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 40432
ENV API_HOST=0.0.0.0

HEALTHCHECK --interval=60s --timeout=2s --start-period=30s --retries=5 CMD curl -f http://localhost:40432/bilichatapi/version || exit 1

ENV TZ=Asia/Shanghai

CMD ["uv", "run", "python", "start_server.py"]
