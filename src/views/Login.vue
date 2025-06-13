<template>
  <div
    style="min-height: 100vh; background: linear-gradient(135deg, #3a8ee6, #6aade9); display: flex; justify-content: center; align-items: center;"
  >
    <el-card
      shadow="hover"
      style="width: 360px; border-radius: 12px; background: white;"
    >
      <h2
        style="text-align: center; margin-bottom: 30px; font-weight: 700; color: #3a8ee6;"
      >
        新材料行业CRM客户管理系统
      </h2>
      <el-form
        ref="loginForm"
        :model="form"
        :rules="rules"
        label-position="top"
        status-icon
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            autocomplete="off"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            type="password"
            v-model="form.password"
            placeholder="请输入密码"
            autocomplete="off"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" block @click="handleLogin" size="large"
            >登录</el-button
          >
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      form: {
        username: "",
        password: "",
      },
      rules: {
        username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }],
      },
    };
  },
  methods: {
    handleLogin() {
      this.$refs.loginForm.validate((valid) => {
        if (!valid) return;
        // 模拟登录成功，跳转主页
        this.$message.success(`欢迎，${this.form.username}`);
        this.$router.push("/");
      });
    },
  },
};
</script>

<style scoped>
.el-card {
  box-shadow: 0 8px 20px rgba(58, 142, 230, 0.3);
}
</style>