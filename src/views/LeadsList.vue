<template>
  <div>
    <h2>线索列表</h2>
    <div style="margin-bottom: 16px; display: flex; align-items: center;">
      <el-input
        v-model="searchPhone"
        placeholder="搜索电话后四位"
        style="width: 250px;"
        clearable
        @clear="loadLeads"
        @input="loadLeads"
      />
    </div>
    <el-table
      :data="leads"
      style="width: 100%"
      stripe
      @sort-change="handleSortChange"
    >
      <el-table-column prop="full_name" label="姓名" />
      <el-table-column prop="phone" label="电话" sortable />
      <el-table-column prop="company_name" label="公司" />
      <el-table-column prop="level" label="客户等级" />
      <el-table-column prop="source" label="客户来源" />
      <el-table-column prop="follow_up_count" label="跟进次数" sortable />
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button size="small" @click="viewDetail(scope.row)">查看</el-button>
          <el-button size="small" type="primary" @click="editLead(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteLead(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      style="margin-top: 16px;"
      background
      layout="prev, pager, next, jumper"
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
  name: 'LeadsList',
  setup() {
    const leads = ref([]);
    const searchPhone = ref('');
    const page = ref(1);
    const pageSize = ref(10);
    const total = ref(0);
    const sortField = ref('');
    const sortOrder = ref('');

    const loadLeads = async () => {
      try {
        let query = `?page=${page.value}&pageSize=${pageSize.value}`;
        if (sortField.value) {
          query += `&sortField=${sortField.value}&sortOrder=${sortOrder.value}`;
        }
        if (searchPhone.value) {
          query += `&phoneLike=${searchPhone.value}`;
        }
        const data = await apiRequest('/leads' + query, 'GET');
        leads.value = data.items || data;
        total.value = data.total || data.length;
      } catch (error) {
        console.error('加载线索失败:', error);
      }
    };

    const handlePageChange = (newPage) => {
      page.value = newPage;
      loadLeads();
    };

    const handleSortChange = ({ prop, order }) => {
      sortField.value = prop;
      sortOrder.value = order === 'ascending' ? 'asc' : 'desc';
      loadLeads();
    };

    const viewDetail = (row) => {
      alert('查看: ' + row.full_name);
    };

    const editLead = (row) => {
      alert('编辑: ' + row.full_name);
    };

    const deleteLead = async (row) => {
      try {
        await apiRequest(`/leads/${row.id}`, 'PATCH', { is_deleted: true });
        loadLeads();
      } catch (error) {
        console.error('删除失败:', error);
      }
    };

    onMounted(() => {
      loadLeads();
    });

    return {
      leads, loadLeads, page, pageSize, total, handlePageChange,
      sortField, sortOrder, handleSortChange, searchPhone,
      viewDetail, editLead, deleteLead
    };
  },
};
</script>

<style scoped>
h2 {
  margin-bottom: 16px;
  color: #2c3e50;
}
</style>