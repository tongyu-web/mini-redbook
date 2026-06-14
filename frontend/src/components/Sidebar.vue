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
      <div class="nav-item create-btn" @click="goCreate">
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
      <div class="nav-item about-item" @click="showAbout = true">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <span class="nav-label">关于</span>
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
.nav-item:hover { background: #f5f5f5; color: #222; }
.nav-item.active { background: #fff0f0; color: #ff2442; font-weight: 600; }
.nav-icon { width: 22px; height: 22px; flex-shrink: 0; }
.nav-label { font-size: 14px; }
.create-btn { margin-top: 4px; background: #ff2442; color: white; border-radius: 10px; }
.create-btn:hover { background: #e01e38; color: white; }
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
.about-item { color: #bbb; font-size: 12px; }
.about-item:hover { color: #999; }
</style>
