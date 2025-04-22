<template>
  <div class="user-entitlement-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户权益管理</span>
          <el-button type="primary" @click="handleAdd">新增权益</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="权益ID">
            <el-input v-model="searchForm.entitlement_id" placeholder="请输入权益ID" clearable />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="searchForm.phone" placeholder="请输入手机号" clearable />
          </el-form-item>
          <el-form-item label="规则ID">
            <el-input v-model="searchForm.rule_id" placeholder="请输入规则ID" clearable />
          </el-form-item>
          <el-form-item label="课程名称">
            <el-input v-model="searchForm.course_name" placeholder="请输入课程名称" clearable />
          </el-form-item>
          <el-form-item label="产品名称">
            <el-input v-model="searchForm.product_name" placeholder="请输入产品名称" clearable />
          </el-form-item>
          <el-form-item label="开始时间">
            <el-date-picker
              v-model="searchForm.start_date"
              type="datetime"
              placeholder="选择开始时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              clearable
            />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-date-picker
              v-model="searchForm.end_date"
              type="datetime"
              placeholder="选择结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              clearable
            />
          </el-form-item>
          <el-form-item label="剩余次数">
            <el-input-number v-model="searchForm.daily_remaining" :min="0" :max="100" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 用户权益表格 -->
      <el-table :data="entitlementList" style="width: 100%" v-loading="loading">
        <el-table-column prop="entitlement_id" label="权益ID" width="220" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="rule_id" label="规则ID" width="220" />
        <el-table-column prop="course_name" label="课程名称" min-width="200" />
        <el-table-column prop="product_name" label="产品名称" min-width="200" />
        <el-table-column prop="start_date" label="开始时间" width="180" />
        <el-table-column prop="end_date" label="结束时间" width="180" />
        <el-table-column prop="daily_remaining" label="剩余次数" width="100" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '有效' : '无效' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 用户权益表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增权益' : '编辑权益'"
      width="500px"
    >
      <el-form ref="formRef" :model="entitlementForm" :rules="rules" label-width="100px">
        <el-form-item label="手机号" prop="phone" v-if="dialogType === 'add'">
          <el-input v-model="entitlementForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="规则" prop="rule_id" v-if="dialogType === 'add'">
          <el-select v-model="entitlementForm.rule_id" placeholder="请选择规则" style="width: 100%">
            <el-option
              v-for="rule in ruleList"
              :key="rule.rule_id"
              :label="`${rule.course_name} - ${rule.product_name}`"
              :value="rule.rule_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_date" v-if="dialogType === 'edit'">
          <el-date-picker
            v-model="entitlementForm.end_date"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="剩余次数" prop="daily_remaining" v-if="dialogType === 'edit'">
          <el-input-number
            v-model="entitlementForm.daily_remaining"
            :min="0"
            :max="100"
            style="width: 100%"
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
import {
  userEntitlementApi,
  type UserEntitlement,
  type CreateUserEntitlementRequest,
  type SearchUserEntitlementRequest,
  type UpdateUserEntitlementRequest,
} from '@/api/userEntitlement'
import { entitlementApi, type EntitlementRule } from '@/api/entitlement'

