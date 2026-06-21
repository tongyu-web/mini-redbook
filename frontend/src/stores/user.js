import { defineStore } from "pinia"
import { ref, computed } from "vue"

const ACCOUNTS_KEY = "mini_accounts"

function loadAccounts() {
  try {
    return JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || "[]")
  } catch { return [] }
}

function saveAccounts(list) {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(list))
}

export const useUserStore = defineStore("user", () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const accounts = ref([])       // All saved accounts (shared via localStorage)
  const activeAccountId = ref("")

  const accountList = computed(() => accounts.value)

  function syncTokens(accessToken, refreshToken) {
    // Use sessionStorage — isolated per browser tab
    if (accessToken) sessionStorage.setItem("access_token", accessToken)
    else sessionStorage.removeItem("access_token")
    if (refreshToken) sessionStorage.setItem("refresh_token", refreshToken)
    else sessionStorage.removeItem("refresh_token")
  }

  function setUser(userData) {
    user.value = userData
    isLoggedIn.value = true
  }

  function addAccount(userData, accessToken, refreshToken) {
    const entry = {
      id: userData.id,
      username: userData.username,
      nickname: userData.nickname || userData.username,
      avatar_url: userData.avatar_url || "",
      privacy: userData.privacy ?? 0,
      access_token: accessToken,
      refresh_token: refreshToken,
    }
    accounts.value = accounts.value.filter(a => a.id !== userData.id)
    accounts.value.unshift(entry)
    saveAccounts(accounts.value)

    activeAccountId.value = userData.id
    syncTokens(accessToken, refreshToken)
    setUser(userData)
  }

  function switchAccount(accountId) {
    const entry = accounts.value.find(a => a.id === accountId)
    if (!entry) return
    activeAccountId.value = accountId
    syncTokens(entry.access_token, entry.refresh_token)
    user.value = {
      id: entry.id,
      username: entry.username,
      nickname: entry.nickname,
      avatar_url: entry.avatar_url,
      privacy: entry.privacy,
    }
    isLoggedIn.value = true
  }

  function removeAccount(accountId) {
    accounts.value = accounts.value.filter(a => a.id !== accountId)
    saveAccounts(accounts.value)
    if (accountId === activeAccountId.value || activeAccountId.value === accountId) {
      // Current tab's account was removed
      if (accounts.value.length > 0) {
        switchAccount(accounts.value[0].id)
      } else {
        clearUser()
      }
    }
  }

  function clearUser() {
    user.value = null
    isLoggedIn.value = false
    activeAccountId.value = ""
    syncTokens(null, null)
    // Don't clear localStorage accounts — other tabs might use them
  }

  async function init() {
    // Load shared account list from localStorage
    accounts.value = loadAccounts()

    // Check if THIS TAB has a session
    const sessionToken = sessionStorage.getItem("access_token")
    if (!sessionToken) {
      // This is a fresh tab — stay logged out
      return
    }

    // Restore from session
    try {
      const { accountsApi } = await import("../api/accounts")
      const userData = await accountsApi.getProfile()
      // Sync with shared account list
      const idx = accounts.value.findIndex(a => a.id === userData.id)
      if (idx >= 0) {
        activeAccountId.value = userData.id
        accounts.value[idx] = { ...accounts.value[idx], ...userData }
        saveAccounts(accounts.value)
      } else {
        // Token exists but account not in list — add it
        activeAccountId.value = userData.id
      }
      setUser(userData)
    } catch (e) {
      // Token expired — clear session
      syncTokens(null, null)
    }
  }

  return {
    user, isLoggedIn, accounts, activeAccountId, accountList,
    setUser, addAccount, switchAccount, removeAccount, clearUser, init,
  }
})
