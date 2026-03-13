import { defineStore } from 'pinia';
export const useAgentStore = defineStore('agent-ui', {
    state: () => ({
        method: 'hybrid',
        topK: 5,
        stylePreference: 'sharp_witty',
        lastAskResponse: null,
        lastAgentResponse: null,
        lastRoastResponse: null
    }),
    actions: {
        setMethod(method) {
            this.method = method;
        },
        setTopK(value) {
            this.topK = value;
        },
        setStylePreference(value) {
            this.stylePreference = value;
        }
    }
});
