# Usa uma versão compatível do Python
FROM python:3.9

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    espeak \
    libespeak1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

COPY .env.example .env

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
