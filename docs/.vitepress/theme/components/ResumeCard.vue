<script setup>
// "Continue de onde parou": aparece só para quem já passou do capítulo 1.
import { computed, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import { data as chapters } from '../chapters.data.mjs'
import { bookAt } from '../terminal-lore.mjs'
import { loadFurthest } from '../composables/useReading.js'

const n = ref(0)
onMounted(() => { n.value = loadFurthest() })
const c = computed(() => (n.value > 1 ? chapters.find((ch) => ch.n === n.value) : null))
const next = computed(() => chapters.find((ch) => ch.n === n.value + 1))
const done = computed(() => Math.round((n.value / (chapters.at(-1)?.n ?? 1)) * 100))
</script>

<template>
  <Transition name="sd-pop">
    <section v-if="c" class="resume-card" aria-label="Continue de onde parou">
      <img v-if="c.image" :src="withBase(c.image)" alt="" loading="lazy">
      <div class="rc-body">
        <p class="sd-eyebrow">Continue de onde parou</p>
        <h3>Cap. {{ c.n }} · {{ c.title }}</h3>
        <p class="rc-sub">{{ bookAt(c.n) }} · {{ Math.ceil(c.words / 200) }} min de leitura<span v-if="next"> · depois: {{ next.title }}</span></p>
        <span class="rc-meter" role="progressbar" :aria-valuenow="done" aria-valuemin="0" aria-valuemax="100" aria-label="Progresso na obra"><i :style="{ width: `${done}%` }" /></span>
      </div>
      <a class="sd-btn pri" :href="withBase(`/capitulo-${c.n}`)">Retomar</a>
    </section>
  </Transition>
</template>
