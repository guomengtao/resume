import os
import sys
import time
import psycopg2
import requests
import ipaddress
from urllib.parse import urlparse, urlunparse

# 环境变量读取
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
NEON_DB_URL = os.getenv("NEON_DB_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")

if not all([SUPABASE_DB_URL, NEON_DB_URL, SUPABASE_API_KEY, SUPABASE_URL]):
    raise Exception("请设置 SUPABASE_DB_URL, NEON_DB_URL, SUPABASE_API_KEY, SUPABASE_URL 环境变量")

# 替换连接字符串中的域名为IPv4，避免IPv6网络不可达问题
def replace_host_with_ipv4(dsn: str, ipv4: str) -> str:
    parsed = urlparse(dsn)
    host = parsed.hostname
    try:
        ipaddress.ip_address(host)
        # 已经是IP，不替换
        return dsn
    except ValueError:
        # 替换域名为ipv4
        netloc = parsed.netloc.replace(host, ipv4)
        new_parsed = parsed._replace(netloc=netloc)
        return urlunparse(new_parsed)

# 查询Supabase域名对应IPv4
def get_ipv4_from_hostname(hostname: str) -> str:
    import socket
    try:
        return socket.gethostbyname(hostname)
    except Exception as e:
        print(f"无法获取 {hostname} 的IPv4地址: {e}")
        sys.exit(1)

# 替换Supabase连接串host为IPv4
supabase_host = urlparse(SUPABASE_DB_URL).hostname
supabase_ipv4 = get_ipv4_from_hostname(supabase_host)
SUPABASE_DB_URL = replace_host_with_ipv4(SUPABASE_DB_URL, supabase_ipv4)
# 添加sslmode=require保证SSL连接
if "sslmode=" not in SUPABASE_DB_URL:
    if "?" in SUPABASE_DB_URL:
        SUPABASE_DB_URL += "&sslmode=require"
    else:
        SUPABASE_DB_URL += "?sslmode=require"

print(f"使用 Supabase 连接串（IPv4替换后）：{SUPABASE_DB_URL}")

# 获取所有用户自定义表（排除系统表）
def get_user_tables():
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_user_tables"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    # 这里如果Supabase没有rpc方法get_user_tables，则改为查询information_schema
    # 这里用 psycopg2 查询示例代替

    with psycopg2.connect(SUPABASE_DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' AND table_type='BASE TABLE';
            """)
            rows = cur.fetchall()
            tables = [row[0] for row in rows]
            return tables

# 获取每张表的主键字段
def get_primary_key(table_name: str):
    with psycopg2.connect(SUPABASE_DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = %s::regclass AND i.indisprimary;
            """, (table_name,))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                # 默认返回id
                return "id"

# 检查目标表是否存在，若不存在则创建表结构（从Supabase复制）
def ensure_table_exists(table_name: str):
    with psycopg2.connect(NEON_DB_URL) as conn_neon, psycopg2.connect(SUPABASE_DB_URL) as conn_supabase:
        with conn_neon.cursor() as cur_neon, conn_supabase.cursor() as cur_supabase:
            # 检查表是否存在
            cur_neon.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = %s
                );
            """, (table_name,))
            exists = cur_neon.fetchone()[0]
            if exists:
                return
            # 不存在则获取创建表语句
            cur_supabase.execute(f"""
                SELECT 'CREATE TABLE ' || quote_ident(table_name) || E' (\n' ||
                string_agg(
                    '  ' || quote_ident(column_name) || ' ' || 
                    pg_catalog.format_type(a.atttypid, a.atttypmod) || 
                    CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                    E',\n'
                ) || E'\n);' AS create_table_sql
                FROM information_schema.columns c
                JOIN pg_attribute a ON a.attrelid = c.table_name::regclass AND a.attname = c.column_name
                WHERE table_name = %s
                GROUP BY table_name;
            """, (table_name,))
            create_sql_row = cur_supabase.fetchone()
            if create_sql_row and create_sql_row[0]:
                create_sql = create_sql_row[0]
                cur_neon.execute(create_sql)
                conn_neon.commit()
                print(f"创建表 {table_name} 完成")

# 获取目标表最大更新时间（用于增量同步）
def get_max_updated_at(table_name: str, updated_at_field: str = "updated_at"):
    with psycopg2.connect(NEON_DB_URL) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"SELECT MAX({updated_at_field}) FROM {table_name};")
                result = cur.fetchone()
                return result[0] if result and result[0] else None
            except Exception:
                # 表不存在或字段不存在，返回None
                return None

# 主增量同步函数
def sync_table(table_name: str, primary_key: str, updated_at_field: str = "updated_at"):
    print(f"同步表 {table_name} 中 ...")
    last_update = get_max_updated_at(table_name, updated_at_field)
    with psycopg2.connect(SUPABASE_DB_URL) as conn_supabase, psycopg2.connect(NEON_DB_URL) as conn_neon:
        with conn_supabase.cursor() as cur_supabase, conn_neon.cursor() as cur_neon:
            if last_update:
                print(f"增量同步，从 {last_update} 开始")
                cur_supabase.execute(f"""
                    SELECT * FROM {table_name} WHERE {updated_at_field} > %s;
                """, (last_update,))
            else:
                print("全量同步")
                cur_supabase.execute(f"SELECT * FROM {table_name};")
            rows = cur_supabase.fetchall()
            if not rows:
                print(f"表 {table_name} 没有新增数据")
                return

            # 获取列名
            colnames = [desc[0] for desc in cur_supabase.description]
            cols_str = ", ".join(colnames)
            placeholders = ", ".join(["%s"] * len(colnames))

            for row in rows:
                # UPSERT (PostgreSQL 9.5+)
                update_set = ", ".join([f"{col}=EXCLUDED.{col}" for col in colnames if col != primary_key])
                sql = f"""
                    INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})
                    ON CONFLICT ({primary_key}) DO UPDATE SET {update_set};
                """
                try:
                    cur_neon.execute(sql, row)
                except Exception as e:
                    print(f"同步行失败: {e}")
            conn_neon.commit()
            print(f"同步表 {table_name} 完成，条数: {len(rows)}")

def main():
    tables = get_user_tables()
    print(f"发现表: {tables}")
    for table in tables:
        pk = get_primary_key(table)
        ensure_table_exists(table)
        sync_table(table, pk)

if __name__ == "__main__":
    main()
