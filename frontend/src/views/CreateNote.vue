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
        
      </div>
    </div>

    <!-- Upload area -->
        <div class="upload-container">
      <!-- Upload zone (same big box for all formats, shown when no media) -->
      <div v-if="!(activeFormat === 'image' && imagePreviews.length) && !(activeFormat === 'video' && previewUrl)" class="upload-zone" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
        <div class="upload-icon-wrapper">
          <svg class="cloud-icon" viewBox="0 0 64 64" fill="none" stroke="#ccc" stroke-width="2.5">
            <path d="M44 28a12 12 0 0 0-23.7-2.5A8 8 0 0 0 20 41h22a10 10 0 0 0 2-19.8z"/>
            <line x1="32" y1="22" x2="32" y2="36"/><line x1="25" y1="29" x2="32" y2="36"/><line x1="39" y1="29" x2="32" y2="36"/>
          </svg>
        </div>
        <p class="upload-guide">{{ activeFormat === "video" ? "拖拽视频到此或点击上传" : "拖拽图片到此或点击上传" }}</p>
        <button class="upload-btn">{{ activeFormat === "video" ? "上传视频" : "上传图片" }}</button>
        <p class="upload-note" v-if="activeFormat === 'video'">支持 MP4、MOV 格式，单文件最大 500MB</p>
        <p class="upload-note" v-else>支持 JPG、PNG、WEBP 格式，单张不超过20MB</p>
      </div>

      <!-- Video editing module (shown after video uploaded) -->
      <div v-if="activeFormat === 'video' && previewUrl" class="image-edit-wrapper">
        <div class="edit-card">
          <div class="edit-card-header">
            <svg class="card-header-icon" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2">
              <polygon points="5,3 19,12 5,21"/>
            </svg>
            <span class="edit-card-title">视频编辑</span>
          </div>
          <div class="video-preview-area">
            <video :src="previewUrl" controls class="edit-video" />
          </div>
        </div>
        <div class="edit-card">
          <div class="edit-card-header">
            <svg class="card-header-icon" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
            <span class="edit-card-title">内容编辑</span>
          </div>
          <input v-model="form.title" class="img-title-input" placeholder="添加标题..." maxlength="100" />
          <div class="img-content-wrapper">
            <textarea v-model="form.content" class="img-content-input" placeholder="分享你的故事、经验或灵感..." rows="5" maxlength="1000"></textarea>
            <span class="content-counter">{{ form.content.length }}/1000</span>
          </div>
          <div class="quick-bar">
            <div class="quick-actions">
              <button class="quick-btn" @click="addTagToContent()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                <span>话题 #</span>
              </button>
            </div>
            <div class="hot-tags">
              <span class="hot-tag-label">热门推荐：</span>
              <span v-for="t in hotTags" :key="t.name" class="hot-tag" :class="{ 'tag-active': TAG_TO_CATEGORY[t.name] && form.category === TAG_TO_CATEGORY[t.name] }" @click="insertTagToContent(t.name)">#{{ t.name }}</span>
            <span v-if="autoCategoryLabel" class="auto-category-label">{{ autoCategoryLabel }}</span>
            </div>
          </div>
        </div>
        <div class="edit-card publish-card">
          <div class="publish-row">
            <div class="publish-info">
              <span class="publish-count">视频已就绪</span>
              <span class="publish-divider">|</span>
              <span class="publish-count">{{ form.content.length }}/1000 字</span>
            </div>
            <button class="publish-btn-primary" :disabled="!form.title || !previewUrl" @click="handlePublish">{{ isEdit ? "保存修改" : "发布笔记" }}</button>
          </div>
        </div>
      </div>

      <!-- Article: simple form -->
      <div v-if="false">
        <div v-if="previewUrl" class="preview-area">
          <video v-if="activeFormat === 'video'" :src="previewUrl" controls class="preview-video" />
        </div>
        <div v-if="previewUrl" class="form-fields">
          <input v-model="form.title" class="field-input title-input" placeholder="添加标题..." maxlength="100" />
          <textarea v-model="form.content" class="field-input content-input" placeholder="填写正文..." rows="4" maxlength="2000"></textarea>
          <div class="category-selector">
            <el-select v-model="form.category" placeholder="选择分类" clearable size="small" class="category-select">
              <el-option v-for="c in categories" :key="c.key" :label="c.name" :value="c.key" />
            </el-select>
          </div>
          <div class="tag-selector">
            <el-tag v-for="(t,i) in form.tag_names" :key="i" closable @close="removeTag(i)" class="tag-item">{{ t }}</el-tag>
            <el-input v-if="showTagInput" v-model="tagInput" size="small" class="tag-input" @keyup.enter="addTag" @blur="addTag" />
            <button v-else class="add-tag-btn" @click="showTagInput = true">+ 添加标签</button>
          </div>
          <button class="publish-btn" :disabled="!form.title" @click="handlePublish">{{ isEdit ? "保存修改" : "发布" }}</button>
        </div>
      </div>

      <!-- Image: edit cards (shown after images uploaded) -->
      <div v-if="activeFormat === 'image' && imagePreviews.length" class="image-edit-wrapper">
        <div class="edit-card">
          <div class="edit-card-header">
            <svg class="card-header-icon" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/>
            </svg>
            <span class="edit-card-title">图片编辑</span>
          </div>
          <div class="image-upload-grid">
            <div class="upload-box" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
              <svg viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" width="32" height="32">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span class="upload-box-label">点击上传</span>
            </div>
            <div v-for="(img,i) in imagePreviews" :key="i" class="thumb-card" @click="previewImage(i)">
              <img :src="img" />
              <div class="thumb-remove" @click.stop="removeImage(i)">
                <svg viewBox="0 0 24 24" fill="white" width="12" height="12"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </div>
              <div class="thumb-order">{{ i + 1 }}</div>
            </div>
            <div v-for="n in Math.max(0, 3 - imagePreviews.length)" :key="'empty-' + n" class="thumb-card thumb-empty">
              <svg viewBox="0 0 24 24" fill="none" stroke="#ddd" stroke-width="1.5" width="20" height="20"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>
            </div>
          </div>
        </div>
        <div class="edit-card">
          <div class="edit-card-header">
            <svg class="card-header-icon" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
            <span class="edit-card-title">图文内容编辑</span>
          </div>
          <input v-model="form.title" class="img-title-input" placeholder="填写标题会有更多赞哦" maxlength="100" />
          <div class="img-content-wrapper">
            <textarea v-model="form.content" class="img-content-input" placeholder="分享你的故事、经验或灵感..." rows="5" maxlength="1000"></textarea>
            <span class="content-counter">{{ form.content.length }}/1000</span>
          </div>
          <div class="quick-bar">
            <div class="quick-actions">
              <button class="quick-btn" @click="addTagToContent()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                <span>话题 #</span>
              </button>
            </div>
            <div class="hot-tags">
              <span class="hot-tag-label">热门推荐：</span>
              <span v-for="t in hotTags" :key="t.name" class="hot-tag" :class="{ 'tag-active': TAG_TO_CATEGORY[t.name] && form.category === TAG_TO_CATEGORY[t.name] }" @click="insertTagToContent(t.name)">#{{ t.name }}</span>
            <span v-if="autoCategoryLabel" class="auto-category-label">{{ autoCategoryLabel }}</span>
            </div>
          </div>
        </div>
        <div class="edit-card publish-card">
          <div class="publish-row">
            <div class="publish-info">
              <span class="publish-count">{{ imagePreviews.length }}/8 张图片</span>
              <span class="publish-divider">|</span>
              <span class="publish-count">{{ form.content.length }}/1000 字</span>
            </div>
            <button class="publish-btn-primary" :disabled="!form.title || !imagePreviews.length" @click="handlePublish">{{ isEdit ? "保存修改" : "发布笔记" }}</button>
          </div>
        </div>
      </div>

      <!-- Image preview overlay -->
      <Transition name="preview-fade">
        <div v-if="previewImgVisible" class="preview-overlay" @click.self="previewImgVisible = false">
          <button class="preview-close-btn" @click="previewImgVisible = false">&times;</button>
          <button class="preview-nav-btn prev" @click.stop="prevPreviewImg">&#8249;</button>
          <img :src="previewImgList[previewImgIndex]" class="preview-full-img" />
          <button class="preview-nav-btn next" @click.stop="nextPreviewImg">&#8250;</button>
          <div class="preview-counter">{{ previewImgIndex + 1 }} / {{ previewImgList.length }}</div>
        </div>
      </Transition>
    </div>

    <!-- Bottom spec bar -->
    <div class="spec-bar" v-if="activeFormat === 'video'">
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
    <div class="spec-bar" v-if="activeFormat === 'image'">
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">图片尺寸</span>
          <span class="spec-value">支持 JPG、PNG、WEBP，单张不超过20MB</span>
        </div>
      </div>
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">版权说明</span>
          <span class="spec-value">请上传原创图片，避免侵权</span>
        </div>
      </div>
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">图片数量</span>
          <span class="spec-value">最多上传8张，支持多选上传</span>
        </div>
      </div>
    </div>
    <div class="spec-bar" v-if="false">
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">字数限制</span>
          <span class="spec-value">正文最多2000字，建议500字以上</span>
        </div>
      </div>
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">内容要求</span>
          <span class="spec-value">支持图文混排，可添加话题标签</span>
        </div>
      </div>
      <div class="spec-item">
        <svg class="spec-icon" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
        <div class="spec-text">
          <span class="spec-label">版权说明</span>
          <span class="spec-value">请发布原创内容，尊重他人知识产权</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { useUserStore } from "../stores/user"
