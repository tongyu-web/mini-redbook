<template>
  <div class="settings">
<div class="content">
      <div class="header">
        <el-button text @click="$router.back()">← 返回</el-button>
        <h2>编辑个人资料</h2>
      </div>

      <el-alert v-if="saveMsg" :title="saveMsg" :type="saveType" show-icon closable @close="saveMsg=''" class="mb-3" />

      <!-- 头像 -->
      <div class="section">
        <div class="section-title">头像</div>
        <div class="avatar-upload" @click="triggerUpload">
          <el-avatar :size="80" :src="previewUrl || form.avatar_url" />
          <div class="upload-overlay">
            <span>更换头像</span>
          </div>
        </div>
        <input ref="fileInput" type="file" accept="image/jpeg,image/png" hidden @change="handleFile" />
        <p class="hint">支持 JPG/PNG，最大 5MB</p>
      </div>

      <!-- 昵称 -->
      <div class="section">
        <div class="section-title">昵称</div>
        <el-input v-model="form.nickname" :maxlength="15" show-word-limit placeholder="输入昵称（15字符以内）" />
        <p class="hint">昵称将展示在你的个人主页</p>
      </div>

      <!-- 个人简介 -->
      <div class="section">
        <div class="section-title">个人简介</div>
        <el-input v-model="form.bio" type="textarea" :rows="3" :maxlength="500" show-word-limit placeholder="介绍一下自己..." />
      </div>

      <!-- 性别 -->
      <div class="section">
        <div class="section-title">性别</div>
        <el-radio-group v-model="form.gender">
          <el-radio value="MALE">男</el-radio>
          <el-radio value="FEMALE">女</el-radio>
          <el-radio value="UNKNOWN">保密</el-radio>
        </el-radio-group>
      </div>

      <el-button type="primary" class="w-full" :loading="saving" @click="saveProfile">保存</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { accountsApi } from "../api/accounts"

const router = useRouter()
const userStore = useUserStore()
const fileInput = ref(null)
const saving = ref(false)
const previewUrl = ref("")
const saveMsg = ref("")
const saveType = ref("success")
const file = ref(null)

const form = reactive({
  nickname: "",
  avatar_url: "",
  bio: "",
  gender: "UNKNOWN",
})

onMounted(async () => {
  try {
    const res = await accountsApi.getProfile()
    form.nickname = res.nickname || ""
    form.avatar_url = res.avatar_url || ""
    form.bio = res.bio || ""
    form.gender = res.gender || "UNKNOWN"
  } catch (e) {
    saveMsg.value = "加载资料失败"
    saveType.value = "error"
  }
})

function triggerUpload() {
  fileInput.value?.click()
}

function handleFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  
  const validTypes = ["image/jpeg", "image/png", "image/jpg"]
  if (!validTypes.includes(f.type)) {
    saveMsg.value = "仅支持 JPG/PNG 格式"
    saveType.value = "error"
    return
  }
  if (f.size > 5 * 1024 * 1024) {
    saveMsg.value = "头像大小不能超过 5MB"
    saveType.value = "error"
    return
  }
  
  file.value = f
  previewUrl.value = URL.createObjectURL(f)
  uploadAvatar()
}

async function uploadAvatar() {
  if (!file.value) return
  saving.value = true
  try {
    const fd = new FormData()
    fd.append("avatar", file.value)
    const res = await accountsApi.uploadAvatar(fd)
    form.avatar_url = res.avatar_url
    previewUrl.value = ""
    saveMsg.value = "头像更新成功"
    saveType.value = "success"
  } catch (e) {
    saveMsg.value = e.message || "头像上传失败"
    saveType.value = "error"
  } finally {
    saving.value = false
  }
}

async function saveProfile() {
  if (!form.nickname.trim()) {
    saveMsg.value = "昵称不能为空"
    saveType.value = "error"
    return
  }
  saving.value = true
  try {
    const res = await accountsApi.updateProfile({
      nickname: form.nickname,
      bio: form.bio,
      gender: form.gender,
    })
    userStore.setUser(res)
    saveMsg.value = "保存成功！"
    saveType.value = "success"
  } catch (e) {
    saveMsg.value = e.message || "保存失败"
    saveType.value = "error"
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings { padding-bottom: 60px; }
.content { max-width: 600px; margin: 0 auto; padding: 16px; }
.header { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.header h2 { margin: 0; font-size: 18px; }
.section { margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid #f0f0f0; }
.section-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 12px; }
.avatar-upload { position: relative; width: 80px; height: 80px; cursor: pointer; border-radius: 50%; overflow: hidden; }
.upload-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; border-radius: 50%; }
.avatar-upload:hover .upload-overlay { opacity: 1; }
.upload-overlay span { color: white; font-size: 12px; }
.hint { font-size: 12px; color: #999; margin-top: 6px; }
.mb-3 { margin-bottom: 16px; }
.w-full { width: 100%; }
</style>
