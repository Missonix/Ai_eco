<template>
  <div class="entitlement-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权益规则管理</span>
          <el-button type="primary" @click="handleAdd">新增规则</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="规则ID">
            <el-input v-model="searchForm.rule_id" placeholder="请输入规则ID" clearable />
          </el-form-item>
          <el-form-item label="课程ID">
            <el-input v-model="searchForm.course_id" placeholder="请输入课程ID" clearable />
          </el-form-item>
          <el-form-item label="课程名称">
            <el-input v-model="searchForm.course_name" placeholder="请输入课程名称" clearable />
          </el-form-item>
          <el-form-item label="产品ID">
            <el-input v-model="searchForm.ai_product_id" placeholder="请输入产品ID" clearable />
          </el-form-item>
          <el-form-item label="产品名称">
            <el-input v-model="searchForm.product_name" placeholder="请输入产品名称" clearable />
          </el-form-item>
          <el-form-item label="每日限制">
            <el-input-number v-model="searchForm.daily_limit" :min="1" :max="100" clearable />
          </el-form-item>
          <el-form-item label="有效期">
            <el-input-number v-model="searchForm.validity_days" :min="1" :max="365" clearable />
          </el-form-item>
          <el-form-item label="创建时间">
            <el-date-picker
              v-model="searchForm.created_at"
              type="datetime"
              placeholder="选择创建时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 权益规则表格 -->
      <el-table :data="ruleList" style="width: 100%" v-loading="loading">
        <el-table-column prop="rule_id" label="规则ID" width="220" />
        <el-table-column prop="course_id" label="课程ID" width="220" />
        <el-table-column prop="course_name" label="课程名称" min-width="200" />
        <el-table-column prop="ai_product_id" label="产品ID" width="220" />
        <el-table-column prop="product_name" label="产品名称" min-width="200" />
        <el-table-column prop="daily_limit" label="每日限制" width="100" />
        <el-table-column prop="validity_days" label="有效期(天)" width="100" />
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

    <!-- 权益规则表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增规则' : '编辑规则'"
      width="500px"
    >
      <el-form ref="formRef" :model="ruleForm" :rules="rules" label-width="100px">
        <el-form-item label="课程" prop="course_id" v-if="dialogType === 'add'">
          <el-select v-model="ruleForm.course_id" placeholder="请选择课程" style="width: 100%">
            <el-option
              v-for="course in courseList"
              :key="course.course_id"
              :label="course.course_name"
              :value="course.course_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="ai_product_id">
          <el-select v-model="ruleForm.ai_product_id" placeholder="请选择产品" style="width: 100%">
            <el-option
              v-for="product in productList"
              :key="product.ai_product_id"
              :label="product.ai_product_name"
              :value="product.ai_product_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="每日限制" prop="daily_limit" v-if="dialogType === 'edit'">
          <el-input-number v-model="ruleForm.daily_limit" :min="1" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="有效期" prop="validity_days" v-if="dialogType === 'edit'">
          <el-input-number
            v-model="ruleForm.validity_days"
            :min="1"
            :max="365"
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
  entitlementApi,
  type EntitlementRule,
  type CreateEntitlementRuleRequest,
  type SearchEntitlementRuleRequest,
  type UpdateEntitlementRuleRequest,
} from '@/api/entitlement'
import { courseApi, type Course } from '@/api/course'
import { productApi, type AIProduct } from '@/api/product'

