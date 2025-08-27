#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "[ERROR] .env が見つかりません。" >&2
  exit 1
fi

docker run -it --rm   --env-file .env   -v "$PWD/data:/app/data"   -v "$PWD/faiss_store:/app/faiss_store"   faq-batch   /bin/bash
