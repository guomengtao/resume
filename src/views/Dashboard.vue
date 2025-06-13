<template>
  <el-container style="padding: 24px; background: #fafafa; min-height: 100vh;">
    <el-header style="font-size: 24px; font-weight: bold; color: #409EFF;">
      数据看板
    </el-header>
    <el-main>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card>
            <div class="stat-title">本月销售额</div>
            <div class="stat-value">{{ formatCurrency(monthlySales) }}</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <div class="stat-title">成交订单数</div>
            <div class="stat-value">{{ totalOrders }}</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <div class="stat-title">新增客户数</div>
            <div class="stat-value">{{ newCustomers }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 24px;">
        <el-col :span="12">
          <el-card>
            <div class="chart-title">月度销售趋势</div>
            <div ref="salesTrendChart" style="height: 300px;"></div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <div class="chart-title">客户来源占比</div>
            <div ref="sourcePieChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 24px;">
        <el-col :span="24">
          <el-card>
            <div class="chart-title">销售漏斗</div>
            <div ref="funnelChart" style="height: 350px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';

// 随机辅助函数
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// --- Mock Data (随机生成) ---
const monthlySales = randomInt(800000, 1500000) + Math.random().toFixed(2) * 100;
const totalOrders = randomInt(250, 500);
const newCustomers = randomInt(50, 120);

const salesTrendData = {
  months: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
  sales: Array.from({ length: 12 }, () => randomInt(100000, 200000)),
};

const sourceData = [
  { value: randomInt(700, 1200), name: '官网' },
  { value: randomInt(500, 900), name: '展会' },
  { value: randomInt(400, 700), name: '推荐' },
  { value: randomInt(300, 600), name: '电话营销' },
  { value: randomInt(150, 400), name: '邮件' },
];

const funnelData = [
  { value: randomInt(800, 1200), name: '线索' },
  { value: randomInt(600, 900), name: '联系' },
  { value: randomInt(400, 700), name: '需求确认' },
  { value: randomInt(200, 500), name: '报价' },
  { value: randomInt(100, 300), name: '成交' },
];

// --- Format currency ---
function formatCurrency(value) {
  return '¥' + Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// --- Chart refs ---
const salesTrendChart = ref(null);
const sourcePieChart = ref(null);
const funnelChart = ref(null);

// --- Init charts ---
function initSalesTrendChart() {
  const chart = echarts.init(salesTrendChart.value);
  const option = {
    // title: { text: '月度销售趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: salesTrendData.months,
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '¥{value}' },
    },
    series: [
      {
        name: '销售额',
        type: 'line',
        data: salesTrendData.sales,
        smooth: true,
        areaStyle: {},
        color: '#409EFF',
      },
    ],
  };
  chart.setOption(option);
}

function initSourcePieChart() {
  const chart = echarts.init(sourcePieChart.value);
  const option = {
    title: { text: '客户来源占比', left: 'center' },
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: '来源',
        type: 'pie',
        radius: '50%',
        data: sourceData,
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' },
        },
      },
    ],
  };
  chart.setOption(option);
}

function initFunnelChart() {
  const chart = echarts.init(funnelChart.value);
  const option = {
   // title: { text: '销售漏斗' },
    tooltip: { trigger: 'item', formatter: '{b}: {c}' },
    series: [
      {
        name: '销售阶段',
        type: 'funnel',
        left: '10%',
        top: 60,
        bottom: 60,
        width: '80%',
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: { show: true, position: 'inside' },
        labelLine: { length: 10, lineStyle: { width: 1, type: 'solid' } },
        itemStyle: { borderColor: '#fff', borderWidth: 1 },
        emphasis: { label: { fontSize: 20 } },
        data: funnelData,
      },
    ],
  };
  chart.setOption(option);
}

onMounted(() => {
  initSalesTrendChart();
  initSourcePieChart();
  initFunnelChart();
});
</script>

<style scoped>
.stat-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
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