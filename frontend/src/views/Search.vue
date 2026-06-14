<template>
  <div class="search-page">
<div class="content">
      <el-input v-model="keyword" placeholder="搜索笔记、用户、标签..." @input="onInput" clearable class="search-input" />
      <div v-if="suggestions.length && keyword" class="suggestions">
        <div v-for="s in suggestions" :key="s.name" @click="doSearch(s.name)" class="suggest-item">{{ s.name }}</div>
      </div>
      <div v-else-if="!keyword" class="hot-tags">
        <h3>热门标签</h3>
        <div class="tags">
          <el-tag v-for="t in hotTags" :key="t.name" @click="doSearch(t.name)" class="tag">{{ t.name }}</el-tag>
        </div>
      </div>
      <div v-else class="results">
        <div v-for="n in results" :key="n.id" class="result-item" @click="$router.push('/note/' + n.id)">
          <img :src="n.cover_img" v-if="n.cover_img" class="result-cover" />
          <div class="result-info">
            <h4>{{ n.title }}</h4>
            <span class="result-user">{{ n.user_nickname }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { searchApi } from "../api/search"


const keyword = ref("")
const suggestions = ref([])
const hotTags = ref([])
const results = ref([])
let timer = null

onMounted(async () => {
  hotTags.value = await searchApi.hotTags()
})

function onInput() {
  clearTimeout(timer)
  if (!keyword.value) { suggestions.value = []; results.value = []; return }
  timer = setTimeout(async () => {
    suggestions.value = await searchApi.suggest(keyword.value)
    const res = await searchApi.search({ q: keyword.value, type: "note" })
    results.value = res.results || res || []
  }, 300)
}

async function doSearch(q) {
  keyword.value = q
  const res = await searchApi.search({ q, type: "note" })
  results.value = res.results || res || []
  suggestions.value = []
}
</script>

<style scoped>
.search-page { padding-bottom: 60px; }
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.search-input { margin-bottom: 16px; }
.suggestions { margin-bottom: 16px; }
.suggest-item { padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f5f5f5; }
.suggest-item:hover { background: #f9f9f9; }
.hot-tags h3 { margin-bottom: 12px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { cursor: pointer; }
.results { display: flex; flex-direction: column; gap: 12px; }
.result-item { display: flex; gap: 12px; cursor: pointer; padding: 8px; border-radius: 8px; }
.result-item:hover { background: #f9f9f9; }
.result-cover { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; }
.result-info h4 { margin: 0 0 4px; }
.result-user { font-size: 12px; color: #999; }
</style>
