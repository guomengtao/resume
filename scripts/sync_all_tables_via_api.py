import os
import requests
import json
from typing import List

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_API_KEY = os.environ["SUPABASE_API_KEY"]
NEON_URL = os.environ["NEON_URL"]  # 示例: https://your-neon-project-url.supabase.co
NEON_API_KEY = os.environ["NEON_API_KEY"]

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def get_user_tables() -> List[str]:
    """调用 Supabase RPC 获取用户表名"""
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/get_user_tables", headers=HEADERS, json={})
    resp.raise_for_status()
    return [r["table_name"] for r in resp.json()]

def get_table_columns(table_name: str):
    """调用 RPC 获取字段信息"""
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/get_table_columns",
                         headers=HEADERS,
                         json={"tname": table_name})
    resp.raise_for_status()
    return resp.json()

def get_primary_key(table_name: str):
    """调用 RPC 获取主键字段"""
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/get_primary_key",
                         headers=HEADERS,
                         json={"tname": table_name})
    resp.raise_for_status()
    result = resp.json()
    return result[0]["column_name"] if result else None

def table_exists_neon(table_name: str) -> bool:
    url = f"{NEON_URL}/rest/v1/{table_name}?limit=1"
    resp = requests.get(url, headers={"apikey": NEON_API_KEY, "Authorization": f"Bearer {NEON_API_KEY}"})
    return resp.status_code == 200

def create_table_in_neon(table_name: str, columns: List[dict]):
    """在 Neon 中建表"""
    col_defs = []
    for col in columns:
        line = f'"{col["column_name"]}" {col["data_type"]}'
        if col["column_default"]:
            line += f' DEFAULT {col["column_default"]}'
        if col["is_nullable"] == "NO":
            line += " NOT NULL"
        col_defs.append(line)

    col_defs_str = ",\n  ".join(col_defs)
    create_sql = f'CREATE TABLE "{table_name}" (\n  {col_defs_str}\n);'

    url = f"{NEON_URL}/rest/v1/rpc/execute_sql"
    payload = {"sql": create_sql}
    headers = {"apikey": NEON_API_KEY, "Authorization": f"Bearer {NEON_API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    resp.raise_for_status()

def get_updated_data(table_name: str, last_updated=None) -> List[dict]:
    """从 Supabase 获取增量数据"""
    params = {
        "select": "*",
        "order": "updated_at.asc",
        "limit": 1000
    }
    if last_updated:
        params["updated_at"] = f"gt.{last_updated}"

    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()

def upsert_data_to_neon(table_name: str, primary_key: str, data: List[dict]):
    """将数据 upsert 到 Neon"""
    if not data:
        return
    url = f"{NEON_URL}/rest/v1/{table_name}"
    headers = {
        "apikey": NEON_API_KEY,
        "Authorization": f"Bearer {NEON_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": f"resolution=merge-duplicates,return=minimal"
    }
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp.raise_for_status()

def sync_table(table_name: str):
    print(f"\n🟡 同步表 {table_name} ...")

    if not table_exists_neon(table_name):
        print(f"⚠️ Neon 缺表 {table_name}，自动建表中...")
        try:
            columns = get_table_columns(table_name)
            create_table_in_neon(table_name, columns)
            print(f"✅ Neon 自动创建表 {table_name}")
        except Exception as e:
            print(f"❌ Neon 创建表 {table_name} 失败: {e}")
            return

    try:
        pk = get_primary_key(table_name)
        if not pk:
            print(f"⚠️ 表 {table_name} 无主键，跳过")
            return

        data = get_updated_data(table_name)
        upsert_data_to_neon(table_name, pk, data)
        print(f"✅ 表 {table_name} 同步完成，共 {len(data)} 条记录")
    except Exception as e:
        print(f"❌ 表 {table_name} 同步失败: {e}")

def main():
    print("✅ 获取 Supabase 用户表...")
    tables = get_user_tables()
    print(f"✅ 获取 Supabase 用户表: {tables}")

    for table in tables:
        sync_table(table)

if __name__ == "__main__":
    main()
