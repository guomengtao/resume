import os
import json
import base64
import requests
import gspread
from datetime import datetime, timezone
from oauth2client.service_account import ServiceAccountCredentials

# ======= 调试信息：打印环境变量关键值 =======
print("\n=== Debug Info: Environment Variables ===")
print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
print(f"SPREADSHEET_ID: {os.environ.get('SPREADSHEET_ID')}")
print(f"GCP_SHEET_CRED length: {len(os.environ.get('GCP_SHEET_CRED', ''))}")
print("==========================================\n")

# 1. Google Sheets API 授权
cred_str = os.environ['GCP_SHEET_CRED']
cred_dict = json.loads(base64.b64decode(cred_str))
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ['SPREADSHEET_ID'])

# Supabase 参数
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_API_KEY']
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# 拉取所有表名
tables = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/get_all_user_tables", headers=headers).json()
print(f"📋 Tables found: {tables}\n")

for table in tables:
    print(f"🔄 Backing up table: {table}")
    worksheet_name = table

    # 获取或新建 worksheet
    try:
        ws = sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
        ws.append_row(["id", "note", "updated_at"])

    # 读取已有数据，找最后一个 updated_at
    records = ws.get_all_values()
    last_updated = "1970-01-01T00:00:00Z"
    if len(records) > 1:
        try:
            raw_ts = records[-1][-1].strip()
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).astimezone(timezone.utc)
            last_updated = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            print(f"⚠️ Warning parsing timestamp: {e}")

    print(f"   ➡ Last updated timestamp used for {table}: {last_updated}")

    # 请求参数
    params = {
        "updated_at": f"gt.{last_updated}",
        "order": "updated_at.asc"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"

    # ======= 调试信息：打印请求细节 =======
    print(f"   ➡ Request URL: {url}")
    print(f"   ➡ Request Params: {params}")
    print(f"   ➡ Request Headers (shortened): {{'apikey': '***', 'Authorization': 'Bearer ***'}}")

    resp = requests.get(url, headers=headers, params=params)

    print(f"   ➡ HTTP Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"❌ Error fetching {table}: {resp.text}")
        continue

    new_data = resp.json()
    print(f"✅ {len(new_data)} rows fetched from {table}")
    if new_data:
        print(f"   Sample row: {new_data[0]}")  # 打印第一条看看实际内容

        fields = list(new_data[0].keys())
        if len(records) <= 1:
            ws.update('A1', [fields])
        for row in new_data:
            values = [row.get(f, '') for f in fields]
            ws.append_row(values)

print("\n=== Backup Finished ===")
