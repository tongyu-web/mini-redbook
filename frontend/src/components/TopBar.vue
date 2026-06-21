<template>
  <div class="topbar">
    <div class="topbar-inner">
      <!-- Search bar section -->
      <div
        class="search-section"
        :class="{ 'has-dropdown': showDropdown }"
        ref="searchSection"
      >
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
            <!-- Suggestions (when user is typing) -->
            <template v-if="searchText.trim() && suggestions.length">
              <div class="sd-section">
                <div class="sd-title-row">
                  <span class="sd-title">搜索建议</span>
                </div>
                <div class="sd-tags">
                  <span
                    v-for="s in suggestions"
                    :key="s.name"
                    class="sd-tag"
                    @click="selectSuggestion(s.name)"
                  >
                    {{ s.name }}
                  </span>
                </div>
              </div>
            </template>

            <!-- History section -->
            <template v-if="localHistory.length">
              <div class="sd-section">
                <div class="sd-title-row">
                  <span class="sd-title">历史记录</span>
                  <button class="sd-clear-btn" @click="clearHistory" title="清空历史记录">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="2" width="16" height="16">
                      <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </div>
                <div class="sd-tags">
                  <span
                    v-for="(item, index) in localHistory"
                    :key="index"
                    class="sd-tag"
                    @click="selectSuggestion(item)"
                  >
                    {{ item }}
                  </span>
                </div>
              </div>
            </template>

            <!-- Trending / Hot search section -->
            <template v-if="hotTerms.length">
              <div class="sd-section">
                <div class="sd-title-row">
                  <span class="sd-title">猜你想搜</span>
                </div>
                <div class="sd-tags">
                  <span
                    v-for="term in hotTerms"
                    :key="term.keyword"
                    class="sd-tag"
                    @click="selectSuggestion(term.keyword)"
                  >
                    {{ term.keyword }}
                  </span>
                </div>
              </div>
            </template>

            <!-- Empty state -->
            <div v-if="!localHistory.length && !hotTerms.length && !suggestions.length" class="sd-empty">
              <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="#ddd" stroke-width="1.5">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <p>搜索你感兴趣的内容</p>
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
import { ref, watch, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { searchApi } from "../api/search"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const searchText = ref("")
const showDropdown = ref(false)
const suggestions = ref([])
const localHistory = ref([])
const hotTerms = ref([])
const searchSection = ref(null)
const activeCat = ref("recommend")

function onSearchFocus() {
  showDropdown.value = true
  loadHotTerms()
}

function onSearchInput() {
  const t = searchText.value.trim()
  if (t.length >= 1) {
    loadSuggestions(t)
  } else {
    suggestions.value = []
  }
}

async function loadSuggestions(q) {
  try {
    const res = await searchApi.suggest({ q })
    if (res?.results) suggestions.value = res.results
  } catch {
    suggestions.value = []
  }
}

async function loadHotTerms() {
  if (hotTerms.value.length) return
  try {
    const res = await searchApi.hot()
    if (res?.results) hotTerms.value = res.results
  } catch {
    hotTerms.value = []
  }
}

function loadHistory() {
  try {
    const stored = localStorage.getItem("search_history")
    localHistory.value = stored ? JSON.parse(stored) : []
  } catch {
    localHistory.value = []
  }
}

function saveHistory(q) {
  if (!q.trim()) return
  let h = [q.trim(), ...localHistory.value.filter(i => i !== q.trim())]
  if (h.length > 10) h = h.slice(0, 10)
  localHistory.value = h
  localStorage.setItem("search_history", JSON.stringify(h))
}

function clearHistory() {
  localHistory.value = []
  localStorage.removeItem("search_history")
}

function selectSuggestion(text) {
  searchText.value = text
  showDropdown.value = false
  saveHistory(text)
  router.push({ path: "/search", query: { q: text } })
  emit("search", text)
}

function doSearch() {
  const t = searchText.value.trim()
  if (!t) return
  showDropdown.value = false
  saveHistory(t)
  router.push({ path: "/search", query: { q: t } })
  emit("search", t)
}

function onDocClick(e) {
  if (searchSection.value && !searchSection.value.contains(e.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener("click", onDocClick)
  loadHistory()
})

onUnmounted(() => {
  document.removeEventListener("click", onDocClick)
})

const categories = [
  { key: "recommend", label: "推荐" },
  { key: "fashion", label: "穿搭" },
  { key: "beauty", label: "美妆" },
  { key: "food", label: "美食" },
  { key: "travel", label: "旅行" },
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

/* ===== Unified search container =====
   Default state: standalone rounded card with shadow.
   .has-dropdown state: top corners round, bottom flat, no bottom border,
   letting the dropdown seamlessly extend below. */
.search-section {
  position: relative;
  max-width: 900px;
  margin: 0 auto;
  padding: 0;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 18px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.search-section:focus-within {
  box-shadow: 0 6px 20px rgba(0,0,0,0.07);
}
.search-section.has-dropdown {
  border-radius: 18px 18px 0 0;
  border-bottom: none;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.04);
}

/* Search bar inner */
.search-card {
  padding: 16px 24px;
}

.search-card-top { margin-bottom: 10px; }
.search-card-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 17px;
  outline: none;
  color: #333;
  line-height: 1.8;
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

/* ===== Search Dropdown =====
   Background (#fff) matches the search-section/search-card exactly.
   Sits flush below search-section when visible — one seamless panel. */
.search-dropdown {
  position: absolute;
  top: 100%;
  left: -1px;
  right: -1px;
  background: #fff;
  border-radius: 0 0 18px 18px;
  border: 1px solid #e8e8e8;
  border-top: none;
  padding: 6px 0 20px;
  z-index: 500;
  max-height: 480px;
  overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* ===== Section title + tags =====
   Two independent modules: 历史记录 / 猜你想搜.
   Separated by generous whitespace — no dividing lines. */
.sd-section {
  padding: 6px 24px;
}

/* Large whitespace between sections */
.sd-section + .sd-section {
  margin-top: 28px;
  padding-top: 0;
}

/* Title row */
.sd-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.sd-title {
  font-size: 13px;
  font-weight: 600;
  color: #888;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* Clear button */
.sd-clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s;
}
.sd-clear-btn:hover { background: #f5f5f5; }
.sd-clear-btn:hover svg { stroke: #999; }

/* Tag flow */
.sd-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Capsule tag — same border color as search-section for harmony */
.sd-tag {
  display: inline-block;
  padding: 6px 14px;
  font-size: 13px;
  color: #999;
  border: 1px solid #e8e8e8;
  border-radius: 999px;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s;
  line-height: 1.4;
  user-select: none;
}
.sd-tag:hover {
  color: #666;
  border-color: #ccc;
  background: #fafafa;
}

/* Empty state */
.sd-empty {
  text-align: center;
  padding: 32px 0 20px;
  color: #ddd;
}
.sd-empty p {
  margin: 8px 0 0;
  font-size: 13px;
  color: #ccc;
}

/* Transition */
.search-drop-enter-active, .search-drop-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.search-drop-enter-from, .search-drop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Category tabs */
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
  padding: 8px 18px;
  font-size: 14px;
  color: #888;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
  font-weight: 400;
}
.cat-tab:hover { color: #555; }
.cat-tab.active {
  color: #ff2442;
  font-weight: 700;
}
</style>
