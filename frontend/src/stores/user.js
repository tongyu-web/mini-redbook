import { defineStore } from "pinia"
import { ref, computed } from "vue"

const ACCOUNTS_KEY = "mini_accounts"
const ACTIVE_KEY = "mini_active_account"

function loadAccounts() {
  try {
    return JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || "[]")
  } catch { return [] }
}

function saveAccounts(list) {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(list))
}

function getActiveId() {
  return localStorage.getItem(ACTIVE_KEY) || ""
}

function setActiveId(id) {
  localStorage.setItem(ACTIVE_KEY, id || "")
}

export const useUserStore = defineStore("user", () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const accounts = ref(loadAccounts())
  const activeAccountId = ref(getActiveId())

  // Computed: full list of saved accounts (for UI)
  const accountList = computed(() => accounts.value)

  function syncTokens(accessToken, refreshToken) {
    localStorage.setItem("access_token", accessToken || "")
    localStorage.setItem("refresh_token", refreshToken || "")
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
      access_token: accessToken,
      refresh_token: refreshToken,
    }
    // Remove old entry if exists, then add to front
    accounts.value = accounts.value.filter(a => a.id !== userData.id)
    accounts.value.unshift(entry)
    saveAccounts(accounts.value)

    // Set as active
    activeAccountId.value = userData.id
    setActiveId(userData.id)
    syncTokens(accessToken, refreshToken)
    setUser(userData)
  }

  function switchAccount(accountId) {
    const entry = accounts.value.find(a => a.id === accountId)
    if (!entry) return
    activeAccountId.value = accountId
    setActiveId(accountId)
    syncTokens(entry.access_token, entry.refresh_token)
    // Load profile from API (or reconstruct from saved data)
    user.value = {
      id: entry.id,
      username: entry.username,
      nickname: entry.nickname,
      avatar_url: entry.avatar_url,
    }
    isLoggedIn.value = true
  }

  function removeAccount(accountId) {
    accounts.value = accounts.value.filter(a => a.id !== accountId)
    saveAccounts(accounts.value)
    if (accounts.value.length === 0) {
      clearUser()
    } else if (activeAccountId.value === accountId) {
      // Switch to first available
      switchAccount(accounts.value[0].id)
    }
  }

  function clearUser() {
    user.value = null
    isLoggedIn.value = false
    accounts.value = []
    activeAccountId.value = ""
    localStorage.removeItem(ACCOUNTS_KEY)
    localStorage.removeItem(ACTIVE_KEY)
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
  }

  async function init() {
    const savedAccounts = loadAccounts()
    accounts.value = savedAccounts
    const activeId = getActiveId()
    activeAccountId.value = activeId

    if (!activeId || savedAccounts.length === 0) return

    const activeEntry = savedAccounts.find(a => a.id === activeId)
    if (!activeEntry) return

    // Restore tokens
    syncTokens(activeEntry.access_token, activeEntry.refresh_token)
    user.value = {
      id: activeEntry.id,
      username: activeEntry.username,
      nickname: activeEntry.nickname,
      avatar_url: activeEntry.avatar_url,
    }
    isLoggedIn.value = true

    // Try to refresh profile from API
    try {
      const { accountsApi } = await import("../api/accounts")
      const userData = await accountsApi.getProfile()
      // Update saved entry
      const idx = accounts.value.findIndex(a => a.id === userData.id)
      if (idx >= 0) {
        accounts.value[idx] = { ...accounts.value[idx], ...userData }
        saveAccounts(accounts.value)
      }
      setUser(userData)
    } catch (e) {
      // Token might be expired; try refresh
      // If refresh also fails, keep basic info from saved data
    }
  }

  return {
    user, isLoggedIn, accounts, activeAccountId, accountList,
    setUser, addAccount, switchAccount, removeAccount, clearUser, init,
  }
})