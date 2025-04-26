<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">新增用户</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchPhone"
          placeholder="请输入手机号搜索"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <!-- 用户表格 -->
      <el-table :data="userList" style="width: 100%" v-loading="loading">
        <el-table-column prop="user_id" label="用户ID" width="220" />
        <el-table-column prop="phone" label="手机号" width="150" />
        <el-table-column prop="is_deleted" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_deleted ? 'danger' : 'success'">
              {{ row.is_deleted ? '已删除' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录时间" width="180">
          <template #default="{ row }">
            {{ row.last_login || '未登录' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增用户' : '编辑用户'"
      width="500px"
    >
      <el-form ref="formRef" :model="userForm" :rules="rules" label-width="100px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { userApi, type User, type CreateUserRequest } from '@/api/user'

// 数据
const userList = ref<User[]>([])
const loading = ref(false)
const searchPhone = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentUserId = ref('')
const total = ref(0)

// 表单
const formRef = ref<FormInstance>()
const userForm = ref<CreateUserRequest>({
  phone: '',
  password: '',
})

// 表单验证规则
const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' },
  ],
}

// 获取用户列表
const fetchUserList = async () => {
  try {
    loading.value = true
    const res = await userApi.getAllUsers()
    userList.value = res.data.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索用户
const handleSearch = async () => {
  if (!searchPhone.value) {
    await fetchUserList()
    return
  }
  try {
    loading.value = true
    const res = await userApi.searchUserByPhone(searchPhone.value)
    if (res.data.code === 200) {
      userList.value = res.data.data.items
      total.value = res.data.data.total
      if (userList.value.length === 0) {
        ElMessage.info('未找到匹配的用户')
      }
    } else {
      ElMessage.error(res.data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索用户失败:', error)
    ElMessage.error('搜索用户失败')
  } finally {
    loading.value = false
  }
}

// 新增用户
const handleAdd = () => {
  dialogType.value = 'add'
  userForm.value = {
    phone: '',
    password: '',
  }
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row: User) => {
  dialogType.value = 'edit'
  currentUserId.value = row.user_id
  userForm.value = {
    phone: row.phone,
    password: '',
  }
  dialogVisible.value = true
}

// 删除用户
const handleDelete = async (row: User) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      type: 'warning',
    })
    await userApi.deleteUser(row.user_id)
    ElMessage.success('删除成功')
    await fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === 'add') {
          await userApi.createUser(userForm.value)
          ElMessage.success('创建成功')
        } else {
          await userApi.updateUser(currentUserId.value, {
            password: userForm.value.password,
          })
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await fetchUserList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '创建失败' : '更新失败')
      }
    }
  })
}

// 初始化
onMounted(() => {
  fetchUserList()
})
</script>

<style scoped>
.user-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
