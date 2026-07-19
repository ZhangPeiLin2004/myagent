<template>
  <div class="container">
    <h1>Hermes AStock Agent 前端</h1>
    <div>
      <h3>会话列表</h3>
      <ul v-if="sessionList.length > 0">
        <li v-for="item in sessionList" :key="item.id">
          {{ item.name }} - 创建时间：{{ item.created_at }}
        </li>
      </ul>
      <p v-else>暂无会话数据，点击按钮加载</p>
      <button @click="loadSession">刷新会话</button>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from 'vue'
const sessionList = ref([])
const instance = getCurrentInstance()
const $api = instance.appContext.config.globalProperties.$api

const loadSession = async () => {
  try {
    const res = await $api.get('/session/list')
    sessionList.value = res.data
  } catch (err) {
    console.error(err)
  }
}
</script>

<style scoped>
.container {
  padding: 20px;
}
button {
  margin-top: 10px;
}
</style>
