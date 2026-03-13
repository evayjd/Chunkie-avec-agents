import { storeToRefs } from 'pinia';
import { useUiStore } from '@/stores/ui';
export function useCitationPreview() {
    const ui = useUiStore();
    const { activeCitation, citationDrawerOpen } = storeToRefs(ui);
    function openCitation(citation) {
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
