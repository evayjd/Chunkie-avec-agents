import { computed } from 'vue';
const props = defineProps();
const entries = computed(() => Object.entries(props.scores || {}));
const radius = 100;
function angle(index) {
    const count = Math.max(entries.value.length, 1);
    return (Math.PI * 2 * index) / count - Math.PI / 2;
}
function pointFor(index, scale) {
    const a = angle(index);
    return {
        x: Math.cos(a) * radius * scale,
        y: Math.sin(a) * radius * scale
    };
}
function axisPoint(index) {
    return pointFor(index, 1);
}
function labelPoint(index) {
    return pointFor(index, 1.22);
}
function valuePoint(index, value) {
    const clamped = Math.max(0, Math.min(100, Number(value || 0))) / 100;
    return pointFor(index, clamped);
}
function ringPoints(scale) {
    return entries.value
        .map((_, index) => {
        const p = pointFor(index, scale);
        return `${p.x},${p.y}`;
    })
        .join(' ');
}
const dataPolygon = computed(() => entries.value
    .map(([_, value], index) => {
    const p = valuePoint(index, value);
    return `${p.x},${p.y}`;
})
    .join(' '));
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "panel-muted p-4" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "mb-4 flex items-center justify-between" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({
    ...{ class: "text-sm font-semibold text-slate-100" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "text-xs text-slate-400" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    viewBox: "0 0 300 300",
    ...{ class: "mx-auto h-[320px] w-full max-w-[360px]" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.g, __VLS_intrinsicElements.g)({
    transform: "translate(150,150)",
});
for (const [ring] of __VLS_getVForSourceType((5))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.polygon)({
        key: (ring),
        points: (__VLS_ctx.ringPoints(ring / 5)),
        fill: "none",
        stroke: "rgba(148,163,184,0.18)",
        'stroke-width': "1",
    });
}
for (const [item, index] of __VLS_getVForSourceType((__VLS_ctx.entries))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.line)({
        key: (item[0]),
        x1: (0),
        y1: (0),
        x2: (__VLS_ctx.axisPoint(index).x),
        y2: (__VLS_ctx.axisPoint(index).y),
        stroke: "rgba(148,163,184,0.25)",
        'stroke-width': "1",
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.polygon)({
    points: (__VLS_ctx.dataPolygon),
    fill: "rgba(51,130,255,0.22)",
    stroke: "rgba(96,165,250,0.95)",
    'stroke-width': "2",
});
for (const [item, index] of __VLS_getVForSourceType((__VLS_ctx.entries))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.circle)({
        key: (`${item[0]}-point`),
        cx: (__VLS_ctx.valuePoint(index, item[1]).x),
        cy: (__VLS_ctx.valuePoint(index, item[1]).y),
        r: "4",
        fill: "rgba(125,211,252,1)",
    });
}
for (const [item, index] of __VLS_getVForSourceType((__VLS_ctx.entries))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.g, __VLS_intrinsicElements.g)({
        key: (`${item[0]}-label`),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.text, __VLS_intrinsicElements.text)({
        x: (__VLS_ctx.labelPoint(index).x),
        y: (__VLS_ctx.labelPoint(index).y),
        'text-anchor': "middle",
        ...{ class: "fill-slate-300 text-[10px]" },
    });
    (item[0]);
}
/** @type {__VLS_StyleScopedClasses['panel-muted']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['mx-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['h-[320px]']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-[360px]']} */ ;
/** @type {__VLS_StyleScopedClasses['fill-slate-300']} */ ;
/** @type {__VLS_StyleScopedClasses['text-[10px]']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            entries: entries,
            axisPoint: axisPoint,
            labelPoint: labelPoint,
            valuePoint: valuePoint,
            ringPoints: ringPoints,
            dataPolygon: dataPolygon,
        };
    },
    __typeProps: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
