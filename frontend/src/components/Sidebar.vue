<template>
  <div class="sidebar">
    <div class="logo" @click="$router.push('/')">
      <div class="logo-icon">R</div>
      <span class="logo-text">Mini小红书</span>
    </div>
    <div class="nav-items">
      <div class="nav-item" :class="{ active: $route.path === '/' }" @click="$router.push('/')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span class="nav-label">首页</span>
      </div>
      <div class="nav-item" :class="{ active: $route.path.startsWith('/create') || $route.path.startsWith('/edit') }" @click="goCreate">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span class="nav-label">发布</span>
      </div>
      <div class="nav-item" :class="{ active: $route.path.startsWith('/message') }" @click="$router.push('/message')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span class="nav-label">消息</span>
        <span v-if="notificationStore.totalUnread > 0" class="nav-badge">{{ notificationStore.totalUnread > 9 ? (notificationStore.totalUnread > 99 ? "99+" : notificationStore.totalUnread + "+") : notificationStore.totalUnread }}</span>
      </div>
      <div class="nav-item" :class="{ active: userStore.isLoggedIn && $route.path === '/user/' + userStore.user?.id }" @click="goProfile">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span class="nav-label">我的</span>
      </div>
    </div>
    <div class="nav-bottom">
      <div class="nav-item" @click="$router.push('/search')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <span class="nav-label">发现</span>
      </div>
      <div class="nav-item" :class="{ active: $route.path === '/view-history' }" @click="$router.push('/view-history')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <span class="nav-label">浏览记录</span>
      </div>
      <div class="nav-item" @click="goRecycle">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
        <span class="nav-label">回收站</span>
      </div>
      <div class="more-container">
        <div class="nav-item more-trigger" :class="{ active: showMore }" @click="showMore = !showMore">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/>
          </svg>
          <span class="nav-label">更多</span>
          <svg class="more-arrow" :class="{ open: showMore }" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#999" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
        <Transition name="more-fade">
          <div v-if="showMore" class="more-dropdown">
            <div class="more-item" @click="openChangePwd"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#555" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg><span>修改密码</span></div>
            <div class="more-item" @click="openBindEmail"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#555" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg><span>绑定邮箱</span></div>
            <div class="more-item" @click="openBindPhone"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#555" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg><span>绑定手机</span></div>
            <div class="more-item" @click="goPrivacy"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#555" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg><span>隐私设置</span></div>
            <div class="more-item more-item-danger" @click="openCancelAccount"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ff2442" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg><span>注销账号</span></div>
          </div>
        </Transition>
      </div>
      <!-- Account Switcher -->
      <div class="account-section">
        <div v-if="userStore.isLoggedIn" class="account-trigger" @click="showAccounts = !showAccounts">
          <img class="account-avatar" :src="userStore.user?.avatar_url || defaultAvatar" />
          <span class="account-name">{{ userStore.user?.nickname || userStore.user?.username }}</span>
          <svg class="account-arrow" :class="{ open: showAccounts }" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
        <div v-else class="account-trigger" @click="goLogin">
          <div class="account-avatar-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" width="18" height="18"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <span class="account-name" style="color:#999">未登录</span>
        </div>
        <Transition name="account-fade">
          <div v-if="showAccounts && userStore.isLoggedIn" class="account-dropdown">
            <div v-for="acc in userStore.accountList" :key="acc.id" class="account-dropdown-item" :class="{ active: acc.id === userStore.activeAccountId }" @click="switchTo(acc.id)">
              <img class="dd-avatar" :src="acc.avatar_url || defaultAvatar" />
              <span class="dd-name">{{ acc.nickname }}</span>
              <span v-if="acc.id === userStore.activeAccountId" class="dd-check">&#10003;</span>
              <button v-if="acc.id !== userStore.activeAccountId && userStore.accountList.length > 1" class="dd-remove" @click.stop="removeAccount(acc.id)" title="移除">&#10005;</button>
            </div>
            <div class="account-dropdown-divider"></div>
            <div class="account-dropdown-item add-account" @click="addAccount">
              <span class="dd-plus">+</span>
              <span class="dd-name">添加账号</span>
            </div>
            <div class="account-dropdown-item logout-item" @click="handleLogout">
              <span class="dd-logout">退出登录</span>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
  <!-- Change Password Dialog -->

