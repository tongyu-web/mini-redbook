<template>
  <div class="message-page">
    <NavBar />
    <div class="content">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="通知" name="notification">
          <div class="filter-btns">
            <el-button v-for="t in types" :key="t.key" :type="filterType === t.key ? 'primary' : 'default'" size="small" @click="filterType = t.key; loadNotifications()">{{ t.label }}</el-button>
          </div>
          <el-button size="small" @click="markAllRead" class="read-all">全部已读</el-button>
          <div v-for="n in notifications" :key="n.id" class="notif-item" @click="handleClick(n)">
            <el-avatar :size="36" :src="n.from_user_avatar" />
            <div class="notif-body">
              <p><strong>{{ n.from_user_nickname }}</strong> {{ typeText(n.type) }}了你的笔记</p>
              <span class="time">{{ n.created_at }}</span>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="私信" name="chat">
          <div v-for="c in conversations" :key="c.user_id" class="conv-item" @click="$router.push('/chat/' + c.user_id)">
            <el-avatar :size="40" :src="c.avatar_url" />
            <div class="conv-body">
              <div class="conv-header">
                <strong>{{ c.nickname }}</strong>
                <span v-if="c.unread_count > 0" class="unread-badge">{{ c.unread_count }}</span>
              </div>
              <p class="last-msg">{{ c.last_message }}</p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { messageApi } from "../api/messaging"
import { useNotificationStore } from "../stores/notification"
import NavBar from "../components/NavBar.vue"

const notificationStore = useNotificationStore()
const activeTab = ref("notification")
const filterType = ref("")
const notifications = ref([])
const conversations = ref([])
const types = ref([{key:"",label:"全部"}, {key:"like",label:"点赞"}, {key:"comment",label:"评论"}, {key:"follow",label:"关注"}, {key:"favorite",label:"收藏"}])

onMounted(() => {
  loadNotifications()
  loadConversations()
})

async function loadNotifications() {
  const params = filterType.value ? { type: filterType.value } : {}
  const res = await messageApi.getNotifications(params)
  notifications.value = res.results || res || []
}

async function loadConversations() {
  conversations.value = await messageApi.getConversations()
}

async function markAllRead() {
  await messageApi.markAllRead()
  notificationStore.reset()
}

function typeText(t) {
  const map = { like: "点赞", comment: "评论", follow: "关注", favorite: "收藏" }
  return map[t] || t
}

async function handleClick(n) {
  if (!n.is_read) {
    await messageApi.markRead(n.id)
    notificationStore.fetchUnreadCount()
  }
}
</script>

<style scoped>
.message-page { padding-bottom: 60px; }
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.filter-btns { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.read-all { margin-bottom: 12px; }
.notif-item { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.notif-body p { margin: 0; font-size: 14px; }
.time { font-size: 12px; color: #999; }
.conv-item { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.conv-header { display: flex; align-items: center; gap: 6px; }
.last-msg { font-size: 13px; color: #999; margin: 2px 0 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.unread-badge { background: #ff2442; color: white; font-size: 11px; border-radius: 10px; padding: 1px 6px; }
</style>
