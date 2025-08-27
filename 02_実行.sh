#!/usr/bin/env bash
set -euo pipefail

OPENAI_PROXY=""
HTTP_PROXY=""
HTTPS_PROXY=""
ALL_PROXY=""

docker run --rm   --env-file .env   -e OPENAI_PROXY="$OPENAI_PROXY"   -e HTTP_PROXY="$HTTP_PROXY"   -e HTTPS_PROXY="$HTTPS_PROXY"   -e ALL_PROXY="$ALL_PROXY"   -v "$PWD/data:/app/data"   -v "$PWD/faiss_store:/app/faiss_store"   faq-batch

echo "===== 実行完了 ====="
