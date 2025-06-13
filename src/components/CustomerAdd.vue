<template>
  <div class="customer-add">
    <h2>添加客户</h2>
    <form @submit.prevent="addCustomer">
      <div>
        <label for="name">姓名:</label>
        <input id="name" v-model="name" required />
      </div>
      <div>
        <label for="phone">电话:</label>
        <input id="phone" v-model="phone" />
      </div>
      <button type="submit">提交</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: '',
      phone: '',
      message: ''
    };
  },
  methods: {
    async addCustomer() {
      try {
        const response = await fetch('http://localhost:8080/customers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.name,
            phone: this.phone
          })
        });
        if (!response.ok) {
          throw new Error('添加失败');
        }
        this.message = '添加成功！';
        this.name = '';
        this.phone = '';
        // 这里你可以选择触发列表刷新，或发事件告诉父组件
      } catch (error) {
        this.message = '添加失败，请重试。';
        console.error('添加客户失败:', error);
      }
    }
  }
};
</script>

<style scoped>
.customer-add {
  max-width: 400px;
  margin: 20px auto;
}
label {
  display: block;
  margin-bottom: 5px;
}
input {
  width: 100%;
  margin-bottom: 10px;
  padding: 6px;
}
button {
  padding: 8px 16px;
}
p {
  margin-top: 10px;
  color: green;
}
</style>