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

  async function init() {
    const token = localStorage.getItem("access_token")
    if (!token) return
    try {
      const { accountsApi } = await import("../api/accounts")
      const userData = await accountsApi.getProfile()
      setUser(userData)
    } catch (e) {
      clearUser()
    }
  }

  return { user, isLoggedIn, setUser, clearUser, init }
})
