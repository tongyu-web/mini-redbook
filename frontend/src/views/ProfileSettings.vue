<template>
  <div class="edit-profile-page">
    <div class="top-nav">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#333" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <span class="nav-title">编辑资料</span>
      <button class="preview-btn" @click="handlePreview">预览</button>
    </div>

    <div class="content">
      <el-alert v-if="saveMsg" :title="saveMsg" :type="saveType" show-icon closable @close="saveMsg=''" class="mb-3" />

      <!-- Card: 头像 -->
      <div class="profile-card">
        <div class="info-row" @click="triggerUpload">
          <span class="row-label">头像</span>
          <div class="row-right">
            <el-avatar :size="48" :src="previewUrl || form.avatar_url" />
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ccc" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        </div>
        <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleFile" />
      </div>

      <!-- Card: 基本信息 -->
      <div class="profile-card">
        <div class="info-row">
          <span class="row-label">昵称</span>
          <div class="row-right input-row">
            <el-input v-model="form.nickname" :maxlength="15" placeholder="输入昵称" class="inline-input" />
          </div>
        </div>
        <div class="info-row">
          <span class="row-label">简介</span>
          <div class="row-right input-row">
            <el-input v-model="form.bio" :maxlength="500" placeholder="介绍一下自己" class="inline-input" />
          </div>
        </div>
        <div class="info-row">
          <span class="row-label">性别</span>
          <div class="row-right select-row" @click="showGenderPicker = true">
            <span :class="{ 'placeholder': !form.gender }">{{ genderLabel }}</span>
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ccc" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        </div>
        <div class="info-row">
          <span class="row-label">生日</span>
          <div class="row-right select-row" @click="showBirthPicker = true">
            <span :class="{ 'placeholder': !form.birthday }">{{ form.birthday || '选择生日' }}</span>
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ccc" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        </div>
      </div>

      <button class="save-btn" :disabled="saving" @click="saveProfile">{{ saving ? '保存中...' : '保存' }}</button>
    </div>

    <!-- Gender picker dialog -->
    <el-dialog v-model="showGenderPicker" title="选择性别" width="85%" max-width="360px">
      <div class="picker-options">
        <div class="picker-option" @click="form.gender = 'MALE'; showGenderPicker = false">男</div>
        <div class="picker-option" @click="form.gender = 'FEMALE'; showGenderPicker = false">女</div>
        <div class="picker-option" @click="form.gender = 'UNKNOWN'; showGenderPicker = false">保密</div>
      </div>
    </el-dialog>

    <!-- Birthday picker dialog -->
    <el-dialog v-model="showBirthPicker" title="选择生日" width="85%" max-width="360px">
      <el-date-picker v-model="birthdayTemp" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
      <template #footer>
        <el-button @click="showBirthPicker = false">取消</el-button>
        <el-button type="primary" style="background:#ff2442;border-color:#ff2442" @click="form.birthday = birthdayTemp; showBirthPicker = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
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

const showGenderPicker = ref(false)
const showBirthPicker = ref(false)
const birthdayTemp = ref("")

const form = reactive({
  avatar_url: "",
  nickname: "",
  bio: "",
  gender: "UNKNOWN",
  birthday: "",
})

const genderLabel = computed(() => {
  const map = { MALE: "男", FEMALE: "女", UNKNOWN: "保密" }
  return map[form.gender] || "选择性别"
})

onMounted(async () => {
  try {
    const userData = await accountsApi.getProfile()
    form.avatar_url = userData.avatar_url || ""
    form.nickname = userData.nickname || ""
    form.bio = userData.bio || ""
    form.gender = userData.gender || "UNKNOWN"
    form.birthday = userData.birthday || ""
  } catch (e) {
    console.error(e)
  }
})

function handlePreview() {
  router.push("/user/" + userStore.user?.id)
}

function triggerUpload() {
  fileInput.value?.click()
}

async function handleFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  previewUrl.value = URL.createObjectURL(f)
  await uploadAvatar(f)
}

async function uploadAvatar(file) {
  saving.value = true
  try {
    const fd = new FormData()
    fd.append("avatar", file)
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
      birthday: form.birthday || undefined,
    })
    userStore.setUser(res)
    saveMsg.value = "保存成功"
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
.edit-profile-page {
  min-height: 100vh;
  background: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.top-nav {
  display: flex;
  align-items: center;
  height: 52px;
  padding: 0 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}
.back-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.nav-title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}
.preview-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: #ff2442;
  font-weight: 500;
  cursor: pointer;
  padding: 4px 8px;
}
.content {
  padding: 12px 16px 40px;
  max-width: 600px;
  margin: 0 auto;
}
.mb-3 { margin-bottom: 12px; }

.profile-card {
  background: #f7f7f7;
  border-radius: 12px;
  padding: 0 16px;
  margin-bottom: 12px;
}
.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 52px;
  padding: 6px 0;
  cursor: pointer;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}
.info-row:last-child {
  border-bottom: none;
}
.row-label {
  font-size: 15px;
  color: #666;
  white-space: nowrap;
  min-width: 56px;
}
.row-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: flex-end;
}
.input-row {
  flex: 1;
  max-width: 70%;
}
.inline-input {
  width: 100%;
}
.inline-input :deep(.el-input__wrapper) {
  background: transparent;
  box-shadow: none !important;
  padding: 0;
  border: none;
}
.inline-input :deep(.el-input__inner) {
  text-align: right;
  font-size: 14px;
  color: #333;
  padding: 0;
  border: none;
  background: transparent;
}
.inline-input :deep(.el-input__inner::placeholder) {
  color: #bbb;
}
.select-row {
  cursor: pointer;
  gap: 4px;
}
.select-row span {
  font-size: 14px;
  color: #333;
}
.select-row span.placeholder {
  color: #bbb;
}

.save-btn {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: 22px;
  background: #ff2442;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 20px;
  transition: opacity 0.2s;
}
.save-btn:hover { opacity: 0.9; }
.save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.picker-options {
  padding: 8px 0;
}
.picker-option {
  padding: 14px 0;
  text-align: center;
  font-size: 15px;
  color: #333;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}
.picker-option:last-child { border-bottom: none; }
.picker-option:hover { color: #ff2442; }
</style>