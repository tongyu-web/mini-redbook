<template>
  <div class="search-page">
    <div class="content">
      <div v-if="results.length" class="results">
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
import { ref } from "vue"

const results = ref([])
</script>

<style scoped>
.search-page { }
.content { max-width: 700px; margin: 0 auto; padding: 16px; }
.results { display: flex; flex-direction: column; gap: 12px; }
.result-item { display: flex; gap: 12px; cursor: pointer; padding: 8px; border-radius: 8px; }
.result-item:hover { background: #f9f9f9; }
.result-cover { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; }
.result-info h4 { margin: 0 0 4px; }
.result-user { font-size: 12px; color: #999; }
</style>