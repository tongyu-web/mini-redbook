<template>
  <div class="page-center">
    <div class="auth-card">
      <h2 class="auth-title">注册</h2>
      <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon closable @close="errorMsg=''" class="mb-3" />
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="input-group">
          <input v-model="form.username" placeholder="手机号" maxlength="11" class="auth-input" />
        </div>
        <div class="input-group">
          <input v-model="form.nickname" placeholder="昵称（选填）" class="auth-input" />
        </div>
        <div class="input-group">
          <input v-model="form.password" type="password" placeholder="密码（至少6位）" class="auth-input" />
        </div>
        <button type="submit" class="auth-btn" :disabled="loading">
          <span v-if="loading" class="btn-loading"></span>
          <span v-else>注册</span>
        </button>
      </form>
      <p class="auth-footer">已有账号？<router-link to="/login" class="auth-link">去登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { accountsApi } from "../api/accounts"

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const errorMsg = ref("")
const form = reactive({ username: "", nickname: "", password: "" })

async function handleRegister() {
  errorMsg.value = ""
  if (!form.username || !form.password) {
    errorMsg.value = "请填写手机号和密码"
    return
  }
  if (form.username.length !== 11 || !/^\d{11}$/.test(form.username)) {
    errorMsg.value = "手机号必须为11位数字"
    return
  }
  if (form.password.length < 6) {
    errorMsg.value = "密码至少6位"
    return
  }
  loading.value = true
  try {
    const res = await accountsApi.register(form)
    userStore.addAccount(res.user, res.access_token, res.refresh_token)
    router.push("/")
  } catch (e) {
    errorMsg.value = e.message || "注册失败，请重试"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}
.auth-card {
  width: 360px;
  padding: 40px 32px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
.auth-title {
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 28px;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.input-group {
  position: relative;
}
.auth-input {
  width: 100%;
  height: 48px;
  padding: 0 14px;
  border: 1.5px solid #e8e8e8;
  border-radius: 10px;
  font-size: 15px;
  color: #1a1a1a;
  background: #fafafa;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.auth-input::placeholder {
  color: #bbb;
  font-size: 14px;
}
.auth-input:focus {
  border-color: #ff2442;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(255,36,66,0.08);
}
.auth-input:focus::placeholder {
  color: #ccc;
}
.auth-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 10px;
  background: #ff2442;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.1s;
  margin-top: 4px;
}
.auth-btn:hover {
  background: #d61e38;
}
.auth-btn:active {
  transform: scale(0.98);
}
.auth-btn:disabled {
  background: #f0f0f0;
  color: #ccc;
  cursor: default;
  transform: none;
}
.btn-loading {
  width: 20px;
  height: 20px;
  border: 2.5px solid #ddd;
  border-top-color: #ff2442;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.auth-footer {
  text-align: center;
  margin-top: 22px;
  font-size: 13px;
  color: #999;
}
.auth-link {
  color: #ff2442;
  text-decoration: none;
  font-weight: 500;
}
.auth-link:hover {
  text-decoration: underline;
}
.mb-3 { margin-bottom: 16px; }
</style>