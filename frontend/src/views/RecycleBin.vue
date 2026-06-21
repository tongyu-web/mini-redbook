<template>
  <div class="recycle-page">
    <!-- Sticky header -->
    <div class="rp-header">
      <button class="rp-back" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="20" height="20"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <h2 class="rp-title">回收站</h2>
      <button class="rp-cleanup" @click="cleanup">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        <span>清理过期</span>
      </button>
    </div>

    <!-- Subtitle -->
    <div class="rp-subtitle">笔记删除后进入回收站，30天内可恢复</div>

    <!-- Loading state -->
    <div v-if="loading" class="rp-center">
      <div class="rp-loader"></div>
      <p>加载中...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="items.length === 0" class="rp-center rp-empty">
      <svg viewBox="0 0 24 24" fill="none" stroke="#ddd" stroke-width="1.5" width="64" height="64"><path d="M21 12v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h7"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
      <p>回收站空空如也</p>
      <span>删除的笔记将会出现在这里</span>
    </div>

    <!-- Note list -->
    <div v-else class="rp-list">
      <div v-for="n in items" :key="n.id" class="rp-card">
        <div class="rp-card-left">
          <div v-if="n.cover_img" class="rp-cover">
            <img :src="n.cover_img" :alt="n.title" />
          </div>
          <div v-else class="rp-cover rp-cover-placeholder">
            {{ n.title?.[0] || "R" }}
          </div>
        </div>
        <div class="rp-card-body">
          <h4 class="rp-card-title">{{ n.title || "无标题" }}</h4>
          <div class="rp-card-meta">
            <svg viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" width="12" height="12"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span>删除于 {{ formatTime(n.deleted_at || n.created_at) }}</span>
          </div>
          <div class="rp-card-meta">
            <svg viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" width="12" height="12"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            <span>{{ n.days_left !== undefined ? "剩余 " + n.days_left + " 天" : "30天内可恢复" }}</span>
          </div>
        </div>
        <div class="rp-card-actions">
          <button class="rp-btn rp-btn-restore" @click="restore(n.id)" :disabled="restoring === n.id">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
            <span>{{ restoring === n.id ? "恢复中..." : "恢复" }}</span>
          </button>
          <button class="rp-btn rp-btn-delete" @click="hardDelete(n.id)" :disabled="deleting === n.id">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            <span>{{ deleting === n.id ? "删除中..." : "永久删除" }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { notesApi } from "../api/notes"
import { ElMessage, ElMessageBox } from "element-plus"

const items = ref([])
const loading = ref(true)
const restoring = ref("")
const deleting = ref("")

onMounted(load)

async function load() {
  loading.value = true
  try {
    const res = await notesApi.getRecycle()
    items.value = res.results || res || []
  } catch (e) { items.value = [] }
  finally { loading.value = false }
}

async function restore(id) {
  restoring.value = id
  try {
    await notesApi.restoreNote(id)
    ElMessage.success("已恢复")
    items.value = items.value.filter(n => n.id !== id)
  } catch (e) {} finally { restoring.value = "" }
}

async function hardDelete(id) {
  try {
    await ElMessageBox.confirm("确定永久删除？此操作不可撤销！", "警告", { confirmButtonText: "删除", cancelButtonText: "取消", type: "warning" })
    deleting.value = id
    await notesApi.hardDeleteNote(id)
    ElMessage.success("已永久删除")
    items.value = items.value.filter(n => n.id !== id)
  } catch (e) {} finally { deleting.value = "" }
}

async function cleanup() {
  try {
    const res = await notesApi.cleanupRecycle()
    ElMessage.success(res.message || "清理完成")
    await load()
  } catch (e) {}
}

function formatTime(t) {
  if (!t) return ""
  const d = new Date(t)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return "刚刚"
  if (diff < 3600000) return Math.floor(diff / 60000) + "分钟前"
  if (diff < 86400000) return Math.floor(diff / 3600000) + "小时前"
  return d.toLocaleDateString("zh-CN", { month: "2-digit", day: "2-digit" })
}
</script>

<style scoped>
.recycle-page {
  min-height: 100vh;
  background: #f5f5f5;
}
/* Header */
.rp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 10;
}
.rp-back {
  width: 34px; height: 34px;
  display: flex; align-items: center; justify-content: center;
  border: none; background: none; cursor: pointer;
  border-radius: 50%; color: #333;
  transition: background 0.15s;
}
.rp-back:hover { background: #f5f5f5; }
.rp-title {
  font-size: 16px; font-weight: 700; margin: 0; color: #222;
}
.rp-cleanup {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 12px; border: none; background: #fff0f0;
  color: #ff2442; border-radius: 20px; cursor: pointer;
  font-size: 12px; font-weight: 500;
  transition: background 0.15s;
}
.rp-cleanup:hover { background: #ffe0e0; }

/* Subtitle */
.rp-subtitle {
  text-align: center;
  padding: 14px 16px 0;
  font-size: 12px; color: #bbb;
}

/* Center states */
.rp-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #ccc;
}
.rp-center p { margin: 12px 0 4px; font-size: 14px; }
.rp-empty span { font-size: 12px; color: #ddd; }

/* Loader */
.rp-loader {
  width: 28px; height: 28px;
  border: 3px solid #f0f0f0;
  border-top-color: #ff2442;
  border-radius: 50%;
  animation: rp-spin 0.6s linear infinite;
}
@keyframes rp-spin { to { transform: rotate(360deg); } }

/* List */
.rp-list {
  max-width: 640px;
  margin: 0 auto;
  padding: 12px 16px 80px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Card */
.rp-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  gap: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}
.rp-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }

.rp-card-left { flex-shrink: 0; }
.rp-cover {
  width: 56px; height: 56px;
  border-radius: 8px; overflow: hidden;
  background: #f0f0f0;
}
.rp-cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.rp-cover-placeholder {
  display: flex;
  align-items: center; justify-content: center;
  font-size: 20px; font-weight: 700; color: #fff;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.rp-card-body { flex: 1; min-width: 0; }
.rp-card-title {
  margin: 0 0 6px;
  font-size: 14px; font-weight: 600; color: #222;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.rp-card-meta {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; color: #999; margin-top: 3px;
}

.rp-card-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}
.rp-btn {
  display: flex; align-items: center; gap: 3px;
  padding: 5px 10px; border: none; border-radius: 8px;
  cursor: pointer; font-size: 11px; font-weight: 500;
  white-space: nowrap;
  transition: background 0.15s, opacity 0.15s;
}
.rp-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.rp-btn-restore {
  background: #fff0f0; color: #ff2442;
}
.rp-btn-restore:hover:not(:disabled) { background: #ffe0e0; }
.rp-btn-delete {
  background: #f5f5f5; color: #999;
}
.rp-btn-delete:hover:not(:disabled) { background: #eee; color: #666; }
</style>
