import os
import requests
import psycopg2
from psycopg2.extras import execute_values

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_API_KEY = os.environ['SUPABASE_API_KEY']
NEON_DB_URL = os.environ['NEON_DB_URL']

TABLE_NAME = "your_table_name"     # ✅ 替换为你实际的表名
PRIMARY_KEY = "id"                 # ✅ 替换为你表的主键
UPDATED_AT_FIELD = "updated_at"    # ✅ 替换为更新时间字段

# Step 1: 从 Neon 查出最新更新时间
def get_latest_updated_at():
    with psycopg2.connect(NEON_DB_URL) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"SELECT MAX({UPDATED_AT_FIELD}) FROM {TABLE_NAME}")
                result = cur.fetchone()[0]
                return result.isoformat() if result else None
            except Exception as e:
                print("⚠️ Neon 查询失败，默认全量同步：", e)
                return None

# Step 2: 从 Supabase 拉取增量数据
def fetch_supabase_data(since=None):
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Accept": "application/json",
    }
    params = {"limit": 1000, "order": UPDATED_AT_FIELD}
    if since:
        params[f"{UPDATED_AT_FIELD}.gt"] = since
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Step 3: Upsert 到 Neon
def upsert_to_neon(data):
    if not data:
        print("✅ 没有需要同步的数据。")
        return

    columns = data[0].keys()
    rows = [tuple(item[col] for col in columns) for item in data]
    col_list = ', '.join(columns)
    placeholders = ', '.join([f"EXCLUDED.{col}" for col in columns if col != PRIMARY_KEY])

    insert_sql = f"""
    INSERT INTO {TABLE_NAME} ({col_list})
    VALUES %s
    ON CONFLICT ({PRIMARY_KEY}) DO UPDATE SET
      {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != PRIMARY_KEY])};
    """

    with psycopg2.connect(NEON_DB_URL) as conn:
        with conn.cursor() as cur:
            print(f"⬆️ 正在同步 {len(rows)} 行数据到 Neon 表 `{TABLE_NAME}`...")
            execute_values(cur, insert_sql, rows)
        conn.commit()
    print("✅ 数据同步完成。")

# 主程序
if __name__ == "__main__":
    try:
        last_updated = get_latest_updated_at()
        print(f"🕐 上次更新时间: {last_updated or '无'}")
        data = fetch_supabase_data(last_updated)
        upsert_to_neon(data)
    except Exception as e:
        print("❌ 同步过程中发生错误：")
        print(e)
        exit(1)
