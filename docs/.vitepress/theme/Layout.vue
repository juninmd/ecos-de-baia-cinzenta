<script setup>
import DefaultTheme from 'vitepress/theme'
import AudioPlayer from './AudioPlayer.vue'

const { Layout } = DefaultTheme
</script>

<template>
  <Layout>
    <template #doc-before>
      <AudioPlayer />
    </template>
  </Layout>
</template>
