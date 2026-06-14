<template>
  <div class="create-page">
    <!-- Format tabs bar -->
    <div class="tabs-bar">
      <div class="format-tabs">
        <div
          class="format-tab"
          :class="{ active: activeFormat === 'video' }"
          @click="switchFormat('video')"
        >
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5,3 19,12 5,21"/>
          </svg>
          <span>上传视频</span>
        </div>
        <div
          class="format-tab"
          :class="{ active: activeFormat === 'image' }"
          @click="switchFormat('image')"
        >
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21,15 16,10 5,21"/>
          </svg>
          <span>上传图文</span>
        </div>
        <div
          class="format-tab"
          :class="{ active: activeFormat === 'article' }"
          @click="switchFormat('article')"
        >
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <span>写长文</span>
        </div>
      </div>
    </div>

    <!-- Upload area -->
    <div class="upload-container">
      <div class="upload-zone" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
        <div class="upload-icon-wrapper">
          <svg class="cloud-icon" viewBox="0 0 64 64" fill="none" stroke="#ccc" stroke-width="2.5">
            <path d="M44 28a12 12 0 0 0-23.7-2.5A8 8 0 0 0 20 41h22a10 10 0 0 0 2-19.8z"/>
            <line x1="32" y1="22" x2="32" y2="36"/><line x1="25" y1="29" x2="32" y2="36"/><line x1="39" y1="29" x2="32" y2="36"/>
          </svg>
        </div>
        <p class="upload-guide">拖拽视频到此或点击上传</p>
        <button class="upload-btn">{{ activeFormat === "video" ? "上传视频" : activeFormat === "image" ? "上传图片" : "写长文" }}</button>
        <p class="upload-note" v-if="activeFormat === 'video'">支持 MP4、MOV 格式，单文件最大 500MB</p>
      </div>

      <!-- Preview area -->
      <div v-if="previewUrl" class="preview-area">
        <video v-if="activeFormat === 'video'" :src="previewUrl" controls class="preview-video" />
        <div v-else-if="imagePreviews.length" class="preview-grid">
          <div v-for="(img,i) in imagePreviews" :key="i" class="preview-img-wrapper">
            <img :src="img" />
            <div class="preview-remove" @click="removeImage(i)">×</div>
          </div>
        </div>
      </div>

      <!-- Title and content inputs -->
      <div v-if="previewUrl || imagePreviews.length" class="form-fields">
        <input v-model="form.title" class="field-input title-input" placeholder="添加标题..." maxlength="100" />
        <textarea v-model="form.content" class="field-input content-input" placeholder="填写正文..." rows="4" maxlength="2000"></textarea>
        <div class="tag-selector">
          <el-tag v-for="(t,i) in form.tag_names" :key="i" closable @close="removeTag(i)" class="tag-item">{{ t }}</el-tag>
          <el-input v-if="showTagInput" v-model="tagInput" size="small" class="tag-input" @keyup.enter="addTag" @blur="addTag" />
          <button v-else class="add-tag-btn" @click="showTagInput = true">+ 添加标签</button>
        </div>
        <button class="publish-btn" :disabled="!form.title" @click="handlePublish">{{ isEdit ? "保存修改" : "发布" }}</button>
      </div>
    </div>

    <!-- Bottom spec bar -->
    <div class="spec-bar">
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">视频大小</span>
          <span class="spec-value">时长小于5分钟</span>
        </div>
      </div>
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">视频格式</span>
          <span class="spec-value">支持通用格式，推荐 MP4、MOV</span>
        </div>
      </div>
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">视频分辨率</span>
          <span class="spec-value">1080P以上画质，网页端上传清晰度更优</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "../stores/user"
import { notesApi } from "../api/notes"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeFormat = ref("video")
const previewUrl = ref("")
const videoFile = ref(null)
const imageFiles = ref([])
const imagePreviews = ref([])
const showTagInput = ref(false)
const tagInput = ref("")

const isEdit = computed(() => !!route.params.id)
const editId = computed(() => route.params.id)

const form = reactive({
  title: "", content: "", tag_names: []
})

onMounted(async () => {
  if (isEdit.value) await loadEditData()
})

async function loadEditData() {
  try {
    const note = await notesApi.getNote(editId.value)
    form.title = note.title || ""
    form.content = note.content || ""
    form.tag_names = (note.tags || []).map(t => t.name)
    if (note.media_list?.length) {
      note.media_list.forEach(m => imagePreviews.value.push(m.file))
    }
    activeFormat.value = note.type === 1 ? "video" : "image"
  } catch (e) { router.back() }
}

function switchFormat(fmt) {
  activeFormat.value = fmt
  previewUrl.value = ""
  videoFile.value = null
  imageFiles.value = []
  imagePreviews.value = []
}