<!-- Change Password Dialog -->
<Teleport to="body">
  <Transition name="login-fade">
    <div v-if="pwdDialog" class="sd-overlay" @click.self="pwdDialog = false">
      <Transition name="login-scale">
        <div v-if="pwdDialog" class="sd-card">
          <button class="sd-close" @click="pwdDialog = false">&times;</button>
          <h3 class="sd-title">修改密码</h3>
          <div class="sd-body">
            <el-input v-model="pwdForm.old_password" type="password" placeholder="旧密码" class="sd-input" show-password />
            <el-input v-model="pwdForm.new_password" type="password" placeholder="新密码（至少6位）" class="sd-input" show-password />
          </div>
          <div class="sd-footer">
            <button class="sd-btn sd-btn-cancel" @click="pwdDialog = false">取消</button>
            <button class="sd-btn sd-btn-primary" :disabled="pwdSaving" @click="changePassword">{{ pwdSaving ? "保存中..." : "确认修改" }}</button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</Teleport>

<!-- Bind Email Dialog -->
<Teleport to="body">
  <Transition name="login-fade">
    <div v-if="emailDialog" class="sd-overlay" @click.self="emailDialog = false">
      <Transition name="login-scale">
        <div v-if="emailDialog" class="sd-card">
          <button class="sd-close" @click="emailDialog = false">&times;</button>
          <h3 class="sd-title">{{ currentEmail ? "邮箱管理" : "绑定邮箱" }}</h3>
          <div class="sd-body">
            <el-input v-model="emailForm.email" placeholder="输入邮箱地址" class="sd-input" :disabled="!!currentEmail" />
            <div style="display:flex;gap:8px">
              <el-input v-model="emailForm.code" placeholder="输入验证码" class="sd-input" maxlength="6" style="flex:1" />
              <button class="code-btn-sd" :disabled="codeSending || codeCountdown > 0" @click="sendEmailCode">{{ codeCountdown > 0 ? codeCountdown + "s" : "获取验证码" }}</button>
            </div>
            <p v-if="currentEmail" style="font-size:13px;color:#999;margin:4px 0 0">当前绑定：{{ currentEmail }}</p>
          </div>
          <div class="sd-footer" style="flex-wrap:wrap;gap:8px">
            <button class="sd-btn sd-btn-cancel" @click="emailDialog = false">取消</button>
            <button v-if="currentEmail" class="sd-btn sd-btn-cancel" style="color:#ff2442;border:1px solid #ff2442;background:#fff" :disabled="unbindSaving" @click="unbindEmail">{{ unbindSaving ? "解绑中..." : "解绑邮箱" }}</button>
            <button class="sd-btn sd-btn-primary" :disabled="emailSaving || !emailForm.code" @click="bindEmailWithCode">{{ emailSaving ? "绑定中..." : (currentEmail ? "换绑" : "确认绑定") }}</button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</Teleport>

<!-- Bind Phone Dialog -->
<Teleport to="body">
  <Transition name="login-fade">
    <div v-if="phoneDialog" class="sd-overlay" @click.self="phoneDialog = false">
      <Transition name="login-scale">
        <div v-if="phoneDialog" class="sd-card">
          <button class="sd-close" @click="phoneDialog = false">&times;</button>
          <h3 class="sd-title">{{ currentPhone ? "手机管理" : "绑定手机" }}</h3>
          <div class="sd-body">
            <el-input v-model="phoneForm.phone" placeholder="输入手机号" class="sd-input" :disabled="!!currentPhone" />
            <div style="display:flex;gap:8px">
              <el-input v-model="phoneForm.code" placeholder="输入验证码" class="sd-input" maxlength="6" style="flex:1" />
              <button class="code-btn-sd" :disabled="phoneCodeSending || phoneCodeCountdown > 0" @click="sendPhoneCode">{{ phoneCodeCountdown > 0 ? phoneCodeCountdown + "s" : "获取验证码" }}</button>
            </div>
            <p v-if="currentPhone" style="font-size:13px;color:#999;margin:4px 0 0">当前绑定：{{ currentPhone }}</p>
          </div>
          <div class="sd-footer" style="flex-wrap:wrap;gap:8px">
            <button class="sd-btn sd-btn-cancel" @click="phoneDialog = false">取消</button>
            <button v-if="currentPhone" class="sd-btn sd-btn-cancel" style="color:#ff2442;border:1px solid #ff2442;background:#fff" :disabled="phoneUnbindSaving" @click="unbindPhone">{{ phoneUnbindSaving ? "解绑中..." : "解绑手机" }}</button>
            <button class="sd-btn sd-btn-primary" :disabled="phoneSaving || !phoneForm.code" @click="bindPhoneWithCode">{{ phoneSaving ? "绑定中..." : (currentPhone ? "换绑" : "确认绑定") }}</button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</Teleport>
