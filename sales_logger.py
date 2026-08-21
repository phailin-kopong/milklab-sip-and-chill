"""Cozy Toes Sales Logger (S4 Pivot).

Usage:
    python sales_logger.py --product "ถุงเท้ากีฬาหนานุ่ม (Sport Pro)" --size "M" --qty 2 --price 120

Reads GOOGLE_SHEETS_CREDENTIALS and TELEGRAM_BOT_TOKEN (or LINE_CHANNEL_TOKEN) from env.
Appends row [timestamp, product, size, qty, price, total] to a Google Sheet,
then sends a notification via Telegram or LINE bot.

นักศึกษาต้องเติม TODO ใน 4 จุดด้านล่างใน Session 2 Lab 1.3
"""

import argparse
import os
import sys
from datetime import datetime


def append_to_sheet(product: str, size: str, qty: int, price: float) -> dict:
    """TODO 1: ใช้ gspread เปิด Sheet ของตัวเอง แล้ว append_row ด้วย [timestamp, product, size, qty, price, total]

    Returns dict {timestamp, product, size, qty, price, total} ที่ append แล้ว
    Raises RuntimeError ถ้า credentials ไม่มี หรือ Sheet ไม่ accessible
    """
    raise NotImplementedError("Implement in Session 2 Lab 1.3 (TODO 1)")


def send_notification(message: str) -> str:
    """TODO 2: ส่ง message ไปยัง Telegram bot (ใช้ TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)
    หรือ LINE bot (ใช้ LINE_CHANNEL_TOKEN) เลือกตัวใดตัวหนึ่ง

    Returns: provider name ที่ใช้ ("telegram" หรือ "line")
    Raises RuntimeError ถ้า no credentials
    """
    raise NotImplementedError("Implement in Session 2 Lab 1.3 (TODO 2)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cozy Toes Sales Logger")
    parser.add_argument("--product", required=True, help="ชื่อสินค้า (ถุงเท้า)")
    parser.add_argument("--size", required=True, help="ไซส์ถุงเท้า")
    parser.add_argument("--qty", type=int, required=True, help="จำนวนคู่")
    parser.add_argument("--price", type=float, required=True, help="ราคาต่อคู่")
    args = parser.parse_args()

    try:
        # TODO 3: เรียก append_to_sheet แล้ว extract total
        row = append_to_sheet(args.product, args.size, args.qty, args.price)
        total = row["total"]
    except Exception as exc:
        print(f"[ERROR] บันทึก Sheet ล้มเหลว: {exc}", file=sys.stderr)
        print("[HINT] ตรวจ GOOGLE_SHEETS_CREDENTIALS และ share Sheet กับ service account email", file=sys.stderr)
        return 1

    try:
        # TODO 4: เรียก send_notification ด้วย message ที่บอกยอดที่บันทึก
        provider = send_notification(f"🧦 ขายได้แล้ว! {args.product} ไซส์ {args.size} จำนวน {args.qty} คู่ รวม {total} บาท")
    except Exception as exc:
        print(f"[WARN] บันทึก Sheet สำเร็จแต่ส่งแจ้งเตือนล้มเหลว: {exc}", file=sys.stderr)
        return 0

    print(f"[OK] บันทึกและแจ้งเตือนผ่าน {provider} เรียบร้อย ยอด {total} บาท")
    return 0


if __name__ == "__main__":
    sys.exit(main())