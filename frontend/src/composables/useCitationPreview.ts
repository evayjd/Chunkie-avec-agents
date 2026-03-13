import { storeToRefs } from 'pinia';
import { useUiStore } from '@/stores/ui';
import type { CitationItem } from '@/types/api';

export function useCitationPreview() {
  const ui = useUiStore();
  const { activeCitation, citationDrawerOpen } = storeToRefs(ui);

  function openCitation(citation: CitationItem) {
    ui.openCitation(citation);
  }

  function closeCitation() {
    ui.closeCitation();
  }

  return {
    activeCitation,
    citationDrawerOpen,
    openCitation,
    closeCitation
  };
}