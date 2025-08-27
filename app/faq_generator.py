from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def generate_faq(docs):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = JsonOutputParser()

    prompt = PromptTemplate(
        input_variables=["text", "source_hint"],
        template=(
            "以下のテキストを元に、日本語のFAQ（質問と回答）を5件作成してください。"
            "出力は厳密なJSONのみとし、配列で返してください。各要素は "
            "{{\"question\": \"...\", \"answer\": \"...\", \"source\": \"{source_hint}\", \"page\": 1}} "
            "のキーを持ちます。source には元ファイル名を、page には推定ページ番号を入れてください。"
            "不明な場合は page は null としてください。\n\n"
            "{text}"
        ),
    )

    chain = prompt | llm | parser

    text = "\n".join(doc.page_content for doc in docs if getattr(doc, "page_content", ""))
    # source名のヒント（最初のdocから）
    source_hint = ""
    for d in docs:
        meta = getattr(d, "metadata", {}) or {}
        if "source" in meta:
            source_hint = str(meta["source"])
            break

    try:
        result = chain.invoke({"text": text, "source_hint": source_hint})
        # 期待は list[dict]
        if isinstance(result, list):
            return result
    except Exception:
        pass

    # フォールバック（JSONが壊れた時）
    return [{
        "question": "この文書の要点は？",
        "answer": "FAQのJSON生成に失敗しました。後続で再試行してください。",
        "source": source_hint,
        "page": None
    }]
