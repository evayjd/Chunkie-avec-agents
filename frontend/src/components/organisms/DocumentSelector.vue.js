import { storeToRefs } from 'pinia';
import { useDocumentsStore } from '@/stores/documents';
import DocumentListItem from '@/components/molecules/DocumentListItem.vue';
const store = useDocumentsStore();
const { documents, selectedDocumentIds } = storeToRefs(store);
const { toggleDocument, clearSelection } = store;
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex flex-col gap-1" },
});
if (__VLS_ctx.documents.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex items-center justify-between mb-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "section-label" },
    });
    (__VLS_ctx.selectedDocumentIds.length);
    (__VLS_ctx.documents.length);
    if (__VLS_ctx.selectedDocumentIds.length) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (__VLS_ctx.clearSelection) },
            ...{ class: "text-xs text-red-400 hover:text-red-600 transition" },
        });
    }
}
for (const [doc] of __VLS_getVForSourceType((__VLS_ctx.documents))) {
    /** @type {[typeof DocumentListItem, ]} */ ;
    // @ts-ignore
    const __VLS_0 = __VLS_asFunctionalComponent(DocumentListItem, new DocumentListItem({
        ...{ 'onToggle': {} },
        key: (doc.doc_id),
        document: (doc),
        selected: (__VLS_ctx.selectedDocumentIds.includes(doc.doc_id)),
    }));
    const __VLS_1 = __VLS_0({
        ...{ 'onToggle': {} },
        key: (doc.doc_id),
        document: (doc),
        selected: (__VLS_ctx.selectedDocumentIds.includes(doc.doc_id)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_0));
    let __VLS_3;
    let __VLS_4;
    let __VLS_5;
    const __VLS_6 = {
        onToggle: (__VLS_ctx.toggleDocument)
    };
    var __VLS_2;
}
if (!__VLS_ctx.documents.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "text-xs text-stone-400 text-center py-6" },
    });
}
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-1']} */ ;
/** @type {__VLS_StyleScopedClasses['section-label']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['transition']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-400']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['py-6']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            DocumentListItem: DocumentListItem,
            documents: documents,
            selectedDocumentIds: selectedDocumentIds,
            toggleDocument: toggleDocument,
            clearSelection: clearSelection,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
