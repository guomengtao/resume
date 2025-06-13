<template>
  <el-container style="padding: 24px; background: #fafafa; min-height: 100vh;">
    <el-main>
      <el-card shadow="hover" style="max-width: 600px; margin: auto;">
        <template #header>
          <span style="font-size: 18px; font-weight: 600;">新增客户</span>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="电话" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入电话" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submit">提交</el-button>
            <el-button @click="$router.back()">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-main>
  </el-container>
</template>

<script>
export default {
  name: 'CustomerAddPage',
  data() {
    return {
      form: {
        name: '',
        phone: ''
      },
      rules: {
        name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        phone: [{ required: true, message: '请输入电话', trigger: 'blur' }]
      }
    };
  },
  methods: {
    submit() {
      this.$refs.formRef.validate((valid) => {
        if (valid) {
          fetch('http://localhost:8080/customers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.form)
          })
            .then(res => {
              if (!res.ok) throw new Error('提交失败');
              return res.json();
            })
            .then(() => {
              this.$message.success('添加成功');
              this.$router.push('/customers');
            })
            .catch(() => this.$message.error('添加失败'));
        }
      });
    }
  }
};
</script>