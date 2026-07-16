import argparse
import os
import sys
import json
import gspread
import requests
from datetime import datetime

def append_to_sheet(menu: str, qty: int, price: float) -> dict:
    """TODO 1: ใช้ gspread เปิด Sheet ของตัวเอง แล้ว append_row"""
    creds_str = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    if not creds_str or not sheet_id:
        raise RuntimeError("Missing GOOGLE_SHEETS_CREDENTIALS or GOOGLE_SHEETS_ID")
        
    gc = gspread.service_account_from_dict(json.loads(creds_str))
    ws = gc.open_by_key(sheet_id).sheet1
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = qty * price
    ws.append_row([timestamp, menu, qty, price, total])
    
    return {"timestamp": timestamp, "menu": menu, "qty": qty, "price": price, "total": total}

def send_notification(message: str) -> str:
    """TODO 2: ส่ง message ไปยัง Telegram bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})
    return "telegram"

def main() -> int:
    parser = argparse.ArgumentParser(description="MilkLab Sales Logger")
    parser.add_argument("--menu", required=True, help="ชื่อเมนู")
    parser.add_argument("--qty", type=int, required=True, help="จำนวนขวด")
    parser.add_argument("--price", type=float, required=True, help="ราคาต่อขวด")
    args = parser.parse_args()

    try:
        # TODO 3: เรียก append_to_sheet แล้ว extract total
        row = append_to_sheet(args.menu, args.qty, args.price)
        total = row["total"]
    except Exception as exc:
        print(f"[ERROR] บันทึก Sheet ล้มเหลว: {exc}", file=sys.stderr)
        print("[HINT] ตรวจ GOOGLE_SHEETS_CREDENTIALS และ share Sheet กับ service account email", file=sys.stderr)
        return 1

    try:
        # TODO 4: เรียก send_notification ด้วย message
        provider = send_notification(f"บันทึก {args.menu} x{args.qty} = {total} บาท")
    except Exception as exc:
        print(f"[WARN] บันทึก Sheet สำเร็จแต่ส่งแจ้งเตือนล้มเหลว: {exc}", file=sys.stderr)
        return 0

    print(f"[OK] บันทึกและแจ้งเตือนผ่าน {provider} เรียบร้อย ยอด {total} บาท")
    return 0

if __name__ == "__main__":
    sys.exit(main())