<template>
  <div class="profile">
    <NavBar />
    <div class="content" v-if="profile">
      <!-- 未完善资料引导 -->
      <el-alert v-if="!profile.is_profile_complete && isOwn" title="完善个人资料" type="warning" show-icon closable class="mb-3">
        <template #default>
          完善资料，展示更好的个人形象
        </template>
        <template #action>
          <el-button size="small" type="warning" @click="$router.push('/settings')">去完善</el-button>
        </template>
      </el-alert>

      <!-- 头像 + 基础信息 -->
      <div class="profile-header">
        <el-avatar :size="72" :src="profile.avatar_url" />
        <div class="profile-info">
          <h2>{{ profile.nickname || "未设置昵称" }}</h2>
          <p class="bio">{{ profile.bio || "这个人很懒，什么都没写" }}</p>
          <div class="stat-row">
            <div class="stat-item" @click="showFollowers">
              <span class="stat-num">{{ profile.follower_count }}</span>
              <span class="stat-label">粉丝</span>
            </div>
            <div class="stat-item" @click="showFollowing">
              <span class="stat-num">{{ profile.following_count }}</span>
              <span class="stat-label">关注</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">{{ profile.like_received_count }}</span>
              <span class="stat-label">获赞</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">{{ profile.note_count }}</span>
              <span class="stat-label">笔记</span>
            </div>
          </div>
          <el-button v-if="isOwn" size="small" @click="$router.push('/settings')" class="edit-btn">编辑资料</el-button>
          <el-button v-else size="small" :type="isFollowing ? 'default' : 'primary'" @click="toggleFollow" class="edit-btn">
            {{ isFollowing ? "已关注" : "关注" }}
          </el-button>
        </div>
      </div>

      <!-- Tab 切换 -->
      <el-tabs v-model="activeTab" class="content-tabs" @tab-change="loadTab">
        <el-tab-pane label="笔记" name="notes" />
        <el-tab-pane label="收藏" name="favorites" />
        <el-tab-pane label="点赞" name="likes" />
      </el-tabs>

      <!-- 内容列表 -->
      <div v-if="loading" class="center">加载中...</div>
      <div v-else-if="items.length === 0" class="center empty">{{ emptyText }}</div>
      <div v-else class="note-grid">
        <div v-for="n in items" :key="n.id" class="note-card" @click="$router.push('/note/' + n.id)">
          <div class="cover">
            <img v-if="n.cover_img" :src="n.cover_img" :alt="n.title" />
            <div v-else class="placeholder">{{ n.title?.[0] || "?" }}</div>
          </div>
          <div class="note-info">
            <h4>{{ n.title }}</h4>
            <span>❤️ {{ n.like_count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 未登录 -->
    <div v-else class="center">
      <p>请先登录</p>
      <el-button @click="$router.push('/login')">去登录</el-button>
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
import NavBar from "../components/NavBar.vue"

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
  const map = { notes: "暂无笔记", favorites: "暂无收藏", likes: "暂无点赞" }
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
  } catch (e) {
    if (e.message === "未登录") router.push("/login")
  }
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
.profile { padding-bottom: 60px; }
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.mb-3 { margin-bottom: 16px; }
.center { text-align: center; padding: 40px; color: #999; }
.empty { color: #bbb; }

.profile-header { display: flex; gap: 16px; margin-bottom: 20px; align-items: flex-start; }
.profile-info { flex: 1; }
.profile-info h2 { margin: 0 0 4px; font-size: 20px; }
.bio { color: #666; font-size: 13px; margin-bottom: 12px; }
.stat-row { display: flex; gap: 20px; margin-bottom: 12px; }
.stat-item { text-align: center; cursor: pointer; }
.stat-num { display: block; font-size: 18px; font-weight: 700; }
.stat-label { font-size: 12px; color: #999; }
.edit-btn { margin-top: 4px; }

.content-tabs { margin-bottom: 16px; }
:deep(.el-tabs__item) { font-size: 14px; }

.note-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.note-card { background: white; border-radius: 12px; overflow: hidden; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.cover { aspect-ratio: 3/4; overflow: hidden; background: #f0f0f0; }
.cover img { width: 100%; height: 100%; object-fit: cover; }
.placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2em; color: white; background: linear-gradient(135deg, #ff6b6b, #ee5a24); }
.note-info { padding: 8px 10px; display: flex; justify-content: space-between; align-items: center; }
.note-info h4 { margin: 0; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.note-info span { font-size: 12px; color: #999; margin-left: 8px; }
</style>
