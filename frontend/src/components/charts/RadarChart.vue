<template>
  <div class="panel-muted p-4">
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-slate-100">Score Radar</h3>
      <p class="text-xs text-slate-400">0–100 normalized</p>
    </div>

    <svg viewBox="0 0 300 300" class="mx-auto h-[320px] w-full max-w-[360px]">
      <g transform="translate(150,150)">
        <polygon
          v-for="ring in 5"
          :key="ring"
          :points="ringPoints(ring / 5)"
          fill="none"
          stroke="rgba(148,163,184,0.18)"
          stroke-width="1"
        />

        <line
          v-for="(item, index) in entries"
          :key="item[0]"
          :x1="0"
          :y1="0"
          :x2="axisPoint(index).x"
          :y2="axisPoint(index).y"
          stroke="rgba(148,163,184,0.25)"
          stroke-width="1"
        />

        <polygon
          :points="dataPolygon"
          fill="rgba(51,130,255,0.22)"
          stroke="rgba(96,165,250,0.95)"
          stroke-width="2"
        />

        <circle
          v-for="(item, index) in entries"
          :key="`${item[0]}-point`"
          :cx="valuePoint(index, item[1]).x"
          :cy="valuePoint(index, item[1]).y"
          r="4"
          fill="rgba(125,211,252,1)"
        />

        <g v-for="(item, index) in entries" :key="`${item[0]}-label`">
          <text
            :x="labelPoint(index).x"
            :y="labelPoint(index).y"
            text-anchor="middle"
            class="fill-slate-300 text-[10px]"
          >
            {{ item[0] }}
          </text>
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  scores: Record<string, number>;
}>();

const entries = computed(() => Object.entries(props.scores || {}));
const radius = 100;

function angle(index: number) {
  const count = Math.max(entries.value.length, 1);
  return (Math.PI * 2 * index) / count - Math.PI / 2;
}

function pointFor(index: number, scale: number) {
  const a = angle(index);
  return {
    x: Math.cos(a) * radius * scale,
    y: Math.sin(a) * radius * scale
  };
}

function axisPoint(index: number) {
  return pointFor(index, 1);
}

function labelPoint(index: number) {
  return pointFor(index, 1.22);
}

function valuePoint(index: number, value: number) {
  const clamped = Math.max(0, Math.min(100, Number(value || 0))) / 100;
  return pointFor(index, clamped);
}

function ringPoints(scale: number) {
  return entries.value
    .map((_, index) => {
      const p = pointFor(index, scale);
      return `${p.x},${p.y}`;
    })
    .join(' ');
}

const dataPolygon = computed(() =>
  entries.value
    .map(([_, value], index) => {
      const p = valuePoint(index, value);
      return `${p.x},${p.y}`;
    })
    .join(' ')
);
</script>