<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>后台管理系统</h2>
        </div>
      </template>
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" class="login-button">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = ref({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        const response = await axios.post(
          'http://10.7.21.239:4455/api/admins/login',
          loginForm.value,
        )
        if (response.data.code === 200) {
          // 保存token和用户信息
          localStorage.setItem('access_token', response.data.data.access_token)
          localStorage.setItem('admin_id', response.data.data.admin_id)
          localStorage.setItem('username', response.data.data.username)
          ElMessage.success('登录成功')
          router.push('/')
        } else {
          ElMessage.error(response.data.message || '登录失败')
        }
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #409eff;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
}
</style>
