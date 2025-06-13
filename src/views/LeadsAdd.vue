<template>
  <el-card style="max-width: 800px; margin: auto; margin-top: 40px;" shadow="hover">
    <template #header>
      <span>新增线索</span>
    </template>
    <el-form :model="form" ref="formRef" label-width="120px" label-position="left">
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
      <el-form-item label="职位">
        <el-input v-model="form.position" />
      </el-form-item>
      <el-form-item label="客户来源">
        <el-input v-model="form.source" />
      </el-form-item>
      <el-form-item label="渠道详情">
        <el-input v-model="form.channel_detail" />
      </el-form-item>
      <el-form-item label="营销活动编号">
        <el-input v-model="form.campaign_id" />
      </el-form-item>
      <el-form-item label="客户等级">
        <el-select v-model="form.level" placeholder="选择等级">
          <el-option v-for="item in ['A','B','C','D','E','F']" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="线索评分">
        <el-input-number v-model="form.lead_score" :min="0" />
      </el-form-item>
      <el-form-item label="状态">
        <el-input v-model="form.status" />
      </el-form-item>
      <el-form-item label="分配销售">
        <el-input v-model="form.assigned_to" />
      </el-form-item>
      <el-form-item label="下次跟进时间">
        <el-date-picker v-model="form.next_follow_up_date" type="date" placeholder="选择日期" />
      </el-form-item>
      <el-form-item label="最近联系时间">
        <el-date-picker v-model="form.last_contact_date" type="datetime" placeholder="选择时间" />
      </el-form-item>
      <el-form-item label="省份">
        <el-input v-model="form.province" />
      </el-form-item>
      <el-form-item label="城市">
        <el-input v-model="form.city" />
      </el-form-item>
      <el-form-item label="所属行业">
        <el-input v-model="form.industry" />
      </el-form-item>
      <el-form-item label="公司官网">
        <el-input v-model="form.website" />
      </el-form-item>
      <el-form-item label="性别">
        <el-select v-model="form.gender" placeholder="选择性别">
          <el-option label="男" value="男" />
          <el-option label="女" value="女" />
          <el-option label="未知" value="未知" />
        </el-select>
      </el-form-item>
      <el-form-item label="年龄段">
        <el-select v-model="form.age_group" placeholder="选择年龄段">
          <el-option label="18-25" value="18-25" />
          <el-option label="26-35" value="26-35" />
          <el-option label="36-45" value="36-45" />
          <el-option label="46+" value="46+" />
        </el-select>
      </el-form-item>
      <el-form-item label="沟通偏好">
        <el-select v-model="form.communication_preference" placeholder="选择沟通方式">
          <el-option label="电话" value="电话" />
          <el-option label="微信" value="微信" />
          <el-option label="邮件" value="邮件" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否决策人">
        <el-switch v-model="form.decision_maker" />
      </el-form-item>
      <el-form-item label="潜在成交金额">
        <el-input-number v-model="form.estimated_value" :min="0" :step="1000" />
      </el-form-item>
      <el-form-item label="优先级">
        <el-select v-model="form.priority" placeholder="选择优先级">
          <el-option label="高" value="高" />
          <el-option label="中" value="中" />
          <el-option label="低" value="低" />
        </el-select>
      </el-form-item>
      <el-form-item label="竞品信息">
        <el-input type="textarea" v-model="form.competitor_info" />
      </el-form-item>
      <el-form-item label="兴趣标签">
        <el-input v-model="form.interest_tags_str" placeholder="用逗号分隔" />
      </el-form-item>
      <el-form-item label="自定义字段">
        <div style="width: 100%;">
          <div
            v-for="(item, index) in form.custom_fields_kv"
            :key="index"
            style="display: flex; gap: 10px; margin-bottom: 8px;"
          >
            <el-input v-model="item.key" placeholder="字段名（支持中文）" />
            <el-input v-model="item.value" placeholder="内容" />
            <el-button type="danger" :icon="Delete" @click="form.custom_fields_kv.splice(index, 1)">
              删除
            </el-button>
          </div>
          <el-button type="primary" plain @click="form.custom_fields_kv.push({ key: '', value: '' })">
            + 添加字段
          </el-button>
        </div>
      </el-form-item>
      <el-form-item label="备注">
        <el-input type="textarea" v-model="form.notes" />
      </el-form-item>
      <el-form-item label="跟进次数">
        <el-input-number v-model="form.follow_up_count" :min="0" />
      </el-form-item>
      <el-form-item label="是否已转化">
        <el-switch v-model="form.converted" />
      </el-form-item>
      <el-form-item label="转化时间">
        <el-date-picker v-model="form.converted_at" type="datetime" placeholder="选择时间" />
      </el-form-item>
      <el-form-item label="创建人">
        <el-input v-model="form.created_by" />
      </el-form-item>
      <el-form-item label="数据来源系统">
        <el-input v-model="form.source_system" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { Delete } from '@element-plus/icons-vue'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { faker } from '@faker-js/faker/locale/zh_CN'
import { supabase } from '../api/supabaseClient'

