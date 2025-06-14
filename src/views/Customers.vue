<template>
  <el-container style="padding: 24px; background: #fafafa; min-height: 100vh;">
    <el-main>
      <el-card shadow="hover" style="border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); background: #fff;">
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
          <el-table-column prop="company_name" label="公司名称" min-width="180" align="center" />
          <el-table-column prop="full_name" label="姓名" sortable min-width="140" align="center" />

          <el-table-column label="合同是否回传" prop="contract_signed" width="130" align="center">
            <template #default="scope">
              <el-icon
                v-if="scope.row.contract_signed"
                :size="22"
                color="red"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'contract_signed')"
              >
                <Check />
              </el-icon>
              <el-icon
                v-else
                :size="20"
                color="#c0c4cc"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'contract_signed')"
              >
                <Close />
              </el-icon>
            </template>
          </el-table-column>

          <el-table-column label="生产完成" prop="production_scheduled" width="80" align="center">
            <template #default="scope">
              <el-icon
                v-if="scope.row.production_scheduled"
                :size="22"
                color="red"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'production_scheduled')"
              >
                <Check />
              </el-icon>
              <el-icon
                v-else
                :size="20"
                color="#c0c4cc"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'production_scheduled')"
              >
                <Close />
              </el-icon>
            </template>
          </el-table-column>

          <el-table-column label="已发货" prop="shipment_scheduled" width="80" align="center">
            <template #default="scope">
              <el-icon
                v-if="scope.row.shipment_scheduled"
                :size="22"
                color="red"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'shipment_scheduled')"
              >
                <Check />
              </el-icon>
              <el-icon
                v-else
                :size="20"
                color="#c0c4cc"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'shipment_scheduled')"
              >
                <Close />
              </el-icon>
            </template>
          </el-table-column>

          <el-table-column label="已收货" prop="received" width="80" align="center">
            <template #default="scope">
              <el-icon
                v-if="scope.row.received"
                :size="22"
                color="red"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'received')"
              >
                <Check />
              </el-icon>
              <el-icon
                v-else
                :size="20"
                color="#c0c4cc"
                style="cursor: pointer;"
                @click="toggleStepStatus(scope.row, 'received')"
              >
                <Close />
              </el-icon>
            </template>
          </el-table-column>

          <el-table-column label="是否开票" prop="invoice_issued" width="120" align="center">
            <template #default="scope">
              <div style="display: flex; align-items: center; justify-content: center;">
                <el-icon
                  v-if="scope.row.invoice_issued"
                  :size="26"
                  color="red"
                  style="cursor: pointer; font-weight: 800;"
                  @click="toggleStepStatus(scope.row, 'invoice_issued')"
                >
                  <Check />
                </el-icon>
                <el-icon
                  v-else
                  :size="24"
                  color="#c0c4cc"
                  style="cursor: pointer;"
                  @click="toggleStepStatus(scope.row, 'invoice_issued')"
                >
                  <Close />
                </el-icon>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="260" align="center">
            <template #default="scope">
              <el-button type="primary" size="small" @click="viewCustomer(scope.row)">查看</el-button>
              <el-button type="warning" size="small" @click="editCustomer(scope.row)">编辑</el-button>
              <el-button type="danger" size="small" @click="deleteCustomer(scope.row.id)">删除</el-button>
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
    </el-main>
  </el-container>
</template>

<script>
import { apiRequest } from '../api/apiClient';
import { Check, CircleCheck, Close } from '@element-plus/icons-vue';

export default {
  name: "Customers",
  components: {
    Check,
    CircleCheck,
    Close,
  },
  data() {
    return {
      customers: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      sortProp: 'full_name',
      sortOrder: 'ascending',
      stepConfig: [
        { key: 'converted', label: '成交' },
        { key: 'contract_signed', label: '签约' },
        { key: 'production_scheduled', label: '生产' },
        { key: 'shipment_scheduled', label: '发货' },
        { key: 'received', label: '完成' },
      ],
    };
  },
  computed: {
    sortedCustomers() {
      if (!Array.isArray(this.customers) || !this.sortProp) return this.customers || [];
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
        const data = await apiRequest('/view_customers_with_progress', 'GET');
        this.customers = Array.isArray(data.items) ? data.items : [];
        this.total = data.total || this.customers.length;
      } catch (err) {
        console.error("获取客户列表失败:", err);
        this.customers = [];
        this.total = 0;
      }
    },
    viewCustomer(row) {
      console.log("查看", row);
    },
    editCustomer(row) {
      console.log("编辑", row);
    },
    deleteCustomer(id) {
      console.log("删除", id);
    },
    async updateProgress(row) {
      try {
        const progressMap = {
          0: { converted: true, contract_signed: false, production_scheduled: false, shipment_scheduled: false, received: false },
          1: { converted: true, contract_signed: true, production_scheduled: false, shipment_scheduled: false, received: false },
          2: { converted: true, contract_signed: true, production_scheduled: true, shipment_scheduled: false, received: false },
          3: { converted: true, contract_signed: true, production_scheduled: true, shipment_scheduled: true, received: false },
          4: { converted: true, contract_signed: true, production_scheduled: true, shipment_scheduled: true, received: true },
        };

        const fieldsToUpdate = progressMap[row.progress_stage] || {};
        if (!row.uuid) {
          this.$message.error('客户 UUID 不存在，无法更新');
          return;
        }

        await apiRequest(`/customers?uuid=${row.uuid}`, 'PATCH', fieldsToUpdate);
        this.$message.success('进度已更新');
        this.loadCustomers();
      } catch (error) {
        console.error('更新进度失败:', error);
        this.$message.error('更新失败');
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
    handleStepClick(stepKey, row) {
      switch (stepKey) {
        case 'contract_signed':
          // Open contract upload dialog
          this.$message.info('请上传合同');
          break;
        case 'shipment_scheduled':
          // Open logistics form
          this.$message.info('请填写发货信息');
          break;
        default:
          this.toggleStepStatus(row, stepKey);
      }
    },
    async toggleStepStatus(row, stepKey) {
      try {
        const newStatus = !row[stepKey];
        await apiRequest(`/customers?uuid=${row.uuid}`, 'PATCH', {
          [stepKey]: newStatus,
        });
        this.$message.success('状态已更新');
        this.loadCustomers();
      } catch (error) {
        console.error('更新状态失败:', error);
        this.$message.error('更新失败');
      }
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
</style>