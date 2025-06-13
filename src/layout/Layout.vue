<template>
  <el-container style="height: 100vh;">
    <el-header class="top-bar"><TopBar /></el-header>
    <el-container>
      <el-aside width="200px" class="side-container"><SideMenu /></el-aside>
      <el-main class="main-content"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import SideMenu from "./SideMenu.vue";
import TopBar from "./TopBar.vue";
</script>


<style scoped>
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 60px;
  background-color: #333;
  color: white;
  line-height: 60px;
  z-index: 1000;
}

.side-container {
  padding: 0 !important;
  margin: 60px 0 0 0 !important; /* leave space below fixed top bar */
  height: calc(100vh - 60px) !important;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.main-content {
  padding: 20px;
  margin: 60px 0 0 0 !important; /* leave space below fixed top bar */
  background-color: #fff;
  overflow-y: auto;
}
</style>
