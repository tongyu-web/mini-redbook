<template>
  <div class="detail">
    <NavBar />
    <div class="content" v-if="note">
      <div class="user-header">
        <div class="user" @click="$router.push('/user/' + note.user_id)">
          <el-avatar :size="40" :src="note.user_avatar" />
          <div class="user-meta">
            <span class="nickname">{{ note.user_nickname }}</span>
            <span class="time">{{ note.created_at }}</span>
          </div>
        </div>
        <el-dropdown v-if="isOwner" @command="handleAction" trigger="click" class="more-btn">
          <el-button text circle><span style="font-size:20px">⋯</span></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="edit">✏️ 编辑</el-dropdown-item>
              <el-dropdown-item command="delete" divided>🗑️ 删除</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div v-if="note.is_edited" class="edited-badge">已编辑</div>
      <h1 class="title">{{ note.title }}</h1>
      <div v-if="note.media_list?.length" class="image-grid" :class="gridClass">
        <div v-for="(m, i) in images" :key="m.id" class="img-wrapper" :class="{ 'span-2': setWide(i) }" @click="openViewer(i)">
          <img :src="m.file" loading="lazy" />
        </div>
      </div>
      <div v-else-if="note.cover_img" class="cover-img" @click="openUrlViewer(note.cover_img)">
        <img :src="note.cover_img" />
      </div>
      <div v-if="videos.length" class="video-section">
        <video v-for="m in videos" :key="m.id" :src="m.file" controls class="detail-video" />
      </div>
      <p class="content-text">{{ note.content }}</p>
      <div class="tags" v-if="note.tags?.length">
        <el-tag v-for="tag in note.tags" :key="tag.id" size="small" effect="plain">{{ tag.name }}</el-tag>
      </div>
      <div class="actions">
        <div class="action-item" @click="toggleLike">
          <span class="action-icon">{{ note.is_liked ? '❤️' : '🤍' }}</span>
          <span>{{ note.like_count || '点赞' }}</span>
        </div>
        <div class="action-item"><span class="action-icon">💬</span><span>{{ note.comment_count || '评论' }}</span></div>
        <div class="action-item"><span class="action-icon">👁️</span><span>{{ note.view_count || '浏览' }}</span></div>
      </div>
      <div class="comments" v-if="comments.length">
        <h3>评论 ({{ note.comment_count }})</h3>
        <div v-for="c in comments" :key="c.id" class="comment-item">
          <div class="comment-user">
            <el-avatar :size="28" :src="c.user_avatar" />
            <div class="comment-body">
              <span class="c-nickname">{{ c.user_nickname }}</span>
              <p>{{ c.content }}</p>
            </div>
          </div>
          <div v-if="c.replies?.length" class="replies">
            <div v-for="r in c.replies" :key="r.id" class="reply-item"><strong>{{ r.user_nickname }}:</strong> {{ r.content }}</div>
          </div>
        </div>
      </div>
    </div>
    <el-dialog v-model="deleteDialog" title="删除笔记" width="90%" max-width="400px">
      <p>确定要删除这篇笔记吗？删除后将移入回收站，30天内可恢复。</p>
      <template #footer>
        <el-button @click="deleteDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete">确定删除</el-button>
      </template>
    </el-dialog>
    <Teleport to="body">
      <div v-if="viewerVisible" class="image-viewer" @click="closeViewer">
        <span class="viewer-close">×</span>
        <div class="viewer-content" @click.stop>
          <img :src="viewerImages[viewerIndex]" />
          <div v-if="viewerImages.length > 1" class="viewer-nav">
            <span class="nav-btn" @click.stop="prevImage">‹</span>
            <span class="nav-count">{{ viewerIndex + 1 }} / {{ viewerImages.length }}</span>
            <span class="nav-btn" @click.stop="nextImage">›</span>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { notesApi } from "../api/notes"
import { socialApi } from "../api/social"
import NavBar from "../components/NavBar.vue"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const note = ref(null)
const comments = ref([])
const viewerVisible = ref(false)
const viewerIndex = ref(0)
const viewerImages = ref([])
const deleteDialog = ref(false)

const isOwner = computed(() => userStore.isLoggedIn && userStore.user?.id === note.value?.user_id)
const images = computed(() => note.value?.media_list?.filter(m => m.media_type === 0) || [])
const videos = computed(() => note.value?.media_list?.filter(m => m.media_type === 1) || [])
const gridClass = computed(() => {
  const len = images.value.length
  if (len === 1) return 'single-img'
  if (len === 2) return 'two-imgs'
  if (len === 3) return 'three-imgs'
  if (len === 4) return 'four-imgs'
  return ''
})

onMounted(async () => {
  note.value = await notesApi.getNote(route.params.id)
  const res = await notesApi.getComments(route.params.id)
  comments.value = res.results || res || []
})

function setWide(i) {
  const total = images.value.length
  if (total === 1) return true
  if (total === 3 && i === 0) return true
  return false
}

