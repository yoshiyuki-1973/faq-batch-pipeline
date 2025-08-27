from __future__ import annotations

import os
import time
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tenacity import retry, wait_random_exponential, stop_after_attempt

# ==== 環境変数でモデルや処理サイズを調整可能 ====
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gpt-4o-mini")  # gpt-4o / gpt-4o-mini など
CHUNK_SIZE = int(os.getenv("SUMMARY_CHUNK_SIZE", "2000"))  # 1チャンクの目安（文字数）
CHUNK_OVERLAP = int(os.getenv("SUMMARY_CHUNK_OVERLAP", "200"))
MAX_CHUNKS = int(os.getenv("SUMMARY_MAX_CHUNKS", "30"))    # 念のための上限（多すぎる連投を防ぐ）
SLEEP_BETWEEN_CALLS = float(os.getenv("SUMMARY_SLEEP_SEC", "1.0"))  # 連続呼び出しの間隔（秒）


def _make_llm() -> ChatOpenAI:
    # 温度0でブレ低減。必要なら max_tokens, timeout などを追加
    return ChatOpenAI(model=SUMMARY_MODEL, temperature=0)


def _make_chunk_prompt() -> PromptTemplate:
    # JSON例の { } はテンプレ内で {{ }} と二重にして“文字”として扱う
    return PromptTemplate(
        input_variables=["text"],
        template=(
            "以下のテキストを日本語で簡潔に要約し、JSONのみを出力してください。\n"
            "出力フォーマットの例: {{\"summary\": \"...\"}}\n\n"
            "{text}"
        ),
    )


def _make_final_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["summaries"],
        template=(
            "以下は文書の部分要約の一覧です。重複や冗長表現を避け、"
            "全体像が一目で分かる**統合要約**を日本語で作成し、JSONのみを出力してください。\n"
            "出力フォーマットの例: {{\"summary\": \"...\"}}\n\n"
            "{summaries}"
        ),
    )


@retry(wait=wait_random_exponential(min=1, max=8), stop=stop_after_attempt(3))
def _invoke_json(chain, payload):
    """レート制限などで失敗した場合に指数バックオフで再試行。"""
    return chain.invoke(payload)


def generate_summary(docs: List) -> dict:
    """
    文書のリスト（LangChainのDocument想定）から要約JSONを返す。
    1) チャンク分割 → 2) 各チャンクを要約(JSON) → 3) 最終統合要約(JSON)
    """
    # 1) テキスト収集
    all_texts = [getattr(d, "page_content", "") for d in docs if getattr(d, "page_content", "")]
    base_text = "\n".join(all_texts).strip()
    if not base_text:
        return {"summary": ""}

    # 2) チャンク分割（文字数ベース）
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    # Document を再生成せずにテキストだけ分割
    chunks = splitter.split_text(base_text)
    if len(chunks) > MAX_CHUNKS:
        chunks = chunks[:MAX_CHUNKS]

    llm = _make_llm()
    parser = JsonOutputParser()

    # 各チャンク要約用チェーン
    chunk_chain = _make_chunk_prompt() | llm | parser

    chunk_summaries: List[str] = []
    for i, chunk in enumerate(chunks, start=1):
        try:
            result = _invoke_json(chunk_chain, {"text": chunk})
            # 期待: {"summary": "..."}
            if isinstance(result, dict) and "summary" in result:
                chunk_summaries.append(result["summary"])
            else:
                # 念のため素通し
                chunk_summaries.append(str(result))
        except Exception as e:
            # フォールバック（ここでこけても処理は継続）
            chunk_summaries.append(f"(チャンク{i}の要約取得に失敗: {e})")

        # 連続呼び出しで429を避けるため少し待機
        time.sleep(SLEEP_BETWEEN_CALLS)

    # 3) 最終統合要約
    final_chain = _make_final_prompt() | llm | parser
    summaries_joined = "\n- " + "\n- ".join(chunk_summaries)

    try:
        final_result = _invoke_json(final_chain, {"summaries": summaries_joined})
        if isinstance(final_result, dict) and "summary" in final_result:
            return final_result
        return {"summary": str(final_result)}
    except Exception as e:
        # どうしてもパースできなければ、部分要約の連結を返す
        return {"summary": " / ".join(chunk_summaries)}
