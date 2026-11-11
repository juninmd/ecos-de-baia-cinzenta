<script setup>
// Chuva em canvas: gotas que desviam do cursor e acendem em sódio perto dele. Pausa fora da tela
// e não roda com prefers-reduced-motion.
import { onMounted, onUnmounted, ref } from 'vue'

const canvas = ref(null)
let stop = () => {}

onMounted(() => {
  const cv = canvas.value
  if (!cv || matchMedia('(prefers-reduced-motion: reduce)').matches) return
  const ctx = cv.getContext('2d')
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const host = cv.parentElement
  let W = 0, H = 0, drops = [], mx = -1e4, my = -1e4, visible = true, raf = 0

  const size = () => {
    W = cv.width = cv.offsetWidth * dpr
    H = cv.height = cv.offsetHeight * dpr
    drops = Array.from({ length: Math.round((W * H) / 9000 / dpr) }, () => ({
      x: Math.random() * W, y: Math.random() * H, l: (8 + Math.random() * 18) * dpr, v: (9 + Math.random() * 12) * dpr, o: 0.12 + Math.random() * 0.4,
    }))
  }
  const move = (e) => { const r = cv.getBoundingClientRect(); mx = (e.clientX - r.left) * dpr; my = (e.clientY - r.top) * dpr }
  const leave = () => { mx = my = -1e4 }
  const draw = () => {
    raf = requestAnimationFrame(draw)
    if (!visible) return
    ctx.clearRect(0, 0, W, H)
    ctx.lineCap = 'round'
    const R = 140 * dpr
    for (const d of drops) {
      const dx = d.x - mx, dist = Math.hypot(dx, d.y - my)
      const push = dist < R ? (1 - dist / R) * 14 * dpr * Math.sign(dx || 1) : 0
      d.x += push * 0.35 - 0.6 * dpr
      d.y += d.v
      if (d.y > H) { d.y = -d.l; d.x = Math.random() * W * 1.1 }
      if (d.x < 0) d.x += W
      const lit = dist < R * 1.6 ? 0.35 * (1 - dist / (R * 1.6)) : 0
      ctx.strokeStyle = lit ? `rgba(255,181,71,${d.o + lit})` : `rgba(170,200,225,${d.o})`
      ctx.lineWidth = (lit ? 1.6 : 1) * dpr
      ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(d.x - 1.2 * dpr, d.y - d.l); ctx.stroke()
    }
  }
  const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting })
  size()
  io.observe(cv)
  window.addEventListener('resize', size)
  host.addEventListener('pointermove', move)
  host.addEventListener('pointerleave', leave)
  draw()
  stop = () => {
    cancelAnimationFrame(raf); io.disconnect()
    window.removeEventListener('resize', size)
    host.removeEventListener('pointermove', move)
    host.removeEventListener('pointerleave', leave)
  }
})
onUnmounted(() => stop())
</script>

<template>
  <canvas ref="canvas" class="rain-canvas" aria-hidden="true" />
</template>
