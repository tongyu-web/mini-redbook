<template>
  <div class="message-page">
    <div class="content">
      <!-- Search bar -->
      <div class="msg-search-box">
        <div class="msg-search-wrapper">
          <svg class="msg-search-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" width="18" height="18">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="searchText"
            class="msg-search-input"
            placeholder="搜索消息..."
            @keyup.enter="doSearch"
          />
        </div>
      </div>
      <el-tabs v-model="activeTab" @tab-change="loadTab">
        <el-tab-pane label="评论和@" name="comment">
          <div v-if="commentItems.length" class="notif-list">
            <div v-for="n in commentItems" :key="n.id" class="notif-item" @click="handleClick(n)">
              <el-avatar :size="40" :src="n.from_user_avatar" />
              <div class="notif-body">
                <p><strong>{{ n.from_user_nickname }}</strong> 评论了你的笔记</p>
                <p class="notif-preview">{{ n.comment_preview || n.content }}</p>
                <span class="time">{{ n.created_at }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无评论</div>
        </el-tab-pane>
        <el-tab-pane label="赞和收藏" name="like">
          <div v-if="likeItems.length" class="notif-list">
            <div v-for="n in likeItems" :key="n.id" class="notif-item" @click="handleClick(n)">
              <el-avatar :size="40" :src="n.from_user_avatar" />
              <div class="notif-body">
                <p><strong>{{ n.from_user_nickname }}</strong> {{ n.type === "favorite" ? "收藏" : "赞" }}了你的笔记</p>
                <span class="time">{{ n.created_at }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无赞和收藏</div>
        </el-tab-pane>
        <el-tab-pane label="新增关注" name="follow">
          <div v-if="followItems.length" class="notif-list">
            <div v-for="n in followItems" :key="n.id" class="notif-item" @click="handleClick(n)">
              <el-avatar :size="40" :src="n.from_user_avatar" />
              <div class="notif-body">
                <p><strong>{{ n.from_user_nickname }}</strong> 关注了你</p>
                <span class="time">{{ n.created_at }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无新增关注</div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { messageApi } from "../api/messaging"
import { useNotificationStore } from "../stores/notification"

const router = useRouter()
const notificationStore = useNotificationStore()
const activeTab = ref("comment")
const searchText = ref("")

const notifications = ref([])
const commentItems = ref([])
const likeItems = ref([])
const followItems = ref([])

onMounted(() => {
  loadNotifications()
})

async function loadNotifications() {
  const res = await messageApi.getNotifications({})
  notifications.value = res.results || res || []
  filterItems()
}

function filterItems() {
  commentItems.value = notifications.value.filter(n => n.type === "comment")
  likeItems.value = notifications.value.filter(n => n.type === "like" || n.type === "favorite")
  followItems.value = notifications.value.filter(n => n.type === "follow")
}

function loadTab() {
  // already filtered
}

function typeText(t) {
  const map = { like: "点赞", comment: "评论", follow: "关注", favorite: "收藏" }
  return map[t] || t
}

function doSearch() {
  if (searchText.value.trim()) {
    router.push("/search?q=" + encodeURIComponent(searchText.value.trim()))
  }
}

async function handleClick(n) {
  if (!n.is_read) {
    await messageApi.markRead(n.id)
    notificationStore.fetchUnreadCount()
  }
}
</script>

<style scoped>
.message-page { }
.msg-search-box { margin-bottom: 16px; }
.msg-search-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 0 16px;
  height: 42px;
  gap: 8px;
  border: 1px solid transparent;
  transition: border-color 0.2s;
}
.msg-search-wrapper:focus-within { border-color: #ff2442; }
.msg-search-icon { flex-shrink: 0; }
.msg-search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
  color: #333;
}
.msg-search-input::placeholder { color: #bbb; }
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.empty-state { text-align: center; padding: 60px 0; color: #bbb; font-size: 14px; }
.notif-list { display: flex; flex-direction: column; }
.notif-item { display: flex; gap: 12px; padding: 14px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.notif-item:hover { background: #fafafa; }
.notif-body { flex: 1; min-width: 0; }
.notif-body p { margin: 0 0 2px; font-size: 14px; }
.notif-preview { font-size: 13px; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.time { font-size: 12px; color: #bbb; }
</style>