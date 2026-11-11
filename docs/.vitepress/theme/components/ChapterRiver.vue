<script setup>
// Rio de capítulos: uma barra por capítulo, altura = palavras do arquivo, cor = livro.
// Aceso em sódio o que o leitor já abriu; a barra branca marca onde ele parou.
import { computed, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import { data as chapters } from '../chapters.data.mjs'
import { BOOKS } from '../terminal-lore.mjs'
import { loadFurthest, useReading } from '../composables/useReading.js'

const { furthest } = useReading()
const read = ref(0) // 0 até montar: o HTML estático não presume progresso de ninguém
const book = ref(-1)
const tip = ref(null)
const box = ref(null)
onMounted(() => { read.value = loadFurthest() })

const max = Math.max(...chapters.map((c) => c.words))
const last = chapters.at(-1)?.n ?? 1
const bookOf = (n) => BOOKS.findIndex(([a, b]) => n >= a && n <= b)
const books = BOOKS.map(([a, b, name], i) => ({ i, a, b: Math.min(b, last), name: name.replace(/^Livro \d+:\s*/, ''), span: Math.min(b, last) - a + 1 }))
const bars = chapters.map((c) => ({ ...c, b: bookOf(c.n), h: Math.max(6, (c.words / max) * 100) }))
const status = (n) => (n <= read.value ? (n === read.value ? 'onde você parou' : 'lido') : n === read.value + 1 ? 'próximo da fila' : 'ainda não lido')
const pct = computed(() => Math.round((Math.min(read.value, last) / last) * 100))

function show(c, e) {
  const r = e.currentTarget.getBoundingClientRect()
  const b = box.value.getBoundingClientRect()
  tip.value = { ...c, x: Math.min(Math.max(r.left - b.left + r.width / 2, 120), b.width - 120), y: r.top - b.top }
}
</script>

<template>
  <section id="mapa" class="river-sec">
    <div class="river-head">
      <div>
        <p class="sd-eyebrow">Mapa da obra</p>
        <h2 class="sd-h2">O rio de {{ chapters.length }} capítulos</h2>
        <p class="sd-lede">Cada barra é um capítulo; a altura é a contagem de palavras. Em sódio, o que você já leu<span v-if="read > 1"> ({{ pct }}% da obra)</span>.</p>
      </div>
      <div class="river-chips" role="group" aria-label="Filtrar por livro">
        <button type="button" class="sd-chip" :aria-pressed="book === -1" @click="book = -1">Todos</button>
        <button v-for="b in books" :key="b.i" type="button" class="sd-chip" :style="{ '--c': `var(--sd-book-${b.i + 1})` }"
          :aria-pressed="book === b.i" @click="book = book === b.i ? -1 : b.i"><i />{{ b.name }}</button>
      </div>
    </div>
    <div ref="box" class="river-box" @pointerleave="tip = null">
      <div class="river-scroll">
        <ol class="river" aria-label="Capítulos">
          <li v-for="(c, i) in bars" :key="c.n" :style="{ '--h': `${c.h}%`, '--c': `var(--sd-book-${c.b + 1})`, '--i': i }"
            :class="{ read: c.n <= read, here: c.n === read && read > 1, dim: book >= 0 && c.b !== book }">
            <a :href="withBase(`/capitulo-${c.n}`)" :aria-label="`Capítulo ${c.n}: ${c.title}, ${status(c.n)}`"
              @pointerenter="show(c, $event)" @focus="show(c, $event)" @blur="tip = null" />
          </li>
        </ol>
        <div class="river-books" aria-hidden="true">
          <span v-for="b in books" :key="b.i" :style="{ flex: b.span, '--c': `var(--sd-book-${b.i + 1})` }">Livro {{ b.i + 1 }} · {{ b.name }}</span>
        </div>
      </div>
      <div v-if="tip" class="river-tip" :style="{ left: `${tip.x}px`, top: `${tip.y}px` }" aria-hidden="true">
        <small>Cap. {{ tip.n }} · Livro {{ tip.b + 1 }} · {{ tip.words.toLocaleString('pt-BR') }} palavras · {{ Math.ceil(tip.words / 200) }} min</small>
        <strong>{{ tip.title }}</strong>
        <small>{{ status(tip.n) }}</small>
      </div>
    </div>
  </section>
</template>
