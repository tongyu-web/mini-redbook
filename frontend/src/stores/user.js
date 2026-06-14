import { defineStore } from "pinia"
import { ref } from "vue"

export const useUserStore = defineStore("user", () => {
  const user = ref(null)
  const isLoggedIn = ref(false)

  function setUser(userData) {
    user.value = userData
    isLoggedIn.value = true
  }

  function clearUser() {
    user.value = null
    isLoggedIn.value = false
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
  }

  return { user, isLoggedIn, setUser, clearUser }
})
