import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'

// 全局axios配置，对接后端8000端口API
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 10000
})

const app = createApp(App)
app.config.globalProperties.$api = api
app.mount('#app')
