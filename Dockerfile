# ---- Base image ----
    FROM python:3.11-slim

    # ---- Environment ----
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    WORKDIR /app
    
    # ---- Install OS deps ----
    RUN apt-get update && apt-get install -y \
        curl \
        wget \
        gnupg \
        libnss3 \
        libxss1 \
        libasound2 \
        libx11-xcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxi6 \
        libxtst6 \
        libglib2.0-0 \
        libgtk-3-0 \
        libgbm1 \
        libxrandr2 \
        libu2f-udev \
        fonts-liberation \
        ca-certificates \
        unzip \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # ---- Install Python deps ----
    COPY requirements.txt .
    RUN pip install --upgrade pip
    RUN pip install --no-cache-dir -r requirements.txt
    
    # ---- Install Playwright + browsers ----
    RUN pip install playwright
    RUN playwright install --with-deps chromium
    
    # ---- Copy app ----
    COPY . .
    
    # ---- Entrypoint ----
    CMD ["python3", "main.py"]
    