<template>
  <div class="topbar-wrapper">
    <div class="left-side">
      <div class="project-name">新材料行业CRM客户管理系统</div>
    </div>
    <div class="right-side">
      <span class="welcome-text">欢迎 管理员 Admin</span>
      <el-button type="text" @click="logout">退出</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

function logout() {
  router.push('/login')
}
</script>

<style scoped>
.topbar-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px 0 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: relative;
}

.left-side {
  width: auto;
}

.project-name {
  color: #ecf0f1;
  font-weight: 700;
  font-size: 18px;
  white-space: nowrap;
}

.right-side {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #ecf0f1;
  font-weight: 600;
  font-size: 14px;
}
</style>