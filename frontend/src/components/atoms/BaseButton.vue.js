import { computed } from 'vue';
const props = withDefaults(defineProps(), {
    variant: 'primary',
    type: 'button',
    disabled: false,
    loading: false,
    size: 'md'
});
const sizeClass = computed(() => {
    switch (props.size) {
        case 'sm': return 'text-xs px-3 py-1.5';
        case 'lg': return 'text-sm px-5 py-2.5';
        default: return 'text-sm px-4 py-2';
    }
});
const spinSize = computed(() => {
    switch (props.size) {
        case 'sm': return 'h-3 w-3';
        case 'lg': return 'h-4 w-4';
        default: return 'h-3.5 w-3.5';
    }
});
const variantClass = computed(() => {
    switch (props.variant) {
        case 'secondary':
            return 'bg-petal-100 text-petal-600 hover:bg-petal-200';
        case 'ghost':
            return 'bg-transparent text-petal-600 hover:bg-petal-50 border border-petal-200';
        case 'danger':
            return 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200';
        default:
            return 'bg-petal-500 text-white hover:bg-petal-600';
    }
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_withDefaultsArg = (function (t) { return t; })({
    variant: 'primary',
    type: 'button',
    disabled: false,
    loading: false,
    size: 'md'
});
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    type: (__VLS_ctx.type),
    disabled: (__VLS_ctx.disabled || __VLS_ctx.loading),
    ...{ class: ([
            'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-petal-300 focus:ring-offset-1',
            __VLS_ctx.sizeClass,
            __VLS_ctx.variantClass,
            (__VLS_ctx.disabled || __VLS_ctx.loading) ? 'cursor-not-allowed opacity-40' : 'cursor-pointer'
        ]) },
});
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
        ...{ class: "inline-block rounded-full border-2 border-current/30 border-t-current animate-spin shrink-0" },
        ...{ class: (__VLS_ctx.spinSize) },
        'aria-hidden': "true",
    });
}
var __VLS_0 = {};
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
(__VLS_ctx.loading ? (__VLS_ctx.loadingText ?? __VLS_ctx.label ?? '处理中...') : __VLS_ctx.label);
var __VLS_2 = {};
/** @type {__VLS_StyleScopedClasses['inline-block']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['border-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border-current/30']} */ ;
/** @type {__VLS_StyleScopedClasses['border-t-current']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-spin']} */ ;
/** @type {__VLS_StyleScopedClasses['shrink-0']} */ ;
// @ts-ignore
var __VLS_1 = __VLS_0, __VLS_3 = __VLS_2;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            sizeClass: sizeClass,
            spinSize: spinSize,
            variantClass: variantClass,
        };
    },
    __typeProps: {},
    props: {},
});
const __VLS_component = (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeProps: {},
    props: {},
});
export default {};
; /* PartiallyEnd: #4569/main.vue */