<!-- Cancel Account Dialog -->
<Teleport to="body">
  <Transition name="login-fade">
    <div v-if="cancelDialog" class="sd-overlay" @click.self="cancelDialog = false">
      <Transition name="login-scale">
        <div v-if="cancelDialog" class="sd-card">
          <button class="sd-close" @click="cancelDialog = false">&times;</button>
          <h3 class="sd-title">注销账号</h3>
          <p style="font-size:14px;color:#ff2442;font-weight:600;margin-bottom:12px">此操作不可逆，请确认：</p>
          <div class="sd-body">
            <el-input v-model="cancelForm.reason" type="textarea" :rows="2" placeholder="请告诉我们注销原因（选填）" class="sd-input" />
            <el-input v-model="cancelForm.password" type="password" placeholder="请输入密码确认" class="sd-input" show-password />
          </div>
          <div class="sd-footer">
            <button class="sd-btn sd-btn-cancel" @click="cancelDialog = false">取消</button>
            <button class="sd-btn sd-btn-danger" :disabled="cancelSaving" @click="confirmCancel">{{ cancelSaving ? "处理中..." : "确认注销" }}</button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</Teleport>
</template>
<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { useNotificationStore } from "../stores/notification"
import { ElMessage } from "element-plus"
import { openLoginDialog } from "../utils/dialogState"

const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const showAbout = ref(false)
const showAccounts = ref(false)
const showMore = ref(false)
const defaultAvatar = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ddd'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E"

const pwdDialog = ref(false)
const pwdSaving = ref(false)
const pwdForm = reactive({ old_password: "", new_password: "" })
const emailDialog = ref(false)
const emailSaving = ref(false)
const emailForm = reactive({ email: "", code: "" })
const unbindSaving = ref(false)
const currentEmail = ref("")
const phoneDialog = ref(false)
const phoneSaving = ref(false)
const phoneUnbindSaving = ref(false)
const phoneForm = reactive({ phone: "", code: "" })
const currentPhone = ref("")
const phoneCodeSending = ref(false)
const phoneCodeCountdown = ref(0)
let phoneTimer = null
const codeSending = ref(false)
const codeCountdown = ref(0)
let codeTimer = null
const cancelDialog = ref(false)
const cancelSaving = ref(false)
const cancelForm = reactive({ reason: "", password: "" })

