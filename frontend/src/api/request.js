import axios from "axios"
import { ElMessage } from "element-plus"
import router from "../router"

const request = axios.create({
  baseURL: "/api",
  timeout: 15000,
})

// 请求拦截器：自动附加 JWT token
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

// 响应拦截器：统一解包 + 错误处理
request.interceptors.response.use(
  (response) => {
    const { code, data, message } = response.data
    if (code === 0) {
      return data
    }
    ElMessage.error(message || "请求失败")
    return Promise.reject(new Error(message))
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      router.push("/login")
    }
    ElMessage.error(error.response?.data?.message || "网络错误")
    return Promise.reject(error)
  }
)

export default request
