﻿<template>
  <div class="topbar">
    <div class="topbar-inner">
      <!-- Search bar section -->
      <div class="search-section" ref="searchSection">
        <div class="search-input-wrapper">
          <button v-if="$route.path !== `/search`" class="quick-create-btn" @click="goCreate" title="快速发布">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
          <input
            v-model="searchText"
            class="search-input"
            placeholder="搜索或输入任何问题"
            @focus="onSearchFocus"
            @keyup.enter="doSearch"
            @input="onSearchInput"
          />
          <button class="search-submit-btn" @click="doSearch">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="20" height="20">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </button>
        </div>
        <!-- Search Dropdown -->
        <Transition name="search-drop">
          <div v-if="showDropdown" class="search-dropdown">
            <!-- Suggestions (when typing) -->
            <div v-if="searchText.trim() && suggestions.length" class="sd-section">
              <div class="sd-title">联想搜索</div>
              <div v-for="s in suggestions" :key="s.name" class="sd-item" @click="selectSuggestion(s.name)">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#999" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <span>{{ s.name }}</span>
              </div>
            </div>
            <!-- Hot tags (when empty) -->
            <div v-if="!searchText.trim() && hotTags.length" class="sd-section">
              <div class="sd-title">热门搜索</div>
              <div v-for="(tag, i) in hotTags" :key="tag.name" class="sd-item hot-item" @click="selectSuggestion(tag.name)">
                <span class="hot-rank" :class="'rank-' + (i + 1)">{{ i + 1 }}</span>
                <span class="hot-name">{{ tag.name }}</span>
                <span class="hot-count">{{ tag.hot_value || 0 }}</span>
              </div>
            </div>
            <!-- History (when empty, logged in) -->
            <div v-if="!searchText.trim() && userStore.isLoggedIn && localHistory.length" class="sd-section">
              <div class="sd-title history-title">
                <span>搜索历史</span>
                <button class="clear-history-btn" @click.stop="clearHistory">清空</button>
              </div>
              <div v-for="(h, i) in localHistory" :key="i" class="sd-item history-item" @click="selectSuggestion(h)">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#999" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span class="history-keyword">{{ h }}</span>
                <button class="remove-history-btn" @click.stop="removeHistoryItem(i)">&#10005;</button>
              </div>
            </div>
            <div v-if="!searchText.trim() && !hotTags.length && !localHistory.length" class="sd-empty">
              <span>暂无热门搜索</span>
            </div>
          </div>
        </Transition>
      </div>
      <!-- Category tabs section -->
      <div v-if="$route.path !== '/search'" class="tabs-section">
        <div class="category-tabs-wrapper">
          <div class="category-tabs" ref="tabsRef">
            <div
              v-for="cat in categories" :key="cat.key"
              class="cat-tab"
              :class="{ active: activeCat === cat.key }"
              @click="switchCategory(cat.key)"
            >
              {{ cat.label }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { searchApi } from "../api/search"

const router = useRouter()
const userStore = useUserStore()
const searchText = ref("")
const activeCat = ref("recommend")
const tabsRef = ref(null)
const searchSection = ref(null)
const showDropdown = ref(false)
const hotTags = ref([])
const suggestions = ref([])
const localHistory = ref([])

// --- Search history local cache ---
const HISTORY_KEY = "mini_search_history"

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]")
  } catch { return [] }
}

function saveHistory(list) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(list.slice(0, 20)))
}

function addToHistory(keyword) {
  let list = loadHistory()
  list = list.filter(k => k !== keyword)
  list.unshift(keyword)
  saveHistory(list)
  localHistory.value = list
}

function removeHistoryItem(index) {
  let list = loadHistory()
  list.splice(index, 1)
  saveHistory(list)
  localHistory.value = list
}

function clearHistory() {
  localStorage.removeItem(HISTORY_KEY)
  localHistory.value = []
  // Also clear server-side
  if (userStore.isLoggedIn) {
    searchApi.clearHistory().catch(() => {})
  }
}

// --- Hot tags ---
async function loadHotTags() {
  try {
    const tags = await searchApi.hotTags()
    hotTags.value = Array.isArray(tags) ? tags : []
  } catch { hotTags.value = [] }
}

// --- Suggest with debounce ---
let suggestTimer = null
function onSearchInput() {
  showDropdown.value = true
  if (suggestTimer) clearTimeout(suggestTimer)
  if (!searchText.value.trim()) {
    suggestions.value = []
    return
  }
  suggestTimer = setTimeout(async () => {
    try {
      const res = await searchApi.suggest(searchText.value.trim())
      suggestions.value = Array.isArray(res) ? res : []
    } catch { suggestions.value = [] }
  }, 300)
}

function onSearchFocus() {
  showDropdown.value = true
  if (!searchText.value.trim()) {
    suggestions.value = []
    loadHotTags()
  }
  localHistory.value = loadHistory()
}

