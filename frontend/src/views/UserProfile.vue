<template>
  <div class="profile-page">
    <div class="profile-content" v-if="profile">
      <!-- Profile Header -->
      <div class="profile-header">
        <div class="header-avatar">
          <div class="avatar-ring">
            <img v-if="profile.avatar_url" :src="profile.avatar_url" class="avatar-img" />
            <div v-else class="avatar-img avatar-placeholder">😺</div>
          </div>
        </div>
        <div class="header-info">
          <h1 class="header-name">{{ profile.nickname || "未设置昵称" }}</h1>
          <p class="header-id">mini-redbook ID：{{ profile.user_id || route.params.id }}</p>
          <p class="header-bio">{{ profile.bio || "这个人很懒，什么都没写" }}</p>
          <div class="header-stats">
            <div class="hs-item" @click="showFollowing">
              <span class="hs-num">{{ profile.following_count }}</span>
              <span class="hs-label">关注</span>
            </div>
            <div class="hs-item" @click="showFollowers">
              <span class="hs-num">{{ profile.follower_count }}</span>
              <span class="hs-label">粉丝</span>
            </div>
            <div class="hs-item">
              <span class="hs-num">{{ (profile.like_received_count || 0) + (profile.fav_received_count || 0) }}</span>
              <span class="hs-label">获赞收藏</span>
            </div>
          </div>
          <div class="header-actions">
                        <button v-if="isOwn" class="ha-btn edit" @click="$router.push('/settings')">编辑资料</button>
            <template v-else>
              <button class="ha-btn" :class="{ following: isFollowing }" @click="toggleFollow">{{ isFollowing ? "已关注" : "关注" }}</button>
              <button class="ha-btn msg" @click="$router.push('/chat/' + route.params.id)">发私信</button>
            </template>
          </div>
        </div>
      </div>

      <!-- Tabs: equal 1/3 width, full-width underline -->
      <div class="profile-tabs">
        <div class="pt-item" :class="{ active: activeTab === 'notes' }" @click="switchTab('notes')">笔记</div>
        <div class="pt-item" :class="{ active: activeTab === 'favorites' }" @click="switchTab('favorites')">收藏</div>
        <div class="pt-item" :class="{ active: activeTab === 'likes' }" @click="switchTab('likes')">点赞</div>
      </div>

      <!-- Folder management bar -->
      <div v-if="isOwn && activeTab === 'favorites'" class="folder-bar">
        <div class="folder-pills">
          <div class="folder-pill" :class="{ active: selectedFolderId === null }" @click="selectFolder(null)">全部</div>
          <div v-for="f in folders" :key="f.id" class="folder-pill" :class="{ active: selectedFolderId === f.id }" @click="selectFolder(f.id)">
            <span class="folder-pill-name">{{ f.name }}</span>
            <span class="folder-pill-count">{{ f.note_count || 0 }}</span>
            <button v-if="f.name !== '默认收藏夹'" class="folder-pill-del" title="删除收藏夹" @click.stop="deleteFolder(f.id)">×</button>
          </div>
        </div>
        <div class="folder-actions">
          <button class="folder-manage-btn" @click="toggleManageMode">{{ manageMode ? "完成" : "管理" }}</button>
          <button class="folder-add-btn" @click="createFolder">+</button>
        </div>
      </div>

      <!-- Waterfall grid -->
      <div v-if="loading" class="center">加载中...</div>
      <div v-else-if="items.length === 0" class="empty-state">
        <p class="empty-text">{{ emptyText }}</p>
      </div>
      <div v-if="manageMode" class="manage-bar">
        <div class="manage-bar-inner">
          <div class="manage-bar-left">
            <span class="manage-bar-count">已选 {{ selectedItems.length }}</span>
          </div>
          <div class="manage-bar-right">
            <div class="manage-folder-picker" @click="showFolderPicker = true">
              <span class="manage-folder-label">{{ moveTargetFolderName || "移动到..." }}</span>
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#999" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </div>
            <button class="manage-do-btn" :disabled="!moveTargetFolderId || selectedItems.length === 0" @click="doMoveSelected">移动</button>
          </div>
        </div>
      </div>

      <!-- Folder picker sheet -->
      <Teleport to="body">
        <div v-if="showFolderPicker" class="picker-overlay" @click.self="showFolderPicker = false">
          <div class="picker-sheet">
            <div class="picker-handle"></div>
            <div class="picker-title">选择收藏夹</div>
            <div class="picker-list">
              <div v-for="f in folders" :key="f.id" class="picker-item" :class="{ active: moveTargetFolderId === f.id }" @click="selectMoveTarget(f)">
                <span class="picker-item-name">{{ f.name }}</span>
                <span v-if="moveTargetFolderId === f.id" class="picker-item-check">✓</span>
              </div>
            </div>
          </div>
        </div>
      </Teleport>
            <div class="waterfall">
        <div v-for="n in items" :key="n.id" class="wf-card" :class="{ selected: selectedItems.includes(n.id) }" @click="manageMode ? toggleItem(n.id) : noteDetailStore.open(n.id)">
          <div v-if="manageMode" class="wf-check" @click.stop="toggleItem(n.id)">
            <span :class="{ checked: selectedItems.includes(n.id) }">{{ selectedItems.includes(n.id) ? "\u2713" : "" }}</span>
          </div>
          <div class="wf-cover">
            <img v-if="n.cover_img" :src="n.cover_img" :alt="n.title" />
            <div v-else class="wf-placeholder">{{ n.title?.[0] || "?" }}</div>
          </div>
          <div class="wf-bar">
            <span class="wf-title">{{ n.title }}</span>
            <span class="wf-like">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="#999" stroke-width="2" stroke-linejoin="round"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
              {{ n.like_count || 0 }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="center" style="padding: 80px 0;">
      <p style="color: #999; margin-bottom: 16px;">请先登录</p>
      <button class="action-btn" @click="$router.push('/login')">去登录</button>
    </div>
  </div>
  <NoteDetail />
</template>
<script setup>
import { ref, computed, onMounted, watch, defineProps } from "vue"
defineProps({ category: String })
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { accountsApi } from "../api/accounts"
import { notesApi } from "../api/notes"
import { socialApi } from "../api/social"
import { useNoteDetailStore } from "../stores/noteDetail"
import { ElMessage } from "element-plus"
import NoteDetail from "./NoteDetail.vue"

const noteDetailStore = useNoteDetailStore()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const profile = ref(null)
const items = ref([])
const loading = ref(false)
const activeTab = ref("notes")
const isFollowing = ref(false)

const isOwn = computed(() => userStore.isLoggedIn && userStore.user?.id === route.params.id)

const emptyText = computed(() => {
  const map = { notes: "你还没有发布任何内容哦", favorites: "还没有收藏任何内容", likes: "还没有点赞任何内容" }
  return map[activeTab.value] || "暂无内容"
})

onMounted(async () => {
  await loadProfile()
  await loadTab()
})

watch(() => route.params.id, async () => {
  await loadProfile()
  await loadTab()
})

async function loadProfile() {
  try {
    const p = await accountsApi.getProfile(route.params.id)
    profile.value = p
    isFollowing.value = p.is_following || false
  } catch (e) {}
}

async function switchTab(tab) {
  activeTab.value = tab
  if (tab === "favorites" && isOwn.value) {
    selectedFolderId.value = null
    await loadFolders()
  }
  await loadTab()
}

async function loadTab() {
  loading.value = true
  items.value = []
  try {
    const targetId = route.params.id
    if (activeTab.value === "notes") {
      const res = await notesApi.getUserNotes(targetId)
      items.value = res.results || res || []
    } else if (activeTab.value === "favorites") {
      if (isOwn.value) {
        if (selectedFolderId.value) {
          const res = await socialApi.getFavorites(selectedFolderId.value)
          items.value = res.results || res || []
        } else {
          const res = await socialApi.getAllFavorites()
          items.value = res.results || res || []
        }
      } else {
        try {
          const res = await socialApi.getUserFavs(targetId)
          items.value = res.results || res || []
        } catch (e) {
          items.value = []
          ElMessage.warning(e.response?.data?.message || "无法查看该用户的收藏")
        }
      }
    } else if (activeTab.value === "likes") {
      if (isOwn.value) {
        const res = await notesApi.getLikedNotes()
        items.value = res.results || res || []
      } else {
        try {
          const res = await socialApi.getUserLikes(targetId)
          items.value = res.results || res || []
        } catch (e) {
          items.value = []
          ElMessage.warning(e.response?.data?.message || "无法查看该用户的点赞")
        }
      }
    }
  } catch (e) {
    items.value = []
  } finally {
    loading.value = false
  }
}
const folders = ref([])
const selectedFolderId = ref(null)

async function loadFolders() {
  try {
    const res = await socialApi.getFolders()
    folders.value = res || []
  } catch (e) {
    folders.value = []
  }
}

async function selectFolder(folderId) {
  selectedFolderId.value = folderId
  await loadTab()
}

async function createFolder() {
  const name = prompt("请输入新收藏夹名称：")
  if (!name || !name.trim()) return
  try {
    const res = await socialApi.createFolder({ name: name.trim() })
    folders.value.push(res)
    ElMessage.success("收藏夹已创建")
  } catch (e) {
    ElMessage.error("创建失败: " + (e.message || e))
  }
}

async function deleteFolder(folderId) {
  if (!confirm("确定删除该收藏夹？收藏夹内的笔记将自动取消收藏")) return
  try {
    await socialApi.deleteFolder(folderId)
    folders.value = folders.value.filter(f => f.id !== folderId)
    if (selectedFolderId.value === folderId) {
      selectedFolderId.value = null
      await loadTab()
    }
    ElMessage.success("收藏夹已删除")
  } catch (e) {
    ElMessage.error("删除失败: " + (e.message || e))
  }
}

async function toggleFollow() {
  const res = await socialApi.toggleFollow(route.params.id)
  isFollowing.value = res.is_following
  await loadProfile()
}

function showFollowers() {
  router.push({ path: "/follow-list", query: { tab: "followers", user_id: route.params.id } })
}

function showFollowing() {
  router.push({ path: "/follow-list", query: { tab: "following", user_id: route.params.id } })
}

const manageMode = ref(false)
const selectedItems = ref([])
const moveTargetFolderId = ref('')

function toggleManageMode() {
  manageMode.value = !manageMode.value
  if (!manageMode.value) { selectedItems.value = []; moveTargetFolderId.value = '' }
}

function toggleItem(noteId) {
  const idx = selectedItems.value.indexOf(noteId)
  if (idx >= 0) { selectedItems.value.splice(idx, 1) } else { selectedItems.value.push(noteId) }
}

async function doMoveSelected() {
  if (!moveTargetFolderId.value || selectedItems.value.length === 0) return
  try {
    for (const noteId of selectedItems.value) {
      await socialApi.removeFavoriteFromAll(noteId)
      await socialApi.addFavorite({ note_id: noteId, folder_id: moveTargetFolderId.value })
    }
    ElMessage.success("已移动 " + selectedItems.value.length + " 篇笔记")
    selectedItems.value = []
    moveTargetFolderId.value = ''
    await loadTab()
  } catch (e) {
    console.error("move error:", e)
    ElMessage.error("移动失败")
  }
}

const showFolderPicker = ref(false)
const moveTargetFolderName = ref('')

function selectMoveTarget(folder) {
  moveTargetFolderId.value = folder.id
  moveTargetFolderName.value = folder.name
  showFolderPicker.value = false
}
</script>
<style scoped>
.folder-bar { display: flex; align-items: center; gap: 8px; padding: 8px 0; margin-bottom: 8px; }
.folder-pills { display: flex; gap: 6px; flex: 1; overflow-x: auto; padding-bottom: 4px; }
.folder-pills::-webkit-scrollbar { height: 0; }
.folder-pill { display: inline-flex; align-items: center; gap: 4px; padding: 5px 12px; border-radius: 16px; font-size: 13px; color: #666; background: #f5f5f5; cursor: pointer; white-space: nowrap; transition: all 0.15s; }
.folder-pill:hover { background: #eee; }
.folder-pill.active { background: #ff2442; color: #fff; }
.folder-pill-count { font-size: 11px; opacity: 0.7; }
.folder-actions { flex-shrink: 0; }
.folder-add-btn { width: 30px; height: 30px; border-radius: 50%; border: 1px dashed #ccc; background: #fff; color: #999; font-size: 18px; line-height: 1; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.folder-add-btn:hover { border-color: #ff2442; color: #ff2442; }
.profile-page {
  display: flex;
  justify-content: center;
  background: #fff;
  padding: 0 24px;
}
.profile-content {
  width: 100%;
  max-width: 820px;
}

/* ===== Header ===== */
.profile-header {
  display: flex;
  align-items: center;
  gap: 36px;
  padding: 36px 0 28px;
}
.header-avatar { flex-shrink: 0; align-self: flex-start; }
.avatar-ring {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  border: 3px solid #f5f5f5;
  box-shadow: 0 0 0 1px #e8e8e8;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 50%;
}
.avatar-placeholder {
  font-size: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
}
.header-info { flex: 1; min-width: 0; padding-top: 4px; }
.header-name {
  font-size: 24px;
  font-weight: 700;
  color: #222;
  margin: 0 0 4px;
}
.header-id {
  font-size: 13px;
  color: #ccc;
  margin: 0 0 8px;
}
.header-bio {
  font-size: 14px;
  color: #777;
  margin: 0 0 20px;
  line-height: 1.5;
}
.header-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 18px;
}
.hs-item { cursor: pointer; }
.hs-num { font-size: 15px; font-weight: 700; color: #222; }
.hs-label { font-size: 12px; color: #bbb; margin-left: 4px; }
.header-actions { display: flex; gap: 8px; }
.ha-btn {
  background: #ff2442; color: #fff; border: none;
  border-radius: 20px; padding: 8px 28px; font-size: 14px;
  font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.ha-btn:hover { background: #e01e38; }
.ha-btn.following, .ha-btn.edit {
  background: #fff; color: #666; border: 1px solid #ddd;
}
.ha-btn.following:hover, .ha-btn.edit:hover, .ha-btn.msg:hover { border-color: #ff2442; color: #ff2442; }
.ha-btn.msg { background: #fff; color: #ff2442; border: 1px solid #ff2442; }

/* ===== Tabs: equal 1/3, full underline ===== */
.profile-tabs {
  display: flex;
  border-bottom: 2px solid #eee;
  margin-bottom: 20px;
}
.pt-item {
  flex: 1;
  text-align: center;
  padding: 14px 0 12px;
  font-size: 14px;
  color: #ccc;
  cursor: pointer;
  position: relative;
  font-weight: 400;
  transition: color 0.15s;
}
.pt-item:hover { color: #999; }
.pt-item.active {
  color: #222;
  font-weight: 700;
}
.pt-item.active::after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #222;
}

/* ===== Waterfall: column-count 3, strict alignment ===== */
.waterfall {
  column-count: 3;
  column-gap: 14px;
}
.wf-card {
  break-inside: avoid;
  margin-bottom: 14px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #f0f0f0;
}
.wf-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}

/* Cover: consistent rounded top, full width */
.wf-cover {
  width: 100%;
  overflow: hidden;
  background: #f5f5f5;
  line-height: 0;
}
.wf-cover img {
  width: 100%;
  display: block;
}
.wf-placeholder {
  aspect-ratio: 3/4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2em;
  color: white;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

/* Bottom bar: consistent height, title left + like right */
.wf-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  min-height: 40px;
  gap: 6px;
}
.wf-title {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  line-height: 1.3;
}
.wf-like {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
  line-height: 1;
}

/* ===== Utils ===== */
.center { text-align: center; padding: 60px 0; color: #999; font-size: 14px; }
.empty-state { text-align: center; padding: 80px 0; }
.empty-text { font-size: 14px; color: #ccc; }

/* Folder bar - improved */
.folder-bar { display: flex; align-items: center; gap: 8px; padding: 12px 0; overflow-x: auto; }
::-webkit-scrollbar { height: 0; }
.folder-pills { display: flex; gap: 8px; flex: 1; overflow-x: auto; }
.folder-pill { display: flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: 20px; font-size: 13px; color: #666; background: #f5f5f5; cursor: pointer; white-space: nowrap; transition: all 0.2s; flex-shrink: 0; }
.folder-pill:hover { background: #eee; }
.folder-pill.active { background: #ff2442; color: #fff; }
.folder-pill.active .folder-pill-del { color: rgba(255,255,255,0.6); }
.folder-pill.active .folder-pill-del:hover { color: #fff; }
.folder-pill-name { max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.folder-pill-count { font-size: 11px; opacity: 0.7; }
.folder-pill-del { background: none; border: none; font-size: 14px; color: #bbb; cursor: pointer; padding: 0; line-height: 1; margin-left: 2px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; transition: color 0.15s; }
.folder-pill-del:hover { color: #ff2442 !important; }
.folder-actions { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.folder-manage-btn { background: none; border: 1px solid #ddd; border-radius: 16px; padding: 5px 12px; font-size: 12px; color: #666; cursor: pointer; white-space: nowrap; transition: all 0.15s; }
.folder-manage-btn:hover { border-color: #ff2442; color: #ff2442; }
.folder-add-btn { width: 32px; height: 32px; border-radius: 50%; border: 1px dashed #ddd; background: none; font-size: 18px; color: #999; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; flex-shrink: 0; }
.folder-add-btn:hover { border-color: #ff2442; color: #ff2442; }
/* Manage bar - floating bottom */
.manage-bar { position: fixed; bottom: 0; left: 0; right: 0; z-index: 100; background: #fff; border-top: 1px solid #f0f0f0; padding: 0 16px; padding-bottom: env(safe-area-inset-bottom, 12px); box-shadow: 0 -2px 12px rgba(0,0,0,0.06); }
.manage-bar-inner { display: flex; align-items: center; justify-content: space-between; max-width: 1000px; margin: 0 auto; padding: 10px 0; }
.manage-bar-left { display: flex; align-items: center; gap: 8px; }
.manage-bar-count { font-size: 14px; font-weight: 500; color: #ff2442; }
.manage-bar-right { display: flex; align-items: center; gap: 10px; }
.manage-folder-picker { display: flex; align-items: center; gap: 4px; padding: 7px 12px; border: 1px solid #e0e0e0; border-radius: 8px; cursor: pointer; transition: border-color 0.15s; }
.manage-folder-picker:hover { border-color: #ff2442; }
.manage-folder-label { font-size: 13px; color: #333; min-width: 60px; }
.manage-do-btn { background: #ff2442; color: #fff; border: none; border-radius: 18px; padding: 8px 20px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.15s; }
.manage-do-btn:hover { background: #d61e38; }
.manage-do-btn:disabled { background: #f0f0f0; color: #ccc; cursor: default; }

/* Folder picker sheet */
.picker-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.35); z-index: 200; display: flex; align-items: flex-end; justify-content: center; }
.picker-sheet { background: #fff; border-radius: 16px 16px 0 0; width: 100%; max-width: 480px; padding: 16px 0 32px; }
.picker-handle { width: 36px; height: 4px; background: #ddd; border-radius: 2px; margin: 0 auto 12px; }
.picker-title { text-align: center; font-size: 16px; font-weight: 600; color: #333; margin-bottom: 8px; }
.picker-list { max-height: 300px; overflow-y: auto; padding: 0 16px; }
.picker-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; border-radius: 10px; cursor: pointer; transition: background 0.1s; }
.picker-item:hover { background: #f5f5f5; }
.picker-item.active { background: #fff5f5; }
.picker-item-name { font-size: 14px; color: #333; }
.picker-item-check { color: #ff2442; font-size: 16px; font-weight: 600; }

/* Waterfall spacing */
.profile-content { padding-bottom: 70px; }
.wf-card.selected { outline: 2px solid #ff2442; outline-offset: -2px; border-radius: 12px; position: relative; }
.wf-check { position: absolute; top: 8px; left: 8px; z-index: 2; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.wf-check span { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.8); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: transparent; background: rgba(0,0,0,0.15); transition: all 0.15s; }
.wf-check span.checked { background: #ff2442; border-color: #ff2442; color: #fff; }
.wf-card:hover .wf-check span { border-color: #fff; }
</style>





