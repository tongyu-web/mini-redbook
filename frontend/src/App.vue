<template>
  <router-view />
</template>

<script setup>
import { onMounted, onUnmounted } from "vue"
import { useNotificationStore } from "./stores/notification"
import { useUserStore } from "./stores/user"

const notificationStore = useNotificationStore()
const userStore = useUserStore()

onMounted(() => {
  userStore.init()
  notificationStore.startPolling()
})

onUnmounted(() => {
  notificationStore.stopPolling()
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }
a { color: #ff2442; text-decoration: none; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #ddd; border-radius: 3px; }
</style>