import { notesApi } from "../api/notes"
const categories = ref([])
const TAG_TO_CATEGORY = { '美妆':'beauty','旅行':'travel','美食':'food','穿搭':'fashion','健身':'fitness','数码':'tech','学习':'study','艺术':'art','生活':'life','其他':'other' }
const hotTags = ref([{name:'美妆'},{name:'旅行'},{name:'美食'},{name:'穿搭'},{name:'健身'},{name:'数码'},{name:'学习'},{name:'艺术'},{name:'生活'},{name:'其他'}])
const autoCategoryLabel = ref('')
onMounted(async () => {
  try {
    const res = await notesApi.getCategories()
    categories.value = res || []
  } catch (e) {}
})

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeFormat = ref("video")
const previewUrl = ref("")
const videoFile = ref(null)
const videoCoverFile = ref(null)
const imageFiles = ref([])
const imagePreviews = ref([])
const previewImgVisible = ref(false)
const previewImgIndex = ref(0)
const previewImgList = ref([])
const showTagInput = ref(false)
const tagInput = ref("")

function previewImage(idx) {
  previewImgList.value = imagePreviews.value
  previewImgIndex.value = idx
  previewImgVisible.value = true
}
function prevPreviewImg() {
  previewImgIndex.value = (previewImgIndex.value - 1 + previewImgList.value.length) % previewImgList.value.length
}
function nextPreviewImg() {
  previewImgIndex.value = (previewImgIndex.value + 1) % previewImgList.value.length
}
function addTagToContent() {
  form.content += (form.content ? ' ' : '') + '#'
  setTimeout(() => { const ta = document.querySelector('.img-content-input'); if (ta) { ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length) } }, 50)
}
function insertTagToContent(name) {
  const tag = '#' + name
  if (!form.content.includes(tag)) { form.content += (form.content ? ' ' : '') + tag }
  // Auto-set category from tag name
  const catKey = TAG_TO_CATEGORY[name]
  if (catKey) {
    form.category = catKey
    autoCategoryLabel.value = '已分类：' + name
  }
  setTimeout(() => { const ta = document.querySelector('.img-content-input'); if (ta) { ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length) } }, 50)
}
const isEdit = computed(() => !!route.params.id)
const editId = computed(() => route.params.id)

