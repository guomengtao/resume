import os
import sys
import psycopg2
import requests
import ipaddress
import re
from urllib.parse import urlparse
import time

# --------------------------
# 配置环境变量读取
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
NEON_DB_URL = os.getenv("NEON_DB_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")

if not all([SUPABASE_DB_URL, NEON_DB_URL, SUPABASE_API_KEY, SUPABASE_URL]):
    raise Exception("请设置 SUPABASE_DB_URL, NEON_DB_URL, SUPABASE_API_KEY, SUPABASE_URL 环境变量")

# --------------------------
def get_ipv4_from_hostname(hostname: str) -> str:
    """根据主机名获取第一个IPv4地址"""
    try:
        import socket
        addrs = socket.getaddrinfo(hostname, None)
        for addr in addrs:
            family, _, _, _, sockaddr = addr
            if family == socket.AF_INET:  # IPv4
                return sockaddr[0]
    except Exception as e:
        print(f"获取IPv4失败: {e}")
    raise Exception(f"无法获取IPv4地址: {hostname}")

def replace_host_with_ipv4(dsn: str, ipv4: str) -> str:
    """
    替换 PostgreSQL DSN 中的 host 部分为 ipv4 地址。
    兼容带用户名密码的 dsn 格式。
    """
    pattern = r"^(postgres(?:ql)?://(?:[^@]+@)?)([^:/?#]+)(.*)$"
    match = re.match(pattern, dsn)
    if not match:
        raise ValueError("无法解析 DSN: 格式不匹配")
    prefix, host, suffix = match.groups()

    # 检查 host 是否已经是 IP 地址，是则不替换
    try:
        ipaddress.ip_address(host)
        return dsn
    except ValueError:
        pass

    # 替换 host
    return prefix + ipv4 + suffix

# --------------------------
# 替换 Supabase DB URL 中的 host 为 IPv4
supabase_host = None
try:
    m = re.match(r"^(?:postgres(?:ql)?://(?:[^@]+@)?)([^:/?#]+)", SUPABASE_DB_URL)
    supabase_host = m.group(1) if m else None
except Exception:
    supabase_host = None

if not supabase_host:
    raise Exception("无法从 SUPABASE_DB_URL 中提取 host")

supabase_ipv4 = get_ipv4_from_hostname(supabase_host)
SUPABASE_DB_URL = replace_host_with_ipv4(SUPABASE_DB_URL, supabase_ipv4)

if "sslmode=" not in SUPABASE_DB_URL:
    if "?" in SUPABASE_DB_URL:
        SUPABASE_DB_URL += "&sslmode=require"
    else:
        SUPABASE_DB_URL += "?sslmode=require"

print(f"使用的 Supabase DB URL: {SUPABASE_DB_URL}")

# --------------------------
def get_user_tables():
    """
    使用 Supabase REST API 获取所有用户表名（排除系统表）
    """
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_user_tables"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    import requests

    # 你需要在 Supabase 创建一个 RPC 函数 get_user_tables 返回表列表，或者改用 pg_catalog 查询
    # 这里是示范调用，实际可能需要改为直接查询 pg_catalog.tables
    response = requests.post(url, headers=headers, json={})
    response.raise_for_status()
    tables = response.json()
    return [t["table_name"] for t in tables]

def get_primary_key(conn, table_name):
    """获取表主键字段名"""
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                               AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = %s::regclass
            AND    i.indisprimary;
        """, (table_name,))
        result = cur.fetchone()
        return result[0] if result else None

def table_exists(conn, table_name):
    """判断表是否存在"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """, (table_name,))
        return cur.fetchone()[0]

def create_table_like(conn_src, conn_dst, table_name):
    """从源数据库复制表结构到目标数据库（不复制数据）"""
    with conn_src.cursor() as cur_src, conn_dst.cursor() as cur_dst:
        # 获取创建表结构SQL
        cur_src.execute(f"SELECT pg_get_tabledef('{table_name}'::regclass);")
        create_sql = cur_src.fetchone()[0]

        # 在目标库执行
        cur_dst.execute(create_sql)
        conn_dst.commit()

def sync_table(conn_src, conn_dst, table_name, primary_key, updated_at_field="updated_at"):
    """
    增量同步表，基于 updated_at 字段和主键
    """
    with conn_dst.cursor() as cur_dst:
        # 查询目标库表的最大更新时间
        try:
            cur_dst.execute(f"SELECT MAX({updated_at_field}) FROM {table_name}")
            last_updated = cur_dst.fetchone()[0]
        except Exception:
            last_updated = None

    with conn_src.cursor() as cur_src, conn_dst.cursor() as cur_dst:
        if last_updated:
            cur_src.execute(f"""
                SELECT * FROM {table_name} WHERE {updated_at_field} > %s ORDER BY {updated_at_field} ASC
            """, (last_updated,))
        else:
            cur_src.execute(f"SELECT * FROM {table_name}")

        rows = cur_src.fetchall()
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
    except Exception as e:
        print(f"获取表列表失败: {e}")
        # 如果RPC不可用，可换成直接从 pg_catalog 查询，示例略

    # 连接数据库
    with psycopg2.connect(SUPABASE_DB_URL) as conn_src, psycopg2.connect(NEON_DB_URL) as conn_dst:
        for table_name in tables:
            print(f"开始同步表 {table_name}...")
            if not table_exists(conn_dst, table_name):
                print(f"目标库没有表 {table_name}，准备创建...")
                # 如果 pg_get_tabledef 不可用，请改用 pg_dump -s 或手动建表SQL
                # 这里暂时跳过自动建表细节
                print("请先手动创建目标表，或者实现自动建表逻辑")
                continue

            pk = get_primary_key(conn_src, table_name)
            if not pk:
                print(f"表 {table_name} 没有主键，跳过同步")
                continue

            sync_table(conn_src, conn_dst, table_name, pk)
            print(f"表 {table_name} 同步完成。")

if __name__ == "__main__":
    main()
