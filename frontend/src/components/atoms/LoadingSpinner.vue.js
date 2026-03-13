import { computed } from 'vue';
const props = withDefaults(defineProps(), { size: 'md' });
const sizeClass = computed(() => {
    switch (props.size) {
        case 'sm': return 'h-4 w-4';
        case 'lg': return 'h-9 w-9';
        default: return 'h-6 w-6';
    }
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_withDefaultsArg = (function (t) { return t; })({ size: 'md' });
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div)({
    ...{ class: ([
            'inline-block animate-spin rounded-full border-2 border-petal-100 border-t-petal-400',
            __VLS_ctx.sizeClass
        ]) },
    'aria-hidden': "true",
});
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            sizeClass: sizeClass,
        };
    },
    __typeProps: {},
    props: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeProps: {},
    props: {},
});
; /* PartiallyEnd: #4569/main.vue */