const form = reactive({
  title: "", content: "", tag_names: [], category: ""
})

onMounted(async () => {
  if (isEdit.value) await loadEditData()
})

async function loadEditData() {
  try {
    const note = await notesApi.getNote(editId.value)
    if (!note) { console.error("笔记不存在"); router.back(); return }
    form.title = note.title || ""
    form.content = note.content || ""
    form.tag_names = (note.tags || []).map(t => t.name)
    form.category = note.category || ""
    imagePreviews.value = []
    if (note.media_list?.length) {
      if (note.type === 1) {
        const video = note.media_list.find(m => m.media_type === 1)
        if (video) previewUrl.value = video.file
      } else {
        note.media_list.forEach(m => imagePreviews.value.push(m.file))
      }
    }
    activeFormat.value = note.type === 1 ? "video" : "image"
  } catch (e) { console.error("加载编辑数据失败:", e); router.back() }
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
      captureVideoFrame(files[0])
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
    captureVideoFrame(files[0])
  } else {
    files.forEach(f => {
      imageFiles.value.push(f)
      imagePreviews.value.push(URL.createObjectURL(f))
    })
  }
}


function captureVideoFrame(file) {
  const video = document.createElement("video")
  video.preload = "metadata"
  video.muted = true
  video.playsInline = true
  video.src = URL.createObjectURL(file)
  video.onloadeddata = () => {
    video.currentTime = 0.1
  }
  video.onseeked = () => {
    const canvas = document.createElement("canvas")
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext("2d")
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    canvas.toBlob((blob) => {
      if (blob) {
        videoCoverFile.value = new File([blob], "cover.jpg", { type: "image/jpeg" })
      }
    }, "image/jpeg", 0.85)
    URL.revokeObjectURL(video.src)
    video.remove()
  }
  video.onerror = () => {
    URL.revokeObjectURL(video.src)
    video.remove()
  }
}

