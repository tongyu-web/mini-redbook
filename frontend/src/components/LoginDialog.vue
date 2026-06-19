<template>
  <Teleport to="body">
    <Transition name="login-fade">
      <div v-if="visible" class="login-overlay" @click.self="close">
        <Transition name="login-scale">
          <div v-if="visible" class="login-card">
            <button class="login-close" @click="close">&times;</button>

            <div class="login-header">
              <h2 class="login-title">{{ isRegister ? "手机号注册" : "手机号登录" }}</h2>
              <p class="login-subtitle">{{ isRegister ? "注册后即可开始探索" : "欢迎回来，继续你的分享" }}</p>
            </div>

            <form class="login-form" @submit.prevent="handleSubmit">
              <!-- Phone / Username -->
              <div class="form-field">
                <el-input
                  v-model="form.username"
                  :placeholder="isRegister ? '请填写手机号' : '请输入手机号'"
                  :maxlength="20"
                  size="large"
                  clearable
                />
              </div>

              <!-- Verification Code (register only) -->
              <div v-if="isRegister" class="form-field form-field-code">
                <el-input
                  v-model="form.code"
                  placeholder="请输入验证码"
                  :maxlength="6"
                  size="large"
                  class="code-input"
                />
                <el-button
                  class="code-btn"
                  :disabled="codeSending || codeCountdown > 0"
                  @click="sendCode"
                >
                  {{ codeCountdown > 0 ? codeCountdown + "s" : "获取验证码" }}
                </el-button>
              </div>

              <!-- Password -->
              <div class="form-field">
                <el-input
                  v-model="form.password"
                  type="password"
                  :placeholder="isRegister ? '设置密码（至少6位）' : '请输入密码'"
                  show-password
                  size="large"
                />
              </div>

              <el-button
                native-type="submit"
                class="login-btn"
                :loading="loading"
                :disabled="!canSubmit"
              >
                {{ isRegister ? "注册" : "登录" }}
              </el-button>
            </form>

            <div class="login-footer">
              <span class="footer-text" @click="toggleMode">
                {{ isRegister ? "已有账号？去登录" : "没有账号？去注册" }}
              </span>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from "vue"
import { ElMessage } from "element-plus"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { accountsApi } from "../api/accounts"

const props = defineProps({ visible: Boolean })
const emit = defineEmits(["update:visible", "success"])

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const isRegister = ref(false)
const codeSending = ref(false)
const codeCountdown = ref(0)
let codeTimer = null

const form = reactive({ username: "", password: "", code: "" })

const canSubmit = computed(() => {
  if (isRegister.value) {
    return form.username.trim() && form.password.length >= 6 && form.code.trim()
  }
  return form.username.trim() && form.password.trim()
})

function close() {
  emit("update:visible", false)
}

function toggleMode() {
  isRegister.value = !isRegister.value
  form.code = ""
}

function startCountdown() {
  codeCountdown.value = 60
  if (codeTimer) clearInterval(codeTimer)
  codeTimer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(codeTimer)
      codeTimer = null
    }
  }, 1000)
}

async function sendCode() {
  if (!form.username.trim()) {
    ElMessage.warning("请先填写手机号")
    return
  }
  codeSending.value = true
  // Simulate SMS code sending
  await new Promise(r => setTimeout(r, 500))
  ElMessage.success("验证码已发送（开发环境：123456）")
  form.code = "123456"
  codeSending.value = false
  startCountdown()
}

async function handleSubmit() {
  if (!canSubmit.value) return
  loading.value = true
  try {
    if (isRegister.value) {
      const res = await accountsApi.register({
        username: form.username.trim(),
        password: form.password,
        nickname: form.username.trim(),
      })
      userStore.addAccount(res.user, res.access_token, res.refresh_token)
      ElMessage.success("注册成功")
    } else {
      const res = await accountsApi.login({
        username: form.username.trim(),
        password: form.password,
      })
      userStore.addAccount(res.user, res.access_token, res.refresh_token)
    }
    close()
    emit("success")
  } catch (e) {
    // Error handled by interceptor
  } finally {
    loading.value = false
  }
}

watch(() => props.visible, (v) => {
  if (!v) {
    isRegister.value = false
    form.username = ""
    form.password = ""
    form.code = ""
    if (codeTimer) { clearInterval(codeTimer); codeTimer = null }
    codeCountdown.value = 0
  }
})
</script>

<style scoped>
.login-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.45);
  z-index: 3000;
  display: flex; justify-content: center; align-items: center;
  backdrop-filter: blur(2px);
}

.login-card {
  width: 400px;
  max-width: 90vw;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
  padding: 40px 36px 32px;
  position: relative;
}

.login-close {
  position: absolute; top: 16px; right: 16px;
  width: 28px; height: 28px; border-radius: 50%;
  border: none; background: #f5f5f5;
  font-size: 18px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: #999; transition: all 0.15s;
}
.login-close:hover { background: #e8e8e8; color: #333; }

.login-header { margin-bottom: 28px; }
.login-title { font-size: 22px; font-weight: 700; color: #222; margin-bottom: 6px; }
.login-subtitle { font-size: 13px; color: #999; }

.login-form { display: flex; flex-direction: column; gap: 14px; }

.form-field :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e8e8e8 inset;
  padding: 0 14px;
  transition: box-shadow 0.2s;
}
.form-field :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #ddd inset;
}
.form-field :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #ff2442 inset;
}
.form-field :deep(.el-input__inner) {
  height: 46px;
  font-size: 15px;
}

.form-field-code { display: flex; gap: 10px; }
.form-field-code .code-input { flex: 1; }
.code-btn {
  flex-shrink: 0;
  height: 46px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
  background: #fafafa;
  color: #ff2442;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.code-btn:hover:not(:disabled) { background: #fff0f0; border-color: #ff2442; }
.code-btn:disabled { color: #ccc; cursor: not-allowed; }

.login-btn {
  width: 100%;
  height: 46px;
  border-radius: 23px;
  border: none;
  background: #ff2442;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 4px;
  transition: opacity 0.15s;
}
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.login-btn:not(:disabled):hover { opacity: 0.9; }

.login-footer { margin-top: 20px; text-align: center; }
.footer-text {
  font-size: 13px;
  color: #999;
  cursor: pointer;
  transition: color 0.15s;
}
.footer-text:hover { color: #ff2442; }

/* Transitions */
.login-fade-enter-active, .login-fade-leave-active { transition: opacity 0.2s ease; }
.login-fade-enter-from, .login-fade-leave-to { opacity: 0; }
.login-scale-enter-active, .login-scale-leave-active { transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease; }
.login-scale-enter-from, .login-scale-leave-to { transform: scale(0.92); opacity: 0; }
</style>
