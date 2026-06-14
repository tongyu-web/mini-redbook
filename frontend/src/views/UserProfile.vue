<template>
  <div class="profile-page">
    <div class="profile-content" v-if="profile">
      <!-- Incomplete profile alert -->
      <div v-if="!profile.is_profile_complete && isOwn" class="profile-alert" @click="$router.push('/settings')">
        <span>完善资料，展示更好的个人形象</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </div>

      <!-- Profile header -->
      <div class="profile-header">
        <div class="avatar-wrapper">
          <img v-if="profile.avatar_url" :src="profile.avatar_url" class="avatar" />
          <div v-else class="avatar avatar-placeholder">{{ (profile.nickname || "?")[0] }}</div>
        </div>
        <h1 class="username">{{ profile.nickname || "未设置昵称" }}</h1>
        <p class="user-id">mini-redbook ID：{{ profile.user_id || route.params.id }}</p>
        <p class="bio">{{ profile.bio || "这个人很懒，什么都没写" }}</p>

        <!-- Social stats -->
        <div class="stat-row">
          <div class="stat-item" @click="showFollowing">
            <span class="stat-num">{{ profile.following_count }}</span>
            <span class="stat-label">关注</span>
          </div>
          <div class="stat-item" @click="showFollowers">
            <span class="stat-num">{{ profile.follower_count }}</span>
            <span class="stat-label">粉丝</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ (profile.like_received_count || 0) + (profile.favorite_received_count || 0) }}</span>
            <span class="stat-label">获赞与收藏</span>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="action-row">
          <button v-if="isOwn" class="action-btn edit-btn" @click="$router.push('/settings')">编辑资料</button>
          <button v-else class="action-btn" :class="{ 'following': isFollowing }" @click="toggleFollow">
            {{ isFollowing ? "已关注" : "关注" }}
          </button>
        </div>
      </div>

      <!-- Content tabs -->
      <div class="tabs-bar">
        <div class="tab" :class="{ active: activeTab === 'notes' }" @click="switchTab('notes')">笔记</div>
        <div class="tab" :class="{ active: activeTab === 'favorites' }" @click="switchTab('favorites')">收藏</div>
        <div class="tab" :class="{ active: activeTab === 'likes' }" @click="switchTab('likes')">点赞</div>
      </div>

      <!-- Content list -->
      <div v-if="loading" class="center">加载中...</div>
      <div v-else-if="items.length === 0" class="empty-state">
        <div class="empty-illustration">
          <svg viewBox="0 0 120 100" fill="none" width="120" height="100">
            <rect x="25" y="10" width="70" height="50" rx="10" stroke="#ddd" stroke-width="2" fill="#f9f9f9"/>
            <line x1="45" y1="25" x2="75" y2="25" stroke="#ddd" stroke-width="2" stroke-linecap="round"/>
            <line x1="45" y1="35" x2="65" y2="35" stroke="#ddd" stroke-width="2" stroke-linecap="round"/>
            <line x1="45" y1="45" x2="55" y2="45" stroke="#ddd" stroke-width="2" stroke-linecap="round"/>
            <circle cx="60" cy="80" r="15" stroke="#ddd" stroke-width="2" fill="#f9f9f9"/>
            <line x1="72" y1="85" x2="85" y2="75" stroke="#ddd" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <p class="empty-text">{{ emptyText }}</p>
      </div>
      <div v-else class="note-grid">
        <div v-for="n in items" :key="n.id" class="note-card" @click="$router.push('/note/' + n.id)">
          <div class="card-cover">
            <img v-if="n.cover_img" :src="n.cover_img" :alt="n.title" />
            <div v-else class="card-placeholder">{{ n.title?.[0] || "?" }}</div>
          </div>
          <div class="card-info">
            <h4 class="card-title">{{ n.title }}</h4>
            <div class="card-meta">
              <svg viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" width="12" height="12">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
              <span>{{ n.like_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Not logged in -->
    <div v-else class="center" style="padding: 80px 0;">
      <p style="color: #999; margin-bottom: 16px;">请先登录</p>
      <button class="action-btn" @click="$router.push('/login')">去登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { accountsApi } from "../api/accounts"
import { notesApi } from "../api/notes"
import { socialApi } from "../api/social"

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
    profile.value = await accountsApi.getProfile(route.params.id)
  } catch (e) {}
}

async function switchTab(tab) {
  activeTab.value = tab
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
        const res = await socialApi.getAllFavorites()
        items.value = res.results || res || []
      }
    } else if (activeTab.value === "likes") {
      if (isOwn.value) {
        const res = await notesApi.getLikedNotes()
        items.value = res.results || res || []
      }
    }
  } catch (e) {
    items.value = []
  } finally {
    loading.value = false
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
.profile-page {
  padding: 24px;
  display: flex;
  justify-content: center;
}
.profile-content {
  width: 100%;
  max-width: 700px;
}

/* Alert */
.profile-alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff8e6;
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 13px;
  color: #b87a00;
  margin-bottom: 20px;
  cursor: pointer;
}

/* Profile header */
.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 20px;
}
.avatar-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 12px;
  flex-shrink: 0;
}
.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ff2442;
  color: white;
  font-size: 28px;
  font-weight: 700;
}
.username {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px;
  color: #222;
}
.user-id {
  font-size: 13px;
  color: #999;
  margin: 0 0 8px;
}
.bio {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px;
  line-height: 1.5;
}

/* Social stats */
.stat-row {
  display: flex;
  gap: 32px;
  justify-content: center;
  margin-bottom: 16px;
}
.stat-item {
  text-align: center;
  cursor: pointer;
  padding: 0 4px;
}
.stat-num {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #222;
}
.stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

/* Action buttons */
.action-row {
  display: flex;
  gap: 8px;
  justify-content: center;
}
.action-btn {
  background: #ff2442;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 8px 28px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.action-btn:hover {
  background: #e01e38;
}
.action-btn.following {
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
}
.action-btn.following:hover {
  border-color: #ff2442;
  color: #ff2442;
}
.edit-btn {
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
}
.edit-btn:hover {
  border-color: #ff2442;
  color: #ff2442;
  background: #fff;
}

/* Tabs */
.tabs-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 14px;
  color: #888;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}
.tab:hover {
  color: #555;
}
.tab.active {
  color: #ff2442;
  font-weight: 600;
}
.tab.active::after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 3px;
  background: #ff2442;
  border-radius: 2px;
}

/* Loading & Empty */
.center { text-align: center; padding: 40px; color: #999; font-size: 14px; }
.empty-state {
  text-align: center;
  padding: 60px 0;
}
.empty-illustration {
  margin-bottom: 16px;
  opacity: 0.5;
}
.empty-text {
  font-size: 14px;
  color: #bbb;
}

/* Note grid */
.note-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.note-card {
  background: white;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}
.note-card:hover {
  transform: translateY(-3px);
}
.card-cover {
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f0f0f0;
}
.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.card-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2em;
  color: white;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}
.card-info {
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
}
</style>