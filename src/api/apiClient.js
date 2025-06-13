// src/api/apiClient.js
import { supabase } from './supabaseClient';

// Supabase-only request handler with pagination, sorting, filtering support
const useSupabaseRequest = async (path, options = {}) => {
  if (path === '/customers') {
    const { data, error } = await supabase.from('customers').select('*');
    if (error) throw error;
    return data;
  } else if (path.startsWith('/leads')) {
    const url = new URL(path, 'http://localhost');
    const page = parseInt(url.searchParams.get('page') || '1');
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10');
    const sortBy = url.searchParams.get('sortBy') || 'created_at';
    const sortOrder = url.searchParams.get('sortOrder') || 'desc';
    const phoneQuery = url.searchParams.get('phone') || '';

    let query = supabase
      .from('leads')
      .select('*', { count: 'exact' })
      .order(sortBy, { ascending: sortOrder === 'asc' });

    if (phoneQuery) {
      query = query.ilike('phone', `%${phoneQuery}`);
    }

    const from = (page - 1) * pageSize;
    const to = from + pageSize - 1;
    query = query.range(from, to);

    const { data, count, error } = await query;
    if (error) throw error;
    return { items: data, total: count };
  }

  throw new Error('Unsupported path in Supabase request');
};

// apiRequest supports GET and POST (only for leads currently)
async function apiRequest(path, method = 'GET', body = null, headers = {}) {
  if (method === 'GET') {
    return useSupabaseRequest(path, { method, headers });
  } else if (method === 'POST') {
    if (path === '/leads' && body) {
      const { data, error } = await supabase.from('leads').insert([body]);
      if (error) throw error;
      return data;
    }
    throw new Error('POST method not implemented for this path');
  } else {
    throw new Error(`HTTP method ${method} not supported`);
  }
}

export { apiRequest };