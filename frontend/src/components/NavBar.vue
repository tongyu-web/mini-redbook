<template>
  <div class="navbar">
    <div class="tab" :class="{ active: $route.path === '/' }" @click="$router.push('/')">
      <span class="tab-icon">🏠</span>
      <span class="label">首页</span>
    </div>
    <div class="tab" :class="{ active: $route.path === '/search' }" @click="$router.push('/search')">
      <span class="tab-icon">🔍</span>
      <span class="label">发现</span>
    </div>
    <div class="tab" @click="goCreate">
      <span class="create-btn">+</span>
    </div>
    <div class="tab" :class="{ active: $route.path.startsWith('/message') }" @click="$router.push('/message')">
      <span class="tab-icon">💬</span>
      <span v-if="notificationStore.unreadCount > 0" class="badge">{{ notificationStore.unreadCount > 99 ? "99+" : notificationStore.unreadCount }}</span>
      <span class="label">消息</span>
    </div>
    <div class="tab" :class="{ active: $route.path.startsWith('/user') }" @click="goProfile">
      <span class="tab-icon">👤</span>
      <span class="label">我的</span>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { useNotificationStore } from "../stores/notification"

const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

function goCreate() {
  if (!userStore.isLoggedIn) { router.push("/login"); return }
  router.push("/create")
}
function goProfile() {
  if (!userStore.isLoggedIn) { router.push("/login"); return }
  router.push("/user/" + userStore.user.id)
}
</script>

<style scoped>
.navbar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; background: white; border-top: 1px solid #eee; padding: 6px 0; z-index: 100; justify-content: space-around; }
.tab { display: flex; flex-direction: column; align-items: center; cursor: pointer; position: relative; font-size: 12px; color: #999; padding: 4px 16px; }
.tab.active { color: #ff2442; }
.tab span { font-size: 20px; }
.label { font-size: 10px; margin-top: 2px; }
.create-btn { background: #ff2442; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-top: -8px; }
.badge { position: absolute; top: 0; right: 8px; background: #ff2442; color: white; font-size: 10px; border-radius: 10px; padding: 1px 5px; min-width: 16px; text-align: center; }
</style>
