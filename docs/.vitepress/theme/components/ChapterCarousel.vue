<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  images: { type: Array, required: true },
  title: { type: String, default: 'Capítulo' },
})

const track = ref(null)
const active = ref(0)
const loaded = ref(new Set([0, 1])) // só a imagem atual e as vizinhas são baixadas
const total = computed(() => props.images.length)
const showDots = computed(() => total.value <= 10)
let frame = 0

const reveal = (i) => {
  const next = new Set(loaded.value)
  for (const k of [i - 1, i, i + 1]) if (k >= 0 && k < total.value) next.add(k)
  loaded.value = next
}

const onScroll = () => {
  cancelAnimationFrame(frame)
  frame = requestAnimationFrame(() => {
    const el = track.value
    if (!el || !el.clientWidth) return
    const i = Math.min(total.value - 1, Math.max(0, Math.round(el.scrollLeft / el.clientWidth)))
    if (i !== active.value) { active.value = i; reveal(i) }
  })
}

const go = (index) => {
  const el = track.value
  if (!el) return
  const i = (index + total.value) % total.value
  reveal(i)
  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  el.scrollTo({ left: i * el.clientWidth, behavior: calm ? 'auto' : 'smooth' })
}

const onKey = (e) => {
  if (e.altKey || e.ctrlKey || e.metaKey) return // Alt+setas troca de capítulo (Layout)
  if (e.key === 'ArrowRight') { e.preventDefault(); go(active.value + 1) }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); go(active.value - 1) }
}
</script>

<template>
  <section class="chapter-cover-container chapter-carousel" aria-roledescription="carousel" :aria-label="`Imagens de ${title}`">
    <div ref="track" class="carousel-track" tabindex="0" @scroll.passive="onScroll" @keydown="onKey">
      <figure v-for="(src, i) in images" :key="src" class="carousel-slide" role="group"
        aria-roledescription="slide" :aria-label="`${i + 1} de ${total}`">
        <!-- src antes de class: tests/chapter_cover_build.test.mjs confere a capa no HTML pré-renderizado. -->
        <img :src="loaded.has(i) ? src : undefined" class="chapter-cover" :alt="`${title}: imagem ${i + 1} de ${total}`"
          :fetchpriority="i === 0 ? 'high' : undefined" decoding="async" draggable="false" />
      </figure>
    </div>
    <button class="carousel-btn prev" type="button" aria-label="Imagem anterior" @click="go(active - 1)">‹</button>
    <button class="carousel-btn next" type="button" aria-label="Próxima imagem" @click="go(active + 1)">›</button>
    <span class="carousel-count" aria-live="polite">{{ active + 1 }} / {{ total }}</span>
    <div class="carousel-footer">
      <div v-if="showDots" class="carousel-dots">
        <button v-for="(src, i) in images" :key="src" type="button" class="carousel-dot"
          :aria-label="`Ir para a imagem ${i + 1}`" :aria-current="i === active ? 'true' : undefined" @click="go(i)"></button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.chapter-carousel { position: relative; }

.carousel-track {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  overscroll-behavior-x: contain;
  background: #07070b;
}
.carousel-track::-webkit-scrollbar { display: none; }
.carousel-track:focus-visible { outline: 3px solid var(--neon-cyan, #06b6d4); outline-offset: -3px; }

.carousel-slide { flex: 0 0 100%; margin: 0; scroll-snap-align: center; scroll-snap-stop: always; }
.carousel-slide img { width: 100%; background: #07070b; user-select: none; }

.carousel-btn {
  position: absolute;
  top: 50%;
  z-index: 2;
  width: 44px;
  height: 44px;
  margin-top: -22px;
  border-radius: 50%;
  border: 1px solid rgba(168, 85, 247, 0.6);
  background: rgba(10, 10, 15, 0.7);
  color: #fff;
  font-size: 1.7rem;
  line-height: 1;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: background 0.2s ease, transform 0.2s ease;
}
.carousel-btn.prev { left: 12px; }
.carousel-btn.next { right: 12px; }
.carousel-btn:hover { background: var(--neon-purple, #a855f7); transform: scale(1.08); }
.carousel-btn:focus-visible { outline: 3px solid var(--neon-cyan, #06b6d4); outline-offset: 2px; }

.carousel-footer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 10px;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  pointer-events: none;
}
/* Canto superior: a arte costuma trazer legenda queimada na base. */
.carousel-count {
  position: absolute;
  top: 10px;
  right: 12px;
  z-index: 2;
  pointer-events: none;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(10, 10, 15, 0.7);
  color: #fff;
  font-family: var(--vp-font-family-mono);
  font-size: 0.8rem;
}
.carousel-dots { display: flex; gap: 2px; pointer-events: auto; }
.carousel-dot {
  width: 24px;
  height: 24px;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  position: relative;
}
.carousel-dot::after {
  content: "";
  position: absolute;
  inset: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.45);
  transition: background 0.2s ease, transform 0.2s ease;
}
.carousel-dot[aria-current="true"]::after { background: var(--neon-purple-light, #c084fc); transform: scale(1.35); }
.carousel-dot:focus-visible { outline: 2px solid var(--neon-cyan, #06b6d4); border-radius: 50%; }

@media (max-width: 640px) {
  .carousel-btn { width: 40px; height: 40px; margin-top: -20px; }
  .carousel-btn.prev { left: 6px; }
  .carousel-btn.next { right: 6px; }
}
</style>
