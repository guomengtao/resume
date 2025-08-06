import os
import requests
import psycopg2

# === 环境变量配置 ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
NEON_DB_URL = os.getenv("NEON_DB_URL")

if not all([SUPABASE_URL, SUPABASE_API_KEY, NEON_DB_URL]):
    raise Exception("请设置环境变量 SUPABASE_URL, SUPABASE_API_KEY, NEON_DB_URL")

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# === 获取所有 Supabase 用户表名（依赖 RPC 函数 get_user_tables） ===
def get_user_tables():
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_user_tables"
    resp = requests.post(url, headers=HEADERS, json={})
    resp.raise_for_status()
    return [item["table_name"] for item in resp.json()]

# === 从 Supabase 获取指定表数据，支持 updated_at 增量 ===
def get_table_data(table_name, last_updated=None, updated_at_field="updated_at"):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    params = {
        "select": "*",
        "order": f"{updated_at_field}.asc",
        "limit": 1000,
    }
    if last_updated:
        params[updated_at_field] = f"gt.{last_updated}"

    data = []
    offset = 0
    while True:
        params["offset"] = offset
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code == 404:
            print(f"⚠️ Supabase 上找不到表 {table_name}，跳过")
            return []
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        data.extend(batch)
        offset += len(batch)
        if len(batch) < params["limit"]:
            break
    return data

# === 获取表主键字段 ===
def get_primary_key(conn, table_name):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary
        """, (table_name,))
        result = cur.fetchone()
        return result[0] if result else None

# === 检查表是否存在 ===
def table_exists(conn, table_name):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s
            )
        """, (table_name,))
        return cur.fetchone()[0]

# === 获取 Neon 中表的最大 updated_at 时间 ===
def get_latest_updated_at(conn, table_name, updated_at_field="updated_at"):
    with conn.cursor() as cur:
        try:
            cur.execute(f"SELECT MAX({updated_at_field}) FROM {table_name}")
            return cur.fetchone()[0]
        except:
            return None

# === 写入 Neon（支持 upsert）===
def upsert_data(conn, table_name, rows, primary_key):
    if not rows:
        return
    columns = rows[0].keys()
    with conn.cursor() as cur:
        for row in rows:
            values = [row[col] for col in columns]
            placeholders = ", ".join(["%s"] * len(values))
            updates = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key])
            sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT ({primary_key}) DO UPDATE SET {updates}
            """
            cur.execute(sql, values)
        conn.commit()

# === 主流程 ===
def main():
    try:
        tables = get_user_tables()
        print(f"✅ 获取到 Supabase 表: {tables}")
    except Exception as e:
        print(f"❌ 获取表列表失败: {e}")
        return

    with psycopg2.connect(NEON_DB_URL) as conn_dst:
        for table_name in tables:
            print(f"\n🟡 同步表 {table_name} ...")

            if not table_exists(conn_dst, table_name):
                print(f"⚠️ Neon 缺少表 {table_name}，请手动创建表结构")
                continue

            pk = get_primary_key(conn_dst, table_name)
            if not pk:
                print(f"⚠️ 表 {table_name} 缺少主键，跳过")
                continue

            last_updated = get_latest_updated_at(conn_dst, table_name)
            rows = get_table_data(table_name, last_updated)
            upsert_data(conn_dst, table_name, rows, pk)
            print(f"✅ 表 {table_name} 同步完成，共同步 {len(rows)} 条记录")

if __name__ == "__main__":
    main()
