
<template>
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div v-if="store.isOpen" class="drawer-overlay" @click.self="handleClose">
        <Transition name="drawer-slide">
          <div v-if="store.isOpen" class="drawer-panel">
            <!-- Close button -->
            <button class="drawer-close" @click="handleClose">&times;</button>

            <div class="drawer-body" v-if="note">
              <!-- LEFT: Image gallery -->
              <div class="drawer-left">
                <div class="image-gallery">
                  <div v-if="images.length" class="main-image" @click="openViewer(0)">
                    <img :src="images[0].file" />
                  </div>
                  <div v-else-if="note.cover_img" class="main-image">
                    <img :src="note.cover_img" />
                  </div>
                  <div v-if="images.length > 1" class="thumb-strip">
                    <div v-for="(m, i) in images" :key="m.id" class="thumb-item" :class="{ active: i === galleryIdx }" @click="galleryIdx = i">
                      <img :src="m.file" />
                    </div>
                  </div>
                  <div v-if="videos.length" class="video-section">
                    <video v-for="m in videos" :key="m.id" :src="m.file" controls class="detail-video" />
                  </div>
                </div>
              </div>

              <!-- RIGHT: Content panel -->
              <div class="drawer-right">
                <!-- Author header -->
                <div class="author-bar">
                  <div class="author-info" @click="$router.push('/user/' + note.user_id)">
                    <el-avatar :size="36" :src="note.user_avatar" />
                    <div class="author-meta">
                      <span class="author-name">{{ note.user_nickname }}</span>
                      <span class="author-time">{{ note.created_at }}</span>
                    </div>
                  </div>
                  <div class="author-actions">
                    <el-button v-if="!isOwner && userStore.isLoggedIn" size="small" :type="note.is_following ? 'default' : 'primary'" round @click="toggleFollow">{{ note.is_following ? '已关注' : '+ 关注' }}</el-button>
                    <el-dropdown v-if="isOwner" @command="handleAction" trigger="click">
                      <el-button text circle size="small"><span style="font-size:18px">&#8942;</span></el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="edit">&#9998;&#65039; 编辑</el-dropdown-item>
                          <el-dropdown-item command="delete" divided>&#128465;&#65039; 删除</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>

                <div v-if="note.is_edited" class="edited-badge">已编辑</div>

                <!-- Title & content -->
                <div class="note-body">
                  <h2 class="note-title">{{ note.title }}</h2>
                  <p class="note-content">{{ note.content }}</p>
                  <div class="note-tags" v-if="note.tags?.length">
                    <el-tag v-for="tag in note.tags" :key="tag.id" size="small" effect="plain">{{ tag.name }}</el-tag>
                  </div>
                </div>

                <!-- Comments section -->
                <div class="comments-section">
                  <div class="comments-header">
                    <span>评论 ({{ note.comment_count }})</span>
                  </div>
                  <div class="comments-list" ref="commentsRef">
                    <div v-for="c in comments" :key="c.id" class="comment-item">
                      <div class="comment-user">
                        <el-avatar :size="26" :src="c.user_avatar" />
                        <div class="comment-body">
                          <div class="comment-top">
                            <span class="c-nickname">{{ c.user_nickname }}</span>
                            <el-button v-if="userStore.isLoggedIn" text size="small" @click="replyToComment(c)" class="reply-btn">回复</el-button>
                          </div>
                          <p>{{ c.content }}</p>
                          <img v-if="c.image" :src="c.image" class="comment-img" @click="openUrlViewer(c.image)" />
                          <div v-if="c.replies?.length" class="replies">
                            <div v-for="r in c.replies" :key="r.id" class="reply-item"><strong>{{ r.user_nickname }}:</strong> {{ r.content }}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-if="!comments.length" class="no-comments">暂无评论，来说两句吧~</div>
                  </div>
                </div>
                <!-- Bottom action bar -->
                <div class="bottom-bar" :class="{ 'is-composing': commentComposing }">
                  <div class="reply-hint" v-if="replyTo">
                    <span>回复 @{{ replyTo.nickname }}</span>
                    <el-button text size="small" @click="cancelReply">取消</el-button>
                  </div>
                  <!-- Normal mode: input + icons -->
                  <div class="bottom-row" v-if="!commentComposing">
                    <div class="bottom-input" v-if="userStore.isLoggedIn">
                      <el-avatar :size="26" :src="userStore.user?.avatar_url" />
                      <div class="input-wrap">
                        <el-input v-model="commentContent" type="textarea" :rows="1" :maxlength="300" placeholder="写下你的评论..." resize="none" @keydown.enter.ctrl="submitComment" @focus="commentComposing = true" />
                      </div>
                      <label class="upload-btn" for="comment-image-bottom">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#999" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                      </label>
                      <input id="comment-image-bottom" ref="commentInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleCommentImage" />
                    </div>
                    <div v-else class="bottom-input">
                      <el-button text size="small" @click="$router.push('/login')">登录后评论</el-button>
                    </div>
                    <div class="bottom-icons">
                      <div class="bottom-icon-item" @click="toggleLike">
                        <svg viewBox="0 0 24 24" width="20" height="20" :fill="note.is_liked ? '#ff2442' : 'none'" :stroke="note.is_liked ? '#ff2442' : '#666'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                        <span>{{ note.like_count || 0 }}</span>
                      </div>
                      <div class="bottom-icon-item" @click="showFolderDialog">
                        <svg viewBox="0 0 24 24" width="20" height="20" :fill="note.is_favorited ? '#ffb800' : 'none'" :stroke="note.is_favorited ? '#ffb800' : '#666'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                        <span>{{ note.fav_count || 0 }}</span>
                      </div>
                      <div class="bottom-icon-item" @click="toggleCommentCompose">
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                        <span>{{ note.comment_count || 0 }}</span>
                      </div>
                      <div class="bottom-icon-item">
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
                      </div>
                    </div>
                  </div>
                  <!-- Composing mode: full editor with send/cancel -->
                  <div class="compose-panel" v-if="commentComposing">
                    <div class="compose-header">
                      <span class="compose-label">{{ replyTo ? "回复 @" + replyTo.nickname : "发表评论" }}</span>
                      <el-button text size="small" @click="cancelCompose">取消</el-button>
                    </div>
                    <div class="compose-body">
                      <el-input v-model="commentContent" type="textarea" :rows="3" :maxlength="300" placeholder="写下你的评论..." show-word-limit resize="none" ref="composeInputRef" />
                      <div class="compose-footer">
                        <label class="upload-label" for="comment-image-compose">
                          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#999" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                          <span class="upload-text" v-if="!commentFile">添加图片</span>
                          <span class="upload-text" v-else>{{ commentFile.name }}</span>
                        </label>
                        <input id="comment-image-compose" ref="commentInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleCommentImage" />
                        <div class="compose-actions">
                          <el-button size="small" @click="cancelCompose">取消</el-button>
                          <el-button size="small" type="primary" :loading="commenting" @click="submitComment" :disabled="!commentContent.trim()">发送</el-button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Loading state -->
            <div class="drawer-loading" v-else>
              <el-skeleton :rows="8" animated />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>

  <!-- Delete dialog -->
  <el-dialog v-model="deleteDialog" title="删除笔记" width="90%" max-width="400px">
    <p>确定要删除这篇笔记吗？删除后将移入回收站，30天内可恢复。</p>
    <template #footer>
      <el-button @click="deleteDialog = false">取消</el-button>
      <el-button type="danger" @click="confirmDelete">确定删除</el-button>
    </template>
  </el-dialog>

  <!-- Favorite folder dialog -->
  <el-dialog v-model="favDialogVisible" title="收藏到文件夹" width="90%" max-width="400px">
    <div class="folder-list">
      <div v-for="f in folders" :key="f.id" class="folder-item" @click="selectFolder(f)">
        <span class="folder-icon">{{ f.is_public ? '&#128194;' : '&#128274;' }}</span>
        <span class="folder-name">{{ f.name }}</span>
        <span class="folder-count">{{ f.note_count || 0 }} 篇</span>
      </div>
    </div>
    <div class="folder-create" @click="createAndSelect">
      <span class="folder-icon">&#10133;</span>
      <span class="folder-name">新建收藏夹</span>
    </div>
    <template #footer>
      <el-button @click="favDialogVisible = false">取消</el-button>
    </template>
  </el-dialog>

  <!-- Image viewer -->
  <Teleport to="body">
    <div v-if="viewerVisible" class="image-viewer" @click="closeViewer">
      <span class="viewer-close">&times;</span>
      <div class="viewer-content" @click.stop>
        <img :src="viewerImages[viewerIndex]" />
        <div v-if="viewerImages.length > 1" class="viewer-nav">
          <span class="nav-btn" @click.stop="prevImage">&#8249;</span>
          <span class="nav-count">{{ viewerIndex + 1 }} / {{ viewerImages.length }}</span>
          <span class="nav-btn" @click.stop="nextImage">&#8250;</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from "vue"
