import { defineStore } from 'pinia';
import type { AgentResponse, AskResponse, RetrievalMethod, RoastResponse } from '@/types/api';

interface AgentUiState {
  method: RetrievalMethod;
  topK: number;
  stylePreference: string;
  lastAskResponse: AskResponse | null;
  lastAgentResponse: AgentResponse | null;
  lastRoastResponse: RoastResponse | null;
}

export const useAgentStore = defineStore('agent-ui', {
  state: (): AgentUiState => ({
    method: 'hybrid',
    topK: 5,
    stylePreference: 'sharp_witty',
    lastAskResponse: null,
    lastAgentResponse: null,
    lastRoastResponse: null
  }),
  actions: {
    setMethod(method: RetrievalMethod) {
      this.method = method;
    },
    setTopK(value: number) {
      this.topK = value;
    },
    setStylePreference(value: string) {
      this.stylePreference = value;
    }
  }
});