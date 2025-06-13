<template>
  <el-container style="padding: 24px; background: #fafafa; min-height: 100vh;">
    <el-main>
      <el-card
        shadow="hover"
        style="border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); background: #fff;"
      >
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 20px; color: #303133;">
            <span>客户列表</span>
            <el-button type="primary" icon="el-icon-plus" size="default" style="border-radius: 6px;" @click="goToAddCustomer">
              添加客户
            </el-button>
          </div>
        </template>

        <el-table
          :data="pagedCustomers"
          stripe
          border
          highlight-current-row
          style="width: 100%; border-radius: 6px; overflow: hidden;"
          :default-sort="{ prop: 'full_name', order: 'ascending' }"
          @sort-change="handleSortChange"
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="full_name" label="姓名" sortable min-width="140" align="center" />
          <el-table-column prop="phone" label="电话" sortable min-width="160" align="center" />
          <el-table-column prop="email" label="邮箱" min-width="180" align="center" />
          <el-table-column prop="company_name" label="公司" min-width="180" align="center" />
          <el-table-column prop="province" label="省份" min-width="100" align="center" />
          <el-table-column prop="city" label="城市" min-width="100" align="center" />
          <el-table-column prop="status" label="状态" min-width="100" align="center" />
          <el-table-column prop="last_followup" label="最后跟进" min-width="160" align="center">
            <template #default="scope">
              <span>{{ scope.row.last_followup ? scope.row.last_followup.slice(0, 10) : '暂无' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="300" align="center">
            <template #default="scope">
              <el-button type="primary" icon="el-icon-view" size="small" @click="viewCustomer(scope.row)">查看</el-button>
              <el-button type="warning" icon="el-icon-edit" size="small" @click="editCustomer(scope.row)">编辑</el-button>
              <el-button type="danger" icon="el-icon-delete" size="small" @click="deleteCustomer(scope.row.id)">删除</el-button>
              <el-button type="success" icon="el-icon-message" size="small" @click="openFollowUpDialog(scope.row)">跟进</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          background
          layout="total, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          style="margin-top: 30px; text-align: right;"
          @current-change="handlePageChange"
        />
      </el-card>

      <el-dialog v-model="followUpDialogVisible" title="登记跟进" width="500px">
        <el-form :model="followUpForm" label-width="100px">
          <el-form-item label="跟进内容">
            <el-input type="textarea" v-model="followUpForm.contact_result" />
          </el-form-item>
          <el-form-item label="下次时间">
            <el-date-picker v-model="followUpForm.next_follow_up_date" type="date" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="followUpDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitFollowUp">提交</el-button>
        </template>
      </el-dialog>

    </el-main>
  </el-container>
</template>

<script>
import { apiRequest } from '../api/apiClient';

export default {
  name: "Customers",
  data() {
    return {
      customers: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      sortProp: 'full_name',
      sortOrder: 'ascending',
      followUpDialogVisible: false,
      followUpForm: {
        contact_result: '',
        next_follow_up_date: ''
      },
      followUpCustomer: null
    };
  },
  computed: {
    sortedCustomers() {
      if (!Array.isArray(this.customers) || !this.sortProp) {
        return this.customers || [];
      }
      const order = this.sortOrder === 'ascending' ? 1 : -1;
      return [...this.customers].sort((a, b) => {
        const valA = a[this.sortProp];
        const valB = b[this.sortProp];
        if (valA === valB) return 0;
        return valA > valB ? order : -order;
      });
    },
    pagedCustomers() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.sortedCustomers.slice(start, end);
    },
  },
  mounted() {
    this.loadCustomers();
  },
  methods: {
    async loadCustomers() {
  try {
    const data = await apiRequest('/view_customers_with_latest_followup', 'GET');
    console.log('API /view_customers_with_latest_followup response:', data);
    this.customers = Array.isArray(data.items) ? data.items : [];
    this.total = data.total || 0;
  } catch (err) {
    console.error("获取客户列表失败:", err);
    this.customers = [];
    this.total = 0;
  }
},
    viewCustomer(customer) {
      console.log("查看", customer);
    },
    editCustomer(customer) {
      console.log("编辑", customer);
    },
    deleteCustomer(id) {
      console.log("删除", id);
    },
    openFollowUpDialog(customer) {
      this.followUpCustomer = customer;
      this.followUpForm = {
        contact_result: '',
        next_follow_up_date: ''
      };
      this.followUpDialogVisible = true;
    },
    async submitFollowUp() {
      try {
        await apiRequest('/followups', 'POST', {
          customer_id: this.followUpCustomer.uuid,
          contact_result: this.followUpForm.contact_result,
          next_follow_up_date: this.followUpForm.next_follow_up_date
        });
        this.followUpDialogVisible = false;
        this.loadCustomers();
      } catch (err) {
        console.error('提交跟进失败:', err);
      }
    },
    handlePageChange(page) {
      this.currentPage = page;
      this.loadCustomers();
    },
    goToAddCustomer() {
      this.$router.push('/customers/add');
    },
    handleSortChange({ prop, order }) {
      this.sortProp = prop;
      this.sortOrder = order;
      this.loadCustomers();
    },
  },
};
</script>

<style scoped>
.el-table th {
  background-color: #f5f7fa !important;
  color: #606266 !important;
  font-weight: 600;
  user-select: none;
}
.el-button-group .el-button {
  margin-right: 8px;
}
</style>