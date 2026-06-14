<template>
  <div class="create-page">
    <div class="header">
      <el-button text @click="handleBack">← 返回</el-button>
      <h2>{{ isEdit ? "编辑笔记" : "发布笔记" }}</h2>
      <el-button v-if="!isEdit" text type="primary" @click="saveDraft" :disabled="!form.title && !form.content">存草稿</el-button>
    </div>

    <div class="content">
      <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon closable @close="errorMsg=''" class="mb-3" />
      <el-alert v-if="successMsg" :title="successMsg" type="success" show-icon closable @close="successMsg=''" class="mb-3" />

      <!-- 类型选择 -->
      <div class="type-selector">
        <el-radio-group v-model="form.type" :disabled="isEdit">
          <el-radio-button :value="0">📷 图文</el-radio-button>
          <el-radio-button :value="1">🎬 视频</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 图文：图片上传网格 -->
      <div v-if="form.type === 0" class="media-section">
        <div class="image-grid">
          <div v-for="(img, i) in imagePreviews" :key="i" class="image-slot" @click="triggerUpload">
            <img :src="img" />
            <div class="remove-btn" @click.stop="removeImage(i)">×</div>
            <div v-if="i === 0" class="cover-badge">封面</div>
          </div>
          <div v-if="imagePreviews.length < 8" class="image-slot add-btn" @click="triggerUpload">
            <span>+</span>
            <small>{{ imagePreviews.length }}/8</small>
          </div>
        </div>
        <input ref="fileInput" type="file" multiple accept="image/jpeg,image/png,image/webp" hidden @change="handleImages" />
      </div>

      <!-- 视频：上传 -->
      <div v-if="form.type === 1" class="media-section">
        <div v-if="!videoFile" class="video-upload" @click="triggerVideoUpload">
          <span class="video-icon">🎬</span>
          <span>点击上传视频</span>
          <small>支持 MP4，最长 5 分钟，最大 500MB</small>
        </div>
        <div v-else class="video-preview">
          <video :src="videoPreviewUrl" controls />
          <el-button size="small" @click="removeVideo">重新选择</el-button>
        </div>
        <div v-if="videoFile" class="mt-2">
          <p class="label">视频封面</p>
          <div v-if="coverPreview" class="cover-preview" @click="triggerCoverUpload">
            <img :src="coverPreview" />
          </div>
          <div v-else class="cover-preview add-cover" @click="triggerCoverUpload">
            <span>+ 添加封面</span>
          </div>
        </div>
        <input ref="videoInput" type="file" accept="video/mp4,video/quicktime" hidden @change="handleVideo" />
        <input ref="coverInput" type="file" accept="image/jpeg,image/png" hidden @change="handleCover" />
      </div>

      <!-- 标题 -->
      <div class="field">
        <el-input v-model="form.title" placeholder="输入标题..." :maxlength="100" show-word-limit class="title-input" />
      </div>

      <!-- 正文 -->
      <div class="field">
        <el-input v-model="form.content" type="textarea" :rows="6" placeholder="分享你的想法..." :maxlength="2000" show-word-limit />
      </div>

      <!-- 话题标签 -->
      <div class="field">
        <div class="label">话题标签</div>
        <div class="tag-list">
          <el-tag v-for="(tag, i) in form.tag_names" :key="i" closable @close="removeTag(i)" class="tag-item">{{ tag }}</el-tag>
          <el-input v-if="showTagInput" ref="tagInputRef" v-model="tagInput" placeholder="输入标签名" size="small" class="tag-input" @keyup.enter="addTag" @blur="addTag" />
          <el-button v-else size="small" @click="showTagInput = true">+ 添加标签</el-button>
        </div>
        <div v-if="tagSuggestions.length" class="tag-suggestions">
          <div v-for="s in tagSuggestions" :key="s.id" class="suggest-item" @click="selectTag(s)">#{{ s.name }}</div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button type="primary" size="large" class="action-btn" :loading="publishing" @click="handlePublish">{{ isEdit ? "保存修改" : "发布" }}</el-button>
        <el-button size="large" class="action-btn" @click="handleBack">取消</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { notesApi } from "../api/notes"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isEdit = computed(() => !!route.params.id)