function triggerUpload() {
  const input = document.createElement("input")
  if (activeFormat.value === "video") {
    input.accept = "video/mp4,video/quicktime"
  } else {
    input.accept = "image/jpeg,image/png,image/webp"
    input.multiple = true
  }
  input.type = "file"
  input.onchange = (e) => {
    const files = Array.from(e.target.files || [])
    if (activeFormat.value === "video" && files[0]) {
      videoFile.value = files[0]
      previewUrl.value = URL.createObjectURL(files[0])
    } else {
      files.forEach(f => {
        imageFiles.value.push(f)
        imagePreviews.value.push(URL.createObjectURL(f))
      })
    }
  }
  input.click()
}

function handleDrop(e) {
  const files = Array.from(e.dataTransfer.files || [])
  if (activeFormat.value === "video" && files[0]) {
    videoFile.value = files[0]
    previewUrl.value = URL.createObjectURL(files[0])
  } else {
    files.forEach(f => {
      imageFiles.value.push(f)
      imagePreviews.value.push(URL.createObjectURL(f))
    })
  }
}

function removeImage(i) {
  imageFiles.value.splice(i, 1)
  imagePreviews.value.splice(i, 1)
}

function addTag() {
  const name = tagInput.value.trim()
  if (!name || form.tag_names.length >= 8) { showTagInput.value = false; return }
  if (!form.tag_names.includes(name)) form.tag_names.push(name)
  tagInput.value = ""
  showTagInput.value = false
}

function removeTag(i) { form.tag_names.splice(i, 1) }

async function handlePublish() {
  if (!form.title) return
  const fd = new FormData()
  fd.append("title", form.title)
  fd.append("content", form.content)
  fd.append("type", activeFormat.value === "video" ? 1 : 0)
  form.tag_names.forEach(t => fd.append("tag_names", t))
  if (activeFormat.value === "video" && videoFile.value) {
    fd.append("video", videoFile.value)
  } else {
    imageFiles.value.forEach(f => fd.append("images", f))
  }
  try {
    if (isEdit.value) {
      await notesApi.updateNote(editId.value, fd)
    } else {
      await notesApi.createNote(fd)
    }
    router.push("/user/" + userStore.user.id)
  } catch (e) {}
}
</script>

<style scoped>
.create-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 120px);
}

/* Tabs bar */
.tabs-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}
.format-tabs { display: flex; gap: 4px; }
.format-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 10px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  transition: all 0.15s;
}
.format-tab:hover { background: #f5f5f5; }
.format-tab.active {
  background: #ff2442;
  color: #fff;
  font-weight: 600;
}
.tab-icon { width: 16px; height: 16px; }
.draft-entry {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  background: #f9f9f9;
}
.draft-entry:hover { background: #f0f0f0; }
.draft-icon { width: 14px; height: 14px; }

/* Upload zone */
.upload-container { margin-bottom: 24px; }
.upload-zone {
  background: #f7f7f8;
  border: 2px dashed #ddd;
  border-radius: 20px;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s;
}
.upload-zone:hover { border-color: #ff2442; background: #fff5f5; }
.cloud-icon { width: 52px; height: 52px; }
.upload-guide { font-size: 15px; color: #999; }
.upload-btn {
  background: #ff2442;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 12px 40px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.upload-btn:hover { background: #e01e38; }
.upload-note { font-size: 12px; color: #bbb; margin: 0; }

/* Preview */
.preview-area {
  margin-top: 20px;
  border-radius: 16px;
  overflow: hidden;
  background: #000;
}
.preview-video { width: 100%; max-height: 500px; display: block; }
.preview-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.preview-img-wrapper { position: relative; aspect-ratio: 1; border-radius: 10px; overflow: hidden; }
.preview-img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
.preview-remove {
  position: absolute; top: 4px; right: 4px;
  width: 22px; height: 22px; background: rgba(0,0,0,0.5); color: white;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 14px; cursor: pointer;
}

/* Form fields */
.form-fields {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.field-input {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 14px;
  outline: none;
  font-family: inherit;
}
.field-input:focus { border-color: #ff2442; }
.title-input { font-size: 18px; font-weight: 600; }
.content-input { resize: vertical; min-height: 100px; line-height: 1.6; }
.tag-selector { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.tag-item { margin: 0; }
.tag-input { width: 100px; }
.add-tag-btn {
  border: 1px dashed #ddd; background: none;
  border-radius: 8px; padding: 4px 12px; font-size: 12px; color: #999;
  cursor: pointer;
}
.add-tag-btn:hover { border-color: #ff2442; color: #ff2442; }
.publish-btn {
  background: #ff2442; color: #fff; border: none;
  border-radius: 12px; padding: 14px; font-size: 15px; font-weight: 600;
  cursor: pointer; margin-top: 4px;
}
.publish-btn:disabled { background: #ddd; cursor: not-allowed; }
.publish-btn:hover:not(:disabled) { background: #e01e38; }

/* Spec bar */
.spec-bar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  background: #f9f9fa;
  border-radius: 16px;
  padding: 20px 24px;
}
.spec-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.spec-icon { width: 20px; height: 20px; flex-shrink: 0; margin-top: 2px; }
.spec-text { display: flex; flex-direction: column; gap: 4px; }
.spec-label { font-size: 13px; font-weight: 600; color: #333; }
.spec-value { font-size: 12px; color: #999; line-height: 1.4; }
</style>
