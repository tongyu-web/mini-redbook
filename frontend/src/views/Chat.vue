<template>
  <div class="chat">
    <div class="header">
      <el-button text @click="goBack">← 返回</el-button>
      <strong>{{ otherUser?.nickname || "聊天" }}</strong>
      <div class="header-spacer"></div>
      <el-dropdown v-if="otherUser" @command="handleHeaderCommand" trigger="click">
        <el-button text circle size="small"><span style="font-size:18px">&#8942;</span></el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="viewProfile">查看主页</el-dropdown-item>
            <el-dropdown-item command="deleteConversation" divided>&#128465; 删除会话</el-dropdown-item>
            <el-dropdown-item command="blockUser">&#128274; {{ isBlocked ? "取消屏蔽" : "屏蔽联系人" }}</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    <div class="messages" ref="msgRef">
      <div v-if="messages.length === 0" class="empty-msg">暂无消息，发送第一条消息吧</div>
      <div v-for="m in messages" :key="m.id" class="msg" :class="{ mine: m.from_user === currentUserId }">
        <div class="bubble">{{ m.content }}</div>
        <span class="time">{{ formatTime(m.created_at) }}</span>
      </div>
    </div>
    <div class="input-area">
      <el-input v-model="text" placeholder="输入消息..." @keyup.enter="send" />
      <el-button type="primary" @click="send" :disabled="!text.trim()">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import { useUserStore } from "../stores/user"
import { useNotificationStore } from "../stores/notification"
import { messageApi } from "../api/messaging"
import { accountsApi } from "../api/accounts"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const messages = ref([])
const text = ref("")
const otherUser = ref(null)
const msgRef = ref(null)
const isBlocked = ref(false)
const currentUserId = computed(() => userStore.user?.id)
let pollTimer = null

onMounted(async () => {
  try {
    const profileData = await accountsApi.getProfile(route.params.userId)
    otherUser.value = profileData
  } catch (e) {
    otherUser.value = { nickname: "用户" }
  }
  await loadMessages()
  // Auto-poll for new messages every 3 seconds while chat is open
  pollTimer = setInterval(loadMessages, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

function goBack() {
  router.push("/message")
}

function formatTime(t) {
  if (!t) return ""
  const d = new Date(t)
  const now = new Date()
  const pad = n => String(n).padStart(2, "0")
  if (d.toDateString() === now.toDateString()) {
    return pad(d.getHours()) + ":" + pad(d.getMinutes())
  }
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) return "昨天 " + pad(d.getHours()) + ":" + pad(d.getMinutes())
  return pad(d.getMonth() + 1) + "/" + pad(d.getDate()) + " " + pad(d.getHours()) + ":" + pad(d.getMinutes())
}

async function loadMessages() {
  try {
    const res = await messageApi.getMessages(route.params.userId)
    messages.value = res.results || res || []
  } catch (e) {
    messages.value = []
  }
  await nextTick()
  if (msgRef.value) msgRef.value.scrollTop = msgRef.value.scrollHeight
}

async function send() {
  if (!text.value.trim()) return
  try {
    await messageApi.sendMessage({ to_user_id: route.params.userId, content: text.value })
    text.value = ""
    await loadMessages()
    // Refresh notification badge
    notificationStore.fetchUnreadCount()
  } catch (e) {
    ElMessage.error("发送失败: " + (e.message || e))
  }
}

async function handleHeaderCommand(cmd) {
  if (cmd === "viewProfile") {
    router.push("/user/" + route.params.userId)
  } else if (cmd === "deleteConversation") {
    try {
      await ElMessageBox.confirm("确定删除与 " + (otherUser.value?.nickname || "该用户") + " 的会话？删除后将清空所有聊天记录。", "删除会话", { confirmButtonText: "确定", cancelButtonText: "取消", type: "warning" })
      await messageApi.deleteConversation(route.params.userId)
      ElMessage.success("会话已删除")
      router.push("/message")
    } catch (e) { /* cancelled */ }
  } else if (cmd === "blockUser") {
    try {
      if (isBlocked.value) {
        await messageApi.unblockUser(route.params.userId)
        isBlocked.value = false
        ElMessage.success("已取消屏蔽")
      } else {
        await ElMessageBox.confirm("屏蔽后将无法接收对方的消息，确定屏蔽？", "屏蔽联系人", { confirmButtonText: "确定", cancelButtonText: "取消", type: "warning" })
        await messageApi.blockUser(route.params.userId)
        isBlocked.value = true
        ElMessage.success("已屏蔽")
      }
    } catch (e) { /* cancelled */ }
  }
}
</script>

<style scoped>
.chat { display: flex; flex-direction: column; height: 100vh; }
.header { display: flex; align-items: center; gap: 8px; padding: 10px 16px; border-bottom: 1px solid #eee; }
.header-spacer { flex: 1; }
.messages { flex: 1; overflow-y: auto; padding: 16px; }
.empty-msg { text-align: center; padding: 60px 0; color: #bbb; font-size: 14px; }
.msg { margin-bottom: 12px; }
.msg.mine { text-align: right; }
.bubble { display: inline-block; max-width: 70%; padding: 10px 14px; border-radius: 18px; background: #f0f0f0; font-size: 14px; word-break: break-word; }
.msg.mine .bubble { background: #ff2442; color: white; }
.time { display: block; font-size: 11px; color: #999; margin-top: 2px; }
.input-area { display: flex; gap: 8px; padding: 10px 16px; border-top: 1px solid #eee; }
</style>
