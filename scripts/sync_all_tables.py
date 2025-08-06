import os
import requests
import psycopg2

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
NEON_DB_URL = os.getenv("NEON_DB_URL")

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def get_table_data(table_name, last_updated=None, updated_at_field="updated_at"):
    """通过 Supabase REST API 拉取表数据，支持增量拉取"""
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    params = {
        "select": "*",
        "order": f"{updated_at_field}.asc",
        "limit": 1000,
    }
    if last_updated:
        # 过滤只拉更新的数据，Supabase用gte/gt过滤参数
        params[f"{updated_at_field}"] = f"gt.{last_updated}"

    data = []
    offset = 0
    while True:
        params["offset"] = offset
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        data.extend(batch)
        offset += len(batch)
        if len(batch) < params["limit"]:
            break
    return data

def get_latest_updated_at(conn, table_name, updated_at_field="updated_at"):
    """获取目标库某表最新更新时间"""
    with conn.cursor() as cur:
        try:
            cur.execute(f"SELECT MAX({updated_at_field}) FROM {table_name}")
            return cur.fetchone()[0]
        except Exception:
            return None

def upsert_data(conn, table_name, rows, primary_key):
    if not rows:
        return
    columns = rows[0].keys()
    with conn.cursor() as cur:
        for row in rows:
            vals = [row[col] for col in columns]
            placeholders = ", ".join(["%s"] * len(vals))
            update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key])
            sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT ({primary_key}) DO UPDATE SET {update_clause}
            """
            cur.execute(sql, vals)
        conn.commit()

def main():
    # 你可以自己维护表名列表，或用之前RPC查询获得
    tables = ["health_check", "other_table"]
    primary_keys = {"health_check": "id", "other_table": "id"}

    with psycopg2.connect(NEON_DB_URL) as conn_dst:
        for table in tables:
            print(f"同步表 {table} ...")
            last_updated = get_latest_updated_at(conn_dst, table)
            rows = get_table_data(table, last_updated)
            upsert_data(conn_dst, table, rows, primary_keys[table])
            print(f"表 {table} 同步完成，新增/更新 {len(rows)} 条数据。")

if __name__ == "__main__":
    main()
