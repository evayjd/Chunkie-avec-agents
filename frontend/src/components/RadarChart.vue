<template>
  <canvas ref="canvasEl" :width="size" :height="size" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = withDefaults(defineProps<{
  scores: Record<string, number>
  size?: number
}>(), { size: 320 })

const canvasEl = ref<HTMLCanvasElement | null>(null)

function draw() {
  const canvas = canvasEl.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const { size } = props
  const cx = size / 2
  const cy = size / 2
  const r  = size * 0.36

  const entries = Object.entries(props.scores)
  const n       = entries.length
  if (n < 3) return

  const angles = entries.map((_, i) => (i / n) * 2 * Math.PI - Math.PI / 2)

  ctx.clearRect(0, 0, size, size)

  // ── Grid rings ───────────────────────────────────────
  const rings = 5
  for (let ring = 1; ring <= rings; ring++) {
    const rr = (ring / rings) * r
    ctx.beginPath()
    for (let i = 0; i <= n; i++) {
      const a = angles[i % n]
      const x = cx + rr * Math.cos(a)
      const y = cy + rr * Math.sin(a)
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.closePath()
    ctx.strokeStyle = 'rgba(232,194,216,0.5)'
    ctx.lineWidth   = 1
    ctx.stroke()

    if (ring === rings) {
      ctx.fillStyle = 'rgba(254,249,251,0.4)'
      ctx.fill()
    }
  }

  // ── Axis lines ───────────────────────────────────────
  angles.forEach(a => {
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + r * Math.cos(a), cy + r * Math.sin(a))
    ctx.strokeStyle = 'rgba(232,194,216,0.7)'
    ctx.lineWidth   = 1
    ctx.stroke()
  })

  // ── Data polygon ─────────────────────────────────────
  ctx.beginPath()
  entries.forEach(([, val], i) => {
    const a  = angles[i]
    const rv = (val / 100) * r
    const x  = cx + rv * Math.cos(a)
    const y  = cy + rv * Math.sin(a)
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  })
  ctx.closePath()
  ctx.fillStyle   = 'rgba(248,143,168,0.2)'
  ctx.fill()
  ctx.strokeStyle = '#f88fa8'
  ctx.lineWidth   = 2
  ctx.stroke()

  // ── Data dots ────────────────────────────────────────
  entries.forEach(([, val], i) => {
    const a  = angles[i]
    const rv = (val / 100) * r
    const x  = cx + rv * Math.cos(a)
    const y  = cy + rv * Math.sin(a)
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI)
    ctx.fillStyle   = '#f88fa8'
    ctx.fill()
    ctx.strokeStyle = 'white'
    ctx.lineWidth   = 2
    ctx.stroke()
  })

  // ── Labels ───────────────────────────────────────────
  const labelR = r + 22
  ctx.font         = '11px Inter, sans-serif'
  ctx.textAlign    = 'center'
  ctx.textBaseline = 'middle'

  entries.forEach(([label, val], i) => {
    const a = angles[i]
    const x = cx + labelR * Math.cos(a)
    const y = cy + labelR * Math.sin(a)

    ctx.fillStyle = '#3a3a36'
    ctx.fillText(label, x, y - 6)
    ctx.fillStyle = '#f88fa8'
    ctx.font      = '10px Inter, sans-serif'
    ctx.fillText(String(val), x, y + 6)
    ctx.font      = '11px Inter, sans-serif'
  })
}

onMounted(draw)
watch(() => props.scores, draw, { deep: true })
</script>
