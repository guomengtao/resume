<template>
  <el-menu
    class="el-menu-vertical-demo"
    background-color="#545c64"
    text-color="#fff"
    active-text-color="#ffd04b"
    :default-active="$route.path"
    router
  >
    <el-menu-item index="/dashboard">
      <span>首页</span>
    </el-menu-item>
    <el-menu-item index="/customers">
      <span>客户管理</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { useRoute } from 'vue-router'
const $route = useRoute()
</script>