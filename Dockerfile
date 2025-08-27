FROM python:3.10-slim AS app

WORKDIR /app
COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-jpn \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# 先にpipを上げる → 依存解決が安定
RUN python -m pip install --upgrade pip

#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# 追加: tiktoken のキャッシュを作成（ビルド時に1回だけネット接続）
ENV TIKTOKEN_CACHE_DIR=/root/.cache/tiktoken
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"

# ここで freeze を出力
#RUN pip freeze > /app/pip_freeze.txt
#COPY . .

ENV PYTHONPATH="${PYTHONPATH}:/app"
CMD ["python", "app/main.py"]

