import { computed } from 'vue';
const props = withDefaults(defineProps(), { tone: 'default' });
const toneClass = computed(() => {
    switch (props.tone) {
        case 'info': return 'bg-blue-50 text-blue-600';
        case 'success': return 'bg-green-50 text-green-700';
        case 'warning': return 'bg-amber-50 text-amber-700';
        case 'error': return 'bg-red-50 text-red-600';
        default: return 'bg-blush-100 text-petal-600';
    }
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_withDefaultsArg = (function (t) { return t; })({ tone: 'default' });
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: (['pill', __VLS_ctx.toneClass]) },
});
var __VLS_0 = {};
(__VLS_ctx.label);
// @ts-ignore
var __VLS_1 = __VLS_0;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            toneClass: toneClass,
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
