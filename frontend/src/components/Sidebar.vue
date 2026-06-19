<template>
  <div class="sidebar">
    <div class="logo" @click="$router.push('/')">
      <div class="logo-icon">R</div>
      <span class="logo-text">mini-redbook</span>
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
        <span v-if="notificationStore.unreadCount > 0" class="nav-badge">{{ notificationStore.unreadCount > 99 ? "99+" : notificationStore.unreadCount }}</span>
      </div>
      <div class="nav-item" :class="{ active: $route.path.startsWith('/user') }" @click="goProfile">
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
      <div class="nav-item" @click="goRecycle">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
        <span class="nav-label">回收站</span>
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
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { useNotificationStore } from "../stores/notification"

const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const showAbout = ref(false)
const showAccounts = ref(false)
const defaultAvatar = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ddd'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E"

function goCreate() {
  if (!userStore.isLoggedIn) { router.push("/login"); return }
  router.push("/create")
}
function goProfile() {
  if (!userStore.isLoggedIn) { router.push("/login"); return }
  router.push("/user/" + userStore.user.id)
}
function goRecycle() {
  if (!userStore.isLoggedIn) { router.push("/login"); return }
  router.push("/recycle")
}
function goLogin() {
  router.push("/login")
}
function switchTo(accountId) {
  userStore.switchAccount(accountId)
  showAccounts.value = false
  window.location.reload()
}
function removeAccount(accountId) {
  userStore.removeAccount(accountId)
  if (!userStore.isLoggedIn) {
    window.location.reload()
  }
}
function addAccount() {
  showAccounts.value = false
  router.push("/login")
}
async function handleLogout() {
  showAccounts.value = false
  userStore.clearUser()
  window.location.reload()
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
  border-right: 1px solid #f0f0f0;
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
.nav-bottom {
  padding: 12px 10px 20px;
  border-top: 1px solid #f5f5f5;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Account switcher */
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
.account-arrow {
  transition: transform 0.2s; color: #999; flex-shrink: 0;
}
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
</style>