import { ElMessage } from "element-plus"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { useNoteDetailStore } from "../stores/noteDetail"
import { notesApi } from "../api/notes"
import { socialApi } from "../api/social"

const router = useRouter()
const userStore = useUserStore()
const store = useNoteDetailStore()

const note = ref(null)
const comments = ref([])
const galleryIdx = ref(0)
const commentsRef = ref(null)

// Image viewer
const viewerVisible = ref(false)
const viewerIndex = ref(0)
const viewerImages = ref([])

// Delete
const deleteDialog = ref(false)

// Favorite
const favDialogVisible = ref(false)
const folders = ref([])

// Comment
const commentContent = ref("")
const commentFile = ref(null)
const commenting = ref(false)
const replyTo = ref(null)
const commentComposing = ref(false)

const isOwner = computed(() => userStore.isLoggedIn && userStore.user?.id === note.value?.user_id)
const images = computed(() => note.value?.media_list?.filter(m => m.media_type === 0) || [])
const videos = computed(() => note.value?.media_list?.filter(m => m.media_type === 1) || [])

// Load note data when drawer opens
watch(() => store.currentNoteId, async (id) => {
  if (!id) {
    note.value = null
    comments.value = []
    return
  }
  try {
    note.value = await notesApi.getNote(id)
    const res = await notesApi.getComments(id)
    comments.value = res.results || res || []
    galleryIdx.value = 0
  } catch (e) {
    console.error(e)
    store.close()
  }
})

