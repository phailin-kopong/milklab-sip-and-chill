import argparse
import os
import sys
import json
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def append_to_sheet(menu: str, qty: int, price: float) -> dict:
    # 1. โหลด Creds จาก Environment
    creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not creds_json or not sheet_id:
        raise RuntimeError("ต้องตั้งค่า GOOGLE_SHEETS_CREDENTIALS และ GOOGLE_SHEETS_ID")
    
    # 2. เชื่อมต่อ Google Sheets
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    
    # 3. บันทึกข้อมูล
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = qty * price
    sheet.append_row([timestamp, menu, qty, price, total])
    
    return {"timestamp": timestamp, "menu": menu, "qty": qty, "price": price, "total": total}

def send_notification(message: str) -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("ไม่มี Telegram credentials")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Telegram error: {response.text}")
    return "telegram"

def main() -> int:
    parser = argparse.ArgumentParser(description="MilkLab Sales Logger")
    parser.add_argument("--menu", required=True)
    parser.add_argument("--qty", type=int, required=True)
    parser.add_argument("--price", type=float, required=True)
    args = parser.parse_args()

    try:
        row = append_to_sheet(args.menu, args.qty, args.price)
        send_notification(f"บันทึก {args.menu} x{args.qty} = {row['total']} บาท")
        print(f"[OK] บันทึกสำเร็จ: {row['total']} บาท")
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())