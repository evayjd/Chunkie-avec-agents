import { storeToRefs } from 'pinia';
import { useUiStore } from '@/stores/ui';
import ToastItem from '@/components/molecules/ToastItem.vue';
const ui = useUiStore();
const { toasts } = storeToRefs(ui);
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "fixed right-4 top-4 z-[90] flex w-[360px] max-w-[calc(100vw-2rem)] flex-col gap-3" },
});
for (const [toast] of __VLS_getVForSourceType((__VLS_ctx.toasts))) {
    /** @type {[typeof ToastItem, ]} */ ;
    // @ts-ignore
    const __VLS_0 = __VLS_asFunctionalComponent(ToastItem, new ToastItem({
        key: (toast.id),
        toast: (toast),
    }));
    const __VLS_1 = __VLS_0({
        key: (toast.id),
        toast: (toast),
    }, ...__VLS_functionalComponentArgsRest(__VLS_0));
}
/** @type {__VLS_StyleScopedClasses['fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['right-4']} */ ;
/** @type {__VLS_StyleScopedClasses['top-4']} */ ;
/** @type {__VLS_StyleScopedClasses['z-[90]']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['w-[360px]']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-[calc(100vw-2rem)]']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            ToastItem: ToastItem,
            toasts: toasts,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
