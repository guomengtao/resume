// src/api/apiClient.js
import { supabase } from './supabaseClient';

const tables = ['customers', 'leads', 'orders','followups','view_customers_with_latest_followup','view_leads_with_latest_followup'];

// 通用 Supabase 请求支持分页、排序、模糊过滤
const useSupabaseRequest = async (path, options = {}) => {
  // path 形如 '/leads' 或 '/leads?page=1&pageSize=10&sortBy=created_at&sortOrder=desc&filterField=phone&filterValue=123'
  const url = new URL(path, 'http://localhost');
  const [_, table] = url.pathname.split('/'); // e.g. ['', 'leads'] -> 'leads'

  if (!tables.includes(table)) {
    throw new Error('Unsupported path in Supabase request');
  }

  const page = parseInt(url.searchParams.get('page') || '1');
  const pageSize = parseInt(url.searchParams.get('pageSize') || '10');
  const sortBy = url.searchParams.get('sortBy') || 'created_at';
  const sortOrder = url.searchParams.get('sortOrder') || 'desc';

  let query = supabase
    .from(table)
    .select('*', { count: 'exact' })
    .order(sortBy, { ascending: sortOrder === 'asc' });

  // 支持简单模糊查询参数：filterField + filterValue
  const filterField = url.searchParams.get('filterField');
  const filterValue = url.searchParams.get('filterValue');
  if (filterField && filterValue) {
    query = query.ilike(filterField, `%${filterValue}%`);
  }

  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;
  query = query.range(from, to);

  const { data, count, error } = await query;
  if (error) throw error;
  return { items: data, total: count };
};

// 过滤空字符串字段为null，防止Supabase日期等字段错误
function sanitizeData(data) {
  const sanitized = {};
  for (const key in data) {
    sanitized[key] = data[key] === '' ? null : data[key];
  }
  return sanitized;
}

// apiRequest 支持 GET、POST、PATCH 方法
async function apiRequest(path, method = 'GET', body = null, headers = {}) {
  const url = new URL(path, 'http://localhost');
  const [_, table] = url.pathname.split('/');

  if (!tables.includes(table)) {
    throw new Error('Unsupported path in Supabase request');
  }

  if (method === 'GET') {
    return useSupabaseRequest(path, { method, headers });
  } else if (method === 'POST') {
    if (body) {
      const { data, error } = await supabase.from(table).insert([sanitizeData(body)]);
      if (error) throw error;
      return data;
    }
    throw new Error(`POST request missing body for path: ${path}`);
  } else if (method === 'PATCH') {
    // PATCH 需指定 id：path 如 /leads/123
    if (!body) throw new Error('PATCH request missing body');
    const id = url.pathname.split('/')[2];
    if (!id) throw new Error('PATCH request missing id in path');
    const { data, error } = await supabase.from(table).update(sanitizeData(body)).eq('id', id);
    if (error) throw error;
    return data;
  } else {
    throw new Error(`HTTP method ${method} not supported`);
  }
}

export { apiRequest };