// 数据
const ruleList = ref<EntitlementRule[]>([])
const courseList = ref<Course[]>([])
const productList = ref<AIProduct[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentRuleId = ref('')

// 搜索表单
const searchForm = ref<SearchEntitlementRuleRequest>({
  rule_id: '',
  course_id: '',
  course_name: '',
  ai_product_id: '',
  product_name: '',
  daily_limit: undefined,
  validity_days: undefined,
  created_at: '',
})

// 规则表单
const formRef = ref<FormInstance>()
const ruleForm = ref<
  CreateEntitlementRuleRequest & { daily_limit?: number; validity_days?: number }
>({
  course_id: '',
  ai_product_id: '',
  daily_limit: undefined,
  validity_days: undefined,
})

// 表单验证规则
const rules = {
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  ai_product_id: [{ required: true, message: '请选择产品', trigger: 'change' }],
  daily_limit: [{ required: true, message: '请输入每日限制', trigger: 'change' }],
  validity_days: [{ required: true, message: '请输入有效期', trigger: 'change' }],
}

// 获取权益规则列表
const fetchRuleList = async () => {
  try {
    loading.value = true
    const res = await entitlementApi.getAllRules()
    ruleList.value = res.data.data
  } catch (error: unknown) {
    console.error('获取权益规则列表失败:', error)
    ElMessage.error('获取权益规则列表失败')
  } finally {
    loading.value = false
  }
}

// 获取课程列表
const fetchCourseList = async () => {
  try {
    const res = await courseApi.getAllCourses(1, 99)
    courseList.value = res.data.data.items
  } catch (error) {
    console.error('获取课程列表失败:', error)
    ElMessage.error('获取课程列表失败')
  }
}

// 获取产品列表
const fetchProductList = async () => {
  try {
    const res = await productApi.getAllProducts(1, 99)
    productList.value = res.data.data.items
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
  }
}

// 搜索权益规则
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
      {} as Record<string, string | number | undefined>,
    )

    // 如果没有任何搜索条件，则获取所有规则
    if (Object.keys(searchParams).length === 0) {
      await fetchRuleList()
      return
    }

    // 确保规则ID搜索参数正确传递
    if (searchParams.rule_id && typeof searchParams.rule_id === 'string') {
      searchParams.rule_id = searchParams.rule_id.trim()
    }

    console.log('搜索参数:', searchParams) // 添加日志
    const res = await entitlementApi.searchRule(searchParams)
    console.log('搜索结果:', res.data) // 添加日志

    if (res.data.code === 200) {
      ruleList.value = res.data.data
      if (ruleList.value.length === 0) {
        ElMessage.info('未找到匹配的规则')
      }
    } else {
      ElMessage.error(res.data.message || '搜索失败')
    }
  } catch (error: unknown) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索权益规则失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    rule_id: '',
    course_id: '',
    course_name: '',
    ai_product_id: '',
    product_name: '',
    daily_limit: undefined,
    validity_days: undefined,
    created_at: '',
  }
  fetchRuleList()
}

// 新增规则
const handleAdd = () => {
  dialogType.value = 'add'
  ruleForm.value = {
    course_id: '',
    ai_product_id: '',
    daily_limit: undefined,
    validity_days: undefined,
  }
  dialogVisible.value = true
}

// 编辑规则
const handleEdit = (row: EntitlementRule) => {
  dialogType.value = 'edit'
  currentRuleId.value = row.rule_id
  ruleForm.value = {
    course_id: row.course_id,
    ai_product_id: row.ai_product_id,
    daily_limit: row.daily_limit,
    validity_days: row.validity_days,
  }
  dialogVisible.value = true
}

// 删除规则
const handleDelete = async (row: EntitlementRule) => {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '提示', {
      type: 'warning',
    })
    await entitlementApi.deleteRule(row.rule_id)
    ElMessage.success('删除成功')
    await fetchRuleList()
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
          await entitlementApi.createRule(ruleForm.value)
          ElMessage.success('创建成功')
        } else {
          const updateData: UpdateEntitlementRuleRequest = {
            ai_product_id: ruleForm.value.ai_product_id,
            daily_limit: ruleForm.value.daily_limit,
            validity_days: ruleForm.value.validity_days,
          }
          await entitlementApi.updateRule(currentRuleId.value, updateData)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await fetchRuleList()
      } catch (error: unknown) {
        console.error('操作失败:', error)
        ElMessage.error(dialogType.value === 'add' ? '创建失败' : '更新失败')
      }
    }
  })
}

// 初始化
onMounted(async () => {
  await Promise.all([fetchRuleList(), fetchCourseList(), fetchProductList()])
})
</script>

<style scoped>
.entitlement-list {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
