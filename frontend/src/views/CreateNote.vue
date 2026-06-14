<template>
  <div class="create">
    <NavBar />
    <div class="form">
      <h2>发布笔记</h2>
      <el-input v-model="form.title" placeholder="标题" class="mb-3" />
      <el-input v-model="form.content" type="textarea" :rows="6" placeholder="写点什么..." class="mb-3" />
      <div class="mb-3">
        <input type="file" multiple accept="image/*" @change="handleFileChange" />
      </div>
      <div class="preview" v-if="previews.length">
        <img v-for="(url, i) in previews" :key="i" :src="url" class="preview-img" />
      </div>
      <el-button type="primary" @click="handlePublish" :loading="loading" class="w-full">发布</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { notesApi } from "../api/notes"
import NavBar from "../components/NavBar.vue"

const router = useRouter()
const loading = ref(false)
const files = ref([])
const previews = ref([])
const form = reactive({ title: "", content: "" })

function handleFileChange(e) {
  files.value = Array.from(e.target.files || [])
  previews.value = files.value.map(f => URL.createObjectURL(f))
}

async function handlePublish() {
  if (!form.title) return
  loading.value = true
  try {
    const fd = new FormData()
    fd.append("title", form.title)
    fd.append("content", form.content)
    files.value.forEach(f => fd.append("images", f))
    await notesApi.createNote(fd)
    router.push("/")
  } catch (e) {} finally { loading.value = false }
}
</script>

<style scoped>
.form { max-width: 600px; margin: 0 auto; padding: 16px; }
.mb-3 { margin-bottom: 16px; }
.w-full { width: 100%; }
.preview { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.preview-img { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; }
</style>
