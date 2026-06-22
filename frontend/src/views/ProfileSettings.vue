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


      <!-- Privacy settings card -->
      <div class="profile-card">
        <div class="info-row">
          <span class="row-label">隐私</span>
          <div class="row-right select-row" @click="showPrivacyPicker = true">
            <span :class="{ placeholder: privacy === null }">{{ privacyLabel }}</span>
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

        <!-- Birthday picker – mini-redbook style bottom sheet -->
    <div v-if="showBirthPicker" class="birth-overlay" @click.self="showBirthPicker = false">
      <div class="birth-sheet">
        <div class="birth-sheet-header">
          <button class="bs-cancel" @click="showBirthPicker = false">取消</button>
          <button class="bs-confirm" @click="selectBirthDate">确定</button>
        </div>

        <!-- Month view -->
        <div v-if="!showYearPicker" class="birth-calendar">
          <div class="birth-month-nav">
            <button class="bn-btn" @click="prevMonth">&#8249;</button>
            <div class="bn-label" @click="showYearPicker = true">
              <span class="bn-year">{{ birthYear }}</span>
              <span class="bn-unit">年</span>
              <span class="bn-month">{{ birthMonth }}</span>
              <span class="bn-unit">月</span>
            </div>
            <button class="bn-btn" @click="nextMonth">&#8250;</button>
          </div>
          <div class="birth-weekdays">
            <span v-for="w in weekLabels" :key="w">{{ w }}</span>
          </div>
          <div class="birth-days-grid">
            <button v-for="d in birthDays" :key="d.key" class="bd-cell" :class="{ selected: d.val === birthSelected, disabled: !d.val, today: d.today }" @click="pickDay(d)" :disabled="!d.val">{{ d.label }}</button>
          </div>
        </div>

        <!-- Year picker view -->
        <div v-if="showYearPicker" class="birth-year-picker">
          <div class="year-picker-header">
            <button class="bn-btn" @click="prevYearBatch">&#8249;</button>
            <span class="yp-range">{{ yearBatchStart }} - {{ yearBatchStart + 11 }}</span>
            <button class="bn-btn" @click="nextYearBatch">&#8250;</button>
          </div>
          <div class="year-grid">
            <button
              v-for="y in yearBatch"
              :key="y"
              class="yg-cell"
              :class="{ selected: y === birthYear }"
              @click="birthYear = y; showYearPicker = false"
            >{{ y }}</button>
          </div>
        </div>

        <div class="birth-footer">
          <button class="bf-clear" @click="clearBirthday">清除生日</button>
        </div>
      </div>
    </div>

    <!-- Privacy picker dialog -->
    <el-dialog v-model="showPrivacyPicker" title="隐私设置" width="85%" max-width="360px">
      <div class="picker-options">
        <div class="picker-option" :class="{ active: privacy === 0 }" @click="privacy = 0; showPrivacyPicker = false">公开</div>
        <div class="picker-option" :class="{ active: privacy === 1 }" @click="privacy = 1; showPrivacyPicker = false">仅互关好友可见</div>
        <div class="picker-option" :class="{ active: privacy === 2 }" @click="privacy = 2; showPrivacyPicker = false">私密</div>
      </div>
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
const showPrivacyPicker = ref(false)
const privacy = ref(null)
const privacyLabel = computed(() => {
  const map = { 0: "公开", 1: "仅互关好友可见", 2: "私密" }
  return privacy.value !== null ? map[privacy.value] : "选择隐私设置"
})

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

const birthYear = ref(new Date().getFullYear() - 20)
const birthMonth = ref(new Date().getMonth() + 1)
const birthSelected = ref("")
const showYearPicker = ref(false)
const yearBatchStart = ref(Math.floor((new Date().getFullYear() - 20) / 12) * 12)

const yearBatch = computed(() => {
  const start = yearBatchStart.value
  const years = []
  for (let y = start; y <= start + 11; y++) years.push(y)
  return years
})

function prevYearBatch() {
  yearBatchStart.value -= 12
}

function nextYearBatch() {
  yearBatchStart.value += 12
}

const weekLabels = ["日", "一", "二", "三", "四", "五", "六"]

const birthDays = computed(() => {
  const y = birthYear.value
  const m = birthMonth.value
  const daysInMonth = new Date(y, m, 0).getDate()
  const firstDay = new Date(y, m - 1, 1).getDay()
  const todayStr = new Date().toISOString().slice(0, 10)
  const result = []
  for (let i = 0; i < firstDay; i++) {
    result.push({ key: "e" + i, label: "", val: null, today: false })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = y + "-" + String(m).padStart(2, "0") + "-" + String(d).padStart(2, "0")
    result.push({ key: "d" + d, label: String(d), val: dateStr, today: dateStr === todayStr })
  }
  return result
})

