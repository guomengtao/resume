<template>
  <div>
    <el-card v-if="customer">
      <el-button type="primary" @click="$router.push('/customers')">返回客户列表</el-button>
      <el-button type="warning" @click="$router.push(`/customers/edit/${customer.uuid}`)">编辑客户信息</el-button>

      <el-descriptions title="基础信息" :column="2" border :label-style="{ width: '120px' }">
        <el-descriptions-item label="姓名">
          <el-input v-model="customer.full_name" @blur="editCustomer('full_name')" @keyup.enter="editCustomer('full_name')" />
        </el-descriptions-item>
        <el-descriptions-item label="电话">
          <el-input v-model="customer.phone" @blur="editCustomer('phone')" @keyup.enter="editCustomer('phone')" />
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ customer.email }}</el-descriptions-item>
        <el-descriptions-item label="公司名称">
          <el-input v-model="customer.company_name" @blur="editCustomer('company_name')" @keyup.enter="editCustomer('company_name')" />
        </el-descriptions-item>
        <el-descriptions-item label="职位">{{ customer.position }}</el-descriptions-item>
        <el-descriptions-item label="省份">{{ customer.province }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ customer.city }}</el-descriptions-item>
      </el-descriptions>

      <el-descriptions title="业务状态" :column="2" border style="margin-top: 16px" :label-style="{ width: '120px' }">
        <el-descriptions-item label="状态">{{ customer.status }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ customer.assigned_to }}</el-descriptions-item>
        <el-descriptions-item label="下次跟进">{{ formatValue('next_follow_up_date', customer.next_follow_up_date) }}</el-descriptions-item>
        <el-descriptions-item label="最后联系">{{ formatValue('last_contact_date', customer.last_contact_date) }}</el-descriptions-item>
        <el-descriptions-item label="跟进次数">
          {{ customer.follow_up_count || 0 }}
          <el-button type="text" size="small" @click="addFollowUp">新增跟进</el-button>
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions title="订单信息" :column="2" border style="margin-top: 16px" :label-style="{ width: '120px' }">
        <el-descriptions-item label="订单数量">{{ orderCount }}</el-descriptions-item>
        <el-descriptions-item label="累计成交金额">{{ totalValue }} 元</el-descriptions-item>
        <el-descriptions-item label="订单操作">
          <el-button type="primary" size="small" @click="addOrder">新增订单</el-button>
          <el-button size="small" @click="viewOrders">查看订单</el-button>
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions title="备注及其他" :column="2" border style="margin-top: 16px" :label-style="{ width: '120px' }">
        <el-descriptions-item label="备注">{{ customer.notes }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ customer.source }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <div v-else>
      加载中...
    </div>
    <el-drawer v-if="drawer.visible" v-model="drawer.visible" :title="drawer.title" size="40%">
      <template v-if="drawer.type === 'order'">
        <div>这里是新增订单表单（TODO）</div>
      </template>
      <template v-else-if="drawer.type === 'followup'">
        <div>这里是新增跟进表单（TODO）</div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiRequest } from '../api/apiClient';
import dayjs from 'dayjs';
import { ElMessage } from 'element-plus';

const route = useRoute();
const $router = useRouter();
const customer = ref(null);

const orderCount = ref(0);
const totalValue = ref(0);

import { h, reactive } from 'vue';
const drawer = reactive({
  visible: false,
  title: '',
  type: '', // 'order' or 'followup'
});

function addFollowUp() {
  drawer.visible = true;
  drawer.title = '新增跟进';
  drawer.type = 'followup';
}

function addOrder() {
  drawer.visible = true;
  drawer.title = '新增订单';
  drawer.type = 'order';
}

function viewOrders() {
  $router.push(`/orders?customer_id=${customer.value.uuid}`);
}

// 日期字段列表
const dateFields = new Set([
  'next_follow_up_date',
  'last_contact_date',
  'created_at',
  'updated_at',
  'converted_at',
  'contract_signed_at',
  'shipped_at',
  'received_at',
  'invoice_issued_at'
]);

// 格式化显示值
function formatValue(key, value) {
  if (dateFields.has(key) && value) {
    return dayjs(value).format('YYYY-MM-DD HH:mm:ss');
  }
  if (typeof value === 'boolean') {
    return value ? '是' : '否';
  }
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value);
  }
  return value;
}

watch(() => route.params.uuid, async (newUuid) => {
  if (!newUuid) return;
  console.log('CustomerDetail.vue - route uuid:', newUuid);
  const res = await apiRequest(`/customers?uuid=eq.${newUuid}`);
  console.log('CustomerDetail.vue - api response:', res);
  console.log('CustomerDetail.vue - first customer item:', res.items ? res.items[0] : null);
  customer.value = res.items && res.items.length > 0 ? res.items[0] : null;
  console.log('设置 customer.value =', customer.value);

  // TODO: Replace below with real API calls for orders
  orderCount.value = Math.floor(Math.random() * 10);  // simulate dynamic count
  totalValue.value = Math.floor(Math.random() * 100000);  // simulate dynamic total
}, { immediate: true });

// 编辑客户字段自动保存
async function editCustomer(field) {
  console.log('editCustomer 中当前 customer:', customer.value);
  console.log('editCustomer 中当前 uuid:', customer.value?.uuid);
  if (!customer.value || !customer.value.uuid) {
    console.warn('编辑字段失败：customer 或 uuid 不存在');
    return;
  }
  const uuid = customer.value.uuid;
  if (typeof uuid !== 'string' || !uuid || uuid === 'customers') {
    console.warn('编辑字段失败：uuid 非法');
    return;
  }
  const payload = {};
  payload[field] = customer.value[field];
  await apiRequest(`/customers?uuid=eq.${uuid}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  ElMessage.success(`“${field}”字段已成功更新`);
}

</script>