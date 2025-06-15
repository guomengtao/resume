<template>
  <el-container style="padding: 24px; background: #fafafa; min-height: 100vh;">
    <el-main>
      <el-card shadow="hover" style="border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); background: #fff;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 20px; color: #303133;">
            <span>客户列表</span>
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
          <el-table-column type="index" label="序号" width="50" align="center" />
          <el-table-column prop="company_name" label="公司名称" width="100" align="center" />
          <el-table-column prop="full_name" label="姓名" sortable width="80" align="center" />
          <el-table-column label="累计成交金额" prop="total_order_amount" width="100" align="center">
            <template #default="scope">
              <span style="cursor: pointer; color: #409EFF;" @click="goToOrders(scope.row)">
                {{ scope.row.total_order_amount }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="订单数量" prop="order_count" width="80" align="center">
            <template #default="scope">
              <span style="cursor: pointer; color: #409EFF;" @click="goToOrders(scope.row)">
                {{ scope.row.order_count }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="跟进次数" prop="follow_up_count" width="80" align="center" />
          <el-table-column label="客户等级" prop="level" width="80" align="center" />
          <el-table-column label="最近跟进记录" width="160" align="center">
            <template #default="scope">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  {{ scope.row.last_followup || '无' }}
                </span>
                <el-button type="text" size="small" @click="openFollowUpDialog(scope.row)">跟进</el-button>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button type="primary" size="small" @click="openOrderDialog(scope.row)">下单</el-button>
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
  <el-dialog title="提交订单" v-model="showOrderDialog" width="700px" append-to-body>
    <el-form :model="orderList[0]" label-width="120px">
      <el-form-item label="订单号">
        <el-input v-model="orderList[0].order_number" />
      </el-form-item>
      <el-form-item label="总金额">
        <el-input v-model.number="orderList[0].total_amount" type="number" />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="orderList[0].status" placeholder="请选择状态">
          <el-option label="待支付" value="pending" />
          <el-option label="已支付" value="paid" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item label="支付方式">
        <el-input v-model="orderList[0].payment_method" />
      </el-form-item>
      <el-form-item label="支付状态">
        <el-input v-model="orderList[0].payment_status" />
      </el-form-item>
      <el-form-item label="生产类型">
        <el-select v-model="orderList[0].production_type" placeholder="请选择类型">
          <el-option label="批量" value="批量" />
          <el-option label="定制" value="定制" />
          <el-option label="小批量" value="小批量" />
        </el-select>
      </el-form-item>
      <el-form-item label="生产开始日期">
        <el-date-picker
          v-model="orderList[0].production_start_date"
          type="date"
          placeholder="选择日期"
          format="yyyy-MM-dd"
          value-format="yyyy-MM-dd"
        />
      </el-form-item>
      <el-form-item label="预计完成日期">
        <el-date-picker
          v-model="orderList[0].production_end_date"
          type="date"
          placeholder="选择日期"
          format="yyyy-MM-dd"
          value-format="yyyy-MM-dd"
        />
      </el-form-item>
      <el-form-item label="收货地址">
        <el-input v-model="orderList[0].shipping_address" />
      </el-form-item>
      <el-form-item label="物流公司">
        <el-input v-model="orderList[0].logistics_company" />
      </el-form-item>
      <el-form-item label="运单号">
        <el-input v-model="orderList[0].tracking_number" />
      </el-form-item>
      <el-form-item label="折扣金额">
        <el-input v-model.number="orderList[0].discount_amount" type="number" />
      </el-form-item>
      <el-form-item label="税费">
        <el-input v-model.number="orderList[0].tax_amount" type="number" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input type="textarea" v-model="orderList[0].remarks" />
      </el-form-item>
    </el-form>
    <span slot="footer" class="dialog-footer">
      <el-button @click="showOrderDialog = false">取消</el-button>
      <el-button type="primary" @click="submitOrder">提交订单</el-button>
    </span>
  </el-dialog>
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
      showFollowUpDialog: false,
      followUpForm: {
        customer_id: null,
        contact_result: '',
        next_follow_up_date: '',
        notes: ''
      },
      showOrderDialog: false,
      orderList: [{
        order_number: 'ORD' + Math.floor(Math.random() * 1000000),
        total_amount: Math.floor(Math.random() * 10000),
        status: 'pending',
        payment_method: '微信支付',
        payment_status: '未支付',
        production_type: '批量',
        production_start_date: '',
        production_end_date: '',
        shipping_address: '北京市朝阳区建国路',
        logistics_company: '顺丰快递',
        tracking_number: 'SF' + Math.floor(100000 + Math.random() * 900000),
        discount_amount: Math.floor(Math.random() * 500),
        tax_amount: Math.floor(Math.random() * 200),
        remarks: '测试备注信息'
      }],
      currentCustomer: null,
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
        const data = await apiRequest('/view_customers_with_latest_followup', 'GET');
        this.customers = Array.isArray(data.items) ? data.items : [];
        this.total = data.total || this.customers.length;
      } catch (err) {
        console.error("获取客户列表失败:", err);
        this.customers = [];
        this.total = 0;
      }
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
    goToOrders(row) {
      this.$router.push({ path: '/orders', query: { customer_id: row.uuid } });
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
    openFollowUpDialog(row) {
      this.followUpForm = {
        customer_id: row.uuid,
        contact_result: '',
        next_follow_up_date: '',
        notes: ''
      };
      this.showFollowUpDialog = true;
    },
    openOrderDialog(row) {
      this.currentCustomer = row;
      this.orderList = [{
        ...this.orderList[0],
        order_number: 'ORD' + Math.floor(Math.random() * 1000000)
      }];
      this.showOrderDialog = true;
    },
    async submitOrder() {
      try {
        if (!this.currentCustomer) return;
        const sanitizeDate = (d) => d === '' ? null : d;
        const orderData = {
          ...this.orderList[0],
          customer_id: this.currentCustomer.uuid,
          production_start_date: sanitizeDate(this.orderList[0].production_start_date),
          production_end_date: sanitizeDate(this.orderList[0].production_end_date),
        };
        await apiRequest('/orders', 'POST', orderData);
        await this.loadCustomers();
        this.showOrderDialog = false;
        this.$message.success('订单已提交');
      } catch (err) {
        console.error('提交订单失败:', err);
        this.$message.error('提交失败');
      }
    },
    async submitFollowUp() {
      try {
        if (!this.followUpForm.customer_id) return;
        await apiRequest('/followups', 'POST', this.followUpForm);
        this.showFollowUpDialog = false;
        this.loadCustomers();
      } catch (error) {
        console.error('提交跟进失败:', error);
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