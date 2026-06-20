<template>
  <div class="message-page">
    <div class="content">
      <el-tabs v-model="activeTab" @tab-change="loadTab">
        <el-tab-pane label="私信" name="conversations">
          <div v-if="conversations.length" class="conv-list">
            <div v-for="conv in conversations" :key="conv.user_id" class="conv-item" @click="openChat(conv.user_id)">
              <img class="conv-avatar" :src="conv.avatar_url || defaultAvatar" />
              <div class="conv-body">
                <div class="conv-top">
                  <strong class="conv-name">{{ conv.nickname }}</strong>
                  <span class="conv-time">{{ conv.last_time }}</span>
                </div>
                <div class="conv-bottom">
                  <span class="conv-last-msg">{{ conv.last_message || "暂无消息" }}</span>
                  <span v-if="conv.unread_count > 0" class="conv-unread">{{ conv.unread_count > 99 ? "99+" : conv.unread_count }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无私信</div>
        </el-tab-pane>
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
        <el-tab-pane label="消息通知" name="message">
          <div v-if="messageItems.length" class="notif-list">
            <div v-for="n in messageItems" :key="n.id" class="notif-item" @click="handleMessageNotif(n)">
              <el-avatar :size="40" :src="n.from_user_avatar" />
              <div class="notif-body">
                <p><strong>{{ n.from_user_nickname }}</strong> 给你发了一条私信</p>
                <p class="notif-preview">{{ n.content }}</p>
                <span class="time">{{ n.created_at }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">暂无消息通知</div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { messageApi } from "../api/messaging"
import { useNotificationStore } from "../stores/notification"

const router = useRouter()
const notificationStore = useNotificationStore()
const activeTab = ref("conversations")

const defaultAvatar = computed(() => "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50' fill='%23f0f0f0'/%3E%3Ctext x='50' y='55' text-anchor='middle' font-size='40' fill='%23ccc'%3E%F0%9F%91%A4%3C/text%3E%3C/svg%3E")

const notifications = ref([])
const commentItems = ref([])
const likeItems = ref([])
const followItems = ref([])
const messageItems = ref([])
const conversations = ref([])

onMounted(() => {
  loadConversations()
  loadNotifications()
})

async function loadConversations() {
  try {
    const data = await messageApi.getConversations()
    conversations.value = Array.isArray(data) ? data : (data.results || data || [])
  } catch (e) {
    conversations.value = []
  }
}

async function loadNotifications() {
  try {
    const data = await messageApi.getNotifications({})
    notifications.value = data.results || data || []
  } catch (e) {
    notifications.value = []
  }
  filterItems()
}

function filterItems() {
  commentItems.value = notifications.value.filter(n => n.type === "comment")
  likeItems.value = notifications.value.filter(n => n.type === "like" || n.type === "favorite")
  followItems.value = notifications.value.filter(n => n.type === "follow")
  messageItems.value = notifications.value.filter(n => n.type === "message")
}

function loadTab() {
  if (activeTab.value === "conversations") {
    loadConversations()
  }
}


function openChat(userId) {
  router.push("/chat/" + userId)
}

async function handleMessageNotif(n) {
  if (!n.is_read) {
    await messageApi.markRead(n.id)
    notificationStore.fetchUnreadCount()
  }
  if (n.from_user) {
    router.push("/chat/" + n.from_user)
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
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.empty-state { text-align: center; padding: 60px 0; color: #bbb; font-size: 14px; }

/* Conversations */
.conv-list { display: flex; flex-direction: column; }
.conv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.12s;
}
.conv-item:hover { background: #fafafa; }
.conv-avatar {
  width: 48px; height: 48px; border-radius: 50%; object-fit: cover; flex-shrink: 0;
  background: #f0f0f0;
}
.conv-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.conv-top { display: flex; justify-content: space-between; align-items: center; }
.conv-name { font-size: 14px; color: #333; }
.conv-time { font-size: 11px; color: #bbb; }
.conv-bottom { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.conv-last-msg {
  font-size: 13px; color: #999;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1;
}
.conv-unread {
  background: #ff2442; color: white; font-size: 10px; border-radius: 10px;
  padding: 1px 5px; min-width: 16px; text-align: center; flex-shrink: 0;
}

/* Notifications */
.notif-list { display: flex; flex-direction: column; }
.notif-item { display: flex; gap: 12px; padding: 14px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.notif-item:hover { background: #fafafa; }
.notif-body { flex: 1; min-width: 0; }
.notif-body p { margin: 0 0 2px; font-size: 14px; }
.notif-preview { font-size: 13px; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.time { font-size: 12px; color: #bbb; }
</style>



