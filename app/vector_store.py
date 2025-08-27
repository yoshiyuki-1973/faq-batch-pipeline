from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter  # 旧
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 新

def store_documents(docs, faiss_dir):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    vectorstore.save_local(faiss_dir)
