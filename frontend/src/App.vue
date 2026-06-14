<template>
  <div class="app-layout">
    <Sidebar />
    <div class="main-area">
      <TopBar @categoryChange="onCategoryChange" />
      <div class="content-area">
        <router-view :category="currentCategory" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { onMounted, onUnmounted } from "vue"
import { useNotificationStore } from "./stores/notification"
import { useUserStore } from "./stores/user"
import Sidebar from "./components/Sidebar.vue"
import TopBar from "./components/TopBar.vue"

const notificationStore = useNotificationStore()
const userStore = useUserStore()
const currentCategory = ref("recommend")

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
  --topbar-height: 120px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
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
  margin-top: var(--topbar-height);
  flex: 1;
  background: var(--bg);
}
</style>