const editId = computed(() => route.params.id)

const form = reactive({
  title: "", content: "", type: 0, tag_names: [],
})
const imageFiles = ref([])
const imagePreviews = ref([])
const existingMediaIds = ref([])
const videoFile = ref(null)
const videoPreviewUrl = ref("")
const coverFile = ref(null)
const coverPreview = ref("")
const fileInput = ref(null)
const videoInput = ref(null)
const coverInput = ref(null)
const tagInputRef = ref(null)
const tagInput = ref("")
const showTagInput = ref(false)
const tagSuggestions = ref([])
const errorMsg = ref("")
const successMsg = ref("")
const publishing = ref(false)
const hasContent = computed(() => form.title || form.content || imageFiles.value.length || videoFile.value)
const draftSaved = ref(false)

onMounted(async () => {
  if (isEdit.value) {
    await loadEditData()
  } else {
    loadDraft()
    loadHotTags()
  }
})

async function loadEditData() {
  try {
    const note = await notesApi.getNote(editId.value)
    form.title = note.title || ""
    form.content = note.content || ""
    form.type = note.type || 0
    form.tag_names = (note.tags || []).map(t => t.name)

    // 加载已有的图片预览
    if (note.media_list) {
      note.media_list.forEach((m, i) => {
        imagePreviews.value.push(m.file)
        existingMediaIds.value.push(m.id)
      })
    }
    if (note.cover_img) {
      coverPreview.value = note.cover_img
    }
  } catch (e) {
    errorMsg.value = "加载笔记失败"
    router.back()
  }
}

function loadHotTags() {
  notesApi.getTags().then(data => { tagSuggestions.value = data || [] }).catch(() => {})
}

function loadDraft() {
  try {
    const raw = localStorage.getItem("create_draft")
    if (raw) {
      const d = JSON.parse(raw)
      form.title = d.title || ""
      form.content = d.content || ""
      form.type = d.type || 0
    }
  } catch (e) {}
}

function clearDraft() {
  localStorage.removeItem("create_draft")
}

// 图片
function triggerUpload() { fileInput.value?.click() }

function handleImages(e) {
  const files = Array.from(e.target.files || [])
  const total = imageFiles.value.length + files.length
  if (total > 8) {
    errorMsg.value = "最多上传8张图片"
    return
  }
  for (const f of files) {
    if (!["image/jpeg", "image/png", "image/webp"].includes(f.type)) continue
    imageFiles.value.push(f)
    imagePreviews.value.push(URL.createObjectURL(f))
  }
  e.target.value = ""
}

function removeImage(i) {
  imageFiles.value.splice(i, 1)
  imagePreviews.value.splice(i, 1)
}

// 视频
function triggerVideoUpload() { videoInput.value?.click() }

function handleVideo(e) {
  const f = e.target.files?.[0]
  if (!f) return
  if (f.size > 500 * 1024 * 1024) { errorMsg.value = "视频最大500MB"; return }
  videoFile.value = f
  videoPreviewUrl.value = URL.createObjectURL(f)
  e.target.value = ""
}

function removeVideo() {
  videoFile.value = null
  videoPreviewUrl.value = ""
  coverFile.value = null
  coverPreview.value = ""
}

function triggerCoverUpload() { coverInput.value?.click() }

function handleCover(e) {
  const f = e.target.files?.[0]
  if (!f) return
  coverFile.value = f
  coverPreview.value = URL.createObjectURL(f)
  e.target.value = ""
}

// 标签
function addTag() {
  const name = tagInput.value.trim()
  if (!name) { showTagInput.value = false; return }
  if (form.tag_names.length >= 8) { errorMsg.value = "最多8个标签"; return }
  if (!form.tag_names.includes(name)) {
    form.tag_names.push(name)
  }
  tagInput.value = ""
  showTagInput.value = false
}

function removeTag(i) { form.tag_names.splice(i, 1) }

function selectTag(tag) {
  if (!form.tag_names.includes(tag.name) && form.tag_names.length < 8) {
    form.tag_names.push(tag.name)
  }
  showTagInput.value = false
}

