import { ref } from 'vue';
import { runAgent } from '@/services/ragApi';
import { useAgentStore } from '@/stores/agent';
import { useDocumentsStore } from '@/stores/documents';
import { useUiStore } from '@/stores/ui';
import { getErrorMessage } from '@/utils/error';
import type { AgentResponse } from '@/types/api';

export function useAgent() {
  const pending = ref(false);
  const response = ref<AgentResponse | null>(null);

  const documents = useDocumentsStore();
  const agentStore = useAgentStore();
  const ui = useUiStore();

  async function submit(question: string, targetId?: string | null) {
    pending.value = true;
    try {
      const res = await runAgent({
        question,
        method: agentStore.method,
        top_k: agentStore.topK,
        document_ids: documents.selectedDocumentIds.length ? documents.selectedDocumentIds : null,
        target_id: targetId || null,
        style_preference: agentStore.stylePreference
      });

      response.value = res;
      agentStore.lastAgentResponse = res;
      return res;
    } catch (error) {
      ui.pushToast({
        title: 'Agent execution failed',
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