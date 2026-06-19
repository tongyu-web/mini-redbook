<template>
  <div class="page-center">
    <div class="auth-card">
      <h2>登录</h2>
      <el-form @submit.prevent="handleLogin">
        <el-input v-model="form.username" placeholder="用户名" class="mb-3" />
        <el-input v-model="form.password" type="password" placeholder="密码" class="mb-3" show-password />
        <el-button type="primary" native-type="submit" class="w-full" :loading="loading">登录</el-button>
      </el-form>
      <p class="mt-3 text-center">没有账号？<router-link to="/register">去注册</router-link></p>
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
const form = reactive({ username: "", password: "" })

async function handleLogin() {
  loading.value = true
  try {
    const res = await accountsApi.login(form)
    userStore.addAccount(res.user, res.access_token, res.refresh_token)
    router.push("/")
  } catch (e) {
    // error handled by interceptor
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