function handleClose() {
  store.close()
}

onUnmounted(() => {
  document.body.style.overflow = ""
})

function handleAction(cmd) {
  if (cmd === "edit") {
    store.close()
    router.push({ path: "/edit/" + store.currentNoteId })
  }
  if (cmd === "delete") deleteDialog.value = true
}

async function confirmDelete() {
  deleteDialog.value = false
  try {
    await notesApi.deleteNote(store.currentNoteId)
    store.close()
  } catch (e) {}
}

async function toggleFollow() {
  try {
    const res = await socialApi.toggleFollow(note.value.user_id)
    note.value.is_following = res.is_following
  } catch (e) {}
}

async function toggleLike() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning("请先登录")
    router.push("/login")
    store.close()
    return
  }
  if (!note.value) return
  try {
    console.log("toggleLike: calling API for note", store.currentNoteId)
    const res = await socialApi.toggleLike(store.currentNoteId)
    console.log("toggleLike: API response", res)
    if (note.value) {
      note.value.is_liked = res.is_liked
      note.value.like_count = res.like_count
    }
  } catch (e) {
    console.error("toggleLike error:", e)
    ElMessage.error("点赞失败: " + (e.message || e))
  }
}

// Favorite
async function showFolderDialog() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning("请先登录")
    router.push("/login")
    store.close()
    return
  }
  if (!note.value) return
  if (note.value.is_favorited) {
    try {
      await socialApi.removeFavoriteFromAll(store.currentNoteId)
      if (note.value) {
        note.value.is_favorited = false
        note.value.fav_count = Math.max(0, (note.value.fav_count || 1) - 1)
      }
    } catch (e) { console.error(e) }
    return
  }
  try {
    console.log("showFolderDialog: fetching folders")
    const res = await socialApi.getFolders()
    console.log("showFolderDialog: folders", res)
    folders.value = res || []
    favDialogVisible.value = true
  } catch (e) {
    console.error("showFolderDialog error:", e)
    ElMessage.error("获取收藏夹失败: " + (e.message || e))
  }
}

