#!/usr/bin/env bash
set -euo pipefail

echo "[1/1] Docker イメージをビルドします..."
docker build -t faq-batch .

echo "✅ Build 完了: faq-batch"
