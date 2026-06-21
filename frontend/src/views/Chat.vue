<template>
  <div class="chat-wrap">
    <div class="top-bar">
      <button class="btn-back" @click="goBack">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#222" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <span class="top-title">{{ otherUser?.nickname || "聊天" }}</span>
      <el-dropdown v-if="otherUser" @command="handleHeaderCommand" trigger="click">
        <el-button text circle size="small"><span style="font-size:20px;color:#666;letter-spacing:2px">···</span></el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="viewProfile">查看主页</el-dropdown-item>
            <el-dropdown-item command="deleteConversation" divided>删除会话</el-dropdown-item>
            <el-dropdown-item command="blockUser">{{ isBlocked ? "取消屏蔽" : "屏蔽联系人" }}</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div class="msg-area" ref="msgRef">
      <div v-if="messages.length === 0" class="msg-empty">暂无消息，开始聊天吧</div>
      <template v-for="(m, idx) in messages" :key="m.id">
        <div v-if="showTime(idx)" class="time-tag">{{ formatTime(m.created_at) }}</div>
        <div class="msg-row" :class="isMine(m) ? 'msg-right' : 'msg-left'">
          <div v-if="!isMine(m)" class="msg-avt" style="cursor:pointer" @click="$router.push(`/user/` + otherUser?.id)">
            <el-avatar :size="28" :src="otherUser?.avatar_url" />
          </div>
          <div v-if="isMine(m)" class="msg-avt" style="cursor:pointer" @click="$router.push(`/user/` + userStore.user?.id)">
            <el-avatar :size="28" :src="userStore.user?.avatar_url" />
          </div>
          <div class="msg-bubble">{{ m.content }}</div>
        </div>
      </template>
    </div>

    <div class="input-area">
      <el-input v-model="text" class="input-field" placeholder="输入消息..." :maxlength="500" clearable @keydown.enter.prevent="send" />
      <button class="btn-send" :disabled="!text.trim()" @click="send">发送</button>
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
function isMine(m) { return String(m.from_user) === String(currentUserId.value) }
let pollTimer = null

onMounted(async () => {
  try {
    const data = await accountsApi.getProfile(route.params.userId)
    otherUser.value = data
  } catch (e) {
    otherUser.value = { nickname: "用户" }
  }
  await loadMessages()
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
  if (d.toDateString() === now.toDateString()) return pad(d.getHours()) + ":" + pad(d.getMinutes())
  const y = new Date(now)
  y.setDate(y.getDate() - 1)
  if (d.toDateString() === y.toDateString()) return "昨天 " + pad(d.getHours()) + ":" + pad(d.getMinutes())
  return pad(d.getMonth() + 1) + "/" + pad(d.getDate()) + " " + pad(d.getHours()) + ":" + pad(d.getMinutes())
}

function showTime(idx) {
  if (idx === 0) return true
  const prev = new Date(messages.value[idx - 1].created_at)
  const curr = new Date(messages.value[idx].created_at)
  return (curr - prev) > 5 * 60 * 1000
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
    } catch (e) { }
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
    } catch (e) { }
  }
}
</script>

<style scoped>
.chat-wrap {
  display: flex; flex-direction: column;
  height: 100vh; max-width: 800px; margin: 0 auto;
  background: #fff;
}

/* top bar */
.top-bar {
  display: flex; align-items: center;
  padding: 10px 12px; background: #fff;
  flex-shrink: 0;
}
.btn-back {
  background: none; border: none;
  cursor: pointer; padding: 4px; display: flex;
}
.top-title {
  flex: 1; text-align: center;
  font-size: 17px; font-weight: 600; color: #222;
}

/* message area */
.msg-area {
  flex: 1; overflow-y: auto;
  padding: 12px 16px;
  display: flex; flex-direction: column;
  gap: 6px;
}
.msg-empty {
  text-align: center; padding: 60px 0;
  color: #ccc; font-size: 14px;
}

/* time tag */
.time-tag {
  text-align: center;
  font-size: 11px; color: #c9c9c9;
  padding: 12px 0 6px;
}

/* message row */
.msg-row {
  display: flex; gap: 8px;
  max-width: 70%; align-items: flex-end;
}
.msg-left { align-self: flex-start; }
.msg-right {
  align-self: flex-end;
  justify-content: flex-end;
  flex-direction: row-reverse;
  max-width: 60%;
}

/* avatar */
.msg-avt { flex-shrink: 0; }

/* bubble */
.msg-bubble {
  display: inline-block;
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 14px; line-height: 1.5;
  word-break: break-word;
  text-align: left;
}
.msg-left .msg-bubble {
  background: #f2f2f2; color: #222;
}
.msg-right .msg-bubble {
  background: #4a90d9; color: #fff;
}

/* input area */
.input-area {
  display: flex; align-items: center;
  gap: 8px; padding: 8px 12px;
  background: #fff; flex-shrink: 0;
}
.input-field { flex: 1; }
.input-field :deep(.el-input__wrapper) {
  border-radius: 22px;
  background: #f5f5f5;
  box-shadow: none; padding: 0 16px;
}
.input-field :deep(.el-input__inner) {
  height: 40px; font-size: 14px;
}
.btn-send {
  flex-shrink: 0;
  height: 38px; padding: 0 20px;
  border-radius: 19px; border: none;
  background: #ff2442; color: #fff;
  font-size: 14px; font-weight: 500;
  cursor: pointer;
}
.btn-send:disabled { opacity: 0.4; cursor: not-allowed; }
</style>






