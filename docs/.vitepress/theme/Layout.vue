<script setup>
import DefaultTheme from 'vitepress/theme'
import AudioPlayer from './AudioPlayer.vue'
import { useData } from 'vitepress'

const { Layout } = DefaultTheme
const { frontmatter } = useData()
</script>

<template>
  <Layout>
    <template #doc-before>
      <div v-if="frontmatter.image" class="chapter-cover-container">
        <img :src="frontmatter.image" class="chapter-cover" :alt="frontmatter.title || 'Imagem do Capítulo'" />
      </div>
      <AudioPlayer />
    </template>
  </Layout>
</template>

<style>
.chapter-cover-container {
  margin-bottom: 2rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.chapter-cover {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  display: block;
}
</style>