// 数据
const entitlementList = ref<UserEntitlement[]>([])
const ruleList = ref<EntitlementRule[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentEntitlementId = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索表单
const searchForm = ref<SearchUserEntitlementRequest>({
  entitlement_id: '',
  phone: '',
  rule_id: '',
  course_name: '',
  product_name: '',
  start_date: '',
  end_date: '',
  daily_remaining: undefined,
})

// 权益表单
const formRef = ref<FormInstance>()
const entitlementForm = ref<
  CreateUserEntitlementRequest & { end_date?: string; daily_remaining?: number }
>({
  phone: '',
  rule_id: '',
  end_date: '',
  daily_remaining: undefined,
})

// 表单验证规则
const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  rule_id: [{ required: true, message: '请选择规则', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  daily_remaining: [{ required: true, message: '请输入剩余次数', trigger: 'change' }],
}

// 获取用户权益列表
const fetchEntitlementList = async () => {
  try {
    loading.value = true
    const res = await userEntitlementApi.getAllEntitlements(currentPage.value, pageSize.value)
    entitlementList.value = res.data.data.items
    total.value = res.data.data.total
  } catch (error) {
    console.error('获取用户权益列表失败:', error)
    ElMessage.error('获取用户权益列表失败')
  } finally {
    loading.value = false
  }
}

// 获取规则列表
const fetchRuleList = async () => {
  try {
    const res = await entitlementApi.getAllRules()
    ruleList.value = res.data.data
  } catch (error) {
    console.error('获取规则列表失败:', error)
    ElMessage.error('获取规则列表失败')
  }
}

// 搜索用户权益
const handleSearch = async () => {
  try {
    loading.value = true
    // 过滤掉空值
    const searchParams = Object.entries(searchForm.value).reduce(
      (acc, [key, value]) => {
        if (value !== '' && value !== undefined && value !== null) {
          acc[key] = value
        }
        return acc
      },
      {} as Record<string, any>,
    )

    // 如果没有任何搜索条件，则获取所有权益
    if (Object.keys(searchParams).length === 0) {
      await fetchEntitlementList()
      return
    }

    const res = await userEntitlementApi.searchEntitlement(searchParams)
    if (res.data.code === 200) {
      entitlementList.value = res.data.data.items
      total.value = res.data.data.total
      currentPage.value = res.data.data.page
      pageSize.value = res.data.data.page_size
    } else {
      ElMessage.error(res.data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索用户权益失败:', error)
    ElMessage.error('搜索用户权益失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    entitlement_id: '',
    phone: '',
    rule_id: '',
    course_name: '',
    product_name: '',
    start_date: '',
    end_date: '',
    daily_remaining: undefined,
  }
  currentPage.value = 1
  pageSize.value = 10
  fetchEntitlementList()
}

// 处理页码变化
const handleCurrentChange = async (page: number) => {
  currentPage.value = page
  // 如果有搜索条件，使用搜索接口
  if (
    Object.keys(searchForm.value).some(
      (key) => searchForm.value[key as keyof SearchUserEntitlementRequest],
    )
  ) {
    await handleSearch()
  } else {
    await fetchEntitlementList()
  }
}

// 处理每页条数变化
const handleSizeChange = async (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  // 如果有搜索条件，使用搜索接口
  if (
    Object.keys(searchForm.value).some(
      (key) => searchForm.value[key as keyof SearchUserEntitlementRequest],
    )
  ) {
    await handleSearch()
  } else {
    await fetchEntitlementList()
  }
}

// 新增权益
const handleAdd = () => {
  dialogType.value = 'add'
  entitlementForm.value = {
    phone: '',
    rule_id: '',
  }
  dialogVisible.value = true
}

// 编辑权益
const handleEdit = (row: UserEntitlement) => {
  dialogType.value = 'edit'
  currentEntitlementId.value = row.entitlement_id
  entitlementForm.value = {
    phone: row.phone,
    rule_id: row.rule_id,
    end_date: row.end_date,
    daily_remaining: row.daily_remaining,
  }
  dialogVisible.value = true
}

// 删除权益
const handleDelete = async (row: UserEntitlement) => {
  try {
    await ElMessageBox.confirm('确定要删除该权益吗？', '提示', {
      type: 'warning',
    })
    await userEntitlementApi.deleteEntitlement(row.entitlement_id)
    ElMessage.success('删除成功')
    await fetchEntitlementList()
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
          await userEntitlementApi.createEntitlement(entitlementForm.value)
          ElMessage.success('创建成功')
        } else {
          const updateData: UpdateUserEntitlementRequest = {
            end_date: entitlementForm.value.end_date,
            daily_remaining: Number(entitlementForm.value.daily_remaining),
          }
          await userEntitlementApi.updateEntitlement(currentEntitlementId.value, updateData)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await fetchEntitlementList()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(dialogType.value === 'add' ? '创建失败' : '更新失败')
      }
    }
  })
}

// 初始化
onMounted(async () => {
  await Promise.all([fetchEntitlementList(), fetchRuleList()])
})
</script>

<style scoped>
.user-entitlement-list {
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

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 10px;
  margin-right: 0;
  min-width: 200px;
  max-width: 300px;
}

.search-form :deep(.el-input),
.search-form :deep(.el-input-number),
.search-form :deep(.el-date-picker) {
  width: 100%;
}

.search-form :deep(.el-input__wrapper) {
  width: 100%;
  box-sizing: border-box;
  padding-right: 30px;
}

.search-form :deep(.el-input__inner) {
  width: 100%;
  box-sizing: border-box;
}

.search-form :deep(.el-input__suffix) {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
}

.search-form :deep(.el-form-item__content) {
  width: 100%;
  display: flex;
  position: relative;
}

.search-form :deep(.el-form-item:last-child) {
  margin-left: auto;
  min-width: auto;
  max-width: none;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
