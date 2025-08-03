import os
import json
import base64
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# 1. Google Sheets API 授权
cred_str = os.environ['GCP_SHEET_CRED']
cred_dict = json.loads(base64.b64decode(cred_str))
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ['SPREADSHEET_ID'])

# 2. 拉取所有 public 表名
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_API_KEY']
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

tables = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/get_all_user_tables", headers=headers).json()

for table in tables:
    print(f"🔄 Backing up table: {table}")
    worksheet_name = table

    # 获取 Sheet 中的对应 tab，没有就新建
    try:
        ws = sheet.worksheet(worksheet_name)
    except:
        ws = sheet.add_worksheet(title=worksheet_name, rows="1", cols="20")
        ws.append_row(["id", "note", "updated_at"])  # 初始标题，可后续改为自动字段识别

    # 获取最后一行 updated_at（假设在最后一列）
    records = ws.get_all_values()
    last_updated = "1970-01-01T00:00:00Z"
    if len(records) > 1:
        try:
            last_updated = records[-1][-1]
        except:
            pass

    # 拉 Supabase 数据
    params = f"?updated_at=gt.{last_updated}&order=updated_at.asc"
    url = f"{SUPABASE_URL}/rest/v1/{table}{params}"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        new_data = resp.json()
        print(f"✅ {len(new_data)} rows fetched from {table}")

        # 自动识别字段，写入 sheet
        if new_data:
            fields = list(new_data[0].keys())
            if len(records) <= 1:
                ws.update('A1', [fields])
            for row in new_data:
                ws.append_row([row.get(f, '') for f in fields])
    else:
        print(f"❌ Error fetching {table}: {resp.text}")
