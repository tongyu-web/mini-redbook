<template>
  <div class="recycle">
    <div class="header">
      <el-button text @click="$router.back()">← 返回</el-button>
      <h2>回收站</h2>
      <el-button text type="danger" size="small" @click="cleanup">清理过期</el-button>
    </div>
    <div class="content">
      <el-alert title="笔记删除后进入回收站，30天内可恢复" type="info" show-icon :closable="false" class="mb-3" />
      <div v-if="loading" class="center">加载中...</div>
      <div v-else-if="items.length === 0" class="center empty">回收站为空</div>
      <div v-else>
        <div v-for="n in items" :key="n.id" class="item">
          <div class="item-info">
            <h4>{{ n.title }}</h4>
            <span class="item-time">删除于 {{ n.created_at }}</span>
          </div>
          <div class="item-actions">
            <el-button size="small" type="primary" @click="restore(n.id)" :loading="restoring === n.id">恢复</el-button>
            <el-button size="small" type="danger" @click="hardDelete(n.id)" :loading="deleting === n.id">永久删除</el-button>
          </div>
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
</script>

<style scoped>
.recycle { min-height: 100vh; background: #fff; }
.header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #eee; position: sticky; top: 0; background: white; z-index: 10; }
.header h2 { font-size: 16px; margin: 0; }
.content { max-width: 600px; margin: 0 auto; padding: 16px; }
.mb-3 { margin-bottom: 16px; }
.center { text-align: center; padding: 40px; color: #999; }
.item { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.item-info h4 { margin: 0 0 4px; font-size: 14px; }
.item-time { font-size: 12px; color: #999; }
.item-actions { display: flex; gap: 8px; flex-shrink: 0; }
</style>
