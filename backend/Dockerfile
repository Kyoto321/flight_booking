FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (add a few more for Playwright)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libxshmfence1 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 👉 Install Playwright (browser + deps INSIDE container)
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps

# Copy project
COPY . /app/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]









# FROM python:3.12-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Set work directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     libpq-dev \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# # Install python dependencies
# COPY requirements.txt /app/
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Copy project
# COPY . /app/
