
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

                <!-- Action bar -->
                <div class="action-bar">
                  <div class="action-item" @click="toggleLike">
                    <span class="action-icon">{{ note.is_liked ? '&#10084;&#65039;' : '&#129294;' }}</span>
                    <span class="action-count">{{ note.like_count || '赞' }}</span>
                  </div>
                  <div class="action-item" @click="showFolderDialog" v-if="userStore.isLoggedIn">
                    <span class="action-icon">{{ note.is_favorited ? '&#128193;' : '&#128451;&#65039;' }}</span>
                    <span class="action-count">{{ note.is_favorited ? '已收藏' : '收藏' }}</span>
                  </div>
                  <div class="action-item">
                    <span class="action-icon">&#128172;</span>
                    <span class="action-count">{{ note.comment_count || '评论' }}</span>
                  </div>
                  <div class="action-item">
                    <span class="action-icon">&#128065;&#65039;</span>
                    <span class="action-count">{{ note.view_count || '浏览' }}</span>
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

                  <!-- Comment input -->
                  <div class="comment-input-area" v-if="userStore.isLoggedIn">
                    <div class="reply-hint" v-if="replyTo">
                      <span>回复 @{{ replyTo.nickname }}</span>
                      <el-button text size="small" @click="cancelReply">取消</el-button>
                    </div>
                    <div class="comment-form">
                      <el-avatar :size="28" :src="userStore.user?.avatar_url" />
                      <div class="comment-input-wrap">
                        <el-input v-model="commentContent" type="textarea" :rows="1" :maxlength="300" placeholder="写下你的评论..." show-word-limit resize="none" />
                        <div class="comment-actions">
                          <label class="upload-label" for="comment-image">
                            <span class="img-btn">&#128247;</span>
                          </label>
                          <input id="comment-image" ref="commentInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleCommentImage" />
                          <span class="img-name" v-if="commentFile">{{ commentFile.name }}</span>
                          <el-button size="small" type="primary" :loading="commenting" @click="submitComment" :disabled="!commentContent.trim()">发送</el-button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="login-hint">
                    <el-button text @click="$router.push('/login')">登录后发表评论</el-button>
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
    router.push({ path: "/edit/" + store.currentNoteId.value })
  }
  if (cmd === "delete") deleteDialog.value = true
}

async function confirmDelete() {
  deleteDialog.value = false
  try {
    await notesApi.deleteNote(store.currentNoteId.value)
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
  const res = await socialApi.toggleLike(store.currentNoteId.value)
  note.value.is_liked = res.is_liked
  note.value.like_count = res.like_count
}

// Favorite
async function showFolderDialog() {
  if (note.value.is_favorited) {
    try {
      await socialApi.removeFavoriteFromAll(store.currentNoteId.value)
      note.value.is_favorited = false
      note.value.fav_count = (note.value.fav_count || 1) - 1
    } catch (e) { console.error(e) }
    return
  }
  try {
    const res = await socialApi.getFolders()
    folders.value = res || []
    favDialogVisible.value = true
  } catch (e) { console.error(e) }
}

async function selectFolder(folder) {
  try {
    await socialApi.addFavorite({ note_id: store.currentNoteId.value, folder_id: folder.id })
    note.value.is_favorited = true
    note.value.fav_count = (note.value.fav_count || 0) + 1
    favDialogVisible.value = false
  } catch (e) { console.error(e) }
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
function cancelReply() { replyTo.value = null }
function replyToComment(c) { replyTo.value = { id: c.id, nickname: c.user_nickname } }

async function submitComment() {
  if (!commentContent.value.trim()) return
  commenting.value = true
  try {
    const fd = new FormData()
    fd.append("content", commentContent.value.trim())
    if (replyTo.value) fd.append("parent_id", replyTo.value.id)
    if (commentFile.value) fd.append("image", commentFile.value)
    await notesApi.postComment(store.currentNoteId.value, fd)
    commentContent.value = ""
    commentFile.value = null
    replyTo.value = null
    const res = await notesApi.getComments(store.currentNoteId.value)
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
  justify-content: flex-end;
  backdrop-filter: blur(2px);
}

/* Drawer panel */
.drawer-panel {
  width: 92vw;
  max-width: 960px;
  height: 100vh;
  background: #fff;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  position: relative;
}

.drawer-close {
  position: absolute;
  top: 12px;
  left: -40px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.9);
  border: none;
  font-size: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.drawer-close:hover {
  background: #fff;
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
  width: 380px;
  min-width: 380px;
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

/* Action bar */
.action-bar {
  display: flex;
  justify-content: space-around;
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}
.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  font-size: 11px;
  color: #666;
  gap: 2px;
  transition: color 0.15s;
}
.action-item:hover {
  color: #ff2442;
}
.action-icon {
  font-size: 18px;
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

/* Comment input */
.comment-input-area {
  border-top: 1px solid #f0f0f0;
  padding: 10px 20px;
  flex-shrink: 0;
  background: #fff;
}
.reply-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
}
.comment-form {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}
.comment-input-wrap {
  flex: 1;
  min-width: 0;
}
.comment-input-wrap :deep(.el-textarea__inner) {
  font-size: 13px;
  border-radius: 6px;
  min-height: 32px !important;
}
.comment-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}
.upload-label { cursor: pointer; }
.img-btn { font-size: 16px; cursor: pointer; }
.img-name { font-size: 10px; color: #999; max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.login-hint { text-align: center; padding: 12px 20px; border-top: 1px solid #f0f0f0; }

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
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-slide-enter-from, .drawer-slide-leave-to {
  transform: translateX(100%);
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
  }
  .drawer-body {
    flex-direction: column;
  }
  .drawer-left {
    max-height: 45vh;
  }
  .drawer-right {
    width: 100%;
    min-width: 0;
    border-left: none;
    border-top: 1px solid #f0f0f0;
  }
  .drawer-close {
    left: 12px;
    top: 12px;
    background: rgba(0,0,0,0.4);
    color: white;
  }
}
</style>
