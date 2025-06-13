<template>
  <el-container style="padding: 24px; background: #fafafa; min-height: 100vh;">
    <el-header style="font-size: 24px; font-weight: bold; color: #409EFF;">
      欢迎，销售经理！
    </el-header>
    <el-main>
      <el-row :gutter="20">
        <!-- 待办事项 -->
        <el-col :span="12">
          <el-card shadow="hover">
            <h3 style="margin-bottom: 12px;">今日待办事项</h3>
            <el-list v-if="todoList.length">
              <el-list-item
                v-for="item in todoList"
                :key="item.id"
                style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #ebeef5;"
              >
                <el-checkbox v-model="item.completed" @change="toggleTodo(item)">
                  {{ item.title }}
                </el-checkbox>
                <el-button type="text" size="small" @click="viewTodoDetail(item)">查看</el-button>
              </el-list-item>
            </el-list>
            <div v-else style="color: #909399; text-align: center; padding: 20px;">
              暂无待办事项
            </div>
          </el-card>
        </el-col>

        <!-- 重要通知 -->
        <el-col :span="12">
          <el-card shadow="hover">
            <h3 style="margin-bottom: 12px;">重要通知</h3>
            <el-timeline>
              <el-timeline-item
                v-for="note in notifications"
                :key="note.id"
                :timestamp="note.time"
                placement="top"
              >
                {{ note.content }}
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>

      <!-- 快捷按钮 -->
      <el-row style="margin-top: 24px; justify-content: center;">
        <el-button type="primary" @click="addNewLead" style="margin-right: 16px;">
          新增线索
        </el-button>
        <el-button type="success" @click="addNewCustomer" style="margin-right: 16px;">
          新增客户
        </el-button>
        <el-button type="warning" @click="addNewOrder">
          新增订单
        </el-button>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { reactive } from 'vue';

// 模拟待办事项数据
const todoList = reactive([
  { id: 1, title: '跟进客户张三', completed: false },
  { id: 2, title: '确认订单#12345', completed: false },
  { id: 3, title: '回复客户邮件', completed: true },
  { id: 4, title: '安排下周会议', completed: false },
]);

// 模拟通知数据
const notifications = reactive([
  { id: 1, time: '2025-06-12 09:00', content: '系统升级将在今晚22:00进行，届时将无法访问' },
  { id: 2, time: '2025-06-11 16:30', content: '客户李四提交了新的需求变更申请' },
  { id: 3, time: '2025-06-10 10:15', content: '月度销售目标已完成75%' },
]);

// 切换待办完成状态
function toggleTodo(item) {
  item.completed = !item.completed;
  console.log(`待办【${item.title}】完成状态：`, item.completed);
  // 这里可以调用接口更新服务端状态
}

// 查看待办详情
function viewTodoDetail(item) {
  alert(`查看待办详情：${item.title}`);
}

// 新增线索按钮
function addNewLead() {
  alert('跳转到新增线索页面');
  // router.push('/leads/add') 之类的路由跳转
}

// 新增客户按钮
function addNewCustomer() {
  alert('跳转到新增客户页面');
}

// 新增订单按钮
function addNewOrder() {
  alert('跳转到新增订单页面');
}
</script>

<style scoped>
h3 {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
}
</style>