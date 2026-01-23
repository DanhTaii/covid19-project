import pandas as pd
import os
import sys

# import VectorDB
from langchain_community.vectorstores import FAISS
# Dùng cho khởi tạo model LLM trực tuyến, số hóa văn bản
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings, ChatHuggingFace
# Dùng cho văn bản hóa
from langchain_core.documents import Document

current_dir = os.path.dirname(os.path.abspath(__file__))
# root_dir: E:/Python/covid19-project (Lùi 3 cấp)
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
print(f"--- ĐƯỜNG DẪN ROOT MÀ TÔI TÌM ĐƯỢC: {root_dir} ---")
print(f"ĐƯỜNG DẪN HIỆN TẠI LÀ : {current_dir}")
save_path = os.path.join(current_dir, "..", "data", "faiss_covid_index")
print(F"ĐƯỜNG DẪN ĐẾN CHỖ LƯU: {save_path}")

if root_dir not in sys.path:
    sys.path.append(root_dir)

# Bây giờ bạn có thể gọi thoải mái:
from backend.core.data.update_data import load_data_from_parquet
# from backend.chatbot.services.engine import some_function # Thậm chí gọi ngược lại backend cũng được

# Lấy dữ liệu từ file đã được preprocessing
df = load_data_from_parquet()
df_vn = df[df['location'] == 'Vietnam']

df_small = df_vn[['location', 'date' ,'new_cases', 'new_deaths']]


def build_vector_db():
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

    # Khởi tạo mô hình embedding => Nhận văn bản và trả về vector số
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Lấy từng Document trong docs và dùng embeddings để embed page_content và lưu vào DB
    vectorstore = FAISS.from_documents(
        documents=docs,
        embedding=embeddings
    )
    vectorstore.save_local(save_path)
    print("Đã lưu VectorDB thành công!")

# if __name__ == "__main__":
#     build_vector_db()