// 保存/发布
async function saveDraft() {
  if (!hasContent.value) return
  const draft = { title: form.title, content: form.content, type: form.type }
  localStorage.setItem("create_draft", JSON.stringify(draft))
  errorMsg.value = "草稿已保存在本地"
}

async function handlePublish() {
  if (!form.title) {
    errorMsg.value = "请输入标题"
    return
  }
  publishing.value = true
  errorMsg.value = ""
  successMsg.value = ""

  try {
    const fd = new FormData()
    fd.append("title", form.title)
    fd.append("content", form.content)
    fd.append("type", form.type)
    form.tag_names.forEach(t => fd.append("tag_names", t))

    if (form.type === 0) {
      imageFiles.value.forEach(f => fd.append("images", f))
    } else if (videoFile.value) {
      fd.append("video", videoFile.value)
      if (coverFile.value) fd.append("cover_img", coverFile.value)
    }

    if (isEdit.value) {
      await notesApi.updateNote(editId.value, fd)
      successMsg.value = "修改已保存！"
    } else {
      await notesApi.createNote(fd)
      clearDraft()
      successMsg.value = "发布成功！"
    }
    setTimeout(() => router.push("/user/" + userStore.user.id), 1000)
  } catch (e) {
    errorMsg.value = e.message || (isEdit.value ? "修改失败" : "发布失败")
  } finally {
    publishing.value = false
  }
}

function handleBack() {
  if (hasContent.value && !isEdit.value) {
    saveDraft()
  }
  router.back()
}
</script>

<style scoped>
.create-page { min-height: 100vh; background: #fff; }
.header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #eee; position: sticky; top: 0; background: white; z-index: 10; }
.header h2 { font-size: 16px; margin: 0; }
.content { max-width: 600px; margin: 0 auto; padding: 16px; }
.mb-3 { margin-bottom: 16px; }
.mt-2 { margin-top: 8px; }
.field { margin-bottom: 16px; }
.label { font-size: 13px; color: #666; margin-bottom: 6px; }
.title-input { font-size: 18px; font-weight: 600; }
.title-input :deep(input) { font-size: 18px; border: none; padding: 0; }
.type-selector { margin-bottom: 16px; }

/* 图片网格 */
.image-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.image-slot { position: relative; aspect-ratio: 1; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
.image-slot img { width: 100%; height: 100%; object-fit: cover; }
.add-btn { display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f9f9f9; cursor: pointer; border: 2px dashed #ddd; }
.add-btn span { font-size: 28px; color: #999; }
.add-btn small { font-size: 11px; color: #bbb; margin-top: 4px; }
.remove-btn { position: absolute; top: 4px; right: 4px; width: 22px; height: 22px; background: rgba(0,0,0,0.5); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; }
.cover-badge { position: absolute; bottom: 4px; left: 4px; background: #ff2442; color: white; font-size: 10px; padding: 1px 6px; border-radius: 4px; }

/* 视频 */
.video-upload { border: 2px dashed #ddd; border-radius: 12px; padding: 40px; text-align: center; cursor: pointer; }
.video-upload span { display: block; font-size: 14px; color: #666; margin-top: 8px; }
.video-upload .video-icon { font-size: 40px; }
.video-upload small { display: block; font-size: 12px; color: #999; margin-top: 4px; }
.video-preview video { width: 100%; max-height: 400px; border-radius: 8px; }
.cover-preview { width: 120px; height: 160px; border-radius: 8px; overflow: hidden; cursor: pointer; border: 1px solid #eee; }
.cover-preview img { width: 100%; height: 100%; object-fit: cover; }
.add-cover { display: flex; align-items: center; justify-content: center; background: #f9f9f9; font-size: 13px; color: #999; }

/* 标签 */
.tag-list { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.tag-item { margin: 0; }
.tag-input { width: 120px; }
.tag-suggestions { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.suggest-item { padding: 4px 12px; background: #f5f5f5; border-radius: 16px; font-size: 13px; cursor: pointer; }
.suggest-item:hover { background: #ffe9ec; color: #ff2442; }

.actions { display: flex; gap: 12px; margin-top: 24px; }
.action-btn { flex: 1; }
.draft-hint { text-align: center; color: #999; font-size: 12px; margin-top: 8px; }
</style>