function handleAction(cmd) {
  if (cmd === "edit") router.push({ path: "/edit/" + route.params.id })
  if (cmd === "delete") deleteDialog.value = true
}

async function confirmDelete() {
  deleteDialog.value = false
  try {
    await notesApi.deleteNote(route.params.id)
    router.push("/user/" + userStore.user.id)
  } catch (e) {}
}

function openViewer(index) {
  viewerImages.value = images.value.map(m => m.file)
  viewerIndex.value = index
  viewerVisible.value = true
  document.body.style.overflow = "hidden"
}
function openUrlViewer(url) {
  viewerImages.value = [url]
  viewerIndex.value = 0
  viewerVisible.value = true
  document.body.style.overflow = "hidden"
}
function closeViewer() {
  viewerVisible.value = false
  document.body.style.overflow = ""
}
function prevImage() {
  viewerIndex.value = (viewerIndex.value - 1 + viewerImages.value.length) % viewerImages.value.length
}
function nextImage() {
  viewerIndex.value = (viewerIndex.value + 1) % viewerImages.value.length
}

async function toggleLike() {
  const res = await socialApi.toggleLike(route.params.id)
  note.value.is_liked = res.is_liked
  note.value.like_count = res.like_count
}
</script>

<style scoped>
.detail { padding-bottom: 60px; background: #fff; min-height: 100vh; }
.content { max-width: 700px; margin: 0 auto; padding: 0 16px 16px; }
.user-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 0; border-bottom: 1px solid #f5f5f5; margin-bottom: 12px; }
.user { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.user-meta { display: flex; flex-direction: column; }
.nickname { font-weight: 600; font-size: 14px; }
.time { font-size: 11px; color: #999; }
.more-btn { cursor: pointer; }
.edited-badge { display: inline-block; font-size: 11px; color: #999; background: #f5f5f5; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; }
.title { font-size: 20px; font-weight: 700; margin: 12px 0; line-height: 1.4; }
.image-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; border-radius: 12px; overflow: hidden; margin-bottom: 12px; }
.img-wrapper { cursor: pointer; overflow: hidden; background: #f0f0f0; min-height: 200px; border-radius: 4px; }
.img-wrapper.span-2 { grid-column: span 2; min-height: 350px; }
.img-wrapper img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s; }
.img-wrapper:hover img { transform: scale(1.03); }
.cover-img { width: 100%; cursor: pointer; border-radius: 12px; overflow: hidden; margin-bottom: 12px; }
.cover-img img { width: 100%; display: block; }
.image-grid.single-img { grid-template-columns: 1fr; }
.image-grid.single-img .img-wrapper { max-height: 70vh; min-height: 300px; aspect-ratio: auto; }
.image-grid.two-imgs { grid-template-columns: 1fr 1fr; }
.image-grid.two-imgs .img-wrapper { aspect-ratio: 1; min-height: 250px; }
.image-grid.three-imgs .img-wrapper { min-height: 180px; }
.image-grid.three-imgs .img-wrapper.span-2 { min-height: 320px; }
.image-grid.four-imgs .img-wrapper { aspect-ratio: 1; min-height: 200px; }
.video-section { margin-bottom: 12px; }
.detail-video { width: 100%; max-height: 500px; border-radius: 12px; }
.content-text { line-height: 1.8; color: #333; margin: 12px 0; font-size: 15px; white-space: pre-wrap; }
.tags { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.actions { display: flex; justify-content: space-around; padding: 16px 0; border-top: 1px solid #f0f0f0; border-bottom: 1px solid #f0f0f0; margin-bottom: 16px; }
.action-item { display: flex; flex-direction: column; align-items: center; cursor: pointer; font-size: 12px; color: #666; gap: 4px; }
.action-icon { font-size: 20px; }
.comments { }
.comment-item { padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.comment-user { display: flex; gap: 8px; }
.comment-body { flex: 1; }
.comment-body p { margin: 4px 0 0; font-size: 14px; }
.c-nickname { font-weight: 600; font-size: 13px; color: #333; }
.replies { margin-left: 36px; background: #f9f9f9; padding: 8px 12px; border-radius: 8px; margin-top: 8px; }
.reply-item { margin: 4px 0; font-size: 13px; }
:global(.image-viewer) { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; display: flex; align-items: center; justify-content: center; }
:global(.viewer-close) { position: absolute; top: 20px; right: 20px; font-size: 36px; color: white; cursor: pointer; z-index: 10; }
:global(.viewer-content) { max-width: 90vw; max-height: 90vh; display: flex; flex-direction: column; align-items: center; }
:global(.viewer-content img) { max-width: 100%; max-height: 85vh; object-fit: contain; border-radius: 4px; }
:global(.viewer-nav) { display: flex; align-items: center; gap: 20px; margin-top: 16px; color: white; }
:global(.nav-btn) { font-size: 32px; cursor: pointer; padding: 8px 16px; user-select: none; }
:global(.nav-btn:hover) { background: rgba(255,255,255,0.1); border-radius: 8px; }
:global(.nav-count) { font-size: 14px; }
</style>
