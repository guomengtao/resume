<template>
  <div>
    <h2>订单列表</h2>
    <el-table :data="orders" style="width: 100%">
      <el-table-column prop="order_number" label="订单编号" />
      <el-table-column prop="customer_company_name" label="客户公司名称" />
      <el-table-column prop="customer_contact_name" label="联系人姓名" />
      <el-table-column prop="status" label="订单状态" />
      <el-table-column prop="total_amount" label="总金额" />
      <el-table-column prop="payment_status" label="支付状态" />
      <el-table-column label="合同是否回传">
        <template #default="{ row }">
          <el-icon
            v-if="row.production_scheduled"
            :size="22"
            color="red"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'production_scheduled')"
          >
            <Check />
          </el-icon>
          <el-icon
            v-else
            :size="20"
            color="#c0c4cc"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'production_scheduled')"
          >
            <Close />
          </el-icon>
        </template>
      </el-table-column>
      <el-table-column label="生产完成">
        <template #default="{ row }">
          <el-icon
            v-if="row.production_completed"
            :size="22"
            color="red"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'production_completed')"
          >
            <Check />
          </el-icon>
          <el-icon
            v-else
            :size="20"
            color="#c0c4cc"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'production_completed')"
          >
            <Close />
          </el-icon>
        </template>
      </el-table-column>
      <el-table-column label="已发货">
        <template #default="{ row }">
          <el-icon
            v-if="row.shipment_scheduled"
            :size="22"
            color="red"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'shipment_scheduled')"
          >
            <Check />
          </el-icon>
          <el-icon
            v-else
            :size="20"
            color="#c0c4cc"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'shipment_scheduled')"
          >
            <Close />
          </el-icon>
        </template>
      </el-table-column>
      <el-table-column label="已收货">
        <template #default="{ row }">
          <el-icon
            v-if="row.received"
            :size="22"
            color="red"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'received')"
          >
            <Check />
          </el-icon>
          <el-icon
            v-else
            :size="20"
            color="#c0c4cc"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'received')"
          >
            <Close />
          </el-icon>
        </template>
      </el-table-column>
      <el-table-column label="是否开票">
        <template #default="{ row }">
          <el-icon
            v-if="row.invoice_issued"
            :size="22"
            color="red"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'invoice_issued')"
          >
            <Check />
          </el-icon>
          <el-icon
            v-else
            :size="20"
            color="#c0c4cc"
            style="cursor: pointer;"
            @click="toggleStepStatus(row, 'invoice_issued')"
          >
            <Close />
          </el-icon>
        </template>
      </el-table-column>
      <!-- Removed production_status and shipping_address columns -->
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
import { Check, Close } from '@element-plus/icons-vue';
import { useRoute } from 'vue-router';

export default {
  name: 'OrdersList',
  components: {
    Check,
    Close
  },
  setup() {
    const orders = ref([]);
    const page = ref(1);
    const pageSize = ref(10);
    const total = ref(0);

    const route = useRoute();
    const customerId = route.query.customer_id;

    const loadOrders = async () => {
      try {
        let path = '/view_orders_with_customer';
        if (customerId) {
          path += `?customer_id=eq.${customerId}`;
        }
        const data = await apiRequest(path, 'GET');
        console.log('订单数据:', data.items || data);
        orders.value = data.items || data;
        total.value = data.total || data.length;
      } catch (error) {
        console.error('加载订单失败:', error);
      }
    };

    const toggleStepStatus = async (order, field) => {
      console.log('切换状态，order id:', order.id, '字段:', field);
      if (!order.id) {
        console.error('order.id 不存在，无法发起 PATCH 请求');
        return;
      }
      try {
        const updatedValue = !order[field];
        await apiRequest(`/orders?id=${order.id}`, 'PATCH', { [field]: updatedValue });
        await loadOrders();
      } catch (error) {
        console.error(`切换${field}状态失败:`, error);
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
      handlePageChange,
      toggleStepStatus,
      customerId
    };
  }
};
</script>