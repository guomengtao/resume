import os
import psycopg2
import requests
from psycopg2.extras import execute_values

SUPABASE_DB_URL = os.environ['SUPABASE_DB_URL']
NEON_DB_URL = os.environ['NEON_DB_URL']


def get_user_tables():
    with psycopg2.connect(SUPABASE_DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            return [row[0] for row in cur.fetchall()]


def get_primary_key(table):
    with psycopg2.connect(SUPABASE_DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT a.attname
                FROM   pg_index i
                JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE  i.indrelid = 'public.{table}'::regclass AND i.indisprimary;
            """)
            result = cur.fetchone()
            return result[0] if result else None


def fetch_rows(table, updated_since=None):
    with psycopg2.connect(SUPABASE_DB_URL) as conn:
        with conn.cursor() as cur:
            if updated_since:
                cur.execute(f"SELECT * FROM {table} WHERE updated_at > %s ORDER BY updated_at", (updated_since,))
            else:
                cur.execute(f"SELECT * FROM {table} ORDER BY updated_at")
            colnames = [desc[0] for desc in cur.description]
            return [dict(zip(colnames, row)) for row in cur.fetchall()]


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
