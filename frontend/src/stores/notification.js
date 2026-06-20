import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { messageApi } from "../api/messaging"

export const useNotificationStore = defineStore("notification", () => {
  const unreadCount = ref(0)
  const byType = ref({})
  const unreadMessageCount = ref(0)
  let pollTimer = null

  // Total unread including both notifications and private messages
  const totalUnread = computed(() => unreadCount.value + unreadMessageCount.value)

  async function fetchUnreadCount() {
    try {
      const data = await messageApi.getUnreadCount()
      unreadCount.value = data.unread_count || 0
      byType.value = data.by_type || {}
      unreadMessageCount.value = data.unread_message_count || 0
    } catch (e) {}
  }

  function startPolling() {
    fetchUnreadCount()
    pollTimer = setInterval(fetchUnreadCount, 10000)
  }

  function stopPolling() {
    if (pollTimer) clearInterval(pollTimer)
    pollTimer = null
  }

  function reset() {
    unreadCount.value = 0
    byType.value = {}
    unreadMessageCount.value = 0
  }

  return { unreadCount, byType, unreadMessageCount, totalUnread, fetchUnreadCount, startPolling, stopPolling, reset }
})

