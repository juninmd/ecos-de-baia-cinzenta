<script setup>
// Cartão de personagem no texto: a primeira menção de cada nome já apresentado vira um link
// discreto; ao passar o mouse ou focar, o retrato canônico aparece. Nunca mostra o futuro.
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, withBase } from 'vitepress'
import { aliasPattern, castAt } from '../lib/cast.mjs'
import { textNodes } from '../lib/narration-dom.mjs'

const props = defineProps({ chapter: Number })
const route = useRoute()
const card = ref(null)
let hideTimer = 0

function decorate() {
  if (!props.chapter) return
  const cast = castAt(props.chapter)
  const seen = new Set()
  document.querySelectorAll('.vp-doc p').forEach((p) => {
    const queue = textNodes(p)
    while (queue.length) {
      const node = queue.shift()
      if (node.parentElement.closest('a, .cast-ref')) continue
      const pattern = aliasPattern(cast.filter((c) => !c.alias.every((a) => seen.has(a))))
      const m = pattern && pattern.exec(node.data)
      if (!m) continue
      const person = cast.find((c) => c.alias.includes(m[1]))
      person.alias.forEach((a) => seen.add(a))
      const name = node.splitText(m.index)
      queue.unshift(name.splitText(m[1].length)) // o resto do trecho ainda pode citar outro nome
      const span = document.createElement('span')
      span.className = 'cast-ref'
      span.tabIndex = 0
      span.dataset.cast = person.key
      name.replaceWith(span)
      span.append(name)
    }
  })
}

function show(e) {
  const el = e.target.closest?.('.cast-ref')
  if (!el) return
  clearTimeout(hideTimer)
  const person = castAt(props.chapter).find((c) => c.key === el.dataset.cast)
  const r = el.getBoundingClientRect()
  card.value = { ...person, x: Math.min(Math.max(r.left + r.width / 2, 130), window.innerWidth - 130), y: r.top }
}
const keep = () => clearTimeout(hideTimer)
const dismiss = () => { card.value = null }
const hide = (e) => { if (e.target.closest?.('.cast-ref')) hideTimer = setTimeout(() => { card.value = null }, 120) }

watch(() => route.path, () => { card.value = null; nextTick(() => setTimeout(decorate, 50)) })
onMounted(() => {
  setTimeout(decorate, 50)
  document.addEventListener('pointerover', show)
  document.addEventListener('pointerout', hide)
  document.addEventListener('focusin', show)
  document.addEventListener('focusout', hide)
  window.addEventListener('scroll', dismiss, { passive: true })
})
onUnmounted(() => {
  document.removeEventListener('pointerover', show)
  document.removeEventListener('pointerout', hide)
  document.removeEventListener('focusin', show)
  document.removeEventListener('focusout', hide)
  window.removeEventListener('scroll', dismiss)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="sd-pop">
      <a v-if="card" class="cast-pop" :href="withBase(`/personagens#${card.anchor}`)" :style="{ left: `${card.x}px`, top: `${card.y}px` }"
        @pointerenter="keep" @pointerleave="card = null">
        <img :src="withBase(card.retrato)" alt="">
        <span><strong>{{ card.nome }}</strong><small>{{ card.papel }}<template v-if="card.rotulo"> · {{ card.rotulo }}</template></small></span>
      </a>
    </Transition>
  </Teleport>
</template>
