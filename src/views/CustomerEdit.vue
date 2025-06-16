<template>
  <div class="edit-customer">
    <el-card>
      <h2>编辑客户信息</h2>
      <el-form :model="form" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="公司名称">
          <el-input v-model="form.company_name" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveCustomer">保存</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiRequest } from '../api/apiClient';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const form = ref({});

onMounted(async () => {
  const uuid = route.params.uuid;
  const res = await apiRequest(`/customers?uuid=eq.${uuid}`);
  form.value = res.items && res.items.length > 0 ? res.items[0] : {};
});

async function saveCustomer() {
  const id = form.value.id;
  if (!id) return;
  const payload = {
    full_name: form.value.full_name,
    phone: form.value.phone,
    email: form.value.email,
    company_name: form.value.company_name,
  };
  console.log('PATCH payload:', payload);
  await apiRequest(`/customers/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  ElMessage.success('客户信息已更新');
  router.push(`/customers/${id}`);
}
</script>

<style scoped>
.edit-customer {
  max-width: 600px;
  margin: 40px auto;
}
</style>