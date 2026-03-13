import { defineStore } from 'pinia';
function uid() {
    return Math.random().toString(36).slice(2, 10);
}
export const useUiStore = defineStore('ui', {
    state: () => ({
        citationDrawerOpen: false,
        activeCitation: null,
        toasts: [],
        mobileSidebarOpen: false
    }),
    actions: {
        openCitation(citation) {
            this.activeCitation = citation;
            this.citationDrawerOpen = true;
        },
        closeCitation() {
            this.citationDrawerOpen = false;
            this.activeCitation = null;
        },
        pushToast(payload) {
            const toast = { id: uid(), ...payload };
            this.toasts.push(toast);
            setTimeout(() => this.removeToast(toast.id), 4000);
        },
        removeToast(id) {
            this.toasts = this.toasts.filter((item) => item.id !== id);
        },
        setMobileSidebarOpen(value) {
            this.mobileSidebarOpen = value;
        }
    }
});
