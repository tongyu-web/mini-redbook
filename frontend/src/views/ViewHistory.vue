<template>
  <div class="history-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#333" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <h2>浏览记录</h2>
    </div>
    <div class="history-list" v-if="list.length">
      <div v-for="item in list" :key="item.id" class="history-item">
        <div class="item-cover" @click="goNote(item.note)">
          <img :src="item.note_cover || defaultCover" />
        </div>
        <div class="item-info" @click="goNote(item.note)">
          <div class="item-title">{{ item.note_title }}</div>
          <div class="item-author">{{ item.note_user_nickname }}</div>
          <div class="item-time">{{ formatTime(item.viewed_at) }}</div>
        </div>
      </div>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-if="!hasMore && list.length > 0" class="no-more">没有更多了</div>
    </div>
    <div v-else-if="!loading" class="empty-state">
      <svg viewBox="0 0 64 64" width="48" height="48" fill="none" stroke="#ddd" stroke-width="2"><circle cx="32" cy="32" r="28"/><polyline points="28 36 32 40 40 32"/><line x1="32" y1="24" x2="32" y2="40"/></svg>
      <p>暂无浏览记录</p>
    </div>
  </div>
  <NoteDetail />
</template>

<script setup>
defineProps({ category: String })
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { notesApi } from "../api/notes"
import { useNoteDetailStore } from "../stores/noteDetail"
import NoteDetail from "./NoteDetail.vue"

const router = useRouter()
const store = useNoteDetailStore()
const list = ref([])
const page = ref(1)
const hasMore = ref(true)
const loading = ref(false)
const defaultCover = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200' fill='%23f0f0f0'%3E%3Crect width='200' height='200'/%3E%3Ctext x='100' y='110' text-anchor='middle' fill='%23ccc' font-size='14'%3E%E5%9B%BE%E7%89%87%3C/text%3E%3C/svg%3E"

onMounted(() => { loadMore() })

function formatTime(t) {
  if (!t) return ""
  const d = new Date(t)
  const now = new Date()
  const pad = n => String(n).padStart(2, "0")
  if (d.toDateString() === now.toDateString()) return "今天 " + pad(d.getHours()) + ":" + pad(d.getMinutes())
  const y = new Date(now); y.setDate(y.getDate() - 1)
  if (d.toDateString() === y.toDateString()) return "昨天 " + pad(d.getHours()) + ":" + pad(d.getMinutes())
  return pad(d.getMonth() + 1) + "/" + pad(d.getDate()) + " " + pad(d.getHours()) + ":" + pad(d.getMinutes())
}

async function loadMore() {
  if (loading.value || !hasMore.value) return
  loading.value = true
  try {
    const res = await notesApi.getViewHistory(page.value)
    const items = res.results || res || []
    list.value.push(...items)
    page.value++
    hasMore.value = !!res.next
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function goNote(noteId) {
  if (noteId) {
    store.open(noteId)
    router.push({ query: { note: noteId } })
  }
}
</script>

<style scoped>
.history-page {
  max-width: 800px; margin: 0 auto;
  padding: 16px; min-height: 100vh;
  background: #fff;
}
.page-header {
  display: flex; align-items: center;
  gap: 12px; margin-bottom: 20px;
}
.back-btn { background: none; border: none; cursor: pointer; padding: 4px; display: flex; }
.page-header h2 { font-size: 18px; font-weight: 600; color: #222; margin: 0; }
.history-list { display: flex; flex-direction: column; gap: 12px; }
.history-item {
  display: flex; gap: 12px;
  padding: 12px; border-radius: 12px;
  background: #fafafa; cursor: pointer;
  transition: background 0.15s;
}
.history-item:hover { background: #f0f0f0; }
.item-cover {
  width: 80px; height: 80px; border-radius: 8px;
  overflow: hidden; flex-shrink: 0;
}
.item-cover img { width: 100%; height: 100%; object-fit: cover; }
.item-info { flex: 1; display: flex; flex-direction: column; gap: 4px; justify-content: center; }
.item-title { font-size: 14px; font-weight: 500; color: #222; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.item-author { font-size: 12px; color: #888; }
.item-time { font-size: 11px; color: #bbb; }
.loading, .no-more { text-align: center; padding: 16px; color: #bbb; font-size: 13px; }
.empty-state { text-align: center; padding: 80px 0; color: #ccc; }
.empty-state p { margin-top: 12px; font-size: 14px; }
</style>
