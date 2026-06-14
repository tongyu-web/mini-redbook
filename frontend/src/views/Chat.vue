<template>
  <div class="chat">
    <div class="header">
      <el-button text @click="$router.back()">← 返回</el-button>
      <strong>{{ otherUser?.nickname || "聊天" }}</strong>
    </div>
    <div class="messages" ref="msgRef">
      <div v-for="m in messages" :key="m.id" class="msg" :class="{ mine: m.from_user === currentUserId }">
        <div class="bubble">{{ m.content }}</div>
        <span class="time">{{ m.created_at }}</span>
      </div>
    </div>
    <div class="input-area">
      <el-input v-model="text" placeholder="输入消息..." @keyup.enter="send" />
      <el-button type="primary" @click="send" :disabled="!text.trim()">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from "vue"
import { useRoute } from "vue-router"
import { useUserStore } from "../stores/user"
import { messageApi } from "../api/messaging"
import { accountsApi } from "../api/accounts"

const route = useRoute()
const userStore = useUserStore()
const messages = ref([])
const text = ref("")
const otherUser = ref(null)
const msgRef = ref(null)
const currentUserId = computed(() => userStore.user?.id)

onMounted(async () => {
  otherUser.value = await accountsApi.getProfile(route.params.userId)
  await loadMessages()
})

async function loadMessages() {
  const res = await messageApi.getMessages(route.params.userId)
  messages.value = res.results || res || []
  await nextTick()
  if (msgRef.value) msgRef.value.scrollTop = msgRef.value.scrollHeight
}

async function send() {
  if (!text.value.trim()) return
  await messageApi.sendMessage({ to_user_id: route.params.userId, content: text.value })
  text.value = ""
  await loadMessages()
}
</script>

<style scoped>
.chat { display: flex; flex-direction: column; height: 100vh; }
.header { display: flex; align-items: center; gap: 8px; padding: 10px 16px; border-bottom: 1px solid #eee; }
.messages { flex: 1; overflow-y: auto; padding: 16px; }
.msg { margin-bottom: 12px; }
.msg.mine { text-align: right; }
.bubble { display: inline-block; max-width: 70%; padding: 10px 14px; border-radius: 18px; background: #f0f0f0; font-size: 14px; }
.msg.mine .bubble { background: #ff2442; color: white; }
.time { display: block; font-size: 11px; color: #999; margin-top: 2px; }
.input-area { display: flex; gap: 8px; padding: 10px 16px; border-top: 1px solid #eee; }
</style>
