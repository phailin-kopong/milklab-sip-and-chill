# Cozy Toes RAG Chatbot (S4 Pivot)
# Run locally: streamlit run app.py

import os
import json
import time
import uuid
from datetime import datetime

import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# นำเข้าโมดูล Gemini
from google import genai

# ==========================================
# ดึง API Key อย่างปลอดภัย
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

if not api_key:
    st.error("🚨 ไม่พบ API Key! กรุณาตั้งค่า GEMINI_API_KEY ไว้ใน Environment Variable หรือ Streamlit Secrets")
    st.stop()

# สร้าง Client โดยใช้ genai
client = genai.Client(api_key=api_key)


# ==========================================
# ฟังก์ชันระบบ RAG
# ==========================================
@st.cache_resource
def load_index():
    """โหลด cozytoes_kb.md, split เป็น chunk, encode ด้วย sentence-transformers, สร้าง faiss index."""
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # 🚨 เปลี่ยนชื่อไฟล์เป็นร้านถุงเท้า Cozy Toes
    try:
        with open("cozytoes_kb.md", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        st.error("ไม่พบไฟล์ cozytoes_kb.md กรุณาสร้างไฟล์ข้อมูลก่อนครับ")
        st.stop()

    chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 10]

    embeddings = model.encode(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return model, index, chunks


def retrieve_top_k(query: str, model, index, chunks: list[str], k: int = 3) -> list[str]:
    """ค้นหาข้อมูลที่เกี่ยวข้องที่สุดจากคำถาม"""
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), k)

    retrieved_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
    return retrieved_chunks


def generate_answer(query: str, context_chunks: list[str]) -> str:
    """ส่ง query + context ไป Gemini, return answer"""
    context = "\n---\n".join(context_chunks)

    # 🚨 เปลี่ยน Prompt เป็นพนักงานร้านขายถุงเท้า Cozy Toes
    prompt = f"""คุณคือพนักงานบริการลูกค้าของร้านขายถุงเท้าออนไลน์ Cozy Toes 
ตอบคำถามลูกค้าโดยอ้างอิงจากข้อมูล(Context)ด้านล่างนี้เท่านั้น 
ถ้าในข้อมูลไม่มีคำตอบ ให้ตอบอย่างสุภาพว่า "ไม่มีข้อมูลในส่วนนี้นะคะ ขออภัยด้วยค่ะ" ห้ามเดาข้อมูลเองเด็ดขาด

ข้อมูลของร้าน (Context):
{context}

คำถามจากลูกค้า: {query}
"""
    # ใช้โมเดล gemini-3.6-flash ตามที่เครื่องคุณรองรับ
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )
    return response.text


# ==========================================
# ส่วนแสดงผล Streamlit (UI)
# ==========================================
def main():
    # 🚨 เปลี่ยนหน้าตา UI เป็นร้าน Cozy Toes
    st.set_page_config(page_title="Cozy Toes RAG", page_icon="🧦")
    st.title("🧦 Cozy Toes RAG Chatbot")
    st.caption(
        "ถามข้อมูลไซส์ โปรโมชัน และถุงเท้าของ Cozy Toes ได้เลย (อ้างอิงจาก cozytoes_kb.md)")

    # โหลด RAG Components
    try:
        model, index, chunks = load_index()
    except Exception as exc:
        st.error(f"เกิดข้อผิดพลาดในการโหลดระบบ: {exc}")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 🚨 เปลี่ยนข้อความในช่องกรอกคำถาม
    if prompt := st.chat_input("สอบถามเรื่องถุงเท้า ไซส์ หรือโปรโมชันจัดส่งได้เลยค่ะ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("กำลังหาข้อมูลถุงเท้าให้ค่ะ..."):

                trace_id = str(uuid.uuid4())
                trace_data = {
                    "trace_id": trace_id,
                    "timestamp": datetime.now().isoformat(),
                    "query": prompt,
                    "spans": []
                }

                start_ret = time.time()
                context = retrieve_top_k(prompt, model, index, chunks)
                ret_duration = time.time() - start_ret
                trace_data["spans"].append(
                    {"name": "retrieve_top_k", "duration_sec": round(ret_duration, 4)})

                start_gen = time.time()
                answer = generate_answer(prompt, context)
                gen_duration = time.time() - start_gen
                trace_data["spans"].append(
                    {"name": "generate_answer", "duration_sec": round(gen_duration, 4)})

                with open("traces.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(trace_data, ensure_ascii=False) + "\n")

            st.write(answer)

            with st.expander("🔍 Trace (Observability)"):
                st.json(trace_data)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