async function selectFolder(folder) {
  try {
    console.log("selectFolder: adding favorite", { note_id: store.currentNoteId, folder_id: folder.id })
    const res = await socialApi.addFavorite({ note_id: store.currentNoteId, folder_id: folder.id })
    console.log("selectFolder: API response", res)
    if (note.value) {
      note.value.is_favorited = true
      note.value.fav_count = (note.value.fav_count || 0) + 1
    }
    favDialogVisible.value = false
  } catch (e) {
    console.error("selectFolder error:", e)
    ElMessage.error("收藏失败: " + (e.message || e))
  }
}

async function createAndSelect() {
  const name = prompt("请输入新收藏夹名称：")
  if (!name || !name.trim()) return
  try {
    const res = await socialApi.createFolder({ name: name.trim() })
    await selectFolder(res)
  } catch (e) { console.error(e) }
}

// Image viewer functions
function openViewer(index) {
  viewerImages.value = images.value.map(m => m.file)
  viewerIndex.value = index
  viewerVisible.value = true
}
function openUrlViewer(url) {
  viewerImages.value = [url]
  viewerIndex.value = 0
  viewerVisible.value = true
}
function closeViewer() { viewerVisible.value = false }
function prevImage() { viewerIndex.value = (viewerIndex.value - 1 + viewerImages.value.length) % viewerImages.value.length }
function nextImage() { viewerIndex.value = (viewerIndex.value + 1) % viewerImages.value.length }

// Comment functions
const commentInput = ref(null)
function handleCommentImage(e) {
  const f = e.target.files?.[0]
  if (!f) return
  commentFile.value = f
  e.target.value = ""
}
function cancelReply() { 
  replyTo.value = null
  commentComposing.value = false
}
function replyToComment(c) { 
  replyTo.value = { id: c.id, nickname: c.user_nickname }
  commentComposing.value = true
}

function toggleCommentCompose() {
  if (!userStore.isLoggedIn) {
    router.push("/login")
    store.close()
    return
  }
  if (commentComposing.value) {
    cancelCompose()
    return
  }
  commentComposing.value = true
  setTimeout(() => {
    const el = document.querySelector(".compose-body .el-textarea__inner")
    if (el) el.focus()
  }, 100)
}

function scrollToComments() {
    const el = document.querySelector('.comments-list');
    if (el) el.scrollTop = 0;
  }

function cancelCompose() {
  commentComposing.value = false
  commentContent.value = ""
  commentFile.value = null
  replyTo.value = null
}

async function submitComment() {
  if (!userStore.isLoggedIn) return
  if (!commentContent.value.trim()) return
  commenting.value = true
  try {
    const fd = new FormData()
    fd.append("content", commentContent.value.trim())
    if (replyTo.value) fd.append("parent_id", replyTo.value.id)
    if (commentFile.value) fd.append("image", commentFile.value)
    await notesApi.postComment(store.currentNoteId, fd)
    commentContent.value = ""
    commentFile.value = null
    replyTo.value = null
    commentComposing.value = false
    const res = await notesApi.getComments(store.currentNoteId)
    comments.value = res.results || res || []
    if (note.value) note.value.comment_count = (note.value.comment_count || 0) + 1
  } catch (e) { console.error(e) }
  finally { commenting.value = false }
}
</script>

