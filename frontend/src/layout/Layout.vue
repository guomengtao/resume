
<template>
  <el-container style="height: 100vh;">
    <el-aside width="200px"><SideMenu /></el-aside>
    <el-container>
      <el-header><TopBar /></el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import SideMenu from "./SideMenu.vue";
import TopBar from "./TopBar.vue";
</script>

