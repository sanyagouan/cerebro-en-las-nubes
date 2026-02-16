import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../config/api';

export interface WhatsAppMessage {
  id: string;
  message_id: string;
  phone_number: string;
  message_type: 'confirmation' | 'reminder' | 'cancellation' | 'waitlist';
  content: string;
  status: 'sent' | 'delivered' | 'read' | 'failed';
  sent_at: string;
  delivered_at?: string;
  read_at?: string;
  reservation_id?: string;
  reservation_details?: {
    customer_name?: string;
    date?: string;
    time?: string;
    party_size?: number;
  };
  error_message?: string;
  retry_count?: number;
  cost?: number;
}

export interface WhatsAppAnalytics {
  total_messages: number;
  sent_messages: number;
  delivered_messages: number;
  read_messages: number;
  failed_messages: number;
  delivery_rate: number;
  read_rate: number;
  total_cost: number;
  messages_by_type: {
    confirmation: number;
    reminder: number;
    cancellation: number;
    waitlist: number;
  };
  messages_by_status: {
    sent: number;
    delivered: number;
    read: number;
    failed: number;
  };
}

export interface MessageTemplate {
  id: string;
  type: 'confirmation' | 'reminder' | 'cancellation' | 'waitlist';
  name: string;
  content: string;
  variables: string[];
  active: boolean;
  created_at: string;
  updated_at: string;
}

export function useWhatsAppLogs() {
  return useQuery({
    queryKey: ['whatsapp-logs'],
    queryFn: async () => {
      const response = await api.get('/api/whatsapp/logs');
      return response.data;
    },
  });
}

export function useWhatsAppAnalytics() {
  return useQuery({
    queryKey: ['whatsapp-analytics'],
    queryFn: async () => {
      const response = await api.get('/api/whatsapp/analytics');
      return response.data;
    },
  });
}

export function useWhatsAppMessage(messageId: string) {
  return useQuery({
    queryKey: ['whatsapp-message', messageId],
    queryFn: async () => {
      const response = await api.get(`/api/whatsapp/messages/${messageId}`);
      return response.data;
    },
    enabled: !!messageId,
  });
}

export function useResendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (messageId: string) => {
      const response = await api.post(`/api/whatsapp/messages/${messageId}/resend`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-logs'] });
      queryClient.invalidateQueries({ queryKey: ['whatsapp-analytics'] });
    },
  });
}

export function useMessageTemplates() {
  return useQuery({
    queryKey: ['whatsapp-templates'],
    queryFn: async () => {
      const response = await api.get('/api/whatsapp/templates');
      return response.data;
    },
  });
}

export function useUpdateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<MessageTemplate> }) => {
      const response = await api.put(`/api/whatsapp/templates/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-templates'] });
    },
  });
}
