import { defineStore } from "pinia"
import { ref } from "vue"
import { messageApi } from "../api/messaging"

export const useNotificationStore = defineStore("notification", () => {
  const unreadCount = ref(0)
  const byType = ref({})
  let pollTimer = null

  async function fetchUnreadCount() {
    try {
      const data = await messageApi.getUnreadCount()
      unreadCount.value = data.unread_count || 0
      byType.value = data.by_type || {}
    } catch (e) {}
  }

  function startPolling() {
    fetchUnreadCount()
    pollTimer = setInterval(fetchUnreadCount, 30000)
  }

  function stopPolling() {
    if (pollTimer) clearInterval(pollTimer)
    pollTimer = null
  }

  function reset() {
    unreadCount.value = 0
    byType.value = {}
  }

  return { unreadCount, byType, fetchUnreadCount, startPolling, stopPolling, reset }
})
