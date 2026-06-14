import { defineStore } from "pinia"
import { ref } from "vue"

export const useNotificationStore = defineStore("notification", () => {
  const count = ref(0)
  const list = ref([])

  function increment() {
    count.value++
  }

  function reset() {
    count.value = 0
  }

  function setNotifications(notifications) {
    list.value = notifications
    count.value = notifications.length
  }

  return { count, list, increment, reset, setNotifications }
})
