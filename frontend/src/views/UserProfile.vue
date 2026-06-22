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
            {{ f.name }}
            <span class="folder-pill-count">{{ f.note_count || 0 }}</span>
          </div>
        </div>
        <div class="folder-actions">
          <button class="folder-add-btn" @click="createFolder">+</button>
        </div>
      </div>

      <!-- Waterfall grid -->
      <div v-if="loading" class="center">加载中...</div>
      <div v-else-if="items.length === 0" class="empty-state">
        <p class="empty-text">{{ emptyText }}</p>
      </div>
      <div v-else class="waterfall">
        <div v-for="n in items" :key="n.id" class="wf-card" @click="noteDetailStore.open(n.id)">
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
  if (!confirm("确定删除该收藏夹？收藏夹内的笔记不会被删除")) return
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
</style>





