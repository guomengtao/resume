<template>
  <div>
    <h2>线索列表</h2>
    <div style="margin-bottom: 16px; display: flex; align-items: center;">
      <el-button
        type="primary"
        icon="el-icon-plus"
        style="margin-right: 16px;"
        @click="goToAddLead"
      >
        添加线索
      </el-button>
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
      <el-table-column prop="latest_contact_result" label="最近跟进" />
      <el-table-column prop="follow_up_count" label="跟进次数" sortable />
      <el-table-column label="操作" width="400">
        <template #default="scope">
          <el-button size="small" @click="viewDetail(scope.row)">查看</el-button>
          <el-button size="small" v-if="!scope.row.converted" type="info" @click="openFollowUpDialog(scope.row)">跟进</el-button>
          <el-button size="small" v-if="!scope.row.converted" type="primary" @click="editLead(scope.row)">编辑</el-button>
          <el-button size="small" v-if="!scope.row.converted" type="danger" @click="deleteLead(scope.row)">删除</el-button>
          <el-button size="small" v-if="!scope.row.converted" type="success" @click="convertToCustomer(scope.row)">转为客户</el-button>
          <el-button size="small" v-else disabled>已成交</el-button>
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
    
    <!-- 跟进记录弹窗 -->
    <el-dialog title="添加跟进记录" v-model="showFollowUpDialog" width="500px" append-to-body>
      <el-form :model="followUpForm" label-width="100px">
        <el-form-item label="跟进结果">
          <el-input type="textarea" v-model="followUpForm.contact_result" />
        </el-form-item>
        <el-form-item label="下次跟进时间">
          <el-date-picker
            v-model="followUpForm.next_follow_up_date"
            type="date"
            placeholder="选择日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input type="textarea" v-model="followUpForm.notes" />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="showFollowUpDialog = false">取消</el-button>
        <el-button type="primary" @click="submitFollowUp">提交</el-button>
      </span>
    </el-dialog>
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

    const showFollowUpDialog = ref(false);
    const followUpForm = ref({
      customer_id: null, // 使用 uuid
      contact_result: '',
      next_follow_up_date: '',
      notes: ''
    });

    const loadLeads = async () => {
      try {
        let query = `?page=${page.value}&pageSize=${pageSize.value}`;
        if (sortField.value) {
          query += `&sortField=${sortField.value}&sortOrder=${sortOrder.value}`;
        }
        if (searchPhone.value) {
          query += `&phoneLike=${searchPhone.value}`;
        }
        const data = await apiRequest('/view_leads_with_latest_followup' + query, 'GET');
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

    const openFollowUpDialog = (row) => {
      followUpForm.value = {
        customer_id: row.uuid,
        contact_result: '',
        next_follow_up_date: '',
        notes: ''
      };
      showFollowUpDialog.value = true;
    };

    const submitFollowUp = async () => {
      try {
        if (!followUpForm.value.customer_id) return;
        await apiRequest('/followups', 'POST', followUpForm.value);
        showFollowUpDialog.value = false;
        loadLeads();
      } catch (error) {
        console.error('提交跟进失败:', error);
      }
    };

    onMounted(() => {
      loadLeads();
    });

    return {
      leads,
      searchPhone,
      page,
      pageSize,
      total,
      sortField,
      sortOrder,
      showFollowUpDialog,
      followUpForm,
      loadLeads,
      handlePageChange,
      handleSortChange,
      viewDetail,
      editLead,
      deleteLead,
      openFollowUpDialog,
      submitFollowUp,
      goToAddLead() {
        window.location.href = '/leads/add';
      }
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