function openChangePwd() {
  showMore.value = false
  if (!userStore.isLoggedIn) { openLoginDialog(); return }
  pwdForm.old_password = ""
  pwdForm.new_password = ""
  pwdDialog.value = true
}
async function changePassword() {
  if (!pwdForm.old_password || !pwdForm.new_password) { ElMessage.warning("请填写完整"); return }
  if (pwdForm.new_password.length < 6) { ElMessage.warning("新密码至少6位"); return }
  pwdSaving.value = true
  try {
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.changePassword({ old_password: pwdForm.old_password, new_password: pwdForm.new_password })
    ElMessage.success("密码修改成功")
    pwdDialog.value = false
  } catch (e) { ElMessage.error(e.message || "修改失败") }
  finally { pwdSaving.value = false }
}
function openBindEmail() {
  showMore.value = false
  if (!userStore.isLoggedIn) { openLoginDialog(); return }
  emailForm.email = currentEmail.value || ""
  emailDialog.value = true
}
async function sendEmailCode() {
  if (!emailForm.email.trim()) { ElMessage.warning("请输入邮箱地址"); return }
  codeSending.value = true
  try {
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.sendEmailCode({ email: emailForm.email.trim() })
    ElMessage.success("验证码已发送到邮箱")
    codeCountdown.value = 60
    if (codeTimer) clearInterval(codeTimer)
    codeTimer = setInterval(() => {
      codeCountdown.value--
      if (codeCountdown.value <= 0) { clearInterval(codeTimer); codeTimer = null }
    }, 1000)
  } catch (e) { ElMessage.error(e.message || "发送失败") }
  finally { codeSending.value = false }
}

async function bindEmailWithCode() {
  if (!emailForm.email.trim()) { ElMessage.warning("请输入邮箱地址"); return }
  if (!emailForm.code.trim()) { ElMessage.warning("请输入验证码"); return }
  emailSaving.value = true
  try {
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.bindEmailWithCode({ email: emailForm.email.trim(), code: emailForm.code.trim() })
    currentEmail.value = emailForm.email.trim()
    ElMessage.success("邮箱绑定成功")
    emailDialog.value = false
    if (codeTimer) { clearInterval(codeTimer); codeTimer = null }
    codeCountdown.value = 0
  } catch (e) { ElMessage.error(e.message || "绑定失败") }
  finally { emailSaving.value = false }
}
async function unbindEmail() {
  unbindSaving.value = true
  try {
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.unbindEmail()
    currentEmail.value = ""
    ElMessage.success("邮箱已解绑")
    emailDialog.value = false
  } catch (e) { ElMessage.error(e.message || "解绑失败") }
  finally { unbindSaving.value = false }
}

