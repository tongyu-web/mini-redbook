<template>
  <div class="profile">
    <NavBar />
    <div class="content" v-if="profile">
      <!-- 未完善资料引导 -->
      <el-alert v-if="!profile.is_profile_complete && isOwn" title="完善个人资料" type="warning" show-icon :description="'完善资料，展示更好的个人形象'" closable class="mb-3">
        <template #action>
          <el-button size="small" type="warning" @click="$router.push('/settings')">去完善</el-button>
        </template>
      </el-alert>

      <div class="header">
        <el-avatar :size="72" :src="profile.avatar_url" />
        <div class="info">
          <h2>{{ profile.nickname || "未设置昵称" }}</h2>
          <p class="bio">{{ profile.bio || "这个人很懒，什么都没写" }}</p>
          <div class="stats">
            <span>{{ profile.note_count }} 笔记</span>
            <span>{{ profile.follower_count }} 粉丝</span>
            <span>{{ profile.following_count }} 关注</span>
          </div>
          <el-button v-if="isOwn" size="small" @click="$router.push('/settings')" class="mt-2">编辑资料</el-button>
          <el-button v-else size="small" :type="isFollowing ? 'default' : 'primary'" @click="toggleFollow">
            {{ isFollowing ? "已关注" : "关注" }}
          </el-button>
        </div>
      </div>

      <div class="notes" v-if="notes.length">
        <div v-for="n in notes" :key="n.id" class="note-item" @click="$router.push('/note/' + n.id)">
          <img v-if="n.cover_img" :src="n.cover_img" />
          <div v-else class="placeholder">{{ n.title?.[0] }}</div>
          <span>{{ n.title }}</span>
        </div>
      </div>
      <div v-else class="empty">暂无笔记</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useUserStore } from "../stores/user"
import { accountsApi } from "../api/accounts"
import { socialApi } from "../api/social"
import { notesApi } from "../api/notes"
import NavBar from "../components/NavBar.vue"

const route = useRoute()
const userStore = useUserStore()
const profile = ref(null)
const notes = ref([])
const isFollowing = ref(false)
const isOwn = computed(() => userStore.user?.id === route.params.id)

onMounted(async () => {
  try {
    profile.value = await accountsApi.getProfile(route.params.id)
    const res = await notesApi.getNotes()
    notes.value = res.results || res || []
  } catch (e) {}
})

async function toggleFollow() {
  const res = await socialApi.toggleFollow(route.params.id)
  isFollowing.value = res.is_following
}
</script>

<style scoped>
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.header { display: flex; gap: 16px; align-items: flex-start; margin-bottom: 20px; }
.stats { display: flex; gap: 16px; color: #666; font-size: 13px; margin-top: 8px; }
.bio { color: #666; font-size: 13px; margin-top: 4px; }
.mb-3 { margin-bottom: 16px; }
.mt-2 { margin-top: 8px; }
.notes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.note-item { cursor: pointer; text-align: center; }
.note-item img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; }
.placeholder { width: 100%; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; font-size: 1.5em; border-radius: 8px; }
.empty { text-align: center; padding: 40px; color: #999; }
</style>

