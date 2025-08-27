# 🎉 FAQ & 要約バッチ処理システム

AI ✨ を活用して、PDFから **FAQ作成** と **要約** を自動生成するバッチ処理システム。  
RAG（Retrieval-Augmented Generation）＋ FAISS で検索、OpenAI API で生成、Dockerで再現性ばっちり。🚀

---

## 📦 プロジェクト構成（ディレクトリツリー）

```text
.
├─ app/                                   # 🧠 アプリ本体（Python）
│  ├─ main.py                             # ▶️ エントリーポイント（バッチ起動）
│  ├─ pipeline.py                         # 🔄 全体フロー（入出力、再処理フラグ）
│  ├─ pdf_loader.py                       # 📄 PDF読込 & 🖼️ OCR（PyMuPDF + Tesseract）
│  ├─ summarizer.py                       # 📝 要約生成（OpenAI + Prompt）
│  ├─ faq_generator.py                    # ❓ FAQ生成（OpenAI + Prompt）
│  └─ vector_store.py                     # 📚 ベクトル化&FAISS永続化
│
├─ data/
│  ├─ input/                              # 📥 入力PDFを置く（例: *.pdf）
│  └─ output/                             # 📤 生成物（*.json: 要約/FAQ）
│
├─ faiss_store/                           # 💾 ベクトルストア（FAISS）永続化
│   ├─ index.faiss / index.pkl ...        #   （内部ファイル一式）
│
├─ Dockerfile                             # 🐳 Dockerビルド定義
├─ requirements.txt                       # 📦 依存パッケージ（バージョン固定）
├─ .env                           # 🔑 環境変数（OPENAI_API_KEY）
├─ .dockerignore（推奨）                   # 🧹 ビルド対象から除外
└─ README.md                              # 📘 このドキュメント
```

---

## 🗺️ 各モジュールの役割

- **`app/main.py`**：最小限。`pipeline.run_batch_pipeline()` を呼ぶだけ → 起動責務を分離  
- **`app/pipeline.py`**：I/Oとオーケストレーション。  
  - `data/input/*.pdf` を巡回  
  - 既処理スキップ／再処理は **環境変数 `RERUN_EXISTING=true`** または `-it` 実行時の対話で制御  
  - `data/output/*.json` へ保存、`faiss_store/` へ永続化  
- **`app/pdf_loader.py`**：  
  - **テキストPDF** → 文字抽出（PyMuPDF）  
  - **画像PDF** → 1ページずつ画像化（pdf2image）→ **Tesseract（`jpn+eng`）** でOCR  
  - メタ情報（`source`, `page`）を付与して `Document` として返却  
- **`app/summarizer.py`**：  
  - `PromptTemplate` + `ChatOpenAI`（`gpt-4o`/`gpt-4o-mini` 推奨）  
  - **`prompt | llm | JsonOutputParser`** 構成で **厳密JSON** を返す  
  - 長文は将来のために**チャンク要約→統合**の拡張が容易な設計  
- **`app/faq_generator.py`**：  
  - 文書から日本語 FAQ（`[{question, answer, source, page}]`）を生成  
  - JSON破損時のフォールバックを実装  
- **`app/vector_store.py`**：  
  - `RecursiveCharacterTextSplitter` で分割 → `OpenAIEmbeddings`（`text-embedding-3-small`）→ **FAISS**  
  - `faiss_store/` 配下に **save_local**（Dockerボリュームで永続化）

---

## ⚙️ セットアップ（Dockerのビルド）

1️⃣ `.env` を作成（`.env.example` をコピーして編集）
```env
OPENAI_API_KEY=sk-xxxx...
```

2️⃣ 依存とOCR付きのイメージをビルド
```bash
docker build -t faq-batch .
```

> 🧰 遅い時は **BuildKit** と **pipキャッシュ**を有効化：
> ```bash
> DOCKER_BUILDKIT=1 docker build -t faq-batch .
> ```

---

## 🚀 実行方法（バッチ）

### 非対話（既存結果はスキップ）
```bash
docker run --rm --env-file .env   -e RERUN_EXISTING=false   -v "$PWD/data:/app/data"   -v "$PWD/faiss_store:/app/faiss_store"   faq-batch
```

### 非対話（再処理オン）
```bash
docker run --rm --env-file .env   -e RERUN_EXISTING=true   -v "$PWD/data:/app/data"   -v "$PWD/faiss_store:/app/faiss_store"   faq-batch
```

### 対話（`y/n` を聞く）※Windowsは `-it` を付ける
```bash
docker run -it --rm --env-file .env   -v "%cd%/data:/app/data"   -v "%cd%/faiss_store:/app/faiss_store"   faq-batch
```

- 📥 入力：`data/input/` に PDF を置く  
- 📑 出力：`data/output/` に `*_summary.json` と `*_faq.json`  
- 💾 インデックス：`faiss_store/` に FAISS が永続化

---

## 💡 スクリプト概要

| ファイル | 役割 |
|---|---|
| `main.py` | 起動用。CLI/バッチから呼ばれてもシンプル |
| `pipeline.py` | I/Oループ・再処理判定・各処理の呼び出し |
| `pdf_loader.py` | **PyMuPDF**でテキスト、**pdf2image+Tesseract**で画像OCR |
| `summarizer.py` | `prompt | llm | JsonOutputParser` で **厳密JSON要約** |
| `faq_generator.py` | JSON配列のFAQ生成（source/page含む） |
| `vector_store.py` | 分割→埋め込み→**FAISS**保存（`text-embedding-3-small`を明示） |

---

---

## ✍️ 作者

- 名前: 遠藤義之
- GitHub: [@yoshiyuki-1973](https://github.com/yourusername)

---

## 🏃 バッチファイル / シェルスクリプトでの実行

### Windows（ダブルクリックOK）
- `01_build.bat` : Dockerイメージをビルド
- `02_run.bat` : バッチ処理を実行（`data/input` のPDFを処理）
- `03_test.bat` : Docker内で pytest を実行

### Mac / Linux
```bash
chmod +x 01_build.sh 02_run.sh 03_test.sh

./01_build.sh   # ビルド
./02_run.sh     # 実行
./03_test.sh    # テスト（Dockerでpytest）
```
