<template>
  <div class="topbar">
    <div class="topbar-inner">
      <div class="search-box">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="searchText"
            class="search-input"
            placeholder="搜索你感兴趣的内容..."
            @keyup.enter="doSearch"
          />
          <div class="ai-btn" @click="openAI">AI</div>
        </div>
      </div>
      <div class="category-tabs-wrapper">
        <div class="category-tabs" ref="tabsRef">
          <div
            v-for="cat in categories" :key="cat.key"
            class="cat-tab"
            :class="{ active: activeCat === cat.key }"
            @click="switchCategory(cat.key)"
          >
            <span v-if="cat.icon" class="cat-icon">{{ cat.icon }}</span>
            <span>{{ cat.label }}</span>
            <div v-if="cat.key === 'recommend'" class="active-indicator"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const searchText = ref("")
const activeCat = ref("recommend")
const tabsRef = ref(null)

const categories = [
  { key: "recommend", label: "推荐" },
  { key: "latest", label: "最新" },
  { key: "tech", label: "科技" },
  { key: "fashion", label: "时尚" },
  { key: "food", label: "美食" },
  { key: "travel", label: "旅行" },
  { key: "sports", label: "体育" },
]

const emit = defineEmits(["search", "categoryChange"])

function doSearch() {
  if (searchText.value.trim()) {
    router.push("/search?q=" + encodeURIComponent(searchText.value.trim()))
  }
}
function openAI() {
  searchText.value = ""
  router.push("/search?ai=1")
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
.topbar-inner { max-width: 1000px; margin: 0 auto; padding: 16px 24px 0; }
.search-box { margin-bottom: 12px; }
.search-input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 0 16px;
  height: 44px;
  gap: 10px;
}
.search-icon { width: 18px; height: 18px; flex-shrink: 0; }
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
  color: #333;
}
.search-input::placeholder { color: #bbb; }
.ai-btn {
  background: #fff;
  border: 1px solid #ff2442;
  color: #ff2442;
  border-radius: 14px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.ai-btn:hover { background: #fff0f0; }
.category-tabs-wrapper { overflow-x: auto; }
.category-tabs {
  display: flex;
  gap: 4px;
  padding-bottom: 4px;
}
.cat-tab {
  padding: 6px 16px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  white-space: nowrap;
  border-radius: 8px;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 4px;
  position: relative;
}
.cat-tab:hover { background: #f5f5f5; }
.cat-tab.active { color: #ff2442; font-weight: 600; }
.cat-icon { font-size: 16px; }
.active-indicator {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: #ff2442;
  border-radius: 2px;
}
</style>
