import os
import json
import base64
import requests
import gspread
from datetime import datetime, timezone
from oauth2client.service_account import ServiceAccountCredentials

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

for table in tables:
    print(f"🔄 Backing up table: {table}")
    worksheet_name = table

    # 获取或新建 worksheet
    try:
        ws = sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
        ws.append_row(["id", "note", "updated_at"])  # 可以根据实际表结构动态更新

    # 读取已有数据，找最后一个 updated_at
    records = ws.get_all_values()
    last_updated = "1970-01-01T00:00:00Z"
    existing_ids = set()

    if len(records) > 1:
        try:
            # 取已存在的所有 ID 用于去重
            id_index = records[0].index("id") if "id" in records[0] else 0
            for row in records[1:]:
                if len(row) > id_index:
                    existing_ids.add(str(row[id_index]))

            raw_ts = records[-1][-1].strip()  # 最后一行的 updated_at
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).astimezone(timezone.utc)
            last_updated = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            print(f"⚠️ Warning parsing timestamp: {e}")
            last_updated = "1970-01-01T00:00:00Z"

    # 查询 Supabase：gte 避免漏数据
    params = {
        "updated_at": f"gte.{last_updated}",
        "order": "updated_at.asc"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 200:
        new_data = resp.json()
        print(f"✅ {len(new_data)} rows fetched from {table}")

        if new_data:
            fields = list(new_data[0].keys())

            # 表头更新（如果 sheet 只有表头或空）
            if len(records) <= 1:
                ws.update('A1', [fields])

            # 追加新数据行（去重）
            added_count = 0
            for row in new_data:
                if str(row.get("id", "")) not in existing_ids:
                    values = [row.get(f, '') for f in fields]
                    ws.append_row(values)
                    added_count += 1

            print(f"   ➡ Added {added_count} new rows to {table} (duplicates skipped)")
    else:
        print(f"❌ Error fetching {table}: {resp.text}")

print("=== Backup Finished ===")
