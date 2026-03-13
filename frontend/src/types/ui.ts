export interface ToastMessage {
  id: string;
  title: string;
  description?: string;
  tone?: 'info' | 'success' | 'warning' | 'error';
}

export interface NavTab {
  label: string;
  to: string;
}