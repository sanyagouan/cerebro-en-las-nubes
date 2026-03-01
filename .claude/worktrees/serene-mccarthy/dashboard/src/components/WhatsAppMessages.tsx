import { useState } from 'react';
import {
  useWhatsAppMessages,
  useResendWhatsAppMessage,
  useWhatsAppTemplates,
  type WhatsAppMessage,
  type WhatsAppTemplate,
} from '../hooks/useWhatsAppMessages';
import {
  MessageCircle,
  Send,
  CheckCheck,
  Clock,
  XCircle,
  AlertCircle,
  Calendar,
  Filter,
  Search,
  RefreshCw,
  X,
  CheckCircle2,
  FileText,
  Users,
} from 'lucide-react';

const DELIVERY_STATUS_CONFIG = {
  enviado: {
    icon: Send,
    label: 'Enviado',
    color: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    iconBg: 'bg-blue-500/10',
    iconColor: 'text-blue-600',
  },
  entregado: {
    icon: CheckCircle2,
    label: 'Entregado',
    color: 'bg-green-500/10 text-green-600 border-green-500/20',
    iconBg: 'bg-green-500/10',
    iconColor: 'text-green-600',
  },
  leido: {
    icon: CheckCheck,
    label: 'Leído',
    color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20',
    iconBg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-600',
  },
  fallido: {
    icon: XCircle,
    label: 'Fallido',
    color: 'bg-red-500/10 text-red-600 border-red-500/20',
    iconBg: 'bg-red-500/10',
    iconColor: 'text-red-600',
  },
};

const MESSAGE_TYPE_CONFIG = {
  confirmacion: {
    label: 'Confirmación',
    color: 'bg-green-500/10 text-green-700',
    icon: CheckCircle2,
  },
  recordatorio: {
    label: 'Recordatorio',
    color: 'bg-blue-500/10 text-blue-700',
    icon: Clock,
  },
  cancelacion: {
    label: 'Cancelación',
    color: 'bg-red-500/10 text-red-700',
    icon: XCircle,
  },
  general: {
    label: 'General',
    color: 'bg-slate-500/10 text-slate-700',
    icon: MessageCircle,
  },
};