async function handlePublish() {
  if (!form.title) return
  // Auto-parse #tags from content and set category
  if (activeFormat.value === 'image') {
    const contentTags = parseTagsFromContent(form.content)
    contentTags.forEach(t => {
      if (!form.tag_names.includes(t)) form.tag_names.push(t)
      if (!form.category && TAG_TO_CATEGORY[t]) {
        form.category = TAG_TO_CATEGORY[t]
      }
    })
  }
  const fd = new FormData()
  fd.append("title", form.title)
  fd.append("content", form.content)
  fd.append("type", activeFormat.value === "video" ? 1 : 0)
  if (form.category) fd.append("category", form.category)
  form.tag_names.forEach(t => fd.append("tag_names", t))
  if (activeFormat.value === "video" && videoFile.value) {
    fd.append("video", videoFile.value)
    if (videoCoverFile.value) {
      fd.append("cover_img", videoCoverFile.value)
    }
  } else {
    imageFiles.value.forEach(f => fd.append("images", f))
  }
  try {
    if (isEdit.value) {
      await notesApi.updateNote(editId.value, fd)
      ElMessage.success("修改已保存")
    } else {
      await notesApi.createNote(fd)
    }
    router.push("/user/" + userStore.user.id)
  } catch (e) { ElMessage.error("保存失败:" + (e.message || e)) }
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
.edit-title { font-size: 18px; font-weight: 700; color: #222; }
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
.video-preview-area { width: 100%; border-radius: 12px; overflow: hidden; background: #000; }
.edit-video { width: 100%; max-height: 400px; display: block; }
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
.category-selector { margin-bottom: 8px; }
.category-select { width: 160px; }
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

.image-edit-wrapper { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; }
.edit-card { background: #fff; border: 1px solid #f0f0f0; border-radius: 16px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.edit-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid #f5f5f5; }
.card-header-icon { width: 18px; height: 18px; flex-shrink: 0; }
.edit-card-title { font-size: 15px; font-weight: 600; color: #222; }
.image-upload-grid { display: flex; gap: 10px; flex-wrap: wrap; }
.upload-box { width: 100px; height: 100px; border: 2px dashed #ddd; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; cursor: pointer; transition: all 0.2s; background: #fafafa; flex-shrink: 0; }
.upload-box:hover { border-color: #ff2442; background: #fff5f5; }
.upload-box-label { font-size: 12px; color: #999; }
.thumb-card { width: 100px; height: 100px; border-radius: 12px; overflow: hidden; position: relative; flex-shrink: 0; background: #f5f5f5; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.thumb-card img { width: 100%; height: 100%; object-fit: cover; }
.thumb-card.thumb-empty { border: 1px dashed #e8e8e8; cursor: default; }
.thumb-remove { position: absolute; top: 4px; right: 4px; width: 20px; height: 20px; background: rgba(0,0,0,0.5); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; opacity: 0; transition: opacity 0.15s; }
.thumb-card:hover .thumb-remove { opacity: 1; }
.thumb-order { position: absolute; bottom: 4px; left: 4px; width: 18px; height: 18px; background: rgba(0,0,0,0.5); color: white; font-size: 10px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.img-title-input { width: 100%; border: none; border-bottom: 1px solid #f0f0f0; padding: 12px 0; font-size: 17px; font-weight: 600; outline: none; font-family: inherit; color: #222; }
.img-title-input::placeholder { color: #ccc; font-weight: 400; }
.img-title-input:focus { border-bottom-color: #ff2442; }
.img-content-wrapper { position: relative; margin-top: 8px; }
.img-content-input { width: 100%; border: none; padding: 12px 0; font-size: 14px; line-height: 1.7; outline: none; resize: vertical; min-height: 100px; font-family: inherit; color: #444; }
.img-content-input::placeholder { color: #ccc; }
.content-counter { position: absolute; bottom: 8px; right: 0; font-size: 11px; color: #bbb; }
.quick-bar { margin-top: 12px; padding-top: 12px; border-top: 1px solid #f5f5f5; }
.quick-actions { display: flex; gap: 8px; margin-bottom: 10px; }
.quick-btn { display: flex; align-items: center; gap: 4px; padding: 6px 14px; border: none; border-radius: 20px; font-size: 12px; color: #666; cursor: pointer; transition: all 0.15s; background: linear-gradient(135deg, #f5f0ff, #f0f4ff); }
.quick-btn:hover { background: linear-gradient(135deg, #ede5ff, #e5eeff); color: #333; }
.hot-tags { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.hot-tag-label { font-size: 11px; color: #bbb; white-space: nowrap; }
.hot-tag { font-size: 11px; color: #ff2442; cursor: pointer; padding: 2px 8px; border-radius: 10px; background: #fff0f0; transition: background 0.15s; }
.hot-tag:hover { background: #ffe0e0; }
.hot-tag.tag-active { background: #ff2442; color: #fff; }
.auto-category-label { display: inline-block; font-size: 11px; color: #999; margin-left: 8px; }
.hot-tag.tag-active { background: #ff2442; color: #fff; }
.auto-category-label { display: inline-block; font-size: 11px; color: #999; margin-left: 8px; }
.publish-card { background: #fafafa; border-color: #e8e8e8; }
.publish-row { display: flex; align-items: center; justify-content: space-between; }
.publish-info { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #999; }
.publish-divider { color: #e0e0e0; }
.publish-btn-primary { background: #ff2442; color: #fff; border: none; border-radius: 20px; padding: 10px 32px; font-size: 14px; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
.publish-btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.publish-btn-primary:hover:not(:disabled) { opacity: 0.9; }
.preview-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 5000; display: flex; align-items: center; justify-content: center; }
.preview-close-btn { position: absolute; top: 20px; right: 24px; background: none; border: none; color: white; font-size: 36px; cursor: pointer; z-index: 10; }
.preview-nav-btn { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.15); border: none; color: white; font-size: 48px; width: 50px; height: 80px; border-radius: 8px; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; transition: background 0.15s; }
.preview-nav-btn:hover { background: rgba(255,255,255,0.25); }
.preview-nav-btn.prev { left: 20px; }
.preview-nav-btn.next { right: 20px; }
.preview-full-img { max-width: 85vw; max-height: 85vh; object-fit: contain; border-radius: 8px; }
.preview-counter { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); color: rgba(255,255,255,0.7); font-size: 14px; }
.preview-fade-enter-active, .preview-fade-leave-active { transition: opacity 0.2s; }
.preview-fade-enter-from, .preview-fade-leave-to { opacity: 0; }

</style>