<style scoped>
/* Overlay */
.drawer-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.45);
  z-index: 2000;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}

/* Drawer panel */
.drawer-panel {
  width: 90vw;
  max-width: 1100px;
  height: 88vh;
  max-height: 900px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.drawer-close {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0,0,0,0.45);
  border: none;
  font-size: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  z-index: 20;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  transition: background 0.15s;
}
.drawer-close:hover {
  background: rgba(0,0,0,0.7);
}

.drawer-body {
  display: flex;
  height: 100%;
  overflow: hidden;
}

/* LEFT: Image gallery */
.drawer-left {
  flex: 1;
  min-width: 0;
  background: #f8f8f8;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-gallery {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.main-image {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: zoom-in;
}
.main-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.thumb-strip {
  display: flex;
  gap: 6px;
  padding: 12px 0 0;
  overflow-x: auto;
  width: 100%;
  justify-content: center;
}
.thumb-item {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  flex-shrink: 0;
}
.thumb-item.active {
  border-color: #ff2442;
}
.thumb-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-section {
  width: 100%;
  margin-top: 8px;
}
.detail-video {
  width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

/* RIGHT: Content panel */
.drawer-right {
  width: 44%;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #f0f0f0;
  background: #fff;
}

/* Author bar */
.author-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f5f5f5;
  flex-shrink: 0;
}
.author-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
.author-meta {
  display: flex;
  flex-direction: column;
}
.author-name {
  font-weight: 600;
  font-size: 14px;
  color: #222;
}
.author-time {
  font-size: 11px;
  color: #999;
}
.author-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edited-badge {
  font-size: 11px;
  color: #999;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
  margin: 8px 20px 0;
  display: inline-block;
  align-self: flex-start;
}

