import {
  TrendingUp,
  Users,
  Clock,
  AlertCircle,
  CheckCircle,
  Calendar,
  MessageSquare,
  Utensils,
  UserCheck,
  AlertTriangle
} from 'lucide-react';
import { useReservations } from '../hooks/useReservations';
import { useActivity } from '../hooks/useActivity';
import { useWebSocket } from '../hooks/useWebSocket';
import { useMemo, useEffect, useState } from 'react';
import { isToday, parseISO, format, formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Reserva } from '../types';

// Helper function to get badge classes based on reservation status
function getEstadoBadgeClasses(estado: Reserva['estado']): string {
  switch (estado) {
    case 'Confirmada':
      return 'bg-green-100 text-green-800 border-green-300';
    case 'Pendiente':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    case 'Cancelada':
      return 'bg-red-100 text-red-800 border-red-300';
    case 'Completada':
      return 'bg-blue-100 text-blue-800 border-blue-300';
    case 'Sentada':
      return 'bg-purple-100 text-purple-800 border-purple-300';
    case 'NoShow':
      return 'bg-gray-100 text-gray-800 border-gray-300';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300';
  }
}

// Helper function to get icon for activity type
function getActivityIcon(tipo: string) {
  switch (tipo) {
    case 'reserva_creada':
      return Calendar;
    case 'reserva_editada':
      return MessageSquare;
    case 'reserva_cancelada':
      return AlertCircle;
    case 'mesa_asignada':
      return Utensils;
    case 'cliente_sentado':
      return UserCheck;
    case 'reserva_completada':
      return CheckCircle;
    case 'waitlist_agregado':
      return Clock;
    case 'sistema':
      return AlertTriangle;
    default:
      return MessageSquare;
  }
}

// Helper function to format relative time in Spanish
function formatTimeAgo(timestamp: string): string {
  try {
    const date = parseISO(timestamp);
    return formatDistanceToNow(date, { addSuffix: true, locale: es });
  } catch {
    return 'hace un momento';
  }
}

