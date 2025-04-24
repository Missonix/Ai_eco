<template>
  <div class="home-container">
    <!-- 数据卡片区域 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="data-card" @click="navigateTo('/users')">
          <div class="card-content">
            <div class="icon-wrapper blue">
              <el-icon :size="24"><User /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">用户总数</div>
              <div class="data-value">{{ userCount }}</div>
              <div class="data-change">
                <el-icon><ArrowUp /></el-icon>
                <span>较上月增长 12%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card" @click="navigateTo('/courses')">
          <div class="card-content">
            <div class="icon-wrapper green">
              <el-icon :size="24"><Reading /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">课程总数</div>
              <div class="data-value">{{ courseCount }}</div>
              <div class="data-change">
                <el-icon><ArrowUp /></el-icon>
                <span>较上月增长 8%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card" @click="navigateTo('/orders')">
          <div class="card-content">
            <div class="icon-wrapper orange">
              <el-icon :size="24"><List /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">订单总数</div>
              <div class="data-value">{{ orderCount }}</div>
              <div class="data-change">
                <el-icon><ArrowUp /></el-icon>
                <span>较上月增长 15%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card" @click="navigateTo('/products')">
          <div class="card-content">
            <div class="icon-wrapper purple">
              <el-icon :size="24"><Goods /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">产品总数</div>
              <div class="data-value">{{ productCount }}</div>
              <div class="data-change">
                <el-icon><ArrowUp /></el-icon>
                <span>较上月增长 5%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近7天订单趋势</span>
            </div>
          </template>
          <div class="chart" ref="orderTrendChart"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>用户分布</span>
            </div>
          </template>
          <div class="chart" ref="userDistChart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Reading, List, Goods, ArrowUp } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const orderTrendChart = ref<HTMLElement | null>(null)
const userDistChart = ref<HTMLElement | null>(null)

// 模拟数据
const userCount = ref(1234)
const courseCount = ref(56)
const orderCount = ref(789)
const productCount = ref(32)

// 页面跳转
const navigateTo = (path: string) => {
  router.push(path)
}

onMounted(() => {
  // 初始化订单趋势图表
  if (orderTrendChart.value) {
    const chart = echarts.init(orderTrendChart.value)
    chart.setOption({
      tooltip: {
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          data: [150, 230, 224, 218, 135, 147, 260],
          type: 'line',
          smooth: true,
          areaStyle: {
            opacity: 0.3,
          },
          lineStyle: {
            width: 3,
          },
        },
      ],
    })
  }

  // 初始化用户分布图表
  if (userDistChart.value) {
    const chart = echarts.init(userDistChart.value)
    chart.setOption({
      tooltip: {
        trigger: 'item',
      },
      legend: {
        orient: 'vertical',
        left: 'left',
      },
      series: [
        {
          type: 'pie',
          radius: '70%',
          data: [
            { value: 735, name: '普通用户' },
            { value: 580, name: 'VIP用户' },
            { value: 484, name: '企业用户' },
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    })
  }
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.chart-row {
  margin-top: 20px;
}

.data-card {
  cursor: pointer;
  transition: all 0.3s;
}

.data-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.blue {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.green {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.orange {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.purple {
  background-color: rgba(180, 160, 255, 0.1);
  color: #b4a0ff;
}

.data-info {
  flex: 1;
}

.data-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.data-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.data-change {
  font-size: 12px;
  color: #67c23a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.chart {
  height: 300px;
}

.card-header {
  font-weight: bold;
  color: #303133;
}
</style>
