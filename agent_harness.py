"""Cozy Toes Agent Harness (S4 Pivot).

Usage:
    python agent_harness.py --cmd "บันทึกขายถุงเท้ากีฬาหนานุ่ม ไซส์ M จำนวน 2 คู่ คู่ละ 120"

รับคำสั่งภาษาไทย ส่งให้ Gemini พร้อม tool schema parse response เป็น tool call
เรียก tool จริง print trace log

นักศึกษาต้องเติม TODO ใน 3 จุด ใน Session 2 Lab 2.3
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv
from google import genai


TOOL_SCHEMA = [
    {
        "name": "log_sale",
        "description": "บันทึกการขายถุงเท้าลง Google Sheets และส่ง notification",
        "parameters": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "ชื่อสินค้า (ถุงเท้า)"},
                "size": {"type": "string", "description": "ไซส์ถุงเท้า เช่น S, M, L, Free Size"},
                "qty": {"type": "integer", "description": "จำนวนคู่ที่ขาย"},
                "price": {"type": "number", "description": "ราคาต่อคู่"},
            },
            "required": ["product", "size", "qty", "price"],
        },
    },
    {
        "name": "query_sales",
        "description": "ดูยอดขายถุงเท้าของวันที่ระบุ",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "วันที่ format YYYY-MM-DD"},
            },
            "required": ["date"],
        },
    },
    {
        "name": "check_sock_size",
        "description": "เช็กข้อมูลไซส์ถุงเท้าแต่ละประเภทจากระบบ",
        "parameters": {
            "type": "object",
            "properties": {
                "product_type": {"type": "string", "description": "ประเภทถุงเท้าที่ลูกค้าสอบถามไซส์"},
            },
            "required": ["product_type"],
        },
    },
]


def parse_command(cmd: str, api_key: str | None = None) -> dict:
    """TODO 1: ส่ง cmd ไป Gemini พร้อม TOOL_SCHEMA ขอให้ตอบเป็น JSON {tool, args}

    Returns dict {"tool": <name>, "args": <dict>}
    Raises RuntimeError ถ้า parse ไม่ได้
    """
    raise NotImplementedError("Implement in Session 2 Lab 2.3 (TODO 1)")


def dispatch_tool(tool_call: dict) -> str:
    """TODO 2: เรียก tool ตาม tool_call["tool"] ด้วย args จริง

    Returns: ข้อความสรุปผลที่ tool คืน
    """
    raise NotImplementedError("Implement in Session 2 Lab 2.3 (TODO 2)")


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmd", required=True, help="คำสั่งภาษาไทย")
    args = parser.parse_args()

    print(f"[USER] {args.cmd}")

    # TODO 3: เรียก parse_command then dispatch_tool then print trace ตาม format ใน session-2.md
    tool_call = parse_command(args.cmd)
    print(f"[LLM]  tool={tool_call['tool']} args={tool_call['args']}")

    result = dispatch_tool(tool_call)
    print(f"[TOOL] {tool_call['tool']} {result}")
    print(f"[USER] ← {result}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
