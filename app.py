# MilkLab RAG Chatbot(S3)
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
import google.generativeai as genai

# 1. ตั้งค่า API Key สำหรับ Gemini
api_key = os.environ.get("GEMINI_API_KEY")

# --- เติม 2 บรรทัดนี้เพื่อให้ระบบรู้จักตัวแปร llm ---
genai.configure(api_key=api_key)
llm = genai.GenerativeModel('gemini-3.6-flash')
# ----------------------------------------

# 2. ฟังก์ชันโหลด Embeddings และสร้าง FAISS Index


@st.cache_resource
def load_index():
    """TODO 1+2+3: โหลด menu_kb.md, split เป็น chunk, encode ด้วย sentence-transformers, สร้าง faiss index."""
    # โหลด Embedding Model แบบรองรับภาษาไทย/Multilingual
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # อ่านไฟล์และทำ Text Splitting เป็น Chunks
    try:
        with open("menu_kb.md", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        st.error("ไม่พบไฟล์ menu_kb.md กรุณาสร้างไฟล์ข้อมูลก่อนครับ")
        st.stop()

    chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 10]

    # สร้าง FAISS Index
    embeddings = model.encode(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return model, index, chunks


def retrieve_top_k(query: str, model, index, chunks: list[str], k: int = 3) -> list[str]:
    """TODO 4: encode query, search index, return top-k chunks"""
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), k)

    # ดึงข้อความจาก chunks ตาม index ที่ FAISS ค้นหาเจอ
    retrieved_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
    return retrieved_chunks


def generate_answer(query: str, context_chunks: list[str]) -> str:
    """TODO 5: ส่ง query + context ไป Gemini, return answer"""
    # นำ Chunk มาต่อกัน
    context = "\n---\n".join(context_chunks)

    # สร้าง Prompt บังคับให้ตอบจาก Context เท่านั้น (ปรับคำพูดเมื่อหาไม่เจอที่นี่)
    prompt = f"""คุณคือพนักงานต้อนรับและให้ข้อมูลของร้าน MilkLab 
ตอบคำถามลูกค้าโดยอ้างอิงจากข้อมูล(Context)ด้านล่างนี้เท่านั้น 
ถ้าในข้อมูลไม่มีคำตอบ ให้ตอบอย่างสุภาพว่า "ไม่มีค่ะ ขออภัยด้วยนะคะ" ห้ามเดาข้อมูลเองเด็ดขาด

ข้อมูลของร้าน (Context):
{context}

คำถามจากลูกค้า: {query}
"""
    # ส่ง Prompt ไปยัง Gemini
    response = llm.generate_content(prompt)
    return response.text


def main():
    st.set_page_config(page_title="MilkLab° RAG", page_icon="🥛")
    st.title("MilkLab° RAG Chatbot")
    st.caption("ถามอะไรเกี่ยวกับ MilkLab ได้ (ตอบจากฐานข้อมูล menu_kb.md)")

    # โหลด RAG Components
    try:
        model, index, chunks = load_index()
    except Exception as exc:
        st.error(f"เกิดข้อผิดพลาดในการโหลดระบบ: {exc}")
        st.stop()

    # จัดการประวัติการแชท
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # แสดงประวัติการแชทเก่า
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # รับคำถามใหม่จากผู้ใช้
    if prompt := st.chat_input("ถามข้อมูลร้าน MilkLab ได้เลยครับ..."):
        # เพิ่มและแสดงคำถามผู้ใช้
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # ประมวลผลและตอบกลับ
        with st.chat_message("assistant"):
            with st.spinner("กำลังค้นข้อมูลและคิดคำตอบ..."):

                # --- สร้าง Trace ID สำหรับเก็บประวัติการทำงาน (Observability) ---
                trace_id = str(uuid.uuid4())
                trace_data = {
                    "trace_id": trace_id,
                    "timestamp": datetime.now().isoformat(),
                    "query": prompt,
                    "spans": []
                }

                # --- Span 1: จับเวลา Retrieval ---
                start_ret = time.time()
                context = retrieve_top_k(prompt, model, index, chunks)
                ret_duration = time.time() - start_ret
                trace_data["spans"].append(
                    {"name": "retrieve_top_k", "duration_sec": round(ret_duration, 4)})

                # --- Span 2: จับเวลา Generate Answer (TODO 6) ---
                start_gen = time.time()
                answer = generate_answer(prompt, context)
                gen_duration = time.time() - start_gen
                trace_data["spans"].append(
                    {"name": "generate_answer", "duration_sec": round(gen_duration, 4)})

                # บันทึกประวัติลงไฟล์ traces.jsonl
                with open("traces.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(trace_data, ensure_ascii=False) + "\n")

            # แสดงคำตอบให้ผู้ใช้เห็น
            st.write(answer)

            # แสดงกล่อง Trace ใต้คำตอบตามที่โจทย์ Session 3 กำหนด
            with st.expander("🔍 Trace (Observability)"):
                st.json(trace_data)

        # บันทึกคำตอบลงประวัติ
        st.session_state.messages.append(
            {"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
