<script setup>
// Moldura "Sódio": capa/carrossel e metadados no topo do capítulo, dock de leitura, narração
// com marcador, paleta Lázaro, cartões de personagem e "próximo capítulo".
import DefaultTheme from 'vitepress/theme'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useData, useRouter, withBase } from 'vitepress'
import { buildChapterIndex, neighbors } from './chapter-index.mjs'
import { bookAt } from './terminal-lore.mjs'
import { archivePages } from './lib/palette-search.mjs'
import { data as stats } from './chapters.data.mjs'
import { initNarration, onPageChange, stop as stopNarration } from './composables/useNarration.js'
import { initReaderPrefs, exitFocus } from './composables/useReaderPrefs.js'
import { loadFurthest, measure, startReading, track, useReading } from './composables/useReading.js'
import { useShortcuts } from './composables/useShortcuts.js'
import ChapterCarousel from './components/ChapterCarousel.vue'
import ReaderDock from './components/ReaderDock.vue'
import LazaroPalette from './components/LazaroPalette.vue'
import NextChapterCard from './components/NextChapterCard.vue'
import CastHover from './components/CastHover.vue'
import CastDossier from './components/CastDossier.vue'

const { Layout } = DefaultTheme
const { frontmatter, page, theme } = useData()
const router = useRouter()
const { progress, minutes, furthest } = useReading()

const chapters = computed(() => buildChapterIndex(theme.value.sidebar))
const pages = computed(() => archivePages(theme.value.sidebar))
const gallery = computed(() => frontmatter.value.gallery ?? [])
const isHome = computed(() => frontmatter.value.layout === 'home')
const number = computed(() => {
  const m = page.value.relativePath?.match(/(?:^|\/)capitulo-(\d+)\.md$/)
  return m ? Number(m[1]) : null
})
const around = computed(() => neighbors(chapters.value, number.value))
const nextCover = computed(() => stats.find((c) => c.n === around.value.next?.number)?.image)
const place = computed(() => frontmatter.value['Localização'])
const people = computed(() => String(frontmatter.value['Personagens Presentes'] ?? '').split(/,\s*/).filter(Boolean).slice(0, 5))

const paletteOpen = ref(false)
const togglePalette = () => { paletteOpen.value = !paletteOpen.value }
// A narração não para aqui: na troca de página ela retoma sozinha se o modo contínuo estiver ligado.
const go = (chapter) => chapter && router.go(withBase(chapter.link))
const goNumber = (n) => { paletteOpen.value = false; go({ link: `/capitulo-${n}` }) }
const goLink = (link) => { paletteOpen.value = false; router.go(withBase(link)) }

useShortcuts({ palette: togglePalette, prev: () => go(around.value.prev), next: () => go(around.value.next) })

const refresh = () => nextTick(() => {
  track(number.value)
  measure()
  if (isHome.value) stopNarration()
  else onPageChange()
})

onMounted(() => {
  initReaderPrefs()
  loadFurthest()
  initNarration(() => (around.value.next ? () => go(around.value.next) : null))
  startReading()
  refresh()
})
watch(() => page.value.relativePath, () => { exitFocus(); refresh() })
</script>

<template>
  <div class="reading-progress-bar" :style="{ width: `${progress * 100}%` }" aria-hidden="true" />
  <Layout>
    <template #doc-before>
      <ChapterCarousel v-if="gallery.length > 1" :key="page.relativePath" :images="gallery" :title="page.title" />
      <div v-else-if="frontmatter.image" class="chapter-cover-container">
        <img :src="frontmatter.image" class="chapter-cover" fetchpriority="high" decoding="async" :alt="frontmatter.title || 'Imagem do Capítulo'">
      </div>
      <div v-if="number" class="chapter-meta">
        <span class="hot">{{ bookAt(number) }}</span>
        <span>{{ minutes }} min de leitura</span>
        <span v-if="place">📍 {{ place }}</span>
        <span v-for="p in people" :key="p">{{ p }}</span>
      </div>
      <CastDossier v-if="page.relativePath === 'personagens.md'" title="Elenco" />
    </template>
    <template #layout-bottom>
      <ReaderDock v-if="!isHome" :is-chapter="!!number" :prev="around.prev" :next="around.next" @go="go" @lazaro="togglePalette" />
      <NextChapterCard :next="around.next" :cover="nextCover" />
      <CastHover v-if="number" :chapter="number" />
      <LazaroPalette :is-open="paletteOpen" :chapter="furthest" :chapters="chapters" :pages="pages"
        @close="paletteOpen = false" @go="goNumber" @link="goLink" />
    </template>
  </Layout>
</template>
