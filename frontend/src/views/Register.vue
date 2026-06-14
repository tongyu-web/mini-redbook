<template>
  <div class="page-center">
    <div class="auth-card">
      <h2>注册</h2>
      <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon closable @close="errorMsg=''" class="mb-3" />
      <el-form @submit.prevent="handleRegister">
        <el-input v-model="form.username" placeholder="手机号/用户名" class="mb-3" />
        <el-input v-model="form.nickname" placeholder="昵称（选填）" class="mb-3" />
        <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" class="mb-3" show-password />
        <el-button type="primary" native-type="submit" class="w-full" :loading="loading">注册</el-button>
      </el-form>
      <p class="mt-3 text-center">已有账号？<router-link to="/login">去登录</router-link></p>
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
  if (form.password.length < 6) {
    errorMsg.value = "密码至少6位"
    return
  }
  loading.value = true
  try {
    const res = await accountsApi.register(form)
    localStorage.setItem("access_token", res.access_token)
    localStorage.setItem("refresh_token", res.refresh_token)
    userStore.setUser(res.user)
    router.push("/")
  } catch (e) {
    errorMsg.value = e.message || "注册失败，请重试"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-center { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f5f5f5; }
.auth-card { width: 360px; padding: 32px; background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.mb-3 { margin-bottom: 16px; }
.mt-3 { margin-top: 16px; }
.w-full { width: 100%; }
</style>
