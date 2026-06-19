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
      <div v-if="activeTab === 'note'" class="note-results">
        <div v-for="n in results" :key="n.id" class="nr-item" @click="noteDetailStore.open(n.id)">
          <img :src="n.cover_img" v-if="n.cover_img" class="nr-cover" />
          <div class="nr-info" :class="{ 'no-cover': !n.cover_img }">
            <h4 class="nr-title">{{ n.title }}</h4>
            <p class="nr-desc">{{ n.content }}</p>
            <div class="nr-meta">
              <span class="nr-user">{{ n.user_nickname }}</span>
              <span class="nr-stats">{{ n.like_count || 0 }} 赞 · {{ n.comment_count || 0 }} 评论</span>
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
import { searchApi } from "../api/search"
import { useNoteDetailStore } from "../stores/noteDetail"

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

/* Note results */
.nr-item { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f8f8f8; cursor: pointer; transition: background 0.12s; }
.nr-item:hover { background: #fafafa; margin: 0 -12px; padding: 12px; border-radius: 8px; }
.nr-cover { width: 100px; height: 100px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.nr-info { flex: 1; min-width: 0; }
.nr-info.no-cover { }
.nr-title { margin: 0 0 4px; font-size: 15px; color: #222; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nr-desc { margin: 0 0 8px; font-size: 13px; color: #777; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.nr-meta { display: flex; gap: 12px; font-size: 12px; color: #bbb; }
.nr-user { color: #999; }

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
