import axios from 'axios';

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;

    if (Array.isArray(detail)) {
      return detail.map((item) => item?.msg || JSON.stringify(item)).join('; ');
    }

    if (typeof error.response?.data?.message === 'string') {
      return error.response.data.message;
    }

    if (error.response?.status === 400) {
      return 'Request rejected by backend. Check input fields and selected documents.';
    }

    if (error.response?.status === 500) {
      return 'Backend execution failed. This usually means retrieval, model inference, or Ollama connectivity has broken.';
    }

    return error.message;
  }

  if (error instanceof Error) return error.message;
  return 'Unknown error.';
}