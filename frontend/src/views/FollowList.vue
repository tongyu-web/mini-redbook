<template>
  <div class="follow-list">
    <div class="header">
      <el-button text @click="$router.back()">← 返回</el-button>
      <h2>{{ tab === "followers" ? "粉丝" : "关注" }}</h2>
    </div>
    <div class="content">
      <div v-if="loading" class="center">加载中...</div>
      <div v-else-if="items.length === 0" class="center empty">{{ tab === "followers" ? "暂无粉丝" : "暂无关注" }}</div>
      <div v-else>
        <div v-for="item in items" :key="item.id" class="user-item">
          <div class="user-info" @click="$router.push('/user/' + item.id)">
            <el-avatar :size="44" :src="item.avatar_url" />
            <div class="user-meta">
              <span class="nickname">{{ item.nickname || item.username }}</span>
              <span class="bio">{{ item.bio || (item.is_following ? "已关注" : "") }}</span>
            </div>
          </div>
          <div class="user-actions">
            <el-button
              v-if="tab === 'followers' && isOwn"
              size="small"
              text
              type="danger"
              @click="removeFollower(item.id)"
            >移除</el-button>
            <el-button
              v-if="tab === 'following'"
              size="small"
              :type="item.is_following ? 'default' : 'primary'"
              @click="toggleFollow(item)"
            >{{ item.is_following ? "已关注" : "关注" }}</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { accountsApi } from "../api/accounts"
import { socialApi } from "../api/social"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const tab = ref(route.query.tab || "followers")
const targetUserId = ref(route.query.user_id || userStore.user?.id || "")
const items = ref([])
const loading = ref(true)

const isOwn = computed(() => userStore.isLoggedIn && userStore.user?.id === targetUserId.value)

onMounted(loadList)

async function loadList() {
  loading.value = true
  try {
    if (tab.value === "followers") {
      const res = await accountsApi.getFollowers(targetUserId.value)
      items.value = res.results || res || []
    } else {
      const res = await accountsApi.getFollowing(targetUserId.value)
      items.value = res.results || res || []
    }
  } catch (e) {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function toggleFollow(item) {
  const res = await socialApi.toggleFollow(item.id)
  item.is_following = res.is_following
}

async function removeFollower(userId) {
  try {
    await socialApi.removeFollower(userId)
    items.value = items.value.filter(i => i.id !== userId)
  } catch (e) {}
}
</script>

<style scoped>
.follow-list { min-height: 100vh; background: #fff; }
.header { display: flex; align-items: center; gap: 8px; padding: 12px 16px; border-bottom: 1px solid #eee; position: sticky; top: 0; background: white; z-index: 10; }
.header h2 { font-size: 16px; margin: 0; }
.content { max-width: 600px; margin: 0 auto; padding: 0 16px; }
.center { text-align: center; padding: 40px; color: #999; }
.user-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.user-info { display: flex; align-items: center; gap: 12px; cursor: pointer; flex: 1; }
.user-meta { display: flex; flex-direction: column; }
.nickname { font-weight: 600; font-size: 14px; }
.bio { font-size: 12px; color: #999; margin-top: 2px; }
</style>
