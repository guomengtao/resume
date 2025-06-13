
<template>
  <el-menu :default-active="active" router>
    <el-menu-item index="/dashboard">首页</el-menu-item>
    <el-menu-item index="/customers">客户管理</el-menu-item>
  </el-menu>
</template>

<script setup>
import { useRoute } from "vue-router";
const route = useRoute();
const active = route.path;
</script>

