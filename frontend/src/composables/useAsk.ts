import { ref } from 'vue';
import { askQuestion } from '@/services/ragApi';
import { useAgentStore } from '@/stores/agent';
import { useDocumentsStore } from '@/stores/documents';
import { useUiStore } from '@/stores/ui';
import { getErrorMessage } from '@/utils/error';
import type { AskResponse } from '@/types/api';

export function useAsk() {
  const pending = ref(false);
  const response = ref<AskResponse | null>(null);

  const documents = useDocumentsStore();
  const agentStore = useAgentStore();
  const ui = useUiStore();

  async function submit(question: string) {
    pending.value = true;
    try {
      const res = await askQuestion({
        question,
        document_ids: documents.selectedDocumentIds.length ? documents.selectedDocumentIds : null,
        top_k: agentStore.topK,
        method: agentStore.method
      });

      response.value = res;
      agentStore.lastAskResponse = res;
      return res;
    } catch (error) {
      ui.pushToast({
        title: 'Ask request failed',
        description: getErrorMessage(error),
        tone: 'error'
      });
      throw error;
    } finally {
      pending.value = false;
    }
  }

  return {
    pending,
    response,
    submit
  };
}