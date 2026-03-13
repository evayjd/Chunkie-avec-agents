import { ref } from 'vue';
import { runRoast } from '@/services/ragApi';
import { useAgentStore } from '@/stores/agent';
import { useDocumentsStore } from '@/stores/documents';
import { useUiStore } from '@/stores/ui';
import { getErrorMessage } from '@/utils/error';
import type { RoastResponse } from '@/types/api';

export function useRoast() {
  const pending = ref(false);
  const response = ref<RoastResponse | null>(null);

  const documents = useDocumentsStore();
  const agentStore = useAgentStore();
  const ui = useUiStore();

  async function submit(query: string, targetId?: string | null) {
    pending.value = true;
    try {
      const res = await runRoast({
        query,
        document_ids: documents.selectedDocumentIds.length ? documents.selectedDocumentIds : null,
        top_k: Math.max(agentStore.topK, 6),
        method: agentStore.method,
        style_preference: agentStore.stylePreference,
        target_id: targetId || null
      });

      response.value = res;
      agentStore.lastRoastResponse = res;
      return res;
    } catch (error) {
      ui.pushToast({
        title: 'Roast pipeline failed',
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