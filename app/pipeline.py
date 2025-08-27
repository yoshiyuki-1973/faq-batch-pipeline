import os
import sys
import json
import time
import shutil
from typing import List

from app.pdf_loader import load_pdf_with_ocr
from app.summarizer import generate_summary
from app.faq_generator import generate_faq
from app.vector_store import store_documents


def _safe_json_dump(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _unique_dest_path(dest_dir: str, filename: str) -> str:
    dest = os.path.join(dest_dir, filename)
    if not os.path.exists(dest):
        return dest
    name, ext = os.path.splitext(filename)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return os.path.join(dest_dir, f"{name}_{stamp}{ext}")


def run_batch_pipeline():
    input_dir = "data/input"
    output_dir = "data/output"
    processed_dir = "data/processed"
    faiss_dir = "faiss_store"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(faiss_dir, exist_ok=True)

    rerun_existing = os.getenv("RERUN_EXISTING", "false").lower() == "true"

    if sys.stdin.isatty():
        ans = input("すでに処理済みのPDFがある場合、再処理しますか？ (y/n): ").strip().lower()
        rerun_existing = (ans == "y")

    move_processed = os.getenv("MOVE_PROCESSED", "true").lower() == "true"

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("入力PDFが見つかりませんでした（data/input を確認してください）。")
        return

    for file_name in pdf_files:
        input_path = os.path.join(input_dir, file_name)
        base = os.path.splitext(file_name)[0]
        summary_path = os.path.join(output_dir, f"{base}_summary.json")
        faq_path = os.path.join(output_dir, f"{base}_faq.json")

        if not rerun_existing and os.path.exists(summary_path) and os.path.exists(faq_path):
            print(f"スキップ: {file_name}（既に処理済み）")
            continue

        print(f"処理中: {input_path}")
        try:
            docs = load_pdf_with_ocr(input_path)
            if not docs:
                raise RuntimeError("PDFからテキストを抽出できませんでした。")

            store_documents(docs, faiss_dir)

            summary = generate_summary(docs)
            _safe_json_dump(summary_path, summary)

            faq = generate_faq(docs)
            _safe_json_dump(faq_path, faq)

            if move_processed:
                dest_path = _unique_dest_path(processed_dir, file_name)
                shutil.move(input_path, dest_path)
                print(f"✅ 完了: {file_name} → {dest_path}")
            else:
                print(f"✅ 完了: {file_name}（移動は無効化）")

        except Exception as e:
            print(f"❌ エラー: {file_name} ({e})")
