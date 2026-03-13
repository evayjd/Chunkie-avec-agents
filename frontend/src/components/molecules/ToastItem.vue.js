import { computed } from 'vue';
const props = defineProps();
const __VLS_emit = defineEmits();
const borderClass = computed(() => {
    switch (props.toast.tone) {
        case 'success': return 'border-l-4 border-green-400 border-y-stone-200 border-r-stone-200';
        case 'warning': return 'border-l-4 border-amber-400 border-y-stone-200 border-r-stone-200';
        case 'error': return 'border-l-4 border-red-400 border-y-stone-200 border-r-stone-200';
        default: return 'border-l-4 border-petal-400 border-y-stone-200 border-r-stone-200';
    }
});
const iconColor = computed(() => {
    switch (props.toast.tone) {
        case 'success': return 'text-green-500';
        case 'warning': return 'text-amber-500';
        case 'error': return 'text-red-500';
        default: return 'text-petal-400';
    }
});
const icon = computed(() => {
    switch (props.toast.tone) {
        case 'success': return '✓';
        case 'warning': return '!';
        case 'error': return '✕';
        default: return '✦';
    }
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: ([
            'flex items-start gap-3 rounded-xl border bg-white pl-4 pr-3 py-3 min-w-64 max-w-sm shadow-sm',
            __VLS_ctx.borderClass
        ]) },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: (['mt-0.5 shrink-0 text-sm font-bold', __VLS_ctx.iconColor]) },
});
(__VLS_ctx.icon);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex-1 min-w-0" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "text-sm font-medium text-stone-800" },
});
(__VLS_ctx.toast.title);
if (__VLS_ctx.toast.description) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "mt-0.5 text-xs text-stone-500" },
    });
    (__VLS_ctx.toast.description);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.$emit('dismiss', __VLS_ctx.toast.id);
        } },
    ...{ class: "shrink-0 text-stone-400 hover:text-stone-600 transition text-lg leading-none mt-0.5" },
    'aria-label': "Dismiss",
});
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['min-w-0']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-800']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-500']} */ ;
/** @type {__VLS_StyleScopedClasses['shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-stone-600']} */ ;
/** @type {__VLS_StyleScopedClasses['transition']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-none']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-0.5']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            borderClass: borderClass,
            iconColor: iconColor,
            icon: icon,
        };
    },
    __typeEmits: {},
    __typeProps: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