export default function Dashboard() {
  const {
    data: reservasData,
    isLoading: reservasLoading,
    error: reservasError,
    refetch: refetchReservas
  } = useReservations(100);

  const {
    data: activityData,
    isLoading: activityLoading,
    error: activityError
  } = useActivity(10);

  const reservas = reservasData?.reservas || [];
  const activities = activityData?.events || [];

  // WebSocket integration for real-time updates
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const { status: wsStatus, lastMessage } = useWebSocket({
    autoConnect: true,
    onReservationEvent: (event) => {
      // Show toast notification for reservation events
      const messages = {
        created: `Nueva reserva creada: ${event.reservation?.nombre || 'Cliente'}`,
        updated: `Reserva actualizada: ${event.reservation?.nombre || 'Cliente'}`,
        cancelled: `Reserva cancelada: ${event.reservation?.nombre || 'Cliente'}`,
        confirmed: `Reserva confirmada: ${event.reservation?.nombre || 'Cliente'}`,
        seated: `Cliente sentado: ${event.reservation?.nombre || 'Cliente'}`,
        completed: `Reserva completada: ${event.reservation?.nombre || 'Cliente'}`,
      };
      setToastMessage(messages[event.action] || 'Evento de reserva recibido');
    },
    onTableEvent: (event) => {
      const messages = {
        assigned: 'Mesa asignada',
        freed: 'Mesa liberada',
        occupied: 'Mesa ocupada',
        blocked: 'Mesa bloqueada',
      };
      setToastMessage(messages[event.action] || 'Evento de mesa recibido');
    },
    onWaitlistEvent: (event) => {
      const messages = {
        added: 'Cliente agregado a lista de espera',
        notified: 'Cliente notificado de disponibilidad',
        removed: 'Cliente removido de lista de espera',
        seated: 'Cliente de lista de espera sentado',
      };
      setToastMessage(messages[event.action] || 'Evento de lista de espera recibido');
    },
  });

  // Auto-hide toast after 5 seconds
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => setToastMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  // Calculate stats from real data using useMemo for performance
  const stats = useMemo(() => {
    const reservasHoy = reservas.filter(r => isToday(parseISO(r.fecha)));

    return {
      totalReservasHoy: reservasHoy.length,
      reservasConfirmadas: reservasHoy.filter(r => r.estado === 'Confirmada').length,
      reservasPendientes: reservasHoy.filter(r => r.estado === 'Pendiente').length,
      ocupacion: reservasHoy.length > 0
        ? Math.round((reservasHoy.filter(r => r.estado === 'Sentada' || r.estado === 'Completada').length / reservasHoy.length) * 100)
        : 0,
    };
  }, [reservas]);

  const statCards = [
    {
      label: 'Reservas Hoy',
      value: stats.totalReservasHoy,
      icon: Users,
      gradient: 'from-blue-500 to-blue-600',
      trend: `${stats.totalReservasHoy} reservas`
    },
    {
      label: 'Confirmadas',
      value: stats.reservasConfirmadas,
      icon: CheckCircle,
      gradient: 'from-green-500 to-green-600',
      trend: `${Math.round((stats.reservasConfirmadas / Math.max(stats.totalReservasHoy, 1)) * 100)}% del total`
    },
    {
      label: 'Pendientes',
      value: stats.reservasPendientes,
      icon: Clock,
      gradient: 'from-yellow-500 to-yellow-600',
      trend: stats.reservasPendientes > 0 ? 'Requieren acción' : 'Sin pendientes'
    },
    {
      label: 'Ocupación',
      value: `${stats.ocupacion}%`,
      icon: TrendingUp,
      gradient: 'from-primary-500 to-primary-600',
      trend: 'Capacidad actual'
    },
  ];

  // Loading state with skeleton screens
  if (reservasLoading || activityLoading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-24 mb-3"></div>
                <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-32"></div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b">
                <div className="h-6 bg-gray-200 rounded w-40 animate-pulse"></div>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {[...Array(3)].map((_, j) => (
                    <div key={j} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Error state with retry button
  if (reservasError || activityError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <AlertCircle className="mx-auto text-red-500 mb-4" size={48} />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Error al cargar el dashboard
          </h3>
          <p className="text-gray-600 mb-6">
            {reservasError?.message || activityError?.message || 'No se pudo cargar la información'}
          </p>
          <button
            onClick={() => {
              if (reservasError) refetchReservas();
            }}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  // Empty state when no reservations
  if (reservas.length === 0) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                    <p className="text-sm text-gray-500 mt-2">{stat.trend}</p>
                  </div>
                  <div className={`bg-gradient-to-br ${stat.gradient} p-3 rounded-xl shadow-lg`}>
                    <Icon className="text-white" size={24} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12">
          <div className="text-center max-w-md mx-auto">
            <Calendar className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No hay reservas registradas
            </h3>
            <p className="text-gray-600">
              Las reservas que se creen aparecerán aquí automáticamente.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const reservasRecientes = reservas.slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 flex items-center gap-3 max-w-md">
            <div className="flex-shrink-0">
              <CheckCircle className="text-green-500" size={24} />
            </div>
            <p className="text-sm font-medium text-gray-900">{toastMessage}</p>
            <button
              onClick={() => setToastMessage(null)}
              className="ml-auto flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <span className="sr-only">Cerrar</span>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Stats Grid with modern design */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 p-6 border border-gray-100 group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 group-hover:text-gray-700 transition-colors">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1 group-hover:scale-105 transition-transform">{stat.value}</p>
                  <p className="text-sm text-gray-500 mt-2">{stat.trend}</p>
                </div>
                <div className={`bg-gradient-to-br ${stat.gradient} p-3 rounded-xl shadow-lg group-hover:shadow-xl transition-shadow`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Reservas Recientes */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800">Reservas Recientes</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {reservasRecientes.map((reserva) => (
              <div key={reserva.id} className="p-4 hover:bg-gray-50 transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{reserva.nombre}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {format(parseISO(reserva.fecha), "dd 'de' MMMM", { locale: es })} • {reserva.hora} • {reserva.pax} {reserva.pax === 1 ? 'persona' : 'personas'}
                    </p>
                    {reserva.mesa && (
                      <p className="text-sm text-primary-600 mt-1 font-medium">{reserva.mesa}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getEstadoBadgeClasses(reserva.estado)}`}>
                      {reserva.estado}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 border-t border-gray-100 bg-gray-50">
            <button className="text-primary-600 hover:text-primary-700 font-medium text-sm transition-colors">
              Ver todas las reservas ({reservas.length}) →
            </button>
          </div>
        </div>

        {/* Actividad Reciente - Real-time activity feed */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800">Actividad Reciente</h3>
          </div>
          <div className="p-6">
            {activities.length > 0 ? (
              <div className="space-y-4">
                {activities.map((activity) => {
                  const ActivityIcon = getActivityIcon(activity.tipo);
                  return (
                    <div key={activity.id} className="flex items-start gap-4 p-4 bg-gradient-to-r from-gray-50 to-transparent rounded-lg hover:from-gray-100 transition-colors">
                      <div className="p-2 bg-white rounded-lg shadow-sm border border-gray-200">
                        <ActivityIcon className="text-primary-600" size={20} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 text-sm">
                          {activity.descripcion}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatTimeAgo(activity.timestamp)}
                          {activity.usuario && ` • ${activity.usuario}`}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="mx-auto text-gray-400 mb-3" size={32} />
                <p className="text-sm text-gray-600">No hay actividad reciente</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