function openBindPhone() {
  showMore.value = false
  if (!userStore.isLoggedIn) { openLoginDialog(); return }
  phoneForm.phone = currentPhone.value || ""
  phoneDialog.value = true
}
async function sendPhoneCode() {
  if (!phoneForm.phone.trim()) { ElMessage.warning("请输入手机号"); return }
  phoneCodeSending.value = true
  try {
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.sendPhoneCode({ phone: phoneForm.phone.trim() })
    ElMessage.success("验证码已发送（开发环境：666666）")
    phoneCodeCountdown.value = 60
    if (phoneTimer) clearInterval(phoneTimer)
    phoneTimer = setInterval(() => {
      phoneCodeCountdown.value--
      if (phoneCodeCountdown.value <= 0) { clearInterval(phoneTimer); phoneTimer = null }
    }, 1000)
  } catch (e) { ElMessage.error(e.message || "发送失败") }
  finally { phoneCodeSending.value = false }
}
async function bindPhoneWithCode() {
  if (!phoneForm.phone.trim()) { ElMessage.warning("请输入手机号"); return }
  if (!phoneForm.code.trim()) { ElMessage.warning("请输入验证码"); return }
  phoneSaving.value = true
  try {
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.bindPhoneWithCode({ phone: phoneForm.phone.trim(), code: phoneForm.code.trim() })
    currentPhone.value = phoneForm.phone.trim()
    ElMessage.success("手机绑定成功")
    phoneDialog.value = false
    if (phoneTimer) { clearInterval(phoneTimer); phoneTimer = null }
    phoneCodeCountdown.value = 0
  } catch (e) { ElMessage.error(e.message || "绑定失败") }
  finally { phoneSaving.value = false }
}
async function unbindPhone() {
  phoneUnbindSaving.value = true
  try {
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.unbindPhone()
    currentPhone.value = ""
    ElMessage.success("手机已解绑")
    phoneDialog.value = false
  } catch (e) { ElMessage.error(e.message || "解绑失败") }
  finally { phoneUnbindSaving.value = false }
}
function goPrivacy() {
  showMore.value = false
  router.push("/settings")
}
function openCancelAccount() {
  showMore.value = false
  if (!userStore.isLoggedIn) { openLoginDialog(); return }
  cancelForm.reason = ""
  cancelForm.password = ""
  cancelDialog.value = true
}
async function confirmCancel() {
  cancelSaving.value = true
    const { accountsApi } = await import("../api/accounts")
    await accountsApi.cancelAccount({ reason: cancelForm.reason, password: cancelForm.password })
    cancelDialog.value = false
    userStore.clearUser()
    window.location.reload()
}
function goCreate() {
  if (!userStore.isLoggedIn) { openLoginDialog(); return }
  router.push("/create")
}
function goProfile() {
  if (!userStore.isLoggedIn) { openLoginDialog(); return }
  router.push("/user/" + userStore.user.id)
}
function goRecycle() {
  if (!userStore.isLoggedIn) { openLoginDialog(); return }
  router.push("/recycle")
}
function goLogin() {
  openLoginDialog()
}
function switchTo(accountId) {
  userStore.switchAccount(accountId)
  showAccounts.value = false
  window.location.reload()
}
function removeAccount(accountId) {
  userStore.removeAccount(accountId)
}
function addAccount() {
  showAccounts.value = false
  openLoginDialog()
}
async function handleLogout() {
  showAccounts.value = false
  userStore.clearUser()
  router.push("/")
}
if (typeof document !== "undefined") {
  document.addEventListener("click", function(e) {
    var el = document.querySelector(".account-section")
    if (el && !el.contains(e.target)) {
      showAccounts.value = false
    }
  })
}
</script>
<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 220px;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  z-index: 200;
  padding: 0;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px 20px 20px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
}
.logo-icon {
  width: 36px;
  height: 36px;
  background: #ff2442;
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
}
.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #222;
}
.nav-items {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  color: #555;
  position: relative;
}
.nav-item:hover { background: #e8e8e8; color: #222; }
.nav-item.active { background: #fff0f0; color: #ff2442; font-weight: 600; }
.nav-icon { width: 22px; height: 22px; flex-shrink: 0; }
.nav-label { font-size: 14px; }
.nav-badge {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: #ff2442; color: white; font-size: 10px; border-radius: 10px;
  padding: 1px 5px; min-width: 16px; text-align: center; font-weight: 600;
}
.more-container { position: relative; }
.more-arrow { transition: transform 0.2s; }
.more-arrow.open { transform: rotate(180deg); }
.more-dropdown {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  padding: 6px;
  z-index: 300;
}
.more-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #555;
  transition: background 0.12s;
}
.more-item:hover { background: #f5f5f5; color: #222; }
.more-item-danger { color: #ff2442; }
.more-item-danger:hover { background: #fff0f0; }
.more-fade-enter-active, .more-fade-leave-active { transition: opacity 0.15s, transform 0.15s; }
.more-fade-enter-from, .more-fade-leave-to { opacity: 0; transform: translateY(-4px); }
.dialog-input { margin-bottom: 10px; }
.nav-bottom {
  padding: 12px 10px 20px;
  border-top: 1px solid #f5f5f5;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.account-section {
  position: relative;
  border-top: 1px solid #f0f0f0;
  margin-top: 4px;
  padding-top: 4px;
}
.account-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
}
.account-trigger:hover { background: #e8e8e8; }
.account-avatar, .account-avatar-placeholder {
  width: 28px; height: 28px; border-radius: 50%; object-fit: cover; flex-shrink: 0;
}
.account-avatar-placeholder {
  background: #f0f0f0; display: flex; align-items: center; justify-content: center;
}
.account-name {
  flex: 1; font-size: 13px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.account-arrow { transition: transform 0.2s; color: #999; flex-shrink: 0; }
.account-arrow.open { transform: rotate(180deg); }
.account-dropdown {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  padding: 6px;
  z-index: 300;
  max-height: 280px;
  overflow-y: auto;
}
.account-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.12s;
  font-size: 13px;
}
.account-dropdown-item:hover { background: #f5f5f5; }
.account-dropdown-item.active { background: #fff0f0; color: #ff2442; font-weight: 600; }
.dd-avatar { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; }
.dd-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dd-check { color: #ff2442; font-weight: 700; font-size: 14px; }
.dd-remove {
  background: none; border: none; color: #ccc; cursor: pointer; font-size: 14px; padding: 2px 4px; border-radius: 4px; line-height: 1;
}
.dd-remove:hover { color: #ff2442; background: #fff0f0; }
.account-dropdown-divider { height: 1px; background: #f0f0f0; margin: 4px 0; }
.add-account { color: #ff2442; }
.add-account:hover { background: #fff0f0; }
.dd-plus { font-size: 18px; font-weight: 700; width: 24px; text-align: center; }
.logout-item { color: #999; }
.logout-item:hover { color: #ff2442; background: #fff0f0; }
.dd-logout { font-size: 13px; }
.account-fade-enter-active, .account-fade-leave-active { transition: opacity 0.15s, transform 0.15s; }
.account-fade-enter-from, .account-fade-leave-to { opacity: 0; transform: translateY(4px); }


/* Sidebar dialog overlay - matching LoginDialog style */
.sd-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.45);
  z-index: 3000;
  display: flex; justify-content: center; align-items: center;
  backdrop-filter: blur(2px);
}
.sd-card {
  width: 380px;
  max-width: 90vw;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
  padding: 32px 28px 24px;
  position: relative;
}
.sd-close {
  position: absolute; top: 14px; right: 14px;
  width: 28px; height: 28px; border-radius: 50%;
  border: none; background: #f5f5f5;
  font-size: 18px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: #999; transition: all 0.15s;
}
.sd-close:hover { background: #e8e8e8; color: #333; }
.sd-title {
  font-size: 20px; font-weight: 700; color: #222;
  margin: 0 0 20px;
}
.sd-body {
  display: flex; flex-direction: column; gap: 12px;
  margin-bottom: 20px;
}
.sd-input { width: 100%; }
.sd-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e8e8e8 inset;
  padding: 0 14px;
  background: #fff;
}
.sd-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #ddd inset;
}
.sd-input :deep(.el-input__wrapper.is-focus),
.sd-input :deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 1px #ff2442 inset;
}
.sd-input :deep(.el-input__inner) {
  height: 44px;
  font-size: 14px;
}
.sd-input :deep(.el-textarea__inner) {
  border-radius: 10px;
  font-size: 14px;
  box-shadow: 0 0 0 1px #e8e8e8 inset;
  padding: 10px 14px;
}
.sd-input :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #ff2442 inset;
}
.sd-footer {
  display: flex; gap: 10px;
}
.sd-btn {
  flex: 1; height: 44px; border-radius: 22px;
  border: none; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.15s;
}
.sd-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.sd-btn-cancel {
  background: #f5f5f5; color: #666;
}
.sd-btn-cancel:hover { background: #e8e8e8; }
.sd-btn-primary {
  background: #ff2442; color: #fff;
}
.sd-btn-primary:hover { opacity: 0.9; }
.sd-btn-danger {
  background: #ff2442; color: #fff;
}
.sd-btn-danger:hover { opacity: 0.9; }
/* Dialog transitions */
.sd-overlay .login-fade-enter-active,
.sd-overlay .login-fade-leave-active {
  transition: opacity 0.2s ease;
}
.sd-overlay .login-fade-enter-from,
.sd-overlay .login-fade-leave-to {
  opacity: 0;
}
.sd-overlay .login-scale-enter-active,
.sd-overlay .login-scale-leave-active {
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease;
}
.sd-overlay .login-scale-enter-from,
.sd-overlay .login-scale-leave-to {
  transform: scale(0.92);
  opacity: 0;
}
.code-btn-sd {
  height: 44px; padding: 0 14px; border-radius: 10px;
  border: 1px solid #e8e8e8; background: #fafafa;
  color: #ff2442; font-size: 13px; cursor: pointer;
  transition: all 0.15s; white-space: nowrap; flex-shrink: 0;
}
.code-btn-sd:hover:not(:disabled) { background: #fff0f0; border-color: #ff2442; }
.code-btn-sd:disabled { color: #ccc; cursor: not-allowed; }
</style>