/* Note body */
.note-body {
  padding: 12px 20px;
  flex-shrink: 0;
  max-height: 35vh;
  overflow-y: auto;
}
.note-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 8px;
  line-height: 1.4;
  color: #222;
}
.note-content {
  font-size: 14px;
  line-height: 1.7;
  color: #555;
  white-space: pre-wrap;
  margin: 0;
}
.note-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 10px;
}
/* Bottom action bar */
.bottom-bar {
  border-top: 1px solid #f0f0f0;
  background: #fff;
  flex-shrink: 0;
}
.bottom-bar .reply-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
  padding: 4px 16px 0;
}
.bottom-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
}
.bottom-input {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.input-wrap {
  flex: 1;
  min-width: 0;
}
.input-wrap :deep(.el-textarea__inner) {
  font-size: 13px;
  border-radius: 18px;
  min-height: 32px !important;
  padding: 5px 12px;
  background: #f5f5f5;
  border-color: transparent;
}
.input-wrap :deep(.el-textarea__inner:focus) {
  background: #fff;
  border-color: #ff2442;
}
.upload-btn {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.15s;
}
.upload-btn:hover svg { stroke: #ff2442; }
.bottom-icons {
  display: flex;
  align-items: center;
  gap: 0;
  flex-shrink: 0;
}
.bottom-icon-item {
  display: flex;
  align-items: center;
  gap: 3px;
  cursor: pointer;
  padding: 6px 10px;
  transition: color 0.15s;
  color: #666;
  font-size: 12px;
  white-space: nowrap;
}
.bottom-icon-item:hover {
  color: #ff2442;
}
.bottom-icon-item svg {
  transition: fill 0.15s, stroke 0.15s;
}

/* Composing panel */
.bottom-bar.is-composing {
  padding: 0;
}
.compose-panel {
  padding: 12px 16px;
}
.compose-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.compose-label {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}
.compose-body :deep(.el-textarea__inner) {
  font-size: 14px;
  border-radius: 8px;
  min-height: 80px !important;
}
.compose-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}
.upload-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}
.upload-label:hover {
  background: #f5f5f5;
}
.upload-text {
  font-size: 12px;
  color: #999;
}
.compose-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Comments section */
.comments-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.comments-header {
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #f5f5f5;
  flex-shrink: 0;
}
.comments-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px;
}
.comment-item {
  padding: 10px 0;
  border-bottom: 1px solid #f8f8f8;
}
.comment-item:last-child {
  border-bottom: none;
}
.comment-user {
  display: flex;
  gap: 8px;
}
.comment-body {
  flex: 1;
  min-width: 0;
}
.comment-top {
  display: flex;
  align-items: center;
  gap: 4px;
}
.comment-body p {
  margin: 3px 0 0;
  font-size: 13px;
  color: #333;
  word-break: break-word;
}
.c-nickname {
  font-weight: 600;
  font-size: 12px;
  color: #555;
}
.reply-btn {
  font-size: 11px;
  color: #999;
}
.reply-btn:hover { color: #ff2442; }
.replies {
  margin-left: 34px;
  background: #f9f9f9;
  padding: 6px 10px;
  border-radius: 6px;
  margin-top: 6px;
}
.reply-item {
  margin: 3px 0;
  font-size: 12px;
  color: #555;
}
.no-comments {
  text-align: center;
  padding: 32px 0;
  color: #ccc;
  font-size: 14px;
}
.comment-img {
  max-width: 120px;
  max-height: 120px;
  border-radius: 6px;
  margin-top: 4px;
  cursor: pointer;
}


/* Loading */
.drawer-loading {
  padding: 40px;
}

/* Transitions */
.drawer-fade-enter-active, .drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-fade-enter-from, .drawer-fade-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active, .drawer-slide-leave-active {
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease;
}
.drawer-slide-enter-from, .drawer-slide-leave-to {
  transform: scale(0.92);
  opacity: 0;
}

/* Folder dialog */
.folder-list { max-height: 260px; overflow-y: auto; }
.folder-item { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 8px; cursor: pointer; transition: background 0.15s; }
.folder-item:hover { background: #f5f5f5; }
.folder-icon { font-size: 18px; }
.folder-name { flex: 1; font-size: 14px; color: #333; }
.folder-count { font-size: 12px; color: #999; }
.folder-create { display: flex; align-items: center; gap: 10px; padding: 10px; border-top: 1px solid #f0f0f0; margin-top: 6px; cursor: pointer; border-radius: 8px; color: #ff2442; font-size: 14px; }
.folder-create:hover { background: #fff0f0; }

/* Image viewer */
:global(.image-viewer) { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; display: flex; align-items: center; justify-content: center; }
:global(.viewer-close) { position: absolute; top: 20px; right: 20px; font-size: 36px; color: white; cursor: pointer; z-index: 10; }
:global(.viewer-content) { max-width: 90vw; max-height: 90vh; display: flex; flex-direction: column; align-items: center; }
:global(.viewer-content img) { max-width: 100%; max-height: 85vh; object-fit: contain; border-radius: 4px; }
:global(.viewer-nav) { display: flex; align-items: center; gap: 20px; margin-top: 16px; color: white; }
:global(.nav-btn) { font-size: 32px; cursor: pointer; padding: 8px 16px; user-select: none; }
:global(.nav-btn:hover) { background: rgba(255,255,255,0.1); border-radius: 8px; }
:global(.nav-count) { font-size: 14px; }

/* Responsive */
@media (max-width: 768px) {
  .drawer-panel {
    width: 100vw;
    max-width: 100vw;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
  }
  .drawer-body {
    flex-direction: column;
  }
  .drawer-left {
    max-height: 40vh;
  }
  .drawer-right {
    width: 100%;
    min-width: 0;
    border-left: none;
    border-top: 1px solid #f0f0f0;
  }
}
</style>
