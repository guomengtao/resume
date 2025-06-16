// src/api/apiClient.js
import { supabase } from './supabaseClient';

const tables = [
  'customers', 
  'leads', 'orders', 'followups',
  'view_customers_with_latest_followup',
  'view_leads_with_latest_followup',
  'view_customers_with_progress',
  'view_orders_with_customer'
];

// 通用 Supabase 请求支持分页、排序、模糊过滤
const useSupabaseRequest = async (path, options = {}) => {
  const url = new URL(path, 'http://localhost');
  const pathSegments = url.pathname.split('/').filter(Boolean);
  const table = pathSegments[0];

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

  // Multi-field filter support (e.g., ?filter_customer_id=eq.123)
  url.searchParams.forEach((value, key) => {
    if (key.startsWith('filter_')) {
      const field = key.slice('filter_'.length);
      const dotIndex = value.indexOf('.');
      if (dotIndex !== -1) {
        const op = value.slice(0, dotIndex);
        const val = value.slice(dotIndex + 1);
        if (typeof query[op] === 'function') {
          query = query[op](field, val);
        }
      }
    }
  });

  // 兼容直接使用字段名和运算符，如 ?customer_id=eq.123
  url.searchParams.forEach((value, key) => {
    if (!key.startsWith('filter_') && !['page', 'pageSize', 'sortBy', 'sortOrder'].includes(key)) {
      const dotIndex = value.indexOf('.');
      if (dotIndex !== -1) {
        const op = value.slice(0, dotIndex);
        const val = value.slice(dotIndex + 1);
        if (typeof query[op] === 'function') {
          query = query[op](key, val);
        }
      }
    }
  });

  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;
  query = query.range(from, to);

  const { data, count, error } = await query;
  if (error) throw error;
  return { items: data, total: count };
};

// 过滤空字符串字段为 null，防止 Supabase 日期等字段错误
function sanitizeData(data) {
  const sanitized = {};
  for (const key in data) {
    sanitized[key] = data[key] === '' ? null : data[key];
  }
  return sanitized;
}

// 支持 GET、POST、PATCH 方法
async function apiRequest(path, options = {}) {
  const method = options.method || 'GET';
  const body = options.body || null;
  const headers = options.headers || {};

  const url = new URL(path, 'http://localhost');
  const pathSegments = url.pathname.split('/').filter(Boolean);
  const table = pathSegments[0];

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
    if (!body) throw new Error('PATCH request missing body');

    const id = pathSegments.length > 1 ? pathSegments[pathSegments.length - 1] : null;
    if (!id || id === table) {
      throw new Error('PATCH request missing id or uuid in path');
    }

    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    const key = uuidRegex.test(id) ? 'uuid' : 'id';

    console.log('PATCH Debug Info:');
    console.log('  Full path:', path);
    console.log('  Table:', table);
    console.log('  ID:', id);
    console.log('  Key (id or uuid):', key);
    console.log('  Payload:', body);

    // Use .eq() instead of .match()
    const { error } = await supabase
      .from(table)
      .update(sanitizeData(body))
      .eq(key, id);

    if (error) {
      console.error('PATCH update error:', error);
      throw error;
    }

    // Return success without extra select to avoid 400 errors
    return { success: true };
  } else {
    throw new Error(`HTTP method ${method} not supported`);
  }
}

export { apiRequest };