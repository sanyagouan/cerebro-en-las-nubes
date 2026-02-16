import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

export interface WhatsAppMessage {
  id: string;
  message_sid: string;
  to: string;
  from: string;
  body: string;
  status: 'queued' | 'sending' | 'sent' | 'delivered' | 'read' | 'failed' | 'undelivered';
  type: 'confirmation' | 'reminder' | 'cancellation' | 'waitlist_notification' | 'custom';
  reserva_id?: string;
  created_at: string;
  updated_at?: string;
  delivered_at?: string;
  read_at?: string;
  error_code?: string;
  error_message?: string;
  num_segments: number;
  price?: number;
  price_unit?: string;
  metadata?: {
    reserva_nombre?: string;
    reserva_fecha?: string;
    reserva_hora?: string;
    reserva_pax?: number;
    template_used?: string;
  };
}

export interface WhatsAppStats {
  total_messages: number;
  sent_messages: number;
  delivered_messages: number;
  failed_messages: number;
  delivery_rate: number;
  total_cost: number;
  messages_by_type: {
    confirmation: number;
    reminder: number;
    cancellation: number;
    waitlist_notification: number;
    custom: number;
  };
  messages_by_status: {
    queued: number;
    sending: number;
    sent: number;
    delivered: number;
    read: number;
    failed: number;
    undelivered: number;
  };
}

interface WhatsAppMessagesResponse {
  messages: WhatsAppMessage[];
  total: number;
  stats?: WhatsAppStats;
}

async function fetchWhatsAppMessages(
  limit: number = 100,
  status?: string,
  type?: string,
  desde?: string,
  hasta?: string,
  token?: string
): Promise<WhatsAppMessagesResponse> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (status) params.append('status', status);
  if (type) params.append('type', type);
  if (desde) params.append('desde', desde);
  if (hasta) params.append('hasta', hasta);

  const response = await fetch(`${API_BASE_URL}/api/whatsapp/messages?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar mensajes de WhatsApp');
  }

  return response.json();
}

async function fetchWhatsAppStats(
  desde?: string,
  hasta?: string,
  token?: string
): Promise<WhatsAppStats> {
  const params = new URLSearchParams();
  if (desde) params.append('desde', desde);
  if (hasta) params.append('hasta', hasta);

  const response = await fetch(`${API_BASE_URL}/api/whatsapp/stats?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al cargar estadísticas de WhatsApp');
  }

  return response.json();
}

async function resendWhatsAppMessage(
  messageId: string,
  token?: string
): Promise<WhatsAppMessage> {
  const response = await fetch(`${API_BASE_URL}/api/whatsapp/messages/${messageId}/resend`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Error al reenviar mensaje');
  }

  return response.json();
}

async function sendCustomWhatsAppMessage(
  data: { to: string; body: string; reserva_id?: string },
  token?: string
): Promise<WhatsAppMessage> {
  const response = await fetch(`${API_BASE_URL}/api/whatsapp/messages/send`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Error al enviar mensaje personalizado');
  }

  return response.json();
}

export function useWhatsAppMessages(
  limit: number = 100,
  status?: string,
  type?: string,
  desde?: string,
  hasta?: string,
  token?: string
) {
  return useQuery({
    queryKey: ['whatsapp-messages', limit, status, type, desde, hasta],
    queryFn: () => fetchWhatsAppMessages(limit, status, type, desde, hasta, token),
    refetchInterval: 15000, // Refetch every 15 seconds
  });
}

export function useWhatsAppStats(
  desde?: string,
  hasta?: string,
  token?: string
) {
  return useQuery({
    queryKey: ['whatsapp-stats', desde, hasta],
    queryFn: () => fetchWhatsAppStats(desde, hasta, token),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useResendWhatsAppMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ messageId, token }: { messageId: string; token?: string }) =>
      resendWhatsAppMessage(messageId, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-messages'] });
      queryClient.invalidateQueries({ queryKey: ['whatsapp-stats'] });
    },
  });
}

export function useSendCustomWhatsAppMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ data, token }: { data: { to: string; body: string; reserva_id?: string }; token?: string }) =>
      sendCustomWhatsAppMessage(data, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-messages'] });
      queryClient.invalidateQueries({ queryKey: ['whatsapp-stats'] });
    },
  });
}
