<template>
  <div>
    <h2>客户列表</h2>
    <ul>
      <li v-for="customer in customers" :key="customer.id">
        {{ customer.name }} - {{ customer.phone || "无电话" }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "CustomerList",
  data() {
    return {
      customers: []
    };
  },
  mounted() {
    fetch("http://localhost:8080/customers")
      .then(res => res.json())
      .then(data => {
        this.customers = data;
      })
      .catch(err => {
        console.error("获取客户列表失败:", err);
      });
  }
};
</script>

<style scoped>
h2 {
  color: #42b983;
}
</style>
