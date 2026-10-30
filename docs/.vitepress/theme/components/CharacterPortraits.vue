<script setup>
import { computed, ref } from 'vue'
import { withBase } from 'vitepress'
import { portraitGalleries } from '../portrait-galleries.mjs'

const props = defineProps({
  name: { type: String, required: true },
  portrait: { type: String, required: true },
})
const index = ref(0)
const slides = computed(() => [
  { src: props.portrait, label: 'Retrato de referência' },
  ...(portraitGalleries[props.portrait] || []),
])
const current = computed(() => slides.value[index.value])
const move = (direction) => {
  index.value = (index.value + direction + slides.value.length) % slides.value.length
}
</script>

<template>
  <section v-if="slides.length > 1" class="portrait-carousel" :aria-label="`Retratos de ${name}`" aria-roledescription="carrossel">
    <figure class="portrait-carousel__figure">
      <img :src="withBase(current.src)" :alt="`${name} — ${current.label}`" loading="lazy" decoding="async">
      <figcaption aria-live="polite">{{ current.label }} · {{ index + 1 }} / {{ slides.length }}</figcaption>
    </figure>
    <div class="portrait-carousel__controls">
      <button type="button" :aria-label="`Imagem anterior de ${name}`" @click="move(-1)">← Anterior</button>
      <button type="button" :aria-label="`Próxima imagem de ${name}`" @click="move(1)">Próxima →</button>
    </div>
  </section>
  <slot v-else />
</template>

<style scoped>
.portrait-carousel { width: min(100%, 36rem); margin: 1.5rem 0; }
.portrait-carousel__figure { margin: 0; }
.portrait-carousel__figure img { display: block; width: 100%; max-height: 32rem; object-fit: contain; object-position: left center; border-radius: 0.5rem; }
.portrait-carousel__figure figcaption { margin-top: 0.45rem; color: var(--vp-c-text-2); font-size: 0.9rem; }
.portrait-carousel__controls { display: flex; gap: 0.65rem; margin-top: 0.75rem; }
.portrait-carousel__controls button { border: 1px solid var(--vp-c-divider); border-radius: 0.4rem; padding: 0.45rem 0.8rem; color: var(--vp-c-text-1); cursor: pointer; }
.portrait-carousel__controls button:hover { border-color: var(--vp-c-brand-1); }
.portrait-carousel__controls button:focus-visible { outline: 2px solid var(--vp-c-brand-1); outline-offset: 3px; }
</style>
