<!-- src/components/StockPanel.vue -->
<template>
  <div class="p-4">
    <h2>股票预测分析</h2>
    <button @click="loadData">查询 000001</button>

    <div v-if="loading">加载中...</div>
    <div v-if="error" class="text-red-500">{{ error }}</div>

    <div v-if="predData">
      <h3>预测结果：<span :class="predData.predict_result==='up'?'text-green-500':'text-red-500'">
        {{ predData.predict_result === "up" ? "看涨" : "看跌" }}
      </span></h3>

      <div class="my-3">
        <h4>量化特征</h4>
        <p>三日均价：{{ predData.feature.mean_close.toFixed(2) }}</p>
        <p>平均成交量：{{ predData.feature.mean_volume }}</p>
        <p>价格振幅：{{ predData.feature.price_range.toFixed(2) }}</p>
        <p>当日涨跌幅：{{ (predData.feature.last_pct*100).toFixed(2) }}%</p>
      </div>

      <h4>三日K线原始数据</h4>
      <pre>{{ JSON.stringify(predData.raw_3day_data,null,2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { fetchStockPredict } from "../api/stockAPI";

const predData = ref(null);
const loading = ref(false);
const error = ref("");

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    predData.value = await fetchStockPredict("000001");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>
