<template>
  <div class="home-page">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
    <div v-else-if="notes.length === 0" class="empty-state">暂无内容</div>
    <div v-else class="waterfall-grid">
      <div v-for="note in notes" :key="note.id" class="feed-card" @click="openNote(note.id)">
        <div class="card-media">
          <img v-if="note.cover_img" :src="note.cover_img" :alt="note.title" />
          <div v-else class="card-placeholder">{{ note.title?.[0] || "R" }}</div>
          <div v-if="note.type === 1" class="video-badge">
            <svg viewBox="0 0 24 24" fill="white" width="12" height="12"><polygon points="5,3 19,12 5,21"/></svg>
          </div>
        </div>
        <div class="card-body">
          <div class="card-category" v-if="note.category">
            <span class="cat-badge">{{ categoryLabel(note.category) }}</span>
          </div>
          <h3 class="card-title">{{ note.title }}</h3>
          <div class="card-tags" v-if="note.tags?.length">
            <span class="card-tag" v-for="tag in note.tags.slice(0,3)" :key="tag.id">#{{ tag.name }}</span>
          </div>
          <div class="card-footer">
            <div class="card-author">
              <img v-if="note.user_avatar" :src="note.user_avatar" class="author-avatar" />
              <div v-else class="author-avatar author-avatar-placeholder">{{ note.user_nickname?.[0] || "?" }}</div>
              <span class="author-name">{{ note.user_nickname }}</span>
            </div>
            <div class="card-likes">
              <svg viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" width="14" height="14">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
              <span>{{ note.like_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Note Detail Drawer -->
  <NoteDetail />
</template>

<script setup>
import { ref, watch } from "vue"
import { searchApi } from "../api/search"
import { notesApi } from "../api/notes"
import { useNoteDetailStore } from "../stores/noteDetail"
import NoteDetail from "./NoteDetail.vue"

const noteDetailStore = useNoteDetailStore()
const props = defineProps({
  category: { type: String, default: "recommend" }
})

const notes = ref([])
const loading = ref(true)

const NOTE_CATEGORIES = {
  beauty: "\u7f8e\u5986", travel: "\u65c5\u884c", food: "\u7f8e\u98df", fashion: "\u7a7f\u642d",
  fitness: "\u5065\u8eab", tech: "\u6570\u7801", study: "\u5b66\u4e60", art: "\u827a\u672f",
  life: "\u751f\u6d3b", other: "\u5176\u4ed6"
}

function categoryLabel(key) {
  return NOTE_CATEGORIES[key] || key
}

function openNote(id) {
  noteDetailStore.open(id)
}

async function loadNotes() {
  loading.value = true
  try {
    if (props.category === "recommend") {
      const res = await searchApi.recommend()
      notes.value = res.results || res || []
    } else {
      const res = await notesApi.getNotesByCategory(props.category)
      notes.value = res.results || res || []
    }
  } catch (e) {
    notes.value = []
  } finally {
    loading.value = false
  }
}
loadNotes()
watch(() => props.category, loadNotes)
</script>

<style scoped>
.home-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px 24px;
  min-height: calc(100vh - 120px);
}
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #999;
  font-size: 14px;
  gap: 12px;
}
.loading-spinner {
  width: 28px; height: 28px;
  border: 3px solid #f0f0f0;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.waterfall-grid {
  column-count: 2;
  column-gap: 10px;
}
.feed-card {
  break-inside: avoid;
  margin-bottom: 10px;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.feed-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
.card-media {
  position: relative;
  overflow: hidden;
  background: #f0f0f0;
}
.card-media img { width: 100%; display: block; }
.card-placeholder {
  width: 100%;
  aspect-ratio: 3/4;
  display: flex; align-items: center; justify-content: center;
  font-size: 2em; color: white;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}
.video-badge {
  position: absolute; bottom: 8px; left: 8px;
  background: rgba(0,0,0,0.7); border-radius: 4px;
  padding: 3px 6px; display: flex; align-items: center; gap: 3px;
}
.card-body { padding: 8px 10px 10px; }
.card-title {
  font-size: 13px; font-weight: 600; line-height: 1.3;
  margin: 0 0 4px; color: #222;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.card-tag { font-size: 11px; color: #999; }
.card-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding-top: 6px; border-top: 1px solid #f5f5f5;
}
.card-author { display: flex; align-items: center; gap: 6px; min-width: 0; }
.author-avatar { width: 18px; height: 18px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.author-avatar-placeholder {
  display: flex; align-items: center; justify-content: center;
  background: #ff2442; color: white; font-size: 10px; font-weight: 600;
}
.author-name { font-size: 12px; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-likes { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #999; flex-shrink: 0; }
.card-category { margin-bottom: 4px; }
.cat-badge { display: inline-block; background: #fff0f0; color: #ff2442; font-size: 10px; padding: 1px 8px; border-radius: 8px; font-weight: 600; }
</style>
