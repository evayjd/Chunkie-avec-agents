import { defineStore } from 'pinia';
import type { CitationItem } from '@/types/api';
import type { ToastMessage } from '@/types/ui';

interface UiState {
  citationDrawerOpen: boolean;
  activeCitation: CitationItem | null;
  toasts: ToastMessage[];
  mobileSidebarOpen: boolean;
}

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export const useUiStore = defineStore('ui', {
  state: (): UiState => ({
    citationDrawerOpen: false,
    activeCitation: null,
    toasts: [],
    mobileSidebarOpen: false
  }),
  actions: {
    openCitation(citation: CitationItem) {
      this.activeCitation = citation;
      this.citationDrawerOpen = true;
    },
    closeCitation() {
      this.citationDrawerOpen = false;
      this.activeCitation = null;
    },
    pushToast(payload: Omit<ToastMessage, 'id'>) {
      const toast = { id: uid(), ...payload };
      this.toasts.push(toast);
      setTimeout(() => this.removeToast(toast.id), 4000);
    },
    removeToast(id: string) {
      this.toasts = this.toasts.filter((item) => item.id !== id);
    },
    setMobileSidebarOpen(value: boolean) {
      this.mobileSidebarOpen = value;
    }
  }
});