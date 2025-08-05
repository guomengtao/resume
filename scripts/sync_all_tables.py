import os
import requests
import psycopg2
from psycopg2.extras import execute_values

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_API_KEY = os.environ['SUPABASE_API_KEY']
NEON_DB_URL = os.environ['NEON_DB_URL']

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Accept": "application/json",
}


def get_user_tables():
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_type='BASE TABLE';
    """
    url = f"{SUPABASE_URL}/rest/v1/rpc"
    response = requests.post(
        url,
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"q": query},
    )
    response.raise_for_status()
    tables = [row['table_name'] for row in response.json()]
    return tables


def get_primary_key(table):
    query = f"""
        SELECT a.attname as column_name
        FROM   pg_index i
        JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE  i.indrelid = 'public.{table}'::regclass AND i.indisprimary;
    """
    url = f"{SUPABASE_URL}/rest/v1/rpc"
    response = requests.post(
        url,
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"q": query},
    )
    response.raise_for_status()
    results = response.json()
    return results[0]['column_name'] if results else None


def fetch_rows(table, updated_since=None):
    params = {"select": "*", "order": "updated_at"}
    if updated_since:
        params[f"updated_at.gt"] = updated_since
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def get_latest_updated_at(table):
    with psycopg2.connect(NEON_DB_URL) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"SELECT MAX(updated_at) FROM {table}")
                result = cur.fetchone()[0]
                return result.isoformat() if result else None
            except:
                return None


def upsert_rows(table, pk_field, rows):
    if not rows:
        print(f"✅ {table}: 无需更新")
        return
    cols = rows[0].keys()
    values = [tuple(row[c] for c in cols) for row in rows]
    sql = f"""
        INSERT INTO {table} ({', '.join(cols)})
        VALUES %s
        ON CONFLICT ({pk_field}) DO UPDATE SET
        {', '.join([f'{col}=EXCLUDED.{col}' for col in cols if col != pk_field])};
    """
    with psycopg2.connect(NEON_DB_URL) as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, values)
        conn.commit()
    print(f"⬆️ {table}: 同步 {len(rows)} 行")


if __name__ == "__main__":
    tables = get_user_tables()
    for table in tables:
        print(f"\n🔄 正在同步表: {table}")
        try:
            pk = get_primary_key(table)
            if not pk:
                print(f"⚠️ {table}: 未找到主键，跳过")
                continue
            latest = get_latest_updated_at(table)
            new_rows = fetch_rows(table, updated_since=latest)
            upsert_rows(table, pk, new_rows)
        except Exception as e:
            print(f"❌ {table} 同步失败: {e}")