const formRef = ref(null)
const form = ref({
  full_name: '',
  phone: '',
  email: '',
  company_name: '',
  position: '',
  source: '',
  channel_detail: '',
  campaign_id: '',
  level: 'C',
  lead_score: 0,
  status: '',
  assigned_to: '',
  next_follow_up_date: null,
  last_contact_date: null,
  province: '',
  city: '',
  industry: '',
  website: '',
  gender: '',
  age_group: '',
  communication_preference: '',
  decision_maker: false,
  estimated_value: 0,
  priority: '',
  competitor_info: '',
  interest_tags_str: '', // 用逗号分隔的字符串
  custom_fields_kv: [
    { key: '备注1', value: '值1' }
  ],
  notes: '',
  follow_up_count: 0,
  converted: false,
  converted_at: null,
  created_by: '',
  source_system: '',
  contract_signed: false,
  contract_signed_at: null,
  deposit_paid: false,
  deposit_amount: 0,
  production_scheduled: false,
  production_completed: false,
  balance_paid: false,
  balance_amount: 0,
  shipment_scheduled: false,
  shipped_at: null,
  received: false,
  received_at: null,
  invoice_issued: false,
  invoice_number: '',
  invoice_issued_at: null
})

// 载入页面时生成随机中文演示数据
const randomizeForm = () => {
  form.value.full_name = faker.person.fullName()
  form.value.phone = faker.phone.number('1##########')
  form.value.email = faker.internet.email()
  form.value.company_name = faker.company.name()
  form.value.position = faker.person.jobTitle()
  form.value.source = faker.company.name() + '推荐'
  form.value.channel_detail = faker.lorem.sentence()
  form.value.campaign_id = faker.string.alphanumeric(6)
  form.value.level = ['A', 'B', 'C', 'D', 'E', 'F'][Math.floor(Math.random() * 6)]
  form.value.lead_score = Math.floor(Math.random() * 100)
  form.value.status = '新建'
  form.value.assigned_to = faker.person.fullName()
  form.value.province = faker.address.state()
  form.value.city = faker.address.city()
  form.value.industry = faker.commerce.department()
  form.value.website = faker.internet.url()
  form.value.gender = ['男', '女', '未知'][Math.floor(Math.random() * 3)]
  form.value.age_group = ['18-25', '26-35', '36-45', '46+'][Math.floor(Math.random() * 4)]
  form.value.communication_preference = ['电话', '微信', '邮件'][Math.floor(Math.random() * 3)]
  form.value.decision_maker = faker.datatype.boolean()
  form.value.estimated_value = Math.floor(Math.random() * 100000)
  form.value.priority = ['高', '中', '低'][Math.floor(Math.random() * 3)]
  form.value.competitor_info = faker.lorem.sentences(2)
  form.value.interest_tags_str = faker.helpers.arrayElements(['ERP', 'SaaS', '云计算', '大数据', 'AI', '物联网'], 3).join(', ')
  form.value.custom_fields_kv = [
    { key: '跟进方式', value: faker.helpers.arrayElement(['电话', '微信', '拜访']) },
    { key: '客户预算', value: faker.commerce.price() + '元' }
  ];
  form.value.notes = faker.lorem.sentences(2)
  form.value.follow_up_count = Math.floor(Math.random() * 20)
  form.value.converted = false
  form.value.created_by = faker.person.fullName()
  form.value.source_system = ['CRM导入', '表单', '电话销售'][Math.floor(Math.random() * 3)]
  form.value.contract_signed = false
  form.value.deposit_paid = false
  form.value.production_scheduled = false
  form.value.production_completed = false
  form.value.balance_paid = false
  form.value.shipment_scheduled = false
  form.value.received = false
  form.value.invoice_issued = false
}

randomizeForm()

const submitForm = async () => {
  // 转换 interest_tags 和 custom_fields
  let interestTags = form.value.interest_tags_str.split(',').map(t => t.trim()).filter(Boolean);
  let customFields = {};
  form.value.custom_fields_kv.forEach(({ key, value }) => {
    if (key) customFields[key] = value;
  });

  const insertData = {
    full_name: form.value.full_name,
    phone: form.value.phone,
    email: form.value.email,
    company_name: form.value.company_name,
    position: form.value.position,
    source: form.value.source,
    channel_detail: form.value.channel_detail,
    campaign_id: form.value.campaign_id,
    level: form.value.level,
    lead_score: form.value.lead_score,
    status: form.value.status,
    assigned_to: form.value.assigned_to,
    next_follow_up_date: form.value.next_follow_up_date,
    last_contact_date: form.value.last_contact_date,
    province: form.value.province,
    city: form.value.city,
    industry: form.value.industry,
    website: form.value.website,
    gender: form.value.gender,
    age_group: form.value.age_group,
    communication_preference: form.value.communication_preference,
    decision_maker: form.value.decision_maker,
    estimated_value: form.value.estimated_value,
    priority: form.value.priority,
    competitor_info: form.value.competitor_info,
    notes: form.value.notes,
    follow_up_count: form.value.follow_up_count,
    converted: form.value.converted,
    converted_at: form.value.converted_at,
    created_by: form.value.created_by,
    source_system: form.value.source_system,
    interest_tags: interestTags,
    custom_fields: customFields
  };

  try {
    const { data, error } = await supabase.from('leads').insert([insertData]);
    if (error) throw error;
    ElMessage.success('提交成功');
    randomizeForm();
  } catch (err) {
    console.error(err);
    ElMessage.error('提交失败');
  }
}
</script>

<style scoped>
.el-card {
  padding: 20px;
}
</style>
