import fitz
from pdf2image import convert_from_path
import pytesseract
# from langchain.schema import Document  # 旧
from langchain_core.documents import Document  # 新

def load_pdf_with_ocr(file_path):
    docs = []
    pdf_file = fitz.open(file_path)
    for page_number, page in enumerate(pdf_file, start=1):
        text = page.get_text()
        if not text.strip():
            images = convert_from_path(file_path, first_page=page_number, last_page=page_number)
            text = pytesseract.image_to_string(images[0], lang="jpn+eng")
        metadata = {"source": file_path, "page": page_number}
        docs.append(Document(page_content=text, metadata=metadata))
    return docs
