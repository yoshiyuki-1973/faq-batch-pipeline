#!/usr/bin/env bash
set -euo pipefail

read -r -p "data/output と faiss_store を削除して再作成します。続行しますか？ [y/N]: " ans
ans=${ans:-N}
if [[ ! "$ans" =~ ^[yY]$ ]]; then
  echo "キャンセルしました。"
  exit 0
fi

rm -rf "./data/output" "./faiss_store"
mkdir -p "./data/output" "./faiss_store"

echo "✅ クリーン完了: data/output, faiss_store"
