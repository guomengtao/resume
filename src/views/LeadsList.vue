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
    
    <!-- 转为客户弹窗 -->
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

    const showOrderDialog = ref(false);
    const currentLead = ref(null);
    const orderList = ref([{
      order_number: '订单' + Math.floor(Math.random() * 1000000),
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
    }]);

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

    const convertToCustomer = (row) => {
      currentLead.value = row;
      orderList.value = [{
        ...orderList.value[0],
        order_number: 'ORD' + Math.floor(Math.random() * 1000000)
      }];
      showOrderDialog.value = true;
    };

    const submitOrder = async () => {
      try {
        if (!currentLead.value) return;

        const sanitizeDate = (d) => d === '' ? null : d;

        const orderData = {
          ...orderList.value[0],
          customer_id: currentLead.value.uuid,
          production_start_date: sanitizeDate(orderList.value[0].production_start_date),
          production_end_date: sanitizeDate(orderList.value[0].production_end_date),
        };

        await apiRequest('/orders', 'POST', orderData);

        await apiRequest('/customers', 'POST', {
          uuid: currentLead.value.uuid,
          full_name: currentLead.value.full_name,
          phone: currentLead.value.phone,
          email: currentLead.value.email,
          company_name: currentLead.value.company_name,
          position: currentLead.value.position,
          source: currentLead.value.source,
          level: currentLead.value.level,
          follow_up_count: currentLead.value.follow_up_count,
          created_by: currentLead.value.created_by,
          source_system: 'lead-convert'
        });

        await apiRequest(`/leads/${currentLead.value.id}`, 'PATCH', { converted: true });

        showOrderDialog.value = false;
        loadLeads();
      } catch (err) {
        console.error('提交订单失败:', err);
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
      showOrderDialog,
      orderList,
      currentLead,
      convertToCustomer,
      submitOrder,
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