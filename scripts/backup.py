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
        ws.append_row(["id", "note", "updated_at"])  # 这里可以改为动态字段识别

    # 读取已有数据，找最后一个 updated_at
    records = ws.get_all_values()
    last_updated = "1970-01-01T00:00:00Z"
    if len(records) > 1:
        try:
            raw_ts = records[-1][-1].strip()  # 去掉首尾空格
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).astimezone(timezone.utc)
            # 格式化为标准ISO 8601，末尾带Z
            last_updated = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            print(f"⚠️ Warning parsing timestamp: {e}")
            last_updated = "1970-01-01T00:00:00Z"

    # 使用 params 传递查询参数，避免手动拼接URL错误
    params = {
        "updated_at": f"gt.{last_updated}",
        "order": "updated_at.asc"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 200:
        new_data = resp.json()
        print(f"✅ {len(new_data)} rows fetched from {table}")

        if new_data:
            fields = list(new_data[0].keys())
            # 表头更新（如果sheet只有表头或空）
            if len(records) <= 1:
                ws.update('A1', [fields])
            # 追加新数据行
            for row in new_data:
                values = [row.get(f, '') for f in fields]
                ws.append_row(values)
    else:
        print(f"❌ Error fetching {table}: {resp.text}")
