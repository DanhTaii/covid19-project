import pandas as pd
import os
import sys

# import VectorDB
from langchain_community.vectorstores import FAISS
# Dùng để biến dạng trả về của LLM thành String
from langchain_core.output_parsers import StrOutputParser
# Dùng cho template dạng String thành ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
# Dùng để nhận vào input và truyền thẳng vào question
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# Dùng cho khởi tạo model LLM trực tuyến, số hóa văn bản
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings, ChatHuggingFace
# Dùng cho văn bản hóa
from langchain_core.documents import Document
from dotenv import load_dotenv
from pathlib import Path

# Lấy ra file trong thư mục hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__))
# Lùi về trước đó 2 thư mục
backend_dir = os.path.abspath(os.path.join(current_dir, "../../"))

base_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = base_dir / '.env'

# Thêm vào hệ thống tìm kiếm của Python
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from core.data.update_data import load_data_from_parquet

# Lấy dữ liệu từ file đã được preprocessing
df = load_data_from_parquet()
df_small = df[['location', 'date' ,'new_cases', 'new_deaths']].tail(50)

# Lấy API của LLM về để sử dụng trực tuyến
load_dotenv(dotenv_path=env_path)
hf_token = os.getenv("HF_TOKEN")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

# Chuyển đổi dữ liệu thành văn bản
docs = [
    Document(
        # Tạo ra 1 câu tiếng việt hoàn chỉnh
        page_content=f"Tại {r['location']} ngày {r['date']}, ghi nhận {r['new_cases']} ca nhiễm và {r['new_deaths']} ca tử vọng",
        # Lưu dữ liệu như dạng JSON
        metadata=r.to_dict()
    )
    # Duyệt qua từng dòng trong DataFrame
    for _, r in df_small.iterrows()
]

# LLM không hiểu List chỉ hiểu văn bản nên phải biến nó thành String
def format_doc(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Khởi tạo mô hình ngôn ngữ lớn (LLM)
llm_endpoint = HuggingFaceEndpoint(
    # Model muốn dùng
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    # Nói cho HuggingFace biết là dùng để sinh ra văn bản
    task="text-generation",
    # Gioiws hạn số token được sinh ra => Tránh trả lời quá dài
    max_new_tokens=512,
    # Giamr việc model lặp lại chữ
    repetition_penalty=1.03,
    # Lấy API token từ biến mỗi trường
    huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"]
)

# Khởi tạo mô hình embedding => Nhận văn bản và trả về vector số
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Lấy từng Document trong docs và dùng embeddings để embed page_content và lưu vào DB
vectorstore = FAISS.from_documents(
    documents=docs,
    embedding=embeddings
)

# Là bộ tìm kiếm tài liệu liên quan
# Nhận vào câu hỏi và Embed nó rồi so vector mới embed với toàn bộ vector trong FAISS
# Trả về 'k' document gần nhất
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Bọc llm_endpoint lại và biến nó thành Chat Model
chat_llm = ChatHuggingFace(llm=llm_endpoint)

# Gán role cho LLM và bắt LLM chỉ trả lời trong context không bịa
template = """ Bạn là trợ lý ảo Covid-19. Trả lời câu hỏi dựa trên ngữ cảnh sau:
{context}

Câu hỏi: {question}
Trả lời:"""

# Dùng cho template dạng String thành ChatPromptTemplate
prompt = ChatPromptTemplate.from_template(template)
# format_docs_runnable = RunnableLambda(format_doc)

rag_chain = (
    {
        # Nhận được question rồi retriver hđ và trả về List[Document]
        # Đưa List[Document] cho format_doc để nó chuyển về String
        "context": retriever | format_doc,
        # để nhận vào input và truyền thẳng vào question
        "question": RunnablePassthrough()
    }
    # LangChain tự gán {context} và {question}
    | prompt
    # Gửi prompt sang cho Qwen Chat Model sinh câu trả lời
    | chat_llm
    # Chuyển AIMessage(content="...") thành "..."
    | StrOutputParser()
)

# --- CHẠY THỬ ---
if __name__ == "__main__":
    query = "Việt Nam đến nay đã có bao nhiêu ca mắc covid rồi?"
    # Sử dụng invoke thay cho run
    result = rag_chain.invoke(query)
    print(f"Q: {query}")
    print(f"A: {result}")
