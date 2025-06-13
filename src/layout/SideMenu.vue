<template>
  <el-aside :width="'200px'" style="background-color: #f5f7fa; height: 100vh; color: black; padding: 0; margin: 0;">
    <el-menu
      :default-active="active"
      router
      background-color="#f5f7fa"
      text-color="#000000"
      active-text-color="#000000"
      unique-opened
      style="height: 100vh; margin: 0; padding: 0;"
    >
      <el-menu-item index="/dashboard">
        <el-icon><House /></el-icon>
        <span>首页</span>
      </el-menu-item>

      <el-menu-item index="/admin">
        <el-icon><User /></el-icon>
        <span>管理员管理</span>
      </el-menu-item>

      <el-menu-item index="/customers">
        <el-icon><User /></el-icon>
        <span>客户管理</span>
      </el-menu-item>
      <el-menu-item index="/leads">
        <el-icon><User /></el-icon>
        <span>销售线索管理</span>
      </el-menu-item>
      <el-menu-item index="/opportunities">
        <el-icon><User /></el-icon>
        <span>销售机会管理</span>
      </el-menu-item>
      <el-menu-item index="/orders">
        <el-icon><User /></el-icon>
        <span>销售订单管理</span>
      </el-menu-item>
      <el-menu-item index="/funnel">
        <el-icon><User /></el-icon>
        <span>销售漏斗分析</span>
      </el-menu-item>
      <el-menu-item index="/reports">
        <el-icon><User /></el-icon>
        <span>销售报表生成</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute } from "vue-router";
import { ElIcon } from 'element-plus';
import { House, User } from '@element-plus/icons-vue';

const route = useRoute();
const active = route.path;
// 无折叠功能，菜单始终展开
</script>

<style scoped>
.el-menu-item > span,
.el-sub-menu .el-menu-item > span {
  color: #333333; /* 深色文字 */
  font-size: 14px;
  font-weight: 400;
}

.el-menu-item.is-active > span,
.el-sub-menu .el-menu-item.is-active > span {
  color: #1f2937; /* 稍微深一点 */
  font-weight: 600;
}
</style>
