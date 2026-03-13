import { computed, ref, watch } from 'vue';
import { useAgent } from '@/composables/useAgent';
import { useCitationPreview } from '@/composables/useCitationPreview';
import { useAgentStore } from '@/stores/agent';
import BaseTextarea from '@/components/atoms/BaseTextarea.vue';
import BaseInput from '@/components/atoms/BaseInput.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import CitationChip from '@/components/molecules/CitationChip.vue';
import TraceStepItem from '@/components/molecules/TraceStepItem.vue';
import RetrievalVerifierPanel from './RetrievalVerifierPanel.vue';
import { prettyJson } from '@/utils/format';
const agentStore = useAgentStore();
const question = ref('');
const targetId = ref('');
const method = ref(agentStore.method);
const topKText = ref(String(agentStore.topK));
const stylePreference = ref(agentStore.stylePreference);
const methods = ['vector', 'hybrid', 'rerank'];
const { pending, response, submit } = useAgent();
const { openCitation } = useCitationPreview();
watch(method, v => agentStore.setMethod(v));
watch(stylePreference, v => agentStore.setStylePreference(v));
watch(topKText, v => { const n = Number(v); if (!isNaN(n) && n > 0)
    agentStore.setTopK(n); });
async function submitAgent() {
    if (!question.value.trim())
        return;
    await submit(question.value.trim(), targetId.value.trim() || null);
}
const toolArgumentsJson = computed(() => prettyJson(response.value?.tool_arguments || {}));
const retrievalVerifier = computed(() => {
    const r = response.value?.tool_result;
    return r?.retrieval_verifier ?? null;
});
const citations = computed(() => {
    const r = response.value?.tool_result;
    return Array.isArray(r?.citations) ? r.citations : [];
});
const fallbackNotice = computed(() => {
    const r = response.value?.tool_result;
    return typeof r?.fallback_notice === 'string' ? r.fallback_notice : '';
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex flex-col gap-5" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "card p-5" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({
    ...{ class: "page-title mb-4" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.form, __VLS_intrinsicElements.form)({
    ...{ onSubmit: (__VLS_ctx.submitAgent) },
    ...{ class: "flex flex-col gap-4" },
});
/** @type {[typeof BaseTextarea, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(BaseTextarea, new BaseTextarea({
    modelValue: (__VLS_ctx.question),
    label: "问题",
    placeholder: "例：总结这份文档、对比选中的文档、Roast 这个用户…",
    rows: (3),
}));
const __VLS_1 = __VLS_0({
    modelValue: (__VLS_ctx.question),
    label: "问题",
    placeholder: "例：总结这份文档、对比选中的文档、Roast 这个用户…",
    rows: (3),
}, ...__VLS_functionalComponentArgsRest(__VLS_0));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "grid grid-cols-2 gap-3 sm:grid-cols-4" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "col-span-2 sm:col-span-1" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "text-xs font-medium text-stone-500 mb-1.5" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex gap-1" },
});
for (const [m] of __VLS_getVForSourceType((__VLS_ctx.methods))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.method = m;
            } },
        key: (m),
        type: "button",
        ...{ class: ([
                'px-2.5 py-1 rounded-full text-xs font-medium transition',
                __VLS_ctx.method === m
                    ? 'bg-petal-500 text-white'
                    : 'bg-stone-100 text-stone-500 hover:bg-petal-100 hover:text-petal-600'
            ]) },
    });
    (m);
}
/** @type {[typeof BaseInput, ]} */ ;
// @ts-ignore
const __VLS_3 = __VLS_asFunctionalComponent(BaseInput, new BaseInput({
    modelValue: (__VLS_ctx.topKText),
    label: "Top K",
    type: "number",
}));
const __VLS_4 = __VLS_3({
    modelValue: (__VLS_ctx.topKText),
    label: "Top K",
    type: "number",
}, ...__VLS_functionalComponentArgsRest(__VLS_3));
/** @type {[typeof BaseInput, ]} */ ;
// @ts-ignore
const __VLS_6 = __VLS_asFunctionalComponent(BaseInput, new BaseInput({
    modelValue: (__VLS_ctx.targetId),
    label: "Target ID",
    placeholder: "文档 UUID",
}));
const __VLS_7 = __VLS_6({
    modelValue: (__VLS_ctx.targetId),
    label: "Target ID",
    placeholder: "文档 UUID",
}, ...__VLS_functionalComponentArgsRest(__VLS_6));
/** @type {[typeof BaseInput, ]} */ ;
// @ts-ignore
const __VLS_9 = __VLS_asFunctionalComponent(BaseInput, new BaseInput({
    modelValue: (__VLS_ctx.stylePreference),
    label: "风格偏好",
    placeholder: "sharp_witty",
}));
const __VLS_10 = __VLS_9({
    modelValue: (__VLS_ctx.stylePreference),
    label: "风格偏好",
    placeholder: "sharp_witty",
}, ...__VLS_functionalComponentArgsRest(__VLS_9));
/** @type {[typeof BaseButton, ]} */ ;
// @ts-ignore
const __VLS_12 = __VLS_asFunctionalComponent(BaseButton, new BaseButton({
    label: "执行 Agent",
    type: "submit",
    loading: (__VLS_ctx.pending),
    loadingText: "执行中…",
}));
const __VLS_13 = __VLS_12({
    label: "执行 Agent",
    type: "submit",
    loading: (__VLS_ctx.pending),
    loadingText: "执行中…",
}, ...__VLS_functionalComponentArgsRest(__VLS_12));
if (__VLS_ctx.response) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex items-center gap-2 flex-wrap" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: (['pill', __VLS_ctx.response.workflow_status === 'DONE' ? 'bg-petal-100 text-petal-600' : 'bg-stone-100 text-stone-500']) },
    });
    (__VLS_ctx.response.workflow_status);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "pill bg-blush-100 text-stone-600 font-mono" },
    });
    (__VLS_ctx.response.tool_used);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "pill bg-stone-100 text-stone-500" },
    });
    (__VLS_ctx.response.trace.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card p-5" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "section-label mb-4" },
    });
    if (__VLS_ctx.response.trace.length) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "flex flex-col" },
        });
        for (const [step, i] of __VLS_getVForSourceType((__VLS_ctx.response.trace))) {
            /** @type {[typeof TraceStepItem, ]} */ ;
            // @ts-ignore
            const __VLS_15 = __VLS_asFunctionalComponent(TraceStepItem, new TraceStepItem({
                key: (`${i}-${step.action}`),
                step: (step),
                index: (i),
            }));
            const __VLS_16 = __VLS_15({
                key: (`${i}-${step.action}`),
                step: (step),
                index: (i),
            }, ...__VLS_functionalComponentArgsRest(__VLS_15));
        }
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
            ...{ class: "text-sm text-stone-400" },
        });
    }
    if (__VLS_ctx.fallbackNotice) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800" },
        });
        (__VLS_ctx.fallbackNotice);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card p-5" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex items-center justify-between mb-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "section-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "pill bg-blush-100 text-stone-600 text-xs font-mono" },
    });
    (__VLS_ctx.response.tool_used);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "text-sm text-stone-700 leading-relaxed whitespace-pre-wrap" },
    });
    (__VLS_ctx.response.final_answer);
    /** @type {[typeof RetrievalVerifierPanel, ]} */ ;
    // @ts-ignore
    const __VLS_18 = __VLS_asFunctionalComponent(RetrievalVerifierPanel, new RetrievalVerifierPanel({
        verifier: (__VLS_ctx.retrievalVerifier),
    }));
    const __VLS_19 = __VLS_18({
        verifier: (__VLS_ctx.retrievalVerifier),
    }, ...__VLS_functionalComponentArgsRest(__VLS_18));
    if (__VLS_ctx.citations.length) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "card p-5" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
            ...{ class: "section-label mb-3" },
        });
        (__VLS_ctx.citations.length);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "flex flex-wrap gap-2" },
        });
        for (const [c] of __VLS_getVForSourceType((__VLS_ctx.citations))) {
            /** @type {[typeof CitationChip, ]} */ ;
            // @ts-ignore
            const __VLS_21 = __VLS_asFunctionalComponent(CitationChip, new CitationChip({
                ...{ 'onOpen': {} },
                key: (c.citation_id),
                citation: (c),
            }));
            const __VLS_22 = __VLS_21({
                ...{ 'onOpen': {} },
                key: (c.citation_id),
                citation: (c),
            }, ...__VLS_functionalComponentArgsRest(__VLS_21));
            let __VLS_24;
            let __VLS_25;
            let __VLS_26;
            const __VLS_27 = {
                onOpen: (__VLS_ctx.openCitation)
            };
            var __VLS_23;
        }
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.details, __VLS_intrinsicElements.details)({
        ...{ class: "card p-4 text-sm" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.summary, __VLS_intrinsicElements.summary)({
        ...{ class: "section-label cursor-pointer select-none" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.pre, __VLS_intrinsicElements.pre)({
        ...{ class: "mt-3 overflow-x-auto rounded-lg bg-stone-50 p-3 text-xs text-stone-600 leading-relaxed" },
    });
    (__VLS_ctx.toolArgumentsJson);
}
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-5']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['page-title']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-4']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-2']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:grid-cols-4']} */ ;
/** @type {__VLS_StyleScopedClasses['col-span-2']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:col-span-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-500']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['pill']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-blush-100']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-600']} */ ;
/** @type {__VLS_StyleScopedClasses['font-mono']} */ ;
/** @type {__VLS_StyleScopedClasses['pill']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-stone-100']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-500']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['section-label']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-400']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-amber-200']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-amber-50']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-amber-800']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-3']} */ ;
/** @type {__VLS_StyleScopedClasses['section-label']} */ ;
/** @type {__VLS_StyleScopedClasses['pill']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-blush-100']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-600']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-mono']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-700']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-relaxed']} */ ;
/** @type {__VLS_StyleScopedClasses['whitespace-pre-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['section-label']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-3']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['section-label']} */ ;
/** @type {__VLS_StyleScopedClasses['cursor-pointer']} */ ;
/** @type {__VLS_StyleScopedClasses['select-none']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-3']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-x-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-stone-50']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-600']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-relaxed']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            BaseTextarea: BaseTextarea,
            BaseInput: BaseInput,
            BaseButton: BaseButton,
            CitationChip: CitationChip,
            TraceStepItem: TraceStepItem,
            RetrievalVerifierPanel: RetrievalVerifierPanel,
            question: question,
            targetId: targetId,
            method: method,
            topKText: topKText,
            stylePreference: stylePreference,
            methods: methods,
            pending: pending,
            response: response,
            openCitation: openCitation,
            submitAgent: submitAgent,
            toolArgumentsJson: toolArgumentsJson,
            retrievalVerifier: retrievalVerifier,
            citations: citations,
            fallbackNotice: fallbackNotice,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
