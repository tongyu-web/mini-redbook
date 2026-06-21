<template>
  <div class="search-page">
    <!-- Tabs -->
    <div class="sp-tabs">
      <div v-for="t in tabs" :key="t.key" class="sp-tab" :class="{ active: activeTab === t.key }" @click="switchTab(t.key)">
        {{ t.label }}
      </div>
    </div>
    <!-- Results -->
    <div class="sp-results" v-if="query">
      <div v-if="activeTab === 'note'" class="note-waterfall">
        <div v-for="n in results" :key="n.id" class="sc-card" @click="noteDetailStore.open(n.id)">
          <div class="sc-media">
            <img v-if="n.cover_img" :src="n.cover_img" :alt="n.title" />
            <div v-else class="sc-placeholder">{{ n.title?.[0] || "R" }}</div>
          </div>
          <div class="sc-body">
            <h3 class="sc-title">{{ n.title }}</h3>
            <div class="sc-footer">
              <div class="sc-author">
                <img v-if="n.user_avatar" :src="n.user_avatar" class="sc-avatar" />
                <div v-else class="sc-avatar sc-avatar-placeholder">{{ n.user_nickname?.[0] || "?" }}</div>
                <span class="sc-name">{{ n.user_nickname }}</span>
              </div>
              <div class="sc-likes">
                <svg viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" width="14" height="14">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
                <span>{{ n.like_count || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="!results.length && loaded" class="no-results">未找到相关笔记</div>
      </div>
      <div v-if="activeTab === 'user'" class="user-results">
        <div v-for="u in users" :key="u.id" class="ur-item" @click="$router.push('/user/' + u.id)">
          <img :src="u.avatar_url || defaultAvatar" class="ur-avatar" />
          <div class="ur-info">
            <span class="ur-name">{{ u.nickname }}</span>
            <span class="ur-bio">{{ u.bio || "这个人很懒，什么都没写" }}</span>
          </div>
        </div>
        <div v-if="!users.length && loaded" class="no-results">未找到相关用户</div>
      </div>
      <div v-if="activeTab === 'tag'" class="tag-results">
        <div v-for="t in tags" :key="t.name" class="tr-item" @click="searchTag(t.name)">
          <span class="tr-name"># {{ t.name }}</span>
          <span class="tr-count">{{ t.note_count || 0 }} 篇笔记</span>
        </div>
        <div v-if="!tags.length && loaded" class="no-results">未找到相关话题</div>
      </div>
    </div>
    <!-- No query state -->
    <div v-if="!query" class="sp-empty">
      <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#ddd" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <p>输入关键词搜索笔记、用户和话题</p>
    </div>
    <!-- Loading -->
    <div v-if="loading" class="sp-loading"><div class="loader"></div></div>
  </div>
  <NoteDetail />
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import NoteDetail from "./NoteDetail.vue"
import { searchApi } from "../api/search"
import { useNoteDetailStore } from "../stores/noteDetail"

const props = defineProps({
  category: { type: String, default: "recommend" }
})

const route = useRoute()
const router = useRouter()
const noteDetailStore = useNoteDetailStore()

const query = ref("")
const activeTab = ref("note")
const results = ref([])
const users = ref([])
const tags = ref([])
const loading = ref(false)
const loaded = ref(false)
const defaultAvatar = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ddd'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E"

const tabs = [
  { key: "note", label: "笔记" },
  { key: "user", label: "用户" },
  { key: "tag", label: "话题" },
]

function switchTab(key) {
  activeTab.value = key
  if (query.value) doSearch()
}

async function doSearch() {
  const q = query.value.trim()
  if (!q) return
  loading.value = true
  loaded.value = false
  try {
    if (activeTab.value === "note") {
      const res = await searchApi.search({ q, type: "note", page: 1 })
      results.value = res?.results || []
    } else if (activeTab.value === "user") {
      const res = await searchApi.search({ q, type: "user", page: 1 })
      users.value = res?.results || []
    } else if (activeTab.value === "tag") {
      const res = await searchApi.search({ q, type: "tag", page: 1 })
      tags.value = res?.results || []
    }
  } catch { results.value = []; users.value = []; tags.value = [] }
  finally { loading.value = false; loaded.value = true }
}

function searchTag(name) {
  query.value = name
  activeTab.value = "note"
  doSearch()
}

// Load from URL param on mount
onMounted(() => {
  const q = route.query.q
  if (q) {
    query.value = q
    doSearch()
  }
})

watch(() => route.query.q, (q) => {
  if (q && q !== query.value) {
    query.value = q
    doSearch()
  }
})
</script>

<style scoped>
.search-page {
  max-width: 800px; margin: 0 auto; padding: 20px 24px;
}
/* Tabs */
.sp-tabs { display: flex; gap: 0; border-bottom: 1px solid #f0f0f0; margin-bottom: 16px; }
.sp-tab {
  padding: 10px 24px; font-size: 14px; color: #888; cursor: pointer;
  border-bottom: 2px solid transparent; transition: all 0.15s;
}
.sp-tab:hover { color: #555; }
.sp-tab.active { color: #ff2442; border-bottom-color: #ff2442; font-weight: 600; }

/* Note waterfall */
.note-waterfall {
  column-count: 3;
  column-gap: 14px;
}
.sc-card {
  break-inside: avoid;
  margin-bottom: 14px;
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid #f0f0f0;
}
.sc-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
.sc-media { position: relative; overflow: hidden; background: #f0f0f0; }
.sc-media img { width: 100%; display: block; }
.sc-placeholder {
  width: 100%; aspect-ratio: 3/4;
  display: flex; align-items: center; justify-content: center;
  font-size: 2em; color: white;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}
.sc-body { padding: 10px 12px 12px; }
.sc-title {
  font-size: 13px; font-weight: 600; line-height: 1.4;
  margin: 0 0 6px; color: #222;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.sc-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding-top: 6px; border-top: 1px solid #f5f5f5;
}
.sc-author { display: flex; align-items: center; gap: 5px; min-width: 0; }
.sc-avatar { width: 20px; height: 20px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.sc-avatar-placeholder {
  display: flex; align-items: center; justify-content: center;
  background: #ff2442; color: white; font-size: 9px; font-weight: 600;
}
.sc-name { font-size: 11px; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sc-likes { display: flex; align-items: center; gap: 3px; font-size: 11px; color: #999; flex-shrink: 0; }
/* User results */
.ur-item { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f8f8f8; cursor: pointer; }
.ur-item:hover { background: #fafafa; margin: 0 -12px; padding: 12px; border-radius: 8px; }
.ur-avatar { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; }
.ur-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.ur-name { font-size: 14px; font-weight: 600; color: #333; }
.ur-bio { font-size: 12px; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Tag results */
.tr-item { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f8f8f8; cursor: pointer; }
.tr-item:hover { background: #fafafa; margin: 0 -12px; padding: 12px; border-radius: 8px; }
.tr-name { flex: 1; font-size: 15px; color: #ff2442; font-weight: 600; }
.tr-count { font-size: 12px; color: #bbb; }

.no-results { text-align: center; padding: 60px 0; color: #ccc; font-size: 14px; }
.sp-empty { text-align: center; padding: 80px 0; color: #ccc; }
.sp-empty p { margin-top: 12px; font-size: 14px; }
.sp-loading { text-align: center; padding: 60px 0; }
.loader { display: inline-block; width: 28px; height: 28px; border: 3px solid #f0f0f0; border-top-color: #ff2442; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
