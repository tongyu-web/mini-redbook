<template>
  <div class="app-layout">
    <template v-if="!isAuthPage">
      <Sidebar />
      <div class="main-area">
        <TopBar v-if="showTopBar" @categoryChange="onCategoryChange" />
        <div class="content-area" :class="{ 'with-topbar': showTopBar }">
          <router-view :category="currentCategory" />
        </div>
      </div>
    </template>
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { onMounted, onUnmounted } from "vue"
import { useRoute } from "vue-router"
import { useNotificationStore } from "./stores/notification"
import { useUserStore } from "./stores/user"
import Sidebar from "./components/Sidebar.vue"
import TopBar from "./components/TopBar.vue"

const route = useRoute()
const notificationStore = useNotificationStore()
const userStore = useUserStore()
const currentCategory = ref("recommend")

const authRoutes = ["Login", "Register"]
const isAuthPage = computed(() => authRoutes.includes(route.name))

const topbarRoutes = ["Home", "NoteDetail", "Search"]
const showTopBar = computed(() => topbarRoutes.includes(route.name))

onMounted(() => {
  userStore.init()
  notificationStore.startPolling()
})

onUnmounted(() => {
  notificationStore.stopPolling()
})

function onCategoryChange(key) {
  currentCategory.value = key
}
</script>

<style>
:root {
  --primary: #ff2442;
  --primary-light: #fff0f0;
  --bg: #f5f5f5;
  --bg-white: #fff;
  --text: #333;
  --text-secondary: #999;
  --border: #f0f0f0;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 24px;
  --sidebar-width: 220px;
  --topbar-height: 96px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: #fff;
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}
a { color: var(--primary); text-decoration: none; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: #ddd; border-radius: 2px; }
.app-layout { display: flex; min-height: 100vh; }
.main-area {
  margin-left: var(--sidebar-width);
  flex: 1;
  display: flex;
  flex-direction: column;
}
.content-area {
  flex: 1;
  background: #fff;
}
.content-area.with-topbar {
  margin-top: var(--topbar-height);
}
</style>