import os
import requests
import json

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
NEON_URL = os.getenv("NEON_URL")  # Neon REST endpoint (PostgREST)

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
}

def get_user_tables():
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_user_tables"
    resp = requests.post(url, headers=HEADERS, json={})
    resp.raise_for_status()
    tables = [row["table_name"] for row in resp.json()]
    print(f"✅ 获取 Supabase 用户表: {tables}")
    return tables

def get_primary_key(table_name):
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_primary_key"
    resp = requests.post(url, headers=HEADERS, json={"tname": table_name})
    resp.raise_for_status()
    result = resp.json()
    return result[0]["column_name"] if result else None

def get_table_columns(table_name):
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_table_columns"
    resp = requests.post(url, headers=HEADERS, json={"tname": table_name})
    resp.raise_for_status()
    return resp.json()

def table_exists_neon(table_name):
    url = f"{NEON_URL}/{table_name}?limit=1"
    resp = requests.get(url, headers=HEADERS)
    return resp.status_code == 200

def create_table_neon(table_name):
    print(f"⚠️ Neon 缺表 {table_name}，自动建表中...")
    try:
        columns = get_table_columns(table_name)
        column_defs = []
        for col in columns:
            name = col["column_name"]
            dtype = col["data_type"]
            nullable = "NOT NULL" if col["is_nullable"] == "NO" else ""
            default = f"DEFAULT {col['column_default']}" if col["column_default"] else ""
            column_defs.append(f'"{name}" {dtype} {nullable} {default}'.strip())
        create_sql = f'CREATE TABLE "{table_name}" (\n  {",\n  ".join(column_defs)}\n);'
        payload = {
            "sql": create_sql
        }
        sql_url = f"{NEON_URL}/rpc/execute_sql"
        r = requests.post(sql_url, headers=HEADERS, json=payload)
        r.raise_for_status()
        print(f"✅ Neon 自动创建表 {table_name}")
        return True
    except Exception as e:
        print(f"❌ Neon 创建表 {table_name} 失败: {e}")
        return False

def get_table_data(table_name, last_updated=None):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&order=updated_at.asc&limit=1000"
    if last_updated:
        url += f"&updated_at=gt.{last_updated}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_max_updated_at_neon(table_name):
    url = f"{NEON_URL}/rpc/get_max_updated_at"
    resp = requests.post(url, headers=HEADERS, json={"tname": table_name})
    if resp.status_code == 200:
        result = resp.json()
        return result[0]["max"] if result and result[0]["max"] else None
    return None

def insert_rows_neon(table_name, rows):
    for row in rows:
        url = f"{NEON_URL}/{table_name}"
        resp = requests.post(url, headers=HEADERS, json=row)
        if not resp.ok:
            print(f"❌ 插入失败: {resp.text}")

def sync_table(table_name):
    print(f"\n🟡 同步表 {table_name} ...")

    if not table_exists_neon(table_name):
        if not create_table_neon(table_name):
            print(f"❌ 表 {table_name} 创建失败或仍不存在，跳过")
            return

    pk = get_primary_key(table_name)
    if not pk:
        print(f"⚠️ 表 {table_name} 无主键，跳过")
        return

    last_updated = get_max_updated_at_neon(table_name)
    rows = get_table_data(table_name, last_updated)
    if not rows:
        print(f"✅ 表 {table_name} 同步完成，共 0 条记录")
        return

    insert_rows_neon(table_name, rows)
    print(f"✅ 表 {table_name} 同步完成，共 {len(rows)} 条记录")

def main():
    tables = get_user_tables()
    for table in tables:
        sync_table(table)

if __name__ == "__main__":
    main()
