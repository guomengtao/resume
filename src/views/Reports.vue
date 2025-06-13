<template>
  <el-container style="padding: 20px;">
    <el-header style="font-size: 24px; font-weight: bold;">销售报表</el-header>
    
    <!-- 时间周期选择 -->
    <el-radio-group v-model="period" size="medium" @change="fetchData">
      <el-radio-button label="week">本周</el-radio-button>
      <el-radio-button label="month">本月</el-radio-button>
      <el-radio-button label="year">本年</el-radio-button>
    </el-radio-group>

    <el-main style="margin-top: 24px;">
      <!-- 关键指标 -->
      <el-row :gutter="20" class="kpi-row">
        <el-col :span="6" v-for="item in kpis" :key="item.label">
          <el-card>
            <div class="kpi-label">{{ item.label }}</div>
            <div class="kpi-value">{{ item.value }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 趋势图 -->
      <el-row :gutter="20" style="margin-top: 32px;">
        <el-col :span="12">
          <el-card>
            <div class="chart-title">销售额趋势</div>
            <div ref="salesChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <div class="chart-title">订单量趋势</div>
            <div ref="orderChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import * as echarts from 'echarts';

const period = ref('month'); // 默认本月

const kpis = reactive([
  { label: '总销售额', value: '¥0' },
  { label: '成交订单数', value: 0 },
  { label: '新增客户数', value: 0 },
  { label: '平均客单价', value: '¥0' },
]);

const salesChart = ref(null);
const orderChart = ref(null);
let salesChartInstance = null;
let orderChartInstance = null;

// 模拟获取数据
function fetchData() {
  // 模拟不同周期返回不同数据（真实项目调用接口）
  if (period.value === 'week') {
    kpis[0].value = '¥350,000';
    kpis[1].value = 120;
    kpis[2].value = 45;
    kpis[3].value = '¥2,916';

    updateSalesChart(['周一', '周二', '周三', '周四', '周五', '周六', '周日'], [50000, 45000, 48000, 52000, 60000, 38000, 35000]);
    updateOrderChart(['周一', '周二', '周三', '周四', '周五', '周六', '周日'], [15, 20, 18, 22, 25, 12, 8]);
  } else if (period.value === 'month') {
    kpis[0].value = '¥1,200,000';
    kpis[1].value = 450;
    kpis[2].value = 120;
    kpis[3].value = '¥2,667';

    const days = Array.from({ length: 30 }, (_, i) => i + 1);
    const sales = days.map(() => Math.floor(30000 + Math.random() * 20000));
    const orders = days.map(() => Math.floor(10 + Math.random() * 20));

    updateSalesChart(days, sales);
    updateOrderChart(days, orders);
  } else if (period.value === 'year') {
    kpis[0].value = '¥15,000,000';
    kpis[1].value = 5200;
    kpis[2].value = 1200;
    kpis[3].value = '¥2,885';

    const months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
    const sales = months.map(() => Math.floor(1000000 + Math.random() * 500000));
    const orders = months.map(() => Math.floor(400 + Math.random() * 100));

    updateSalesChart(months, sales);
    updateOrderChart(months, orders);
  }
}

function updateSalesChart(categories, data) {
  if (!salesChartInstance) salesChartInstance = echarts.init(salesChart.value);
  salesChartInstance.setOption({
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
    tooltip: { trigger: 'axis' },
    series: [{ data, type: 'line', smooth: true, color: '#409EFF' }],
    title: { text: '' }, // 不显示标题
  });
}

function updateOrderChart(categories, data) {
  if (!orderChartInstance) orderChartInstance = echarts.init(orderChart.value);
  orderChartInstance.setOption({
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value' },
    tooltip: { trigger: 'axis' },
    series: [{ data, type: 'bar', itemStyle: { color: '#67C23A' } }],
    title: { text: '' }, // 不显示标题
  });
}

onMounted(() => {
  fetchData();
});

watch(period, () => {
  fetchData();
});
</script>

<style scoped>
.kpi-row {
  margin-top: 20px;
}
.kpi-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}
.kpi-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}
.chart-title {
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 12px;
  color: #303133;
}
</style>