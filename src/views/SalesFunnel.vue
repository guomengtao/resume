<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';

// 生成随机整数，区间[min, max]
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const chartRef = ref(null);

onMounted(() => {
  const chart = echarts.init(chartRef.value);

  // 造随机数据
  const data = [
    { name: '潜在客户', value: randomInt(80, 120) },
    { name: '接触客户', value: randomInt(60, 100) },
    { name: '需求分析', value: randomInt(40, 80) },
    { name: '报价', value: randomInt(20, 60) },
    { name: '成交', value: randomInt(10, 40) },
  ];

  chart.setOption({
    title: {
      text: '销售漏斗分析',
      left: 'center',
      textStyle: { fontSize: 20 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}'
    },
    toolbox: {
      feature: {
        saveAsImage: {}
      }
    },
    series: [
      {
        name: '销售漏斗',
        type: 'funnel',
        left: '10%',
        top: 60,
        bottom: 60,
        width: '80%',
        min: 0,
        max: Math.max(...data.map(d => d.value)),
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: {
          show: true,
          position: 'inside',
          formatter: ({ name, value }) => `${name}\n${value}`
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid'
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          label: {
            fontSize: 20
          }
        },
        data
      }
    ]
  });
});
</script>

<template>
  <div
    ref="chartRef"
    style="width: 100%; height: 400px; background: #fff; border-radius: 8px; padding: 16px;"
  ></div>
</template>

<style scoped>
</style>