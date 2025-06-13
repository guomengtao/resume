<template>
  <div>
    <h2>订单列表</h2>
    <el-table :data="orders" style="width: 100%">
      <el-table-column prop="order_number" label="订单编号" />
      <el-table-column prop="customer_id" label="客户ID" />
      <el-table-column prop="status" label="订单状态" />
      <el-table-column prop="total_amount" label="总金额" />
      <el-table-column prop="payment_status" label="支付状态" />
      <el-table-column prop="production_status" label="生产状态" />
      <el-table-column prop="shipping_address" label="收货地址" />
      <el-table-column prop="created_at" label="创建时间" />
    </el-table>

    <el-pagination
      background
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { apiRequest } from '../api/apiClient';

export default {
  name: 'OrdersList',
  setup() {
    const orders = ref([]);
    const page = ref(1);
    const pageSize = ref(10);
    const total = ref(0);

    const loadOrders = async () => {
      try {
        const data = await apiRequest('/orders', 'GET');
        orders.value = data.items || data;
        total.value = data.total || data.length;
      } catch (error) {
        console.error('加载订单失败:', error);
      }
    };

    const handlePageChange = (newPage) => {
      page.value = newPage;
      loadOrders();
    };

    onMounted(() => {
      loadOrders();
    });

    return {
      orders,
      page,
      pageSize,
      total,
      handlePageChange
    };
  }
};
</script>