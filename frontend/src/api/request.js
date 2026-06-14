import axios from "axios"
import { ElMessage } from "element-plus"
import router from "../router"

const request = axios.create({
  baseURL: "/api",
  timeout: 15000,
})

let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error)
    else prom.resolve(token)
  })
  failedQueue = []
}

// Request interceptor: attach JWT token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token")
    if (token) {
      config.headers.Authorization = "Bearer " + token
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: unwrap + error handling + token refresh
request.interceptors.response.use(
  (response) => {
    const { code, data, message } = response.data
    if (code === 0) {
      return data
    }
    ElMessage.error(message || "请求失败")
    return Promise.reject(new Error(message))
  },
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = "Bearer " + token
          return request(originalRequest)
        })
      }
      originalRequest._retry = true
      isRefreshing = true
      const refreshToken = localStorage.getItem("refresh_token")
      if (!refreshToken) {
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        router.push("/login")
        return Promise.reject(error)
      }
      try {
        const resp = await axios.post("/api/accounts/token/refresh/", { refresh: refreshToken }, { headers: { "Content-Type": "application/json" } })
        const newToken = resp.data.access || resp.data.access_token
        localStorage.setItem("access_token", newToken)
        processQueue(null, newToken)
        originalRequest.headers.Authorization = "Bearer " + newToken
        return request(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        router.push("/login")
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    ElMessage.error(error.response?.data?.message || "网络错误")
    return Promise.reject(error)
  }
)

export default request