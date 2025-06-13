<template>
  <el-container style="padding: 24px; background: #fafafa; min-height: 100vh;">
    <el-main>
      <el-card
        shadow="hover"
        style="
          border-radius: 10px;
          box-shadow: 0 2px 12px rgba(0,0,0,0.05);
          background: #fff;
        "
      >
        <template #header>
          <div
            style="
              display: flex;
              justify-content: space-between;
              align-items: center;
              font-weight: 600;
              font-size: 20px;
              color: #303133;
            "
          >
            <span>客户列表</span>
            <el-button
              type="primary"
              icon="el-icon-plus"
              size="default"
              style="border-radius: 6px;"
              @click="goToAddCustomer"
            >
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
          <el-table-column
            type="index"
            label="序号"
            width="60"
            align="center"
          />
          <el-table-column
            prop="full_name"
            label="姓名"
            sortable
            min-width="140"
            align="center"
          />
          <el-table-column
            prop="phone"
            label="电话"
            sortable
            min-width="160"
            align="center"
          />
          <el-table-column
            prop="email"
            label="邮箱"
            min-width="180"
            align="center"
          />
          <el-table-column
            prop="company_name"
            label="公司"
            min-width="180"
            align="center"
          />
          <el-table-column
            prop="province"
            label="省份"
            min-width="100"
            align="center"
          />
          <el-table-column
            prop="city"
            label="城市"
            min-width="100"
            align="center"
          />
          <el-table-column
            prop="status"
            label="状态"
            min-width="100"
            align="center"
          />
          <el-table-column
            label="操作"
            width="260"
            align="center"
          >
            <template #default="scope">
              <el-button
                type="primary"
                icon="el-icon-view"
                size="small"
                @click="viewCustomer(scope.row)"
              >
                查看
              </el-button>
              <el-button
                type="warning"
                icon="el-icon-edit"
                size="small"
                @click="editCustomer(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                icon="el-icon-delete"
                size="small"
                @click="deleteCustomer(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          background
          layout="total, prev, pager, next, jumper"
          :total="customers.length"
          :page-size="pageSize"
          style="margin-top: 30px; text-align: right;"
          @current-change="handlePageChange"
        />

      </el-card>
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
      currentPage: 1,
      pageSize: 20,
      sortProp: 'name',
      sortOrder: 'ascending',
    };
  },
  computed: {
    sortedCustomers() {
      if (!this.sortProp) {
        return this.customers;
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
      return this.sortedCustomers.slice(start, start + this.pageSize);
    },
  },
  mounted() {
    this.loadCustomers();
  },
  methods: {
    async loadCustomers() {
      try {
        const data = await apiRequest('/customers', 'GET');
        this.customers = data;
      } catch (err) {
        console.error("获取客户列表失败:", err);
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
    addCustomer() {
      // 现在改为弹窗控制，不用此方法
    },
    handlePageChange(page) {
      this.currentPage = page;
    },
    goToAddCustomer() {
      this.$router.push('/customers/add');
    },
    handleSortChange({ prop, order }) {
      this.sortProp = prop;
      this.sortOrder = order;
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