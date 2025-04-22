<template>
  <div class="course-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" @click="handleAdd">新增课程</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchName"
          placeholder="请输入课程名称搜索"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <!-- 课程表格 -->
      <el-table :data="courseList" style="width: 100%" v-loading="loading">
        <el-table-column prop="course_id" label="课程ID" width="220" />
        <el-table-column prop="course_name" label="课程名称" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
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
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 课程表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增课程' : '编辑课程'"
      width="500px"
    >
      <el-form ref="formRef" :model="courseForm" :rules="rules" label-width="100px">
        <el-form-item label="课程名称" prop="course_name">
          <el-input v-model="courseForm.course_name" placeholder="请输入课程名称" />
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
import { courseApi, type Course, type CreateCourseRequest } from '@/api/course'

// 数据
const courseList = ref<Course[]>([])
const loading = ref(false)
const searchName = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentCourseId = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单
const formRef = ref<FormInstance>()
const courseForm = ref<CreateCourseRequest>({
  course_name: '',
})

// 表单验证规则
const rules = {
  course_name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '课程名称长度在2-50个字符之间', trigger: 'blur' },
  ],
}

// 获取课程列表
const fetchCourseList = async () => {
  try {
    loading.value = true
    const res = await courseApi.getAllCourses(currentPage.value, pageSize.value)
    courseList.value = res.data.data.items
    total.value = res.data.data.total
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索课程
const handleSearch = async () => {
  if (!searchName.value) {
    currentPage.value = 1
    await fetchCourseList()
    return
  }
  try {
    loading.value = true
    const res = await courseApi.searchCourse({ course_name: searchName.value })
    courseList.value = [res.data.data]
    total.value = 1
  } catch (error) {
    ElMessage.error('搜索课程失败')
  } finally {
    loading.value = false
  }
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchCourseList()
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchCourseList()
}

// 新增课程
const handleAdd = () => {
  dialogType.value = 'add'
  courseForm.value = {
    course_name: '',
  }
  dialogVisible.value = true
}

// 编辑课程
const handleEdit = (row: Course) => {
  dialogType.value = 'edit'
  currentCourseId.value = row.course_id
  courseForm.value = {
    course_name: row.course_name,
  }
  dialogVisible.value = true
}

// 删除课程
const handleDelete = async (row: Course) => {
  try {
    await ElMessageBox.confirm('确定要删除该课程吗？', '提示', {
      type: 'warning',
    })
    await courseApi.deleteCourse(row.course_id)
    ElMessage.success('删除成功')
    await fetchCourseList()
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
          await courseApi.createCourse(courseForm.value)
          ElMessage.success('创建成功')
        } else {
          await courseApi.updateCourse(currentCourseId.value, courseForm.value)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await fetchCourseList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '创建失败' : '更新失败')
      }
    }
  })
}

// 初始化
onMounted(() => {
  fetchCourseList()
})
</script>

<style scoped>
.course-list {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
