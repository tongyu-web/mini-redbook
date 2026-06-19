﻿<template>
  <div class="topbar">
    <div class="topbar-inner">
      <!-- Search bar section -->
            <div class="search-section" ref="searchSection">
        <div class="search-card">
          <div class="search-card-top">
            <input
              v-model="searchText"
              class="search-card-input"
              placeholder="搜索感兴趣的内容"
              @focus="onSearchFocus"
              @keyup.enter="doSearch"
              @input="onSearchInput"
            />
          </div>
          <div class="search-card-bottom">
            <button class="sc-create-btn" @click="goCreate" title="快速发布">
              <svg viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2.5" width="20" height="20">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <span class="sc-hint">发现精彩内容</span>
            <button class="sc-search-btn" @click="doSearch">
              <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" width="20" height="20">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </button>
          </div>
        </div>
        <!-- Search Dropdown -->
        <Transition name="search-drop">
          <div v-if="showDropdown" class="search-dropdown">
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
  
  
  
  
  height: auto;
  background: #fff;
  
  
}
.topbar-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 10px 24px 0;
}

/* Search section */
.search-section {
  padding-bottom: 6px;
}
.search-input-wrapper {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 16px;
  padding: 0 4px 0 8px;
  height: 50px;
  gap: 6px;
  
  
}
.search-input-wrapper:focus-within {

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
  
  padding-top: 4px;
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

.search-section { position: relative; padding: 0 24px; max-width: 800px; margin: 0 auto; }

.search-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 18px;
  padding: 12px 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}
.search-card:hover, .search-card:focus-within {
  box-shadow: 0 6px 20px rgba(0,0,0,0.07);
}

.search-card-top { margin-bottom: 8px; }
.search-card-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 16px;
  outline: none;
  color: #333;
  line-height: 1.6;
}
.search-card-input::placeholder { color: #ccc; }

.search-card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sc-create-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px dashed #ddd;
  background: transparent;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.15s;
}
.sc-create-btn:hover { border-color: #ff2442; }
.sc-create-btn:hover svg { stroke: #ff2442; }

.sc-hint { font-size: 12px; color: #ccc; }

.sc-search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border: none;
  background: #222;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.2s, transform 0.15s;
}
.sc-search-btn:hover { background: #ff2442; transform: scale(1.05); }
.dd-remove {
  background: none; border: none; color: #ccc; cursor: pointer; font-size: 14px; padding: 2px 4px; border-radius: 4px; line-height: 1;
}
.dd-remove:hover { color: #ff2442; background: #fff0f0; }
.remove-history-btn { background: none; border: none; color: #ccc; cursor: pointer; font-size: 12px; padding: 2px; }
.remove-history-btn:hover { color: #ff2442; }

.sd-empty { text-align: center; padding: 24px 0; color: #ccc; font-size: 13px; }

.search-drop-enter-active, .search-drop-leave-active { transition: opacity 0.15s, transform 0.15s; }
.search-drop-enter-from, .search-drop-leave-to { opacity: 0; transform: translateY(-4px); }
</style>