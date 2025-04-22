<template>
  <div class="order-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <el-button type="primary" @click="handleAdd">新增订单</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="订单ID">
            <el-input v-model="searchForm.order_id" placeholder="请输入订单ID" clearable />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="searchForm.phone" placeholder="请输入手机号" clearable />
          </el-form-item>
          <el-form-item label="课程ID">
            <el-input v-model="searchForm.course_id" placeholder="请输入课程ID" clearable />
          </el-form-item>
          <el-form-item label="购买时间">
            <el-date-picker
              v-model="searchForm.purchase_time"
              type="datetime"
              placeholder="选择购买时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              clearable
            />
          </el-form-item>
          <el-form-item label="退款状态">
            <el-select v-model="searchForm.is_refund" placeholder="请选择退款状态" clearable>
              <el-option label="无" value="无" />
              <el-option label="已退款" value="已退款" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 订单表格 -->
      <el-table :data="orderList" style="width: 100%" v-loading="loading">
        <el-table-column prop="order_id" label="订单ID" width="220" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="course_id" label="课程ID" width="220" />
        <el-table-column prop="purchase_time" label="购买时间" width="180" />
        <el-table-column prop="is_refund" label="退款状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_refund === '已退款' ? 'danger' : 'success'">
              {{ row.is_refund }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_generate" label="权益状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_generate ? 'success' : 'info'">
              {{ row.is_generate ? '已生成' : '未生成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              <el-button
                type="success"
                link
                :disabled="row.is_generate"
                @click="handleGenerateEntitlement(row)"
              >
                生成权益
              </el-button>
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

    <!-- 订单表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增订单' : '编辑订单'"
      width="500px"
    >
      <el-form ref="formRef" :model="orderForm" :rules="rules" label-width="100px">
        <el-form-item label="订单ID" prop="order_id" v-if="dialogType === 'add'">
          <el-input v-model="orderForm.order_id" placeholder="请输入订单ID" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone" v-if="dialogType === 'add'">
          <el-input v-model="orderForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="课程名称" prop="course_name" v-if="dialogType === 'add'">
          <el-input v-model="orderForm.course_name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="购买时间" prop="purchase_time" v-if="dialogType === 'add'">
          <el-date-picker
            v-model="orderForm.purchase_time"
            type="datetime"
            placeholder="选择购买时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="退款状态" prop="is_refund">
          <el-select v-model="orderForm.is_refund" placeholder="请选择退款状态">
            <el-option label="无" value="无" />
            <el-option label="已退款" value="已退款" />
          </el-select>
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
import { orderApi, type Order, type CreateOrderRequest, type SearchOrderRequest } from '@/api/order'

// 数据
const orderList = ref<Order[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentOrderId = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索表单
const searchForm = ref<SearchOrderRequest>({
  order_id: '',
  phone: '',
  course_id: '',
  purchase_time: '',
  is_refund: '',
})

// 订单表单
const formRef = ref<FormInstance>()
const orderForm = ref<CreateOrderRequest>({
  order_id: '',
  phone: '',
  course_name: '',
  purchase_time: '',
  is_refund: '无',
})

// 表单验证规则
const rules = {
  order_id: [{ required: true, message: '请输入订单ID', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  course_name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  purchase_time: [{ required: true, message: '请选择购买时间', trigger: 'change' }],
  is_refund: [{ required: true, message: '请选择退款状态', trigger: 'change' }],
}

// 获取订单列表
const fetchOrderList = async () => {
  try {
    loading.value = true
    const res = await orderApi.getAllOrders(currentPage.value, pageSize.value)
    orderList.value = res.data.data.items
    total.value = res.data.data.total
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索订单
const handleSearch = async () => {
  try {
    loading.value = true
    const res = await orderApi.searchOrder(searchForm.value)
    orderList.value = res.data.data
    total.value = res.data.data.length
  } catch (error) {
    console.error('搜索订单失败:', error)
    ElMessage.error('搜索订单失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    order_id: '',
    phone: '',
    course_id: '',
    purchase_time: '',
    is_refund: '',
  }
  currentPage.value = 1
  fetchOrderList()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchOrderList()
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchOrderList()
}

// 新增订单
const handleAdd = () => {
  dialogType.value = 'add'
  orderForm.value = {
    order_id: '',
    phone: '',
    course_name: '',
    purchase_time: '',
    is_refund: '无',
  }
  dialogVisible.value = true
}

// 编辑订单
const handleEdit = (row: Order) => {
  dialogType.value = 'edit'
  currentOrderId.value = row.order_id
  orderForm.value = {
    order_id: row.order_id,
    phone: row.phone,
    course_name: '',
    purchase_time: row.purchase_time,
    is_refund: row.is_refund,
  }
  dialogVisible.value = true
}

// 删除订单
const handleDelete = async (row: Order) => {
  try {
    await ElMessageBox.confirm('确定要删除该订单吗？', '提示', {
      type: 'warning',
    })
    await orderApi.deleteOrder(row.order_id)
    ElMessage.success('删除成功')
    await fetchOrderList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生成用户权益
const handleGenerateEntitlement = async (row: Order) => {
  try {
    await ElMessageBox.confirm('确定要生成该订单的用户权益吗？', '提示', {
      type: 'warning',
    })
    const res = await orderApi.generateEntitlement(row.order_id)
    if (res.data.code === 200) {
      ElMessage.success('用户权益生成成功')
      await fetchOrderList()
    } else {
      ElMessage.error(res.data.message || '生成失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成用户权益失败:', error)
      ElMessage.error('生成用户权益失败')
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
          await orderApi.createOrder(orderForm.value)
          ElMessage.success('创建成功')
        } else {
          await orderApi.updateOrder(currentOrderId.value, orderForm.value)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await fetchOrderList()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(dialogType.value === 'add' ? '创建失败' : '更新失败')
      }
    }
  })
}

// 初始化
onMounted(async () => {
  await fetchOrderList()
})
</script>

<style scoped>
.order-list {
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
