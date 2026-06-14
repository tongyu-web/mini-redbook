<template>
  <div class="detail">
    <NavBar />
    <div class="content" v-if="note">
      <div class="header">
        <div class="user" @click="$router.push('/user/' + note.user_id)">
          <el-avatar :size="40" :src="note.user_avatar" />
          <span class="nickname">{{ note.user_nickname }}</span>
        </div>
      </div>
      <h1>{{ note.title }}</h1>
      <div class="media" v-if="note.media_list?.length">
        <el-carousel height="400px" indicator-position="outside">
          <el-carousel-item v-for="m in note.media_list" :key="m.id">
            <img :src="m.file" class="carousel-img" />
          </el-carousel-item>
        </el-carousel>
      </div>
      <div class="cover-only" v-else-if="note.cover_img">
        <img :src="note.cover_img" />
      </div>
      <p class="content-text">{{ note.content }}</p>
      <div class="tags" v-if="note.tags?.length">
        <el-tag v-for="tag in note.tags" :key="tag.id" size="small">{{ tag.name }}</el-tag>
      </div>
      <div class="actions">
        <el-button @click="toggleLike" :type="note.is_liked ? 'danger' : 'default'" size="small">
          {{ note.is_liked ? "❤️" : "🤍" }} {{ note.like_count }}
        </el-button>
        <el-button size="small">💬 {{ note.comment_count || 0 }}</el-button>
        <el-button size="small">👁️ {{ note.view_count || 0 }}</el-button>
      </div>
      <div class="comments" v-if="comments.length">
        <h3>评论 ({{ note.comment_count }})</h3>
        <div v-for="c in comments" :key="c.id" class="comment-item">
          <div class="comment-user">
            <el-avatar :size="28" :src="c.user_avatar" />
            <span class="c-nickname">{{ c.user_nickname }}</span>
          </div>
          <p>{{ c.content }}</p>
          <div v-if="c.replies?.length" class="replies">
            <div v-for="r in c.replies" :key="r.id" class="reply-item">
              <strong>{{ r.user_nickname }}:</strong> {{ r.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { notesApi } from "../api/notes"
import { socialApi } from "../api/social"
import NavBar from "../components/NavBar.vue"

const route = useRoute()
const note = ref(null)
const comments = ref([])

onMounted(async () => {
  note.value = await notesApi.getNote(route.params.id)
  const res = await notesApi.getComments(route.params.id)
  comments.value = res.results || res || []
})

async function toggleLike() {
  const res = await socialApi.toggleLike(route.params.id)
  note.value.is_liked = res.is_liked
  note.value.like_count = res.like_count
}
</script>

<style scoped>
.detail { padding-bottom: 60px; }
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.header { display: flex; align-items: center; margin-bottom: 12px; }
.user { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.carousel-img { width: 100%; height: 100%; object-fit: cover; }
.cover-only img { width: 100%; border-radius: 8px; }
.content-text { line-height: 1.8; color: #333; margin: 12px 0; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; margin: 12px 0; }
.actions { display: flex; gap: 8px; margin: 16px 0; }
.comments { border-top: 1px solid #eee; padding-top: 16px; }
.comment-item { padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.comment-user { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.c-nickname { font-weight: 600; font-size: 13px; }
.replies { margin-left: 36px; background: #f9f9f9; padding: 8px 12px; border-radius: 8px; margin-top: 6px; }
.reply-item { margin: 4px 0; font-size: 13px; }
</style>
