import axios from "axios"
import router from "../router"
import { openLoginDialog } from "../utils/dialogState"

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

request.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem("access_token")
    if (token) {
      config.headers.Authorization = "Bearer " + token
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const { code, data, message } = response.data
    if (code === 0) {
      return data
    }
    return Promise.reject(new Error(message || "请求失败"))
  },
  async (error) => {
    if (error.response?.status === 401) {
      const originalRequest = error.config
      if (!originalRequest?._retry) {
        originalRequest._retry = true
        const refreshToken = sessionStorage.getItem("refresh_token")
        if (refreshToken) {
          try {
            const resp = await axios.post("/api/accounts/token/refresh/", { refresh: refreshToken })
            const newToken = resp.data.access || resp.data.access_token
            sessionStorage.setItem("access_token", newToken)
            originalRequest.headers.Authorization = "Bearer " + newToken
            return request(originalRequest)
          } catch (e) {}
        }
      }
      sessionStorage.removeItem("access_token")
      sessionStorage.removeItem("refresh_token")
      openLoginDialog()
      return Promise.reject(error)
    }
    return Promise.reject(error)
  }
)

export default request


