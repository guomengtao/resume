import os
import requests
import psycopg2

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
NEON_DB_URL = os.getenv("NEON_DB_URL")

if not all([SUPABASE_URL, SUPABASE_API_KEY, SUPABASE_DB_URL, NEON_DB_URL]):
    raise Exception("请设置 SUPABASE_URL, SUPABASE_API_KEY, SUPABASE_DB_URL, NEON_DB_URL 环境变量")

# 确保 SUPABASE_DB_URL 里带 sslmode=require
if "sslmode=" not in SUPABASE_DB_URL:
    if "?" in SUPABASE_DB_URL:
        SUPABASE_DB_URL += "&sslmode=require"
    else:
        SUPABASE_DB_URL += "?sslmode=require"

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def get_user_tables():
    """调用 Supabase RPC 获取所有用户表"""
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_user_tables"
    response = requests.post(url, headers=HEADERS, json={})
    response.raise_for_status()
    tables = response.json()
    return [t["table_name"] for t in tables]

def get_primary_key(conn, table_name):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                               AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = %s::regclass
            AND    i.indisprimary;
        """, (table_name,))
        res = cur.fetchone()
        return res[0] if res else None

def table_exists(conn, table_name):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """, (table_name,))
        return cur.fetchone()[0]

def create_table_like(conn_src, conn_dst, table_name):
    with conn_src.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = cur.fetchall()

    column_defs = []
    for col_name, data_type, is_nullable, default in columns:
        col_line = f'"{col_name}" {data_type}'
        if default:
            col_line += f" DEFAULT {default}"
        if is_nullable == "NO":
            col_line += " NOT NULL"
        column_defs.append(col_line)

    joined_columns = ",\n  ".join(column_defs)
    create_sql = f'CREATE TABLE "{table_name}" (\n  {joined_columns}\n);'

    with conn_dst.cursor() as cur:
        cur.execute(create_sql)
    conn_dst.commit()

def sync_table(conn_src, conn_dst, table_name, primary_key, updated_at_field="updated_at"):
    with conn_dst.cursor() as cur_dst:
        try:
            cur_dst.execute(f"SELECT MAX({updated_at_field}) FROM {table_name}")
            last_updated = cur_dst.fetchone()[0]
        except Exception:
            last_updated = None

    with conn_src.cursor() as cur_src, conn_dst.cursor() as cur_dst:
        if last_updated:
            cur_src.execute(
                f"SELECT * FROM {table_name} WHERE {updated_at_field} > %s ORDER BY {updated_at_field} ASC",
                (last_updated,))
        else:
            cur_src.execute(f"SELECT * FROM {table_name}")

        rows = cur_src.fetchall()
        if not rows:
            return

        columns = [desc[0] for desc in cur_src.description]
        for row in rows:
            values_placeholders = ", ".join(["%s"] * len(row))
            updates = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key])
            insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({values_placeholders})
                ON CONFLICT ({primary_key}) DO UPDATE SET {updates}
            """
            try:
                cur_dst.execute(insert_sql, row)
            except Exception as e:
                print(f"同步表 {table_name} 出错: {e}")
        conn_dst.commit()

def main():
    try:
        tables = get_user_tables()
        print(f"获取到用户表: {tables}")
    except Exception as e:
        print(f"获取表列表失败: {e}")
        return

    with psycopg2.connect(SUPABASE_DB_URL) as conn_src, psycopg2.connect(NEON_DB_URL) as conn_dst:
        for table_name in tables:
            print(f"开始同步表 {table_name}...")

            if not table_exists(conn_dst, table_name):
                print(f"目标库缺少表 {table_name}，自动创建中...")
                try:
                    create_table_like(conn_src, conn_dst, table_name)
                    print(f"表 {table_name} 创建完成")
                except Exception as e:
                    print(f"创建表失败: {e}")
                    continue

            pk = get_primary_key(conn_src, table_name)
            if not pk:
                print(f"表 {table_name} 无主键，跳过同步")
                continue

            sync_table(conn_src, conn_dst, table_name, pk)
            print(f"表 {table_name} 同步完成")

if __name__ == "__main__":
    main()
