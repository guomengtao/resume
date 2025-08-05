import os
import requests
import psycopg2
from urllib.parse import urlparse, urlunparse

# 替换连接字符串中的 host 为 IPv4，避免 IPv6 连接问题
def replace_host_with_ipv4(dsn, ipv4):
    parsed = urlparse(dsn)
    userinfo = ''
    if parsed.username:
        userinfo += parsed.username
        if parsed.password:
            userinfo += f':{parsed.password}'
        userinfo += '@'
    new_netloc = f"{userinfo}{ipv4}"
    if parsed.port:
        new_netloc += f":{parsed.port}"
    replaced = parsed._replace(netloc=new_netloc)
    return urlunparse(replaced)

SUPABASE_DB_IPV4 = "3.114.212.26"  # 你的 Supabase IPv4 地址
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
NEON_DB_URL = os.getenv("NEON_DB_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")  # 例如 https://xxxx.supabase.co

if not SUPABASE_DB_URL or not NEON_DB_URL or not SUPABASE_API_KEY or not SUPABASE_URL:
    raise Exception("请设置 SUPABASE_DB_URL, NEON_DB_URL, SUPABASE_API_KEY, SUPABASE_URL 环境变量")

SUPABASE_DB_URL = replace_host_with_ipv4(SUPABASE_DB_URL, SUPABASE_DB_IPV4)

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def get_user_tables():
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_tables"
    # 这里假设你有一个 RPC 或 API 来获取表名，否则改为调用信息表获取表名
    # 如果没有，改为直接写死表列表或者使用 Postgres system catalog 查询
    # 这里给一个示例改成从 system tables 查询
    # 先尝试用 API 获取所有用户表：
    url = f"{SUPABASE_URL}/rest/v1/tables?select=table_name"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    tables = [t['table_name'] for t in resp.json()]
    return tables

def get_primary_key_and_updated_at(conn, table):
    # 查询该表主键字段
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                 AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = %s::regclass
            AND    i.indisprimary;
        """, (table,))
        pk = cur.fetchone()
        pk = pk[0] if pk else 'id'  # 默认主键叫 id
        # 查询 updated_at 字段是否存在
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = 'updated_at'
        """, (table,))
        updated_at_exists = cur.fetchone() is not None
    return pk, 'updated_at' if updated_at_exists else None

def table_exists(conn, table):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, (table,))
        return cur.fetchone()[0]

def create_table_from_supabase(neon_conn, supabase_conn, table):
    with supabase_conn.cursor() as sup_cur, neon_conn.cursor() as neon_cur:
        sup_cur.execute(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %s", (table,))
        columns = sup_cur.fetchall()
        # 拼建创建表SQL，简单版，不包含索引、主键约束等高级内容
        col_defs = []
        for col_name, data_type, is_nullable in columns:
            null_str = "NOT NULL" if is_nullable == "NO" else ""
            col_defs.append(f"{col_name} {data_type} {null_str}")
        create_sql = f"CREATE TABLE {table} ({', '.join(col_defs)});"
        neon_cur.execute(create_sql)
        neon_conn.commit()
        print(f"✅ 已创建表 {table} 到 Neon")

def get_last_updated_at(neon_conn, table, updated_at_field):
    with neon_conn.cursor() as cur:
        cur.execute(f"SELECT MAX({updated_at_field}) FROM {table};")
        res = cur.fetchone()
        return res[0] if res else None

def sync_table(supabase_conn, neon_conn, table):
    pk, updated_at_field = get_primary_key_and_updated_at(supabase_conn, table)
    if not table_exists(neon_conn, table):
        print(f"目标表 {table} 不存在，正在创建...")
        create_table_from_supabase(neon_conn, supabase_conn, table)

    last_update = None
    if updated_at_field:
        last_update = get_last_updated_at(neon_conn, table, updated_at_field)
        print(f"上次同步时间: {last_update}")

    with supabase_conn.cursor() as sup_cur, neon_conn.cursor() as neon_cur:
        if last_update and updated_at_field:
            sup_cur.execute(f"SELECT * FROM {table} WHERE {updated_at_field} > %s", (last_update,))
        else:
            sup_cur.execute(f"SELECT * FROM {table}")
        rows = sup_cur.fetchall()
        columns = [desc[0] for desc in sup_cur.description]

        for row in rows:
            placeholders = ','.join(['%s'] * len(row))
            columns_str = ','.join(columns)
            update_str = ','.join([f"{col}=EXCLUDED.{col}" for col in columns if col != pk])

            sql = f"""
                INSERT INTO {table} ({columns_str}) VALUES ({placeholders})
                ON CONFLICT ({pk}) DO UPDATE SET {update_str};
            """
            neon_cur.execute(sql, row)
        neon_conn.commit()
        print(f"同步表 {table} 完成，共 {len(rows)} 条数据")

def main():
    print("开始同步 Supabase 到 Neon...")

    with psycopg2.connect(SUPABASE_DB_URL) as supabase_conn, psycopg2.connect(NEON_DB_URL) as neon_conn:
        tables = get_user_tables()
        print(f"获取到 {len(tables)} 张表：{tables}")
        for table in tables:
            try:
                print(f"同步表 {table} ...")
                sync_table(supabase_conn, neon_conn, table)
            except Exception as e:
                print(f"同步表 {table} 失败，原因：{e}")

    print("同步完成。")

if __name__ == "__main__":
    main()