export default function WhatsAppMessages() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month' | 'all'>('week');

  const { data, isLoading, error, refetch, isRefetching } = useWhatsAppMessages(
    100,
    selectedStatus !== 'all' ? selectedStatus : undefined,
    selectedType !== 'all' ? selectedType : undefined
  );

  const { data: templatesData } = useWhatsAppTemplates();
  const resendMutation = useResendWhatsAppMessage();

  const messages = data?.messages || [];
  const templates = templatesData?.templates || [];

  // Filter by search and date range
  const filteredMessages = messages.filter((msg) => {
    const matchesSearch =
      searchQuery === '' ||
      msg.to.toLowerCase().includes(searchQuery.toLowerCase()) ||
      msg.recipient_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      msg.content.toLowerCase().includes(searchQuery.toLowerCase());

    const msgDate = new Date(msg.sent_at);
    const now = new Date();
    const daysDiff = Math.floor((now.getTime() - msgDate.getTime()) / (1000 * 60 * 60 * 24));

    let matchesDateRange = true;
    if (dateRange === 'today') matchesDateRange = daysDiff === 0;
    else if (dateRange === 'week') matchesDateRange = daysDiff <= 7;
    else if (dateRange === 'month') matchesDateRange = daysDiff <= 30;

    return matchesSearch && matchesDateRange;
  });

  const handleResend = async (messageId: string) => {
    try {
      await resendMutation.mutateAsync({ messageId });
    } catch (err) {
      console.error('Error reenviando mensaje:', err);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Ahora mismo';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours} h`;
    if (diffDays < 7) return `Hace ${diffDays} días`;

    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusStats = () => {
    return {
      total: messages.length,
      enviados: messages.filter((m) => m.delivery_status === 'enviado').length,
      entregados: messages.filter((m) => m.delivery_status === 'entregado').length,
      leidos: messages.filter((m) => m.delivery_status === 'leido').length,
      fallidos: messages.filter((m) => m.delivery_status === 'fallido').length,
    };
  };

  const stats = getStatusStats();

  const activeFiltersCount =
    (selectedStatus !== 'all' ? 1 : 0) +
    (selectedType !== 'all' ? 1 : 0) +
    (dateRange !== 'all' ? 1 : 0) +
    (searchQuery !== '' ? 1 : 0);

  const clearFilters = () => {
    setSelectedStatus('all');
    setSelectedType('all');
    setDateRange('all');
    setSearchQuery('');
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white/80 backdrop-blur-sm border border-red-200/60 rounded-2xl p-8 shadow-lg shadow-red-500/10">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-500/10 rounded-xl">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900">Error al cargar mensajes</h3>
            </div>
            <p className="text-slate-600 mb-4">
              Hubo un problema al cargar los mensajes de WhatsApp. Por favor, intenta nuevamente.
            </p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors font-medium"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500/10 rounded-2xl shadow-lg shadow-green-500/20">
              <MessageCircle className="w-8 h-8 text-green-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Mensajes WhatsApp</h1>
              <p className="text-slate-600 mt-1">
                Gestión de notificaciones y confirmaciones
              </p>
            </div>
          </div>
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-xl hover:bg-slate-50/50 transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 text-slate-600 ${isRefetching ? 'animate-spin' : ''}`} />
            <span className="text-sm font-medium text-slate-700">Actualizar</span>
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <MessageCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">Total Mensajes</p>
                <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-blue-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <Send className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">Enviados</p>
                <p className="text-2xl font-bold text-slate-900">{stats.enviados}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-green-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">Entregados</p>
                <p className="text-2xl font-bold text-slate-900">{stats.entregados}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-emerald-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-500/10 rounded-xl">
                <CheckCheck className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">Leídos</p>
                <p className="text-2xl font-bold text-slate-900">{stats.leidos}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-red-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-red-500/10 rounded-xl">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">Fallidos</p>
                <p className="text-2xl font-bold text-slate-900">{stats.fallidos}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-lg shadow-slate-500/5">
          <div className="flex items-center gap-4 mb-4">
            <Filter className="w-5 h-5 text-slate-600" />
            <h3 className="text-lg font-semibold text-slate-900">Filtros</h3>
            {activeFiltersCount > 0 && (
              <button
                onClick={clearFilters}
                className="ml-auto flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
              >
                <X className="w-4 h-4" />
                Limpiar ({activeFiltersCount})
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar por teléfono, nombre o contenido..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all"
              />
            </div>

            {/* Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all"
            >
              <option value="all">Todos los estados</option>
              <option value="enviado">Enviado</option>
              <option value="entregado">Entregado</option>
              <option value="leido">Leído</option>
              <option value="fallido">Fallido</option>
            </select>

            {/* Type Filter */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all"
            >
              <option value="all">Todos los tipos</option>
              <option value="confirmacion">Confirmación</option>
              <option value="recordatorio">Recordatorio</option>
              <option value="cancelacion">Cancelación</option>
              <option value="general">General</option>
            </select>

            {/* Date Range Filter */}
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="px-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all"
            >
              <option value="today">Hoy</option>
              <option value="week">Última semana</option>
              <option value="month">Último mes</option>
              <option value="all">Todo el tiempo</option>
            </select>
          </div>

          {activeFiltersCount > 0 && (
            <div className="mt-4 flex items-center gap-2 flex-wrap">
              <span className="text-sm text-slate-600 font-medium">Filtros activos:</span>
              {searchQuery && (
                <span className="px-3 py-1 bg-green-500/10 text-green-700 rounded-lg text-sm font-medium">
                  Búsqueda: "{searchQuery}"
                </span>
              )}
              {selectedStatus !== 'all' && (
                <span className="px-3 py-1 bg-green-500/10 text-green-700 rounded-lg text-sm font-medium">
                  Estado: {DELIVERY_STATUS_CONFIG[selectedStatus as keyof typeof DELIVERY_STATUS_CONFIG]?.label}
                </span>
              )}
              {selectedType !== 'all' && (
                <span className="px-3 py-1 bg-green-500/10 text-green-700 rounded-lg text-sm font-medium">
                  Tipo: {MESSAGE_TYPE_CONFIG[selectedType as keyof typeof MESSAGE_TYPE_CONFIG]?.label}
                </span>
              )}
              {dateRange !== 'all' && (
                <span className="px-3 py-1 bg-green-500/10 text-green-700 rounded-lg text-sm font-medium">
                  Período: {dateRange === 'today' ? 'Hoy' : dateRange === 'week' ? 'Última semana' : 'Último mes'}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Messages List */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl shadow-lg shadow-slate-500/5 overflow-hidden">
          <div className="p-6 border-b border-slate-200/60">
            <h3 className="text-lg font-semibold text-slate-900">
              Historial de Mensajes
            </h3>
            <p className="text-sm text-slate-600 mt-1">
              {filteredMessages.length} mensaje{filteredMessages.length !== 1 ? 's' : ''} encontrado{filteredMessages.length !== 1 ? 's' : ''}
            </p>
          </div>

          <div className="p-6">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-16">
                <div className="w-12 h-12 border-4 border-green-500/20 border-t-green-600 rounded-full animate-spin mb-4" />
                <p className="text-slate-600 font-medium">Cargando mensajes...</p>
              </div>
            ) : filteredMessages.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16">
                <div className="p-4 bg-slate-100 rounded-2xl mb-4">
                  <MessageCircle className="w-12 h-12 text-slate-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No hay mensajes</h3>
                <p className="text-slate-600 text-center max-w-md">
                  {activeFiltersCount > 0
                    ? 'No se encontraron mensajes que coincidan con los filtros aplicados.'
                    : 'Aún no se han enviado mensajes de WhatsApp.'}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredMessages.map((msg) => {
                  const statusConfig = DELIVERY_STATUS_CONFIG[msg.delivery_status];
                  const typeConfig = MESSAGE_TYPE_CONFIG[msg.message_type];
                  const StatusIcon = statusConfig.icon;
                  const TypeIcon = typeConfig.icon;

                  return (
                    <div
                      key={msg.id}
                      className="bg-white border border-slate-200/60 rounded-xl p-6 hover:shadow-md transition-all"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-start gap-4 flex-1">
                          <div className={`p-3 ${statusConfig.iconBg} rounded-xl`}>
                            <StatusIcon className={`w-6 h-6 ${statusConfig.iconColor}`} />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h4 className="text-lg font-semibold text-slate-900">
                                {msg.recipient_name || msg.to}
                              </h4>
                              <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${statusConfig.color}`}>
                                {statusConfig.label}
                              </span>
                              <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${typeConfig.color}`}>
                                <TypeIcon className="w-3 h-3 inline mr-1" />
                                {typeConfig.label}
                              </span>
                            </div>
                            <p className="text-sm text-slate-600 mb-3">{msg.to}</p>
                            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                                {msg.content}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                        <div className="flex items-center gap-4 text-sm text-slate-600">
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            {formatTimestamp(msg.sent_at)}
                          </div>
                          {msg.template_name && (
                            <div className="flex items-center gap-2">
                              <FileText className="w-4 h-4" />
                              Template: {msg.template_name}
                            </div>
                          )}
                        </div>

                        {msg.delivery_status === 'fallido' && (
                          <button
                            onClick={() => handleResend(msg.id)}
                            disabled={resendMutation.isPending}
                            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <RefreshCw className={`w-4 h-4 ${resendMutation.isPending ? 'animate-spin' : ''}`} />
                            Reenviar
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          {filteredMessages.length > 0 && (
            <div className="p-4 bg-slate-50 border-t border-slate-200/60">
              <p className="text-sm text-slate-600 text-center">
                Mostrando {filteredMessages.length} de {messages.length} mensajes totales • Actualización automática cada 15 segundos
              </p>
            </div>
          )}
        </div>

        {/* Templates Section */}
        {templates.length > 0 && (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl shadow-lg shadow-slate-500/5 overflow-hidden">
            <div className="p-6 border-b border-slate-200/60">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-slate-600" />
                <h3 className="text-lg font-semibold text-slate-900">
                  Templates Disponibles
                </h3>
              </div>
              <p className="text-sm text-slate-600 mt-1">
                {templates.length} template{templates.length !== 1 ? 's' : ''} configurado{templates.length !== 1 ? 's' : ''}
              </p>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map((template) => {
                  const typeConfig = MESSAGE_TYPE_CONFIG[template.type];
                  const TypeIcon = typeConfig.icon;

                  return (
                    <div
                      key={template.id}
                      className="bg-white border border-slate-200/60 rounded-xl p-5 hover:shadow-md transition-all"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`p-2 ${typeConfig.color} rounded-lg`}>
                          <TypeIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-900">{template.name}</h4>
                          <span className={`text-xs font-medium ${typeConfig.color}`}>
                            {typeConfig.label}
                          </span>
                        </div>
                      </div>
                      <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                        <p className="text-sm text-slate-700 leading-relaxed">
                          {template.content}
                        </p>
                      </div>
                      {template.variables && template.variables.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-200">
                          <p className="text-xs text-slate-600 font-medium mb-2">Variables:</p>
                          <div className="flex flex-wrap gap-2">
                            {template.variables.map((variable) => (
                              <span
                                key={variable}
                                className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-mono"
                              >
                                {`{{${variable}}}`}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
