<template>
  <div class="app-container">
    <h1>Hermes AStock Agent 前端</h1>

    <!-- 视图切换按钮 -->
    <div class="tab-buttons">
      <button @click="viewMode = 'session'" :class="{active: viewMode === 'session'}">会话管理</button>
      <button @click="viewMode = 'stock'" :class="{active: viewMode === 'stock'}">股票AI预测</button>
    </div>

    <!-- 会话面板 -->
    <div v-if="viewMode === 'session'" class="panel">
      <h3>会话列表</h3>
      <ul v-if="sessionList.length > 0">
        <li v-for="item in sessionList" :key="item.id">
          {{ item.name }} - 创建时间：{{ item.created_at }}
        </li>
      </ul>
      <p v-else>暂无会话数据，点击按钮加载</p>
      <button @click="loadSession">刷新会话</button>
    </div>

    <!-- 股票预测面板 -->
    <div v-if="viewMode === 'stock'" class="panel">
      <h3>股票预测分析模块</h3>
      <div class="stock-operate">
        <label>股票代码：</label>
        <input v-model="stockCode" placeholder="000001"/>
        <button @click="trainModel" :disabled="loading.train">
          {{ loading.train ? "训练中..." : "训练模型" }}
        </button>
        <button @click="fetchPredict" :disabled="loading.predict">
          {{ loading.predict ? "查询中..." : "获取预测结果" }}
        </button>
      </div>

      <div v-if="errMsg" class="text-red">{{ errMsg }}</div>

      <div v-if="predictData" class="stock-result">
        <h4>预测结论：
          <span :class="predictData.predict_result === 'up' ? 'text-green' : 'text-red'">
            {{ predictData.predict_result === "up" ? "看涨 UP" : "看跌 DOWN" }}
          </span>
        </h4>
        <p>预测涨跌幅中位数：<strong>{{ predictData.pred_pct_median }} %</strong></p>
        <p>{{predictData.confidence}}置信区间：
          [{{predictData.pred_pct_low}} %, {{predictData.pred_pct_high}} %]
        </p>
        <h5>原始三日K线数据</h5>
        <pre>{{ JSON.stringify(predictData.raw_3day_data, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from 'vue'
import { getStockPredict, trainStockModel } from './api/stockAPI'

const instance = getCurrentInstance()
const $api = instance.appContext.config.globalProperties.$api

// 视图切换
const viewMode = ref('session')

// ========== 会话模块 ==========
const sessionList = ref([])
const loadSession = async () => {
  try {
    const res = await $api.get('/session/list')
    sessionList.value = res.data
  } catch (err) {
    console.error('会话加载失败：', err)
    alert("后端尚未实现 /session/list 会话接口")
  }
}

// ========== 股票模块 ==========
const stockCode = ref('000001')
const predictData = ref(null)
const errMsg = ref('')
const loading = ref({
  train: false,
  predict: false
})

// 训练模型
const trainModel = async () => {
  errMsg.value = ''
  loading.value.train = true
  try {
    const res = await trainStockModel(stockCode.value)
    alert(`训练完成！${res.data.msg}`)
  } catch (err) {
    errMsg.value = "训练失败：" + err.message
    console.error(err)
  } finally {
    loading.value.train = false
  }
}

// 获取预测
const fetchPredict = async () => {
  errMsg.value = ''
  loading.value.predict = true
  try {
    const res = await getStockPredict(stockCode.value)
    predictData.value = res.data
  } catch (err) {
    errMsg.value = "预测请求失败：" + err.message
    console.error(err)
  } finally {
    loading.value.predict = false
  }
}
</script>

<style scoped>
.app-container {
  padding: 24px;
}
.tab-buttons {
  margin-bottom: 16px;
}
.tab-buttons button {
  padding: 6px 14px;
  margin-right: 8px;
  border: 1px solid #ccc;
  background: #fff;
  cursor: pointer;
}
.tab-buttons button.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}
.panel {
  border: 1px solid #e5e7eb;
  padding: 16px;
  border-radius: 6px;
}
.stock-operate {
  margin-bottom: 16px;
}
.stock-operate input {
  padding: 4px 8px;
  width: 160px;
  margin: 0 8px;
}
pre {
  background: #f3f4f6;
  padding: 10px;
  overflow-x: auto;
  font-size: 12px;
}
.text-red {
  color: #ef4444;
}
.text-green {
  color: #16a34a;
}
.ml-3 {
  margin-left: 12px;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