function prevMonth() {
  if (birthMonth.value <= 1) {
    birthYear.value--
    birthMonth.value = 12
  } else {
    birthMonth.value--
  }
}

function nextMonth() {
  if (birthMonth.value >= 12) {
    birthYear.value++
    birthMonth.value = 1
  } else {
    birthMonth.value++
  }
}

function pickDay(d) {
  if (!d.val) return
  birthSelected.value = d.val
}

function selectBirthDate() {
  if (birthSelected.value) {
    form.birthday = birthSelected.value
  }
  showBirthPicker.value = false
}

function clearBirthday() {
  form.birthday = ""
  birthSelected.value = ""
  showBirthPicker.value = false
}

onMounted(async () => {
  try {
    const userData = await accountsApi.getProfile()
    form.avatar_url = userData.avatar_url || ""
    form.nickname = userData.nickname || ""
    form.bio = userData.bio || ""
    form.gender = userData.gender || "UNKNOWN"
    form.birthday = userData.birthday || ""
    privacy.value = userStore.user?.privacy ?? null
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
    // Save privacy separately
    if (privacy.value !== null && privacy.value !== userStore.user?.privacy) {
      try {
        await accountsApi.updatePrivacy({ privacy: privacy.value })
        userStore.user.privacy = privacy.value
      } catch (e) {
        ElMessage.error("隐私设置保存失败")
      }
    }
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

/* Birth bottom sheet – clean minimal calendar */
.birth-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.45);
  z-index: 2000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.birth-sheet {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px 16px 0 0;
  animation: sheetUp 0.25s ease;
}
@keyframes sheetUp { from { transform: translateY(100%) } to { transform: translateY(0) } }

/* Header: cancel + confirm only */
.birth-sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 0;
}
.bs-cancel, .bs-confirm {
  border: none; background: none;
  font-size: 15px; font-weight: 500;
  cursor: pointer;
}
.bs-cancel { color: #999; }
.bs-confirm { color: #ff2442; font-weight: 600; }

/* Year picker */
.birth-year-picker {
  padding: 20px 24px 8px;
}
.year-picker-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 18px;
}
.yp-range {
  font-size: 16px;
  font-weight: 500;
  color: #222;
  min-width: 126px;
  text-align: center;
  letter-spacing: 0.3px;
}
.year-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding-bottom: 4px;
}
.yg-cell {
  aspect-ratio: 1.6;
  border: none; background: #f7f7f7;
  font-size: 14px;
  color: #333;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.12s;
  font-weight: 400;
}
.yg-cell:hover:not(.selected) { background: #eee; }
.yg-cell.selected {
  background: #ff2442;
  color: #fff;
  font-weight: 500;
}

/* Calendar block – uniform padding */
.birth-calendar {
  padding: 20px 24px 8px;
}
.birth-month-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 18px;
}
.bn-btn {
  border: none; background: none;
  width: 36px; height: 36px;
  border-radius: 50%;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.bn-btn:hover { background: #f5f5f5; }
.bn-label {
  font-size: 16px; font-weight: 500; color: #222;
  min-width: 126px; text-align: center;
  letter-spacing: 0.3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 6px 12px;
  border-radius: 8px;
  transition: background 0.15s;
}
.bn-label:hover { background: #f5f5f5; }
.bn-year {
  font-size: 20px;
  font-weight: 600;
  color: #222;
}
.bn-month {
  font-size: 18px;
  font-weight: 500;
  color: #222;
  margin-left: 4px;
}
.bn-unit {
  font-size: 13px;
  color: #999;
}

.birth-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 6px;
}
.birth-weekdays span {
  font-size: 12px;
  color: #bbb;
  padding: 0 0 8px;
  font-weight: 400;
}

.birth-days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}
.bd-cell {
  aspect-ratio: 1;
  border: none; background: none;
  font-size: 14px;
  color: #333;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s;
  font-weight: 400;
}
.bd-cell:hover:not(.disabled):not(.selected) { background: #f5f5f5; }
.bd-cell.disabled { visibility: hidden; cursor: default; }
.bd-cell.today { font-weight: 600; color: #ff2442; }
.bd-cell.selected {
  background: #ff2442;
  color: #fff;
  font-weight: 500;
}

/* Footer */
.birth-footer {
  padding: 4px 20px 20px;
  text-align: center;
}
.bf-clear {
  border: none; background: none;
  font-size: 13px; color: #ccc;
  cursor: pointer;
  padding: 10px 16px;
  border-radius: 8px;
  transition: background 0.15s, color 0.15s;
}
.bf-clear:hover { background: #f5f5f5; color: #999; }
</style>
