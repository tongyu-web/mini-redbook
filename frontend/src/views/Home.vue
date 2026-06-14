<template>
  <div class="home">
    <NavBar />
    <div class="content">
      <div class="tabs">
        <el-radio-group v-model="activeTab" class="mb-3">
          <el-radio-button value="recommend">推荐</el-radio-button>
          <el-radio-button value="latest">最新</el-radio-button>
        </el-radio-group>
      </div>
      <div v-if="loading" class="text-center">加载中...</div>
      <div v-else-if="notes.length === 0" class="text-center">暂无内容</div>
      <div v-else class="note-grid">
        <div v-for="note in notes" :key="note.id" class="note-card" @click="$router.push('/note/' + note.id)">
          <div class="cover">
            <img v-if="note.cover_img" :src="note.cover_img" :alt="note.title" />
            <div v-else class="placeholder">{{ note.title?.[0] || "?" }}</div>
          </div>
          <div class="info">
            <h3>{{ note.title }}</h3>
            <div class="meta">
              <span>{{ note.user_nickname }}</span>
              <span>❤️ {{ note.like_count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue"
import { searchApi } from "../api/search"
import { notesApi } from "../api/notes"
import NavBar from "../components/NavBar.vue"

const activeTab = ref("recommend")
const notes = ref([])
const loading = ref(true)

async function loadNotes() {
  loading.value = true
  try {
    if (activeTab.value === "recommend") {
      const res = await searchApi.recommend()
      notes.value = res.results || res || []
    } else {
      const res = await notesApi.getNotes()
      notes.value = res.results || res || []
    }
  } catch (e) {
    notes.value = []
  } finally {
    loading.value = false
  }
}
loadNotes()
watch(activeTab, loadNotes)
</script>

<style scoped>
.home { padding-bottom: 60px; }
.content { max-width: 800px; margin: 0 auto; padding: 16px; }
.tabs { text-align: center; margin-bottom: 16px; }
.note-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.note-card { background: white; border-radius: 12px; overflow: hidden; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.06); transition: transform 0.2s; }
.note-card:hover { transform: translateY(-2px); }
.cover { aspect-ratio: 3/4; overflow: hidden; background: #f0f0f0; }
.cover img { width: 100%; height: 100%; object-fit: cover; }
.placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2em; color: white; background: linear-gradient(135deg, #ff6b6b, #ee5a24); }
.info { padding: 10px; }
.info h3 { font-size: 14px; margin: 0 0 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta { display: flex; justify-content: space-between; font-size: 12px; color: #999; }
.mb-3 { margin-bottom: 12px; }
.text-center { text-align: center; padding: 40px; color: #999; }
</style>
