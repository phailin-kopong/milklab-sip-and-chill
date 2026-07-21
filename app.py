import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai
import os

# 1. ตั้งค่า API Key สำหรับ Gemini
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
if api_key:
    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("กรุณาใส่ GEMINI_API_KEY ใน Streamlit Secrets")

# 2. ฟังก์ชันโหลด Embeddings และสร้าง FAISS Index
@st.cache_resource
def load_rag_components():
    embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    with open("menu_kb.md", "r", encoding="utf-8") as f:
        text = f.read()
    chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 10]
    
    embeddings = embedder.encode(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return embedder, index, chunks

embedder, index, chunks = load_rag_components()

# 3. Streamlit Chat UI
st.title("MilkLab° RAG Chatbot")
st.caption("ถามอะไรเกี่ยวกับ MilkLab ได้ ตอบจาก menu_kb.md")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("ถามข้อมูลร้าน MilkLab ได้เลยครับ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # 4. Retrieval (ดึง Top-3 Chunks)
    query_vec = embedder.encode([prompt])
    distances, indices = index.search(np.array(query_vec), 3)
    retrieved_context = "\n---\n".join([chunks[i] for i in indices[0]])
    
    # 5. สร้าง Prompt และเรียก Gemini
    full_prompt = f"""คุณคือพนักงานร้าน MilkLab ตอบคำถามลูกค้าโดยอ้างอิงจากข้อมูลต่อไปนี้เท่านั้น:
{retrieved_context}

คำถาม: {prompt}"""
    
    try:
        response = llm.generate_content(full_prompt)
        reply = response.text
    except Exception as e:
        reply = f"เกิดข้อผิดพลาดในการเชื่อมต่อ Gemini: {e}"
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
