<template>
  <div class="product-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI产品管理</span>
          <el-button type="primary" @click="handleAdd">新增产品</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchName"
          placeholder="请输入产品名称搜索"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <!-- 产品表格 -->
      <el-table :data="productList" style="width: 100%" v-loading="loading">
        <el-table-column prop="ai_product_id" label="产品ID" width="220" />
        <el-table-column prop="ai_product_name" label="产品名称" min-width="200" />
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

    <!-- 产品表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增产品' : '编辑产品'"
      width="500px"
    >
      <el-form ref="formRef" :model="productForm" :rules="rules" label-width="100px">
        <el-form-item label="产品名称" prop="ai_product_name">
          <el-input v-model="productForm.ai_product_name" placeholder="请输入产品名称" />
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
import { productApi, type AIProduct, type CreateAIProductRequest } from '@/api/product'

// 数据
const productList = ref<AIProduct[]>([])
const loading = ref(false)
const searchName = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentProductId = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单
const formRef = ref<FormInstance>()
const productForm = ref<CreateAIProductRequest>({
  ai_product_name: '',
})

// 表单验证规则
const rules = {
  ai_product_name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { min: 2, max: 50, message: '产品名称长度在2-50个字符之间', trigger: 'blur' },
  ],
}

// 获取产品列表
const fetchProductList = async () => {
  try {
    loading.value = true
    const res = await productApi.getAllProducts(currentPage.value, pageSize.value)
    productList.value = res.data.data.items
    total.value = res.data.data.total
  } catch (error) {
    ElMessage.error('获取产品列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索产品
const handleSearch = async () => {
  if (!searchName.value) {
    currentPage.value = 1
    await fetchProductList()
    return
  }
  try {
    loading.value = true
    const res = await productApi.searchProduct(searchName.value)
    if (res.data.code === 200) {
      productList.value = res.data.data.items
      total.value = res.data.data.total
      if (productList.value.length === 0) {
        ElMessage.info('未找到匹配的产品')
      }
    } else {
      ElMessage.error(res.data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索产品失败:', error)
    ElMessage.error('搜索产品失败')
  } finally {
    loading.value = false
  }
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchProductList()
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchProductList()
}

// 新增产品
const handleAdd = () => {
  dialogType.value = 'add'
  productForm.value = {
    ai_product_name: '',
  }
  dialogVisible.value = true
}

// 编辑产品
const handleEdit = (row: AIProduct) => {
  dialogType.value = 'edit'
  currentProductId.value = row.ai_product_id
  productForm.value = {
    ai_product_name: row.ai_product_name,
  }
  dialogVisible.value = true
}

// 删除产品
const handleDelete = async (row: AIProduct) => {
  try {
    await ElMessageBox.confirm('确定要删除该产品吗？', '提示', {
      type: 'warning',
    })
    await productApi.deleteProduct(row.ai_product_id)
    ElMessage.success('删除成功')
    await fetchProductList()
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
          await productApi.createProduct(productForm.value)
          ElMessage.success('创建成功')
        } else {
          await productApi.updateProduct(currentProductId.value, productForm.value)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await fetchProductList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '创建失败' : '更新失败')
      }
    }
  })
}

// 初始化
onMounted(() => {
  fetchProductList()
})
</script>

<style scoped>
.product-list {
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
