import { ref } from 'vue';
import { uploadDocument } from '@/services/ragApi';
import { useDocumentsStore } from '@/stores/documents';
import { useUiStore } from '@/stores/ui';
import { getErrorMessage } from '@/utils/error';
export function useUpload() {
    const uploading = ref(false);
    const documentsStore = useDocumentsStore();
    const ui = useUiStore();
    async function upload(file) {
        uploading.value = true;
        try {
            const result = await uploadDocument(file);
            await documentsStore.loadDocuments(true);
            ui.pushToast({
                title: 'Upload completed',
                description: `${result.filename} processed successfully.`,
                tone: 'success'
            });
            return result;
        }
        catch (error) {
            ui.pushToast({
                title: 'Upload failed',
                description: getErrorMessage(error),
                tone: 'error'
            });
            throw error;
        }
        finally {
            uploading.value = false;
        }
    }
    return {
        uploading,
        upload
    };
}
