<template>
  <div class="topbar">
    <div class="topbar-inner">
      <!-- Search bar section -->
      <div class="search-section">
        <div class="search-input-wrapper">
          <button class="quick-create-btn" @click="goCreate" title="快速发布">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
          <input
            v-model="searchText"
            class="search-input"
            placeholder="搜索或输入任何问题"
            @keyup.enter="doSearch"
          />
          <button class="search-submit-btn" @click="doSearch">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="20" height="20">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </button>
        </div>
      </div>
      <!-- Category tabs section -->
      <div class="tabs-section">
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
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"

const router = useRouter()
const userStore = useUserStore()
const searchText = ref("")
const activeCat = ref("recommend")
const tabsRef = ref(null)

const categories = [
  { key: "recommend", label: "推荐" },
  { key: "dress", label: "穿搭" },
  { key: "food", label: "美食" },
  { key: "makeup", label: "化妆" },
  { key: "movie", label: "影视" },
  { key: "emotion", label: "情感" },
  { key: "home", label: "家居" },
  { key: "game", label: "游戏" },
  { key: "travel", label: "旅行" },
  { key: "video", label: "视频" },
]

const emit = defineEmits(["search", "categoryChange"])

function goCreate() {
  if (!userStore.isLoggedIn) { router.push("/login"); return }
  router.push("/create")
}

function doSearch() {
  if (searchText.value.trim()) {
    router.push("/search?q=" + encodeURIComponent(searchText.value.trim()))
  }
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
</style>