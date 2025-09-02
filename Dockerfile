# Stage 1: Build python dependencies
FROM docker.io/library/python:3.12-slim-bookworm AS builder

ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY

# Install pdm
RUN pip install --no-cache-dir pdm

WORKDIR /app

# Create and activate a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy dependency definition file
COPY pyproject.toml ./
COPY README.md ./

# Install python dependencies into the virtual environment
# This layer is cached as long as pyproject.toml doesn't change
RUN pdm install --prod

# Stage 2: Final application image
FROM docker.io/library/python:3.12-slim-bookworm

ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY

WORKDIR /app

# Add venv to the PATH, this should be early to be available for subsequent commands
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install runtime system dependencies for fonts (wget, unzip) and healthcheck (curl)
# Playwright dependencies will be installed later
RUN apt update && apt install -y wget unzip curl \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# 1. Download and install fonts
RUN mkdir -p data/font && \
    FONT_URL="https://mirrors.bfsu.edu.cn/pypi/web/packages/ad/97/03cd0a15291c6c193260d97586c4adf37a7277d8ae4507d68566c5757a6a/bbot_fonts-0.1.1-py3-none-any.whl" && \
    wget -O /tmp/bbot_fonts.whl $FONT_URL && \
    unzip /tmp/bbot_fonts.whl bbot_fonts/font/* -d data/font/ && \
    rm /tmp/bbot_fonts.whl && \
    mv data/font/bbot_fonts/font/* data/font/ && \
    rm -rf data/font/bbot_fonts && \
    printf "%s" "$FONT_URL" > data/font/.lock

# 2. Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# 3. Install playwright browser and its system dependencies
# This command also runs apt update/install for browser-specific libraries
RUN playwright install firefox --with-deps \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the application source code
COPY . .

# 5. Subsequent processes
EXPOSE 40432
ENV API_HOST=0.0.0.0
ENV DOCKER=true
ENV TZ=Asia/Shanghai

HEALTHCHECK --interval=60s --timeout=2s --start-period=30s --retries=5 CMD curl -f http://localhost:40432/health || exit 1

# Start the server
CMD ["/opt/venv/bin/python", "start_server.py"]
