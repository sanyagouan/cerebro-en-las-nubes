import { useState, useMemo } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  MessageCircle,
  Download,
  X,
  CheckCircle,
  AlertCircle,
  Clock,
  Send,
  Eye,
  RefreshCw,
  DollarSign,
  TrendingUp,
  Edit2,
  Save,
} from 'lucide-react';
import {
  useWhatsAppLogs,
  useWhatsAppAnalytics,
  useWhatsAppMessage,
  useResendMessage,
  useMessageTemplates,
  useUpdateTemplate,
  WhatsAppMessage,
  MessageTemplate,
} from '../hooks/useWhatsAppLogs';

type StatusFilter = 'all' | 'sent' | 'delivered' | 'read' | 'failed';
type TypeFilter = 'all' | 'confirmation' | 'reminder' | 'cancellation' | 'waitlist';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

let toastId = 0;

export default function WhatsAppLogs() {
  const { data: logs, isLoading, error } = useWhatsAppLogs();
  const { data: analytics } = useWhatsAppAnalytics();
  const { data: templates } = useMessageTemplates();

  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all');
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<MessageTemplate | null>(null);
  const [templateContent, setTemplateContent] = useState('');
  const [toasts, setToasts] = useState<Toast[]>([]);

  const resendMutation = useResendMessage();
  const updateTemplateMutation = useUpdateTemplate();

  const showToast = (message: string, type: 'success' | 'error') => {
    const id = toastId++;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const filteredLogs = useMemo(() => {
    if (!logs?.messages) return [];

    return logs.messages.filter((message) => {
      const matchStatus = statusFilter === 'all' || message.status === statusFilter;
      const matchType = typeFilter === 'all' || message.message_type === typeFilter;
      return matchStatus && matchType;
    });
  }, [logs?.messages, statusFilter, typeFilter]);

  const handleExportCSV = () => {
    if (!filteredLogs.length) {
      showToast('No hay mensajes para exportar', 'error');
      return;
    }

    const headers = [
      'ID',
      'Teléfono',
      'Tipo',
      'Contenido',
      'Estado',
      'Enviado',
      'Entregado',
      'Leído',
      'Reserva ID',
      'Cliente',
      'Reintentos',
      'Costo',
      'Error',
    ];

    const rows = filteredLogs.map((msg) => [
      msg.id,
      msg.phone_number,
      msg.message_type,
      msg.content.substring(0, 100),
      msg.status,
      format(new Date(msg.sent_at), 'dd/MM/yyyy HH:mm', { locale: es }),
      msg.delivered_at ? format(new Date(msg.delivered_at), 'dd/MM/yyyy HH:mm', { locale: es }) : 'N/A',
      msg.read_at ? format(new Date(msg.read_at), 'dd/MM/yyyy HH:mm', { locale: es }) : 'N/A',
      msg.reservation_id || 'N/A',
      msg.reservation_details?.customer_name || 'N/A',
      msg.retry_count?.toString() || '0',
      msg.cost ? `$${msg.cost.toFixed(4)}` : 'N/A',
      msg.error_message || 'N/A',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], {
      type: 'text/csv;charset=utf-8;',
    });

    const link = document.createElement('a');
    link.setAttribute('href', URL.createObjectURL(blob));
    link.setAttribute(
      'download',
      `whatsapp_logs_${format(new Date(), 'yyyy-MM-dd_HH-mm', { locale: es })}.csv`
    );
    link.click();

    showToast('CSV exportado exitosamente', 'success');
  };

  const handleResendMessage = async (messageId: string) => {
    try {
      await resendMutation.mutateAsync(messageId);
      showToast('Mensaje reenviado exitosamente', 'success');
    } catch (error) {
      showToast(
        `Error al reenviar mensaje: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        'error'
      );
    }
  };

  const handleEditTemplate = (template: MessageTemplate) => {
    setEditingTemplate(template);
    setTemplateContent(template.content);
  };

  const handleSaveTemplate = async () => {
    if (!editingTemplate) return;

    try {
      await updateTemplateMutation.mutateAsync({
        id: editingTemplate.id,
        content: templateContent,
      });
      showToast('Plantilla actualizada exitosamente', 'success');
      setEditingTemplate(null);
      setTemplateContent('');
    } catch (error) {
      showToast(
        `Error al actualizar plantilla: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        'error'
      );
    }
  };

  const getStatusBadge = (status: WhatsAppMessage['status']) => {
    switch (status) {
      case 'sent':
        return {
          bg: 'bg-blue-100',
          text: 'text-blue-700',
          border: 'border-blue-300',
          label: 'Enviado',
        };
      case 'delivered':
        return {
          bg: 'bg-green-100',
          text: 'text-green-700',
          border: 'border-green-300',
          label: 'Entregado',
        };
      case 'read':
        return {
          bg: 'bg-purple-100',
          text: 'text-purple-700',
          border: 'border-purple-300',
          label: 'Leído',
        };
      case 'failed':
        return {
          bg: 'bg-red-100',
          text: 'text-red-700',
          border: 'border-red-300',
          label: 'Fallido',
        };
      default:
        return {
          bg: 'bg-gray-100',
          text: 'text-gray-700',
          border: 'border-gray-300',
          label: status,
        };
    }
  };

  const getTypeBadge = (type: WhatsAppMessage['message_type']) => {
    switch (type) {
      case 'confirmation':
        return { bg: 'bg-green-100', text: 'text-green-700', label: 'Confirmación' };
      case 'reminder':
        return { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Recordatorio' };
      case 'cancellation':
        return { bg: 'bg-red-100', text: 'text-red-700', label: 'Cancelación' };
      case 'waitlist':
        return { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Lista de Espera' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-700', label: type };
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        Error al cargar logs de WhatsApp: {error.message}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-3 rounded-lg shadow-lg text-white animate-fade-in ${
              toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <MessageCircle size={28} className="text-green-600" />
          Seguimiento WhatsApp/SMS
        </h2>
        <div className="flex gap-3">
          <button
            onClick={() => setShowTemplates(!showTemplates)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Edit2 size={18} />
            <span>Plantillas</span>
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Download size={18} />
            <span>Exportar CSV</span>
          </button>
        </div>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Total de Mensajes</p>
              <MessageCircle size={20} className="text-gray-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{analytics.total_messages}</p>
            <div className="mt-2 text-xs text-gray-500">
              {analytics.messages_by_type.confirmation} confirmaciones,{' '}
              {analytics.messages_by_type.reminder} recordatorios
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Tasa de Entrega</p>
              <CheckCircle size={20} className="text-green-600" />
            </div>
            <p className="text-3xl font-bold text-green-600">
              {analytics.delivery_rate.toFixed(1)}%
            </p>
            <div className="mt-2 text-xs text-gray-500">
              {analytics.delivered_messages} de {analytics.sent_messages} entregados
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Tasa de Lectura</p>
              <Eye size={20} className="text-purple-600" />
            </div>
            <p className="text-3xl font-bold text-purple-600">
              {analytics.read_rate.toFixed(1)}%
            </p>
            <div className="mt-2 text-xs text-gray-500">
              {analytics.read_messages} de {analytics.delivered_messages} leídos
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Mensajes Fallidos</p>
              <AlertCircle size={20} className="text-red-600" />
            </div>
            <p className="text-3xl font-bold text-red-600">{analytics.failed_messages}</p>
            <div className="mt-2 text-xs text-gray-500">
              Costo total: ${analytics.total_cost.toFixed(2)}
            </div>
          </div>
        </div>
      )}

      {/* Templates Section */}
      {showTemplates && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Gestión de Plantillas de Mensajes
          </h3>
          <div className="space-y-4">
            {templates?.templates.map((template) => (
              <div
                key={template.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-semibold text-gray-900">{template.name}</h4>
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        getTypeBadge(template.type).bg
                      } ${getTypeBadge(template.type).text}`}
                    >
                      {getTypeBadge(template.type).label}
                    </span>
                  </div>
                  <button
                    onClick={() => handleEditTemplate(template)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <Edit2 size={16} className="text-gray-600" />
                  </button>
                </div>

                {editingTemplate?.id === template.id ? (
                  <div className="mt-3 space-y-3">
                    <textarea
                      value={templateContent}
                      onChange={(e) => setTemplateContent(e.target.value)}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                    />
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className="font-medium">Variables disponibles:</span>
                      {template.variables.map((v) => (
                        <code key={v} className="px-2 py-1 bg-gray-100 rounded">
                          {`{${v}}`}
                        </code>
                      ))}
                    </div>
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => {
                          setEditingTemplate(null);
                          setTemplateContent('');
                        }}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={handleSaveTemplate}
                        disabled={updateTemplateMutation.isPending}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                      >
                        <Save size={16} />
                        <span>Guardar</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="mt-2 text-sm text-gray-600 whitespace-pre-line">
                    {template.content}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="space-y-4">
          {/* Status Filters */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Filtrar por Estado</p>
            <div className="flex flex-wrap gap-2">
              {(['all', 'sent', 'delivered', 'read', 'failed'] as const).map((status) => {
                const count =
                  status === 'all'
                    ? logs?.messages.length || 0
                    : logs?.messages.filter((m) => m.status === status).length || 0;

                return (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      statusFilter === status
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {status === 'all'
                      ? 'Todos'
                      : status === 'sent'
                      ? 'Enviados'
                      : status === 'delivered'
                      ? 'Entregados'
                      : status === 'read'
                      ? 'Leídos'
                      : 'Fallidos'}{' '}
                    ({count})
                  </button>
                );
              })}
            </div>
          </div>

          {/* Type Filters */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Filtrar por Tipo</p>
            <div className="flex flex-wrap gap-2">
              {(['all', 'confirmation', 'reminder', 'cancellation', 'waitlist'] as const).map(
                (type) => {
                  const count =
                    type === 'all'
                      ? logs?.messages.length || 0
                      : logs?.messages.filter((m) => m.message_type === type).length || 0;

                  return (
                    <button
                      key={type}
                      onClick={() => setTypeFilter(type)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        typeFilter === type
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type === 'all'
                        ? 'Todos'
                        : type === 'confirmation'
                        ? 'Confirmaciones'
                        : type === 'reminder'
                        ? 'Recordatorios'
                        : type === 'cancellation'
                        ? 'Cancelaciones'
                        : 'Lista de Espera'}{' '}
                      ({count})
                    </button>
                  );
                }
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Messages Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Teléfono
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contenido
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Enviado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reserva
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    No hay mensajes para mostrar
                  </td>
                </tr>
              ) : (
                filteredLogs.map((message) => {
                  const statusBadge = getStatusBadge(message.status);
                  const typeBadge = getTypeBadge(message.message_type);

                  return (
                    <tr
                      key={message.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => setSelectedMessageId(message.id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <MessageCircle size={16} className="text-gray-400" />
                          <span className="text-sm font-medium text-gray-900">
                            {message.phone_number}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-block px-2 py-1 rounded text-xs font-medium ${typeBadge.bg} ${typeBadge.text}`}
                        >
                          {typeBadge.label}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <p className="text-sm text-gray-900 truncate max-w-xs">
                          {message.content.substring(0, 80)}
                          {message.content.length > 80 ? '...' : ''}
                        </p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-medium border-2 ${statusBadge.bg} ${statusBadge.text} ${statusBadge.border}`}
                        >
                          {statusBadge.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {format(new Date(message.sent_at), 'dd/MM/yyyy', { locale: es })}
                        </div>
                        <div className="text-xs text-gray-500">
                          {format(new Date(message.sent_at), 'HH:mm', { locale: es })}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {message.reservation_id ? (
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {message.reservation_details?.customer_name || 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500">
                              {message.reservation_details?.date}{' '}
                              {message.reservation_details?.time}
                            </div>
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">Sin reserva</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {message.status === 'failed' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleResendMessage(message.id);
                            }}
                            disabled={resendMutation.isPending}
                            className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                          >
                            <RefreshCw size={14} />
                            <span>Reenviar</span>
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Message Detail Modal */}
      {selectedMessageId && (
        <MessageDetailModal
          messageId={selectedMessageId}
          onClose={() => setSelectedMessageId(null)}
        />
      )}
    </div>
  );
}

// Message Detail Modal Component
interface MessageDetailModalProps {
  messageId: string;
  onClose: () => void;
}

function MessageDetailModal({ messageId, onClose }: MessageDetailModalProps) {
  const { data: message, isLoading } = useWhatsAppMessage(messageId);

  if (!message) return null;

  const statusBadge = (() => {
    switch (message.status) {
      case 'sent':
        return {
          bg: 'bg-blue-100',
          text: 'text-blue-700',
          border: 'border-blue-300',
          label: 'Enviado',
        };
      case 'delivered':
        return {
          bg: 'bg-green-100',
          text: 'text-green-700',
          border: 'border-green-300',
          label: 'Entregado',
        };
      case 'read':
        return {
          bg: 'bg-purple-100',
          text: 'text-purple-700',
          border: 'border-purple-300',
          label: 'Leído',
        };
      case 'failed':
        return {
          bg: 'bg-red-100',
          text: 'text-red-700',
          border: 'border-red-300',
          label: 'Fallido',
        };
      default:
        return {
          bg: 'bg-gray-100',
          text: 'text-gray-700',
          border: 'border-gray-300',
          label: message.status,
        };
    }
  })();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Detalle del Mensaje</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={24} className="text-gray-500" />
          </button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="p-6 space-y-6">
            {/* Status Badge */}
            <div className="flex items-center justify-between">
              <span
                className={`px-4 py-2 rounded-full text-sm font-medium border-2 ${statusBadge.bg} ${statusBadge.text} ${statusBadge.border}`}
              >
                {statusBadge.label}
              </span>
              <span className="text-sm text-gray-500">ID: {message.id.substring(0, 8)}...</span>
            </div>

            {/* Message Content */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contenido del Mensaje</h3>
              <p className="text-gray-700 whitespace-pre-line">{message.content}</p>
            </div>

            {/* Message Metadata */}
            <div className="bg-blue-50 rounded-xl p-6 space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Información del Mensaje</h3>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white rounded-lg">
                    <MessageCircle size={20} className="text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Teléfono</p>
                    <p className="font-medium text-gray-900">{message.phone_number}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white rounded-lg">
                    <Clock size={20} className="text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Enviado</p>
                    <p className="font-medium text-gray-900">
                      {format(new Date(message.sent_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                    </p>
                  </div>
                </div>

                {message.delivered_at && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white rounded-lg">
                      <CheckCircle size={20} className="text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Entregado</p>
                      <p className="font-medium text-gray-900">
                        {format(new Date(message.delivered_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                      </p>
                    </div>
                  </div>
                )}

                {message.read_at && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white rounded-lg">
                      <Eye size={20} className="text-purple-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Leído</p>
                      <p className="font-medium text-gray-900">
                        {format(new Date(message.read_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                      </p>
                    </div>
                  </div>
                )}

                {message.cost && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white rounded-lg">
                      <DollarSign size={20} className="text-gray-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Costo</p>
                      <p className="font-medium text-gray-900">${message.cost.toFixed(4)}</p>
                    </div>
                  </div>
                )}

                {message.retry_count !== undefined && message.retry_count > 0 && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white rounded-lg">
                      <RefreshCw size={20} className="text-gray-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Reintentos</p>
                      <p className="font-medium text-gray-900">{message.retry_count}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Reservation Details */}
            {message.reservation_id && message.reservation_details && (
              <div className="bg-green-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Detalles de la Reserva
                </h3>
                <div className="space-y-2">
                  <p className="text-sm">
                    <span className="text-gray-600">Cliente:</span>{' '}
                    <span className="font-medium text-gray-900">
                      {message.reservation_details.customer_name}
                    </span>
                  </p>
                  <p className="text-sm">
                    <span className="text-gray-600">Fecha:</span>{' '}
                    <span className="font-medium text-gray-900">
                      {message.reservation_details.date}
                    </span>
                  </p>
                  <p className="text-sm">
                    <span className="text-gray-600">Hora:</span>{' '}
                    <span className="font-medium text-gray-900">
                      {message.reservation_details.time}
                    </span>
                  </p>
                  <p className="text-sm">
                    <span className="text-gray-600">Personas:</span>{' '}
                    <span className="font-medium text-gray-900">
                      {message.reservation_details.party_size}
                    </span>
                  </p>
                  <p className="text-sm">
                    <span className="text-gray-600">ID Reserva:</span>{' '}
                    <span className="font-mono text-xs text-gray-900">{message.reservation_id}</span>
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {message.error_message && (
              <div className="bg-red-50 rounded-xl p-6">
                <div className="flex items-start gap-3">
                  <AlertCircle size={20} className="text-red-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-red-900 mb-1">Mensaje de Error</p>
                    <p className="text-sm text-red-700">{message.error_message}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Close Button */}
            <div className="flex justify-end pt-4 border-t border-gray-200">
              <button
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
