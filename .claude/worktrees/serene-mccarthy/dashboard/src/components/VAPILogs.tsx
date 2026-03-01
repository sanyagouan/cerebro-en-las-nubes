import { useState, useMemo } from 'react';
import {
  Phone,
  PhoneIncoming,
  PhoneOutgoing,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  PhoneOff,
  Download,
  FileText,
  DollarSign,
  TrendingUp,
  Users,
} from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { useVAPILogs, useVAPIAnalytics, useVAPICall, VAPICall } from '../hooks/useVapiLogs';

type StatusFilter = 'all' | 'completed' | 'failed' | 'in-progress' | 'no-answer' | 'busy';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

let toastId = 0;

// Call Detail Modal Component
interface CallDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  call: VAPICall | null;
}

function CallDetailModal({ isOpen, onClose, call }: CallDetailModalProps) {
  if (!isOpen || !call) return null;

  const getStatusColor = (status: VAPICall['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-300';
      case 'failed':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'in-progress':
        return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'no-answer':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'busy':
        return 'bg-orange-100 text-orange-700 border-orange-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 transition-opacity" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Detalle de Llamada</h2>
          <button
            type="button"
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <XCircle size={24} className="text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Status Badge */}
          <div className="flex items-center justify-between">
            <span className={`px-4 py-2 rounded-full text-sm font-medium border-2 ${getStatusColor(call.status)}`}>
              {call.status === 'completed' ? 'Completada' :
               call.status === 'failed' ? 'Fallida' :
               call.status === 'in-progress' ? 'En Curso' :
               call.status === 'no-answer' ? 'Sin Respuesta' :
               call.status === 'busy' ? 'Ocupado' : call.status}
            </span>
            <span className="text-sm text-gray-500">
              ID: {call.call_id.substring(0, 12)}...
            </span>
          </div>

          {/* Call Info */}
          <div className="bg-gray-50 rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Información de la Llamada</h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  <Phone size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Teléfono</p>
                  <p className="font-medium text-gray-900">{call.phone_number}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  {call.direction === 'inbound' ? (
                    <PhoneIncoming size={20} className="text-gray-600" />
                  ) : (
                    <PhoneOutgoing size={20} className="text-gray-600" />
                  )}
                </div>
                <div>
                  <p className="text-sm text-gray-500">Dirección</p>
                  <p className="font-medium text-gray-900">
                    {call.direction === 'inbound' ? 'Entrante' : 'Saliente'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  <Clock size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Duración</p>
                  <p className="font-medium text-gray-900">
                    {call.duration_seconds ? `${Math.floor(call.duration_seconds / 60)}:${(call.duration_seconds % 60).toString().padStart(2, '0')}` : 'N/A'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  <DollarSign size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Costo</p>
                  <p className="font-medium text-gray-900">
                    {call.cost ? `$${call.cost.toFixed(2)}` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500">Iniciada</p>
              <p className="font-medium text-gray-900">
                {format(new Date(call.started_at), 'PPpp', { locale: es })}
              </p>
              {call.ended_at && (
                <>
                  <p className="text-sm text-gray-500 mt-2">Finalizada</p>
                  <p className="font-medium text-gray-900">
                    {format(new Date(call.ended_at), 'PPpp', { locale: es })}
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Reservation Info */}
          {call.reservation_created && (
            <div className="bg-green-50 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <CheckCircle size={20} className="text-green-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-green-900 mb-1">Reserva Creada</p>
                  {call.metadata?.customer_name && (
                    <p className="text-sm text-green-700">Cliente: {call.metadata.customer_name}</p>
                  )}
                  {call.metadata?.party_size && (
                    <p className="text-sm text-green-700">Personas: {call.metadata.party_size}</p>
                  )}
                  {call.metadata?.date && call.metadata?.time && (
                    <p className="text-sm text-green-700">
                      Fecha: {call.metadata.date} a las {call.metadata.time}
                    </p>
                  )}
                  {call.reservation_id && (
                    <p className="text-xs text-green-600 mt-1">ID: {call.reservation_id}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {call.status === 'failed' && call.metadata?.error_message && (
            <div className="bg-red-50 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <AlertCircle size={20} className="text-red-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-900 mb-1">Error</p>
                  <p className="text-sm text-red-700">{call.metadata.error_message}</p>
                </div>
              </div>
            </div>
          )}

          {/* Summary */}
          {call.summary && (
            <div className="bg-blue-50 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <FileText size={20} className="text-blue-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">Resumen</p>
                  <p className="text-sm text-blue-700">{call.summary}</p>
                </div>
              </div>
            </div>
          )}

          {/* Transcript */}
          {call.transcript && (
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <FileText size={20} className="text-gray-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 mb-2">Transcripción</p>
                  <div className="bg-white rounded-lg p-4 max-h-64 overflow-y-auto">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{call.transcript}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Close Button */}
          <div className="flex justify-end pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function VapiLogs() {
  const { data: logs, isLoading, error } = useVAPILogs();
  const { data: analytics } = useVAPIAnalytics();
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [selectedCallId, setSelectedCallId] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Fetch selected call details
  const { data: selectedCall } = useVAPICall(selectedCallId || '');

  const showToast = (message: string, type: 'success' | 'error') => {
    const id = toastId++;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // Filtered logs with useMemo
  const filteredLogs = useMemo(() => {
    if (!logs?.calls) return [];
    
    if (statusFilter === 'all') return logs.calls;
    
    return logs.calls.filter(call => call.status === statusFilter);
  }, [logs?.calls, statusFilter]);

  // Export CSV
  const handleExportCSV = () => {
    if (!filteredLogs.length) {
      showToast('No hay llamadas para exportar', 'error');
      return;
    }

    const headers = [
      'ID',
      'Teléfono',
      'Dirección',
      'Estado',
      'Duración (seg)',
      'Inicio',
      'Fin',
      'Reserva Creada',
      'Costo',
    ];

    const rows = filteredLogs.map(call => [
      call.call_id,
      call.phone_number,
      call.direction === 'inbound' ? 'Entrante' : 'Saliente',
      call.status,
      call.duration_seconds?.toString() || '',
      call.started_at,
      call.ended_at || '',
      call.reservation_created ? 'Sí' : 'No',
      call.cost?.toFixed(2) || '',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.setAttribute('href', URL.createObjectURL(blob));
    link.setAttribute('download', `vapi_llamadas_${format(new Date(), 'yyyy-MM-dd_HH-mm', { locale: es })}.csv`);
    link.click();

    showToast('CSV exportado exitosamente', 'success');
  };

  const getStatusIcon = (status: VAPICall['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={18} className="text-green-600" />;
      case 'failed':
        return <XCircle size={18} className="text-red-600" />;
      case 'in-progress':
        return <Clock size={18} className="text-blue-600" />;
      case 'no-answer':
        return <PhoneOff size={18} className="text-yellow-600" />;
      case 'busy':
        return <AlertCircle size={18} className="text-orange-600" />;
      default:
        return <Phone size={18} className="text-gray-600" />;
    }
  };

  const getStatusColor = (status: VAPICall['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      case 'in-progress':
        return 'bg-blue-100 text-blue-700';
      case 'no-answer':
        return 'bg-yellow-100 text-yellow-700';
      case 'busy':
        return 'bg-orange-100 text-orange-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

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
        <h2 className="text-2xl font-bold text-gray-900">Registros VAPI</h2>
        <button
          onClick={handleExportCSV}
          disabled={!filteredLogs.length}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download size={20} />
          <span>Exportar CSV</span>
        </button>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <Phone size={20} className="text-primary-600" />
              <p className="text-sm text-gray-600">Total Llamadas</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">{analytics.total_calls}</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp size={20} className="text-green-600" />
              <p className="text-sm text-gray-600">Conversión</p>
            </div>
            <p className="text-3xl font-bold text-green-600">
              {(analytics.conversion_rate * 100).toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {analytics.reservations_created} reservas
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <Clock size={20} className="text-blue-600" />
              <p className="text-sm text-gray-600">Duración Promedio</p>
            </div>
            <p className="text-3xl font-bold text-blue-600">
              {Math.floor(analytics.avg_duration_seconds / 60)}:{(analytics.avg_duration_seconds % 60).toString().padStart(2, '0')}
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign size={20} className="text-purple-600" />
              <p className="text-sm text-gray-600">Costo Total</p>
            </div>
            <p className="text-3xl font-bold text-purple-600">
              ${analytics.total_cost.toFixed(2)}
            </p>
          </div>
        </div>
      )}

      {/* Status Filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            statusFilter === 'all'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Todos ({logs?.calls.length || 0})
        </button>
        <button
          onClick={() => setStatusFilter('completed')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            statusFilter === 'completed'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Completadas ({analytics?.calls_by_status.completed || 0})
        </button>
        <button
          onClick={() => setStatusFilter('failed')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            statusFilter === 'failed'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Fallidas ({analytics?.calls_by_status.failed || 0})
        </button>
        <button
          onClick={() => setStatusFilter('no-answer')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            statusFilter === 'no-answer'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Sin Respuesta ({analytics?.calls_by_status.no_answer || 0})
        </button>
        <button
          onClick={() => setStatusFilter('busy')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            statusFilter === 'busy'
              ? 'bg-orange-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Ocupado ({analytics?.calls_by_status.busy || 0})
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          Error al cargar llamadas: {error.message}
        </div>
      )}

      {/* Calls Table */}
      {!isLoading && !error && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Teléfono
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dirección
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duración
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Inicio
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
                      No hay llamadas con este filtro
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((call) => (
                    <tr
                      key={call.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => setSelectedCallId(call.id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <Phone size={16} className="text-gray-400" />
                          <span className="text-sm font-medium text-gray-900">
                            {call.phone_number}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          {call.direction === 'inbound' ? (
                            <PhoneIncoming size={16} className="text-blue-600" />
                          ) : (
                            <PhoneOutgoing size={16} className="text-purple-600" />
                          )}
                          <span className="text-sm text-gray-900">
                            {call.direction === 'inbound' ? 'Entrante' : 'Saliente'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(call.status)}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(call.status)}`}>
                            {call.status === 'completed' ? 'Completada' :
                             call.status === 'failed' ? 'Fallida' :
                             call.status === 'in-progress' ? 'En Curso' :
                             call.status === 'no-answer' ? 'Sin Respuesta' :
                             call.status === 'busy' ? 'Ocupado' : call.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {call.duration_seconds
                          ? `${Math.floor(call.duration_seconds / 60)}:${(call.duration_seconds % 60).toString().padStart(2, '0')}`
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {format(new Date(call.started_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {call.reservation_created ? (
                          <span className="flex items-center gap-1 text-sm text-green-600">
                            <CheckCircle size={16} />
                            Sí
                          </span>
                        ) : (
                          <span className="text-sm text-gray-400">No</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedCallId(call.id);
                          }}
                          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                        >
                          Ver Detalles
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Call Detail Modal */}
      <CallDetailModal
        isOpen={!!selectedCallId}
        onClose={() => setSelectedCallId(null)}
        call={selectedCall || null}
      />
    </div>
  );
}
