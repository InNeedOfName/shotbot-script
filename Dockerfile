FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt update && apt install -y \
        libcairo2-dev \
        libjpeg-dev \
        libgif-dev \
        && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "main.py"]
