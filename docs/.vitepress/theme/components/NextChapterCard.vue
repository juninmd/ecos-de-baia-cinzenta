<script setup>
// Fim da narração: cartão com contagem regressiva para o próximo capítulo (cancelável).
import { useNarration, cancelCountdown } from '../composables/useNarration.js'
import { withBase } from 'vitepress'

defineProps({ next: Object, cover: String })
const { countdown } = useNarration()
</script>

<template>
  <Transition name="sd-pop">
    <aside v-if="countdown > 0 && next" class="next-card" role="status" aria-live="polite">
      <img v-if="cover" :src="withBase(cover)" alt="" loading="lazy">
      <div>
        <small>A seguir · em {{ countdown }} s</small>
        <strong>{{ next.title }}</strong>
        <span class="nc-bar"><i :style="{ width: `${(5 - countdown) * 20}%` }" /></span>
        <button type="button" @click="cancelCountdown">Ficar aqui</button>
      </div>
    </aside>
  </Transition>
</template>
