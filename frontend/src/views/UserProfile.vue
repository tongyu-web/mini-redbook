<template>
  <div class="profile">
    <NavBar />
    <div class="content" v-if="user">
      <div class="header">
        <el-avatar :size="72" :src="user.avatar_url" />
        <div class="info">
          <h2>{{ user.nickname }}</h2>
          <p class="bio">{{ user.bio }}</p>
          <div class="stats">
            <span>{{ user.note_count }} 笔记</span>
            <span>{{ user.follower_count }} 粉丝</span>
            <span>{{ user.following_count }} 关注</span>
          </div>
        </div>
      </div>
      <div class="notes" v-if="notes.length">
        <div v-for="n in notes" :key="n.id" class="note-item" @click="$router.push('/note/' + n.id)">
          <img :src="n.cover_img" v-if="n.cover_img" />
          <span>{{ n.title }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { accountsApi } from "../api/accounts"
import { notesApi } from "../api/notes"
import NavBar from "../components/NavBar.vue"

const route = useRoute()
const user = ref(null)
const notes = ref([])

onMounted(async () => {
  user.value = await accountsApi.getProfile(route.params.id)
  notes.value = await notesApi.getNotes()
})
</script>

<style scoped>
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.header { display: flex; gap: 16px; align-items: center; margin-bottom: 20px; }
.stats { display: flex; gap: 16px; color: #666; font-size: 13px; margin-top: 8px; }
.bio { color: #666; font-size: 13px; margin-top: 4px; }
.notes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.note-item { cursor: pointer; text-align: center; }
.note-item img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; }
</style>
