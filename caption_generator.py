"""Cozy Toes Caption Generator (S4 Pivot).

Usage:
    python caption_generator.py

Reads GEMINI_API_KEY from env. Generates a Thai caption for a sock product.
"""

import os
import sys

from dotenv import load_dotenv
from google import genai

PROMPT_TEMPLATE = """\
คุณคือ social media manager ของร้านขายถุงเท้าออนไลน์ Cozy Toes

จงเขียนแคปชั่นภาษาไทย 2 ถึง 3 ประโยคโปรโมตสินค้า: {product}

เงื่อนไข:
- โทนน่ารัก เป็นกันเอง ใช้คำง่าย ใส่ emoji 🧦✨ ได้
- ช่วยดึงจุดเด่นของถุงเท้ามาเชียร์ เช่น ความนุ่ม เนื้อผ้าใส่สบาย ไซส์พอดี หรือลายน่ารักๆ
- แทรกโปรโมชัน "คุ้มสุดๆ! ซื้อ 4 คู่ขึ้นไป ลดเลยคู่ละ 10 บาท!" เข้าไปเนียนๆ
- ต้องมี call-to-action ปิดท้าย เช่น สั่งเลย หรือ ทักแชทมานะคะ
- ห้ามใช้ em dash
"""

def generate_caption(product: str, api_key: str | None = None) -> str:
    """Generate a Thai caption for the given sock product."""
    # 🚨 แก้ไข: บังคับให้ดึง GEMINI_API_KEY ก่อนเป็นอันดับแรก
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("API Key not set in env or argument")
    
    client = genai.Client(api_key=key)
    
    # 🚨 แก้ไข: ใช้โมเดล gemini-3.6-flash ให้ตรงกับที่ app.py รันผ่าน
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=PROMPT_TEMPLATE.format(product=product),
    )
    return response.text or ""

def main() -> int:
    load_dotenv()
    product = input("สินค้า(ถุงเท้า)ที่จะโปรโมต: ").strip()
    if not product:
        print("กรุณาใส่ชื่อสินค้า")
        return 1
    caption = generate_caption(product)
    print()
    print(caption)
    return 0

if __name__ == "__main__":
    sys.exit(main())