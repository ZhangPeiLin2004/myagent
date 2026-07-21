// frontend/src/api/stockAPI.ts
import axios from 'axios'

// 复用全局axios配置，如果你chatAPI.ts已经创建实例，可以直接导入
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Accept': 'application/json'
  }
})

// 类型定义
export interface KLineItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  pre_close: number
  volume: number
  amount: number
}

export interface PredictResponse {
  stock_code: string
  predict_prob: number
  predict_result: 'up' | 'down'
  raw_3day_data: KLineItem[]
}

export interface KLineThreeResponse {
  code: string
  success: boolean
  data: KLineItem[]
}

export interface TrainResponse {
  success: boolean
  accuracy?: number
  train_samples?: number
  test_samples?: number
  msg: string
}

/**
 * 获取3日K线数据
 * @param code 股票代码
 */
export function getThreeKline(code: string = '000001') {
  return api.get<KLineThreeResponse>('/api/kline/three', {
    params: { code }
  })
}

/**
 * AI涨跌预测接口
 * @param code 股票代码
 */
export function getStockPredict(code: string = '000001') {
  return api.get<PredictResponse>('/api/predict', {
    params: { code }
  })
}

/**
 * 训练LightGBM模型
 * @param code 股票代码
 */
export function trainStockModel(code: string = '000001') {
  return api.post<TrainResponse>(`/api/stock/train?code=${code}`)
}

export default api