function selectSuggestion(text) {
  searchText.value = text
  showDropdown.value = false
  addToHistory(text)
  router.push("/search?q=" + encodeURIComponent(text))
}

function doSearch() {
  const q = searchText.value.trim()
  if (!q) return
  showDropdown.value = false
  addToHistory(q)
  router.push("/search?q=" + encodeURIComponent(q))
}

// Close dropdown on outside click
function onDocClick(e) {
  if (searchSection.value && !searchSection.value.contains(e.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  loadHotTags()
  document.addEventListener("click", onDocClick)
  localHistory.value = loadHistory()
})

onUnmounted(() => {
  document.removeEventListener("click", onDocClick)
  if (suggestTimer) clearTimeout(suggestTimer)
})

const categories = [
  { key: "recommend", label: "推荐" },
  { key: "beauty", label: "美妆" },
  { key: "travel", label: "旅行" },
  { key: "food", label: "美食" },
  { key: "fashion", label: "穿搭" },
  { key: "fitness", label: "健身" },
  { key: "tech", label: "数码" },
  { key: "study", label: "学习" },
  { key: "art", label: "艺术" },
  { key: "life", label: "生活" },
  { key: "other", label: "其他" },
]

const emit = defineEmits(["search", "categoryChange"])

function goCreate() {
  if (!userStore.isLoggedIn) { router.push("/login"); return }
  router.push("/create")
}

function switchCategory(key) {
  activeCat.value = key
  emit("categoryChange", key)
}
</script>

<style scoped>
.topbar {
  position: fixed;
  top: 0;
  left: 220px;
  right: 0;
  height: 120px;
  background: #fff;
  z-index: 100;
  border-bottom: 1px solid #f0f0f0;
}
.topbar-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 14px 24px 0;
}

/* Search section */
.search-section {
  padding-bottom: 12px;
}
.search-input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 0 4px 0 8px;
  height: 44px;
  gap: 6px;
  border: 1px solid transparent;
  transition: border-color 0.2s;
}
.search-input-wrapper:focus-within {
  border-color: #ff2442;
}
.quick-create-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #555;
  cursor: pointer;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all 0.15s;
}
.quick-create-btn:hover {
  background: #eee;
  color: #ff2442;
}
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
  color: #333;
}
.search-input::placeholder { color: #bbb; }
.search-submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all 0.15s;
}
.search-submit-btn:hover {
  background: #eee;
  color: #ff2442;
}

/* Tabs section with divider */
.tabs-section {
  border-top: 1px solid #f0f0f0;
  padding-top: 8px;
  display: flex;
  justify-content: center;
}
.category-tabs-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.category-tabs-wrapper::-webkit-scrollbar { display: none; }
.category-tabs {
  display: flex;
  gap: 0;
  padding: 2px 0;
  justify-content: center;
}
.cat-tab {
  padding: 6px 16px;
  font-size: 14px;
  color: #888;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
  font-weight: 400;
}
.cat-tab:hover {
  color: #555;
}
.cat-tab.active {
  color: #ff2442;
  font-weight: 700;
}

/* Search dropdown */
.search-section { position: relative; }
.search-dropdown {
  position: absolute;
  top: calc(100% + 0px);
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  padding: 8px 0;
  z-index: 500;
  max-height: 420px;
  overflow-y: auto;
}
.sd-section { padding: 4px 0; }
.sd-section + .sd-section { border-top: 1px solid #f5f5f5; }
.sd-title {
  font-size: 12px; color: #999; font-weight: 600;
  padding: 6px 16px 4px;
}
.sd-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 16px; cursor: pointer; font-size: 14px; color: #333;
  transition: background 0.12s;
}
.sd-item:hover { background: #f8f8f8; }
.sd-item span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.hot-rank {
  width: 20px; height: 20px; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; flex-shrink: 0;
  background: #f0f0f0; color: #999;
}
.hot-rank.rank-1 { background: #ff2442; color: white; }
.hot-rank.rank-2 { background: #ff6b81; color: white; }
.hot-rank.rank-3 { background: #ff9aa2; color: white; }
.hot-name { flex: 1; }
.hot-count { font-size: 11px; color: #ccc; }

.history-title { display: flex; justify-content: space-between; align-items: center; }
.clear-history-btn { background: none; border: none; color: #999; font-size: 12px; cursor: pointer; padding: 0; }
.clear-history-btn:hover { color: #ff2442; }
.history-keyword { flex: 1; }
.remove-history-btn { background: none; border: none; color: #ccc; cursor: pointer; font-size: 12px; padding: 2px; }
.remove-history-btn:hover { color: #ff2442; }

.sd-empty { text-align: center; padding: 24px 0; color: #ccc; font-size: 13px; }

.search-drop-enter-active, .search-drop-leave-active { transition: opacity 0.15s, transform 0.15s; }
.search-drop-enter-from, .search-drop-leave-to { opacity: 0; transform: translateY(-4px); }
</style>