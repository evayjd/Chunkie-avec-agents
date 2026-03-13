import { ref, nextTick, watch } from 'vue';
import { storeToRefs } from 'pinia';
import BaseButton from '@/components/atoms/BaseButton.vue';
import CitationChip from '@/components/molecules/CitationChip.vue';
import { useAsk } from '@/composables/useAsk';
import { useCitationPreview } from '@/composables/useCitationPreview';
import { useAgentStore } from '@/stores/agent';
const agentStore = useAgentStore();
const { method: storeMethod } = storeToRefs(agentStore);
const method = ref(storeMethod.value);
const question = ref('');
const textareaEl = ref(null);
const scrollEl = ref(null);
const methods = ['vector', 'hybrid', 'rerank'];
const { pending, response, submit } = useAsk();
const { openCitation } = useCitationPreview();
watch(method, v => agentStore.setMethod(v));
const messages = ref([]);
let msgId = 0;
function parseAnswer(answer, citations) {
    const map = new Map();
    citations.forEach(c => map.set(c.citation_id, c));
    const parts = [];
    const regex = /\[(\d+)\]/g;
    let last = 0, m;
    while ((m = regex.exec(answer))) {
        if (m.index > last)
            parts.push({ key: `t${last}`, type: 'text', value: answer.slice(last, m.index) });
        parts.push({ key: `c${m.index}`, type: 'citation', citation: map.get(Number(m[1])) });
        last = regex.lastIndex;
    }
    if (last < answer.length)
        parts.push({ key: `te`, type: 'text', value: answer.slice(last) });
    return parts;
}
async function submitAsk() {
    const q = question.value.trim();
    if (!q || pending.value)
        return;
    messages.value.push({ id: msgId++, role: 'user', content: q });
    question.value = '';
    if (textareaEl.value) {
        textareaEl.value.style.height = 'auto';
    }
    await nextTick();
    scrollToBottom();
    try {
        const res = await submit(q);
        if (res) {
            messages.value.push({
                id: msgId++,
                role: 'assistant',
                parts: parseAnswer(res.answer, res.citations)
            });
        }
    }
    finally {
        await nextTick();
        scrollToBottom();
    }
}
function scrollToBottom() {
    if (scrollEl.value)
        scrollEl.value.scrollTop = scrollEl.value.scrollHeight;
}
function autoResize(e) {
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex flex-col h-full" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ref: "scrollEl",
    ...{ class: "flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-3 min-h-0" },
});
/** @type {typeof __VLS_ctx.scrollEl} */ ;
if (!__VLS_ctx.messages.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex flex-col items-center justify-center h-full gap-2 text-center" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "text-4xl text-petal-200" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "text-sm text-stone-400" },
    });
}
for (const [msg] of __VLS_getVForSourceType((__VLS_ctx.messages))) {
    (msg.id);
    if (msg.role === 'user') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "flex justify-end" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "max-w-[70%] bg-stone-800 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed" },
        });
        (msg.content);
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "flex justify-start" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "max-w-[80%] bg-white border-l-2 border-petal-300 rounded-xl rounded-tl-sm px-4 py-3 text-sm text-stone-700 leading-relaxed" },
        });
        for (const [part] of __VLS_getVForSourceType((msg.parts))) {
            (part.key);
            if (part.type === 'text') {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
                (part.value);
            }
            else if (part.type === 'citation' && part.citation) {
                /** @type {[typeof CitationChip, ]} */ ;
                // @ts-ignore
                const __VLS_0 = __VLS_asFunctionalComponent(CitationChip, new CitationChip({
                    ...{ 'onOpen': {} },
                    citation: (part.citation),
                }));
                const __VLS_1 = __VLS_0({
                    ...{ 'onOpen': {} },
                    citation: (part.citation),
                }, ...__VLS_functionalComponentArgsRest(__VLS_0));
                let __VLS_3;
                let __VLS_4;
                let __VLS_5;
                const __VLS_6 = {
                    onOpen: (__VLS_ctx.openCitation)
                };
                var __VLS_2;
            }
        }
    }
}
if (__VLS_ctx.pending) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "flex justify-start" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "bg-white border-l-2 border-petal-200 rounded-xl px-4 py-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "inline-flex gap-1" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
        ...{ class: "w-1.5 h-1.5 rounded-full bg-petal-300 animate-bounce" },
        ...{ style: {} },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
        ...{ class: "w-1.5 h-1.5 rounded-full bg-petal-300 animate-bounce" },
        ...{ style: {} },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
        ...{ class: "w-1.5 h-1.5 rounded-full bg-petal-300 animate-bounce" },
        ...{ style: {} },
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "illust-placeholder h-32 mx-6 mb-3 shrink-0" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "text-3xl" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "text-xs" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "shrink-0 bg-white border-t border-stone-200 px-6 py-4" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex gap-1.5 mb-3" },
});
for (const [m] of __VLS_getVForSourceType((__VLS_ctx.methods))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.method = m;
            } },
        key: (m),
        ...{ class: ([
                'px-3 py-1 rounded-full text-xs font-medium transition',
                __VLS_ctx.method === m
                    ? 'bg-petal-500 text-white'
                    : 'bg-stone-100 text-stone-500 hover:bg-petal-100 hover:text-petal-600'
            ]) },
    });
    (m);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.form, __VLS_intrinsicElements.form)({
    ...{ onSubmit: (__VLS_ctx.submitAsk) },
    ...{ class: "flex gap-2 items-end" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "flex-1" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.textarea)({
    ...{ onKeydown: (__VLS_ctx.submitAsk) },
    ...{ onInput: (__VLS_ctx.autoResize) },
    ref: "textareaEl",
    value: (__VLS_ctx.question),
    rows: "1",
    placeholder: "输入你的问题…",
    ...{ class: "\u0077\u002d\u0066\u0075\u006c\u006c\u0020\u0072\u006f\u0075\u006e\u0064\u0065\u0064\u002d\u006c\u0067\u0020\u0062\u006f\u0072\u0064\u0065\u0072\u0020\u0062\u006f\u0072\u0064\u0065\u0072\u002d\u0073\u0074\u006f\u006e\u0065\u002d\u0032\u0030\u0030\u0020\u0062\u0067\u002d\u0077\u0068\u0069\u0074\u0065\u0020\u0070\u0078\u002d\u0033\u0020\u0070\u0079\u002d\u0032\u0020\u0074\u0065\u0078\u0074\u002d\u0073\u006d\u0020\u0074\u0065\u0078\u0074\u002d\u0073\u0074\u006f\u006e\u0065\u002d\u0038\u0030\u0030\u000a\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0070\u006c\u0061\u0063\u0065\u0068\u006f\u006c\u0064\u0065\u0072\u002d\u0073\u0074\u006f\u006e\u0065\u002d\u0034\u0030\u0030\u0020\u006f\u0075\u0074\u006c\u0069\u006e\u0065\u002d\u006e\u006f\u006e\u0065\u0020\u0072\u0065\u0073\u0069\u007a\u0065\u002d\u006e\u006f\u006e\u0065\u0020\u0074\u0072\u0061\u006e\u0073\u0069\u0074\u0069\u006f\u006e\u000a\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0066\u006f\u0063\u0075\u0073\u003a\u0062\u006f\u0072\u0064\u0065\u0072\u002d\u0070\u0065\u0074\u0061\u006c\u002d\u0033\u0030\u0030\u0020\u0066\u006f\u0063\u0075\u0073\u003a\u0072\u0069\u006e\u0067\u002d\u0032\u0020\u0066\u006f\u0063\u0075\u0073\u003a\u0072\u0069\u006e\u0067\u002d\u0070\u0065\u0074\u0061\u006c\u002d\u0031\u0030\u0030" },
});
/** @type {typeof __VLS_ctx.textareaEl} */ ;
/** @type {[typeof BaseButton, ]} */ ;
// @ts-ignore
const __VLS_7 = __VLS_asFunctionalComponent(BaseButton, new BaseButton({
    type: "submit",
    label: "发送",
    size: "sm",
    loading: (__VLS_ctx.pending),
    loadingText: "…",
}));
const __VLS_8 = __VLS_7({
    type: "submit",
    label: "发送",
    size: "sm",
    loading: (__VLS_ctx.pending),
    loadingText: "…",
}, ...__VLS_functionalComponentArgsRest(__VLS_7));
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['h-full']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-y-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['min-h-0']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-col']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['h-full']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-4xl']} */ ;
/** @type {__VLS_StyleScopedClasses['text-petal-200']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-400']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-end']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-[70%]']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-stone-800']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-tr-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-relaxed']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-start']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-[80%]']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['border-l-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border-petal-300']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-tl-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-700']} */ ;
/** @type {__VLS_StyleScopedClasses['leading-relaxed']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-start']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['border-l-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border-petal-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-3']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['w-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['h-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-petal-300']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-bounce']} */ ;
/** @type {__VLS_StyleScopedClasses['w-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['h-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-petal-300']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-bounce']} */ ;
/** @type {__VLS_StyleScopedClasses['w-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['h-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-petal-300']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-bounce']} */ ;
/** @type {__VLS_StyleScopedClasses['illust-placeholder']} */ ;
/** @type {__VLS_StyleScopedClasses['h-32']} */ ;
/** @type {__VLS_StyleScopedClasses['mx-6']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-3']} */ ;
/** @type {__VLS_StyleScopedClasses['shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['text-3xl']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['border-t']} */ ;
/** @type {__VLS_StyleScopedClasses['border-stone-200']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-3']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['items-end']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-stone-200']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-stone-800']} */ ;
/** @type {__VLS_StyleScopedClasses['placeholder-stone-400']} */ ;
/** @type {__VLS_StyleScopedClasses['outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['resize-none']} */ ;
/** @type {__VLS_StyleScopedClasses['transition']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:border-petal-300']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-petal-100']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            BaseButton: BaseButton,
            CitationChip: CitationChip,
            method: method,
            question: question,
            textareaEl: textareaEl,
            scrollEl: scrollEl,
            methods: methods,
            pending: pending,
            openCitation: openCitation,
            messages: messages,
            submitAsk: submitAsk,
            autoResize: autoResize,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
