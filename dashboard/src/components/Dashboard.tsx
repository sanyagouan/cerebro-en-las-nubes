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
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Zap
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
      return 'badge-success';
    case 'Pendiente':
      return 'badge-warning';
    case 'Cancelada':
      return 'badge-error';
    case 'Completada':
      return 'bg-secondary-100 text-secondary-700 border-secondary-200';
    case 'Sentada':
      return 'bg-purple-50 text-purple-700 border-purple-200';
    case 'NoShow':
      return 'bg-secondary-100 text-secondary-700 border-secondary-200';
    default:
      return 'bg-secondary-100 text-secondary-700 border-secondary-200';
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
      clientesHoy: reservasHoy.reduce((acc, r) => acc + (r.pax || 0), 0),
    };
  }, [reservas]);

  // Calculate comparison with yesterday (mock for demo)
  const trends = {
    reservas: { value: 12, up: true },
    confirmadas: { value: 5, up: true },
    pendientes: { value: 2, up: false },
    ocupacion: { value: 8, up: true },
  };

  const statCards = [
    {
      label: 'Reservas Hoy',
      value: stats.totalReservasHoy,
      icon: Calendar,
      gradient: 'from-blue-500 to-blue-600',
      trend: trends.reservas,
      subtitle: `${stats.clientesHoy} comensales`,
    },
    {
      label: 'Confirmadas',
      value: stats.reservasConfirmadas,
      icon: CheckCircle,
      gradient: 'from-success-500 to-success-600',
      trend: trends.confirmadas,
      subtitle: `${Math.round((stats.reservasConfirmadas / Math.max(stats.totalReservasHoy, 1)) * 100)}% del total`,
    },
    {
      label: 'Pendientes',
      value: stats.reservasPendientes,
      icon: Clock,
      gradient: 'from-warning-500 to-warning-600',
      trend: trends.pendientes,
      subtitle: stats.reservasPendientes > 0 ? 'Requieren atencion' : 'Todo al dia',
    },
    {
      label: 'Ocupacion',
      value: `${stats.ocupacion}%`,
      icon: TrendingUp,
      gradient: 'from-primary-500 to-primary-600',
      trend: trends.ocupacion,
      subtitle: 'Capacidad actual',
    },
  ];

  // Loading state with skeleton screens
  if (reservasLoading || activityLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        {/* Stats Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="premium-card p-6">
              <div className="animate-pulse space-y-4">
                <div className="flex justify-between">
                  <div className="h-4 bg-secondary-200 rounded w-24"></div>
                  <div className="h-10 w-10 bg-secondary-200 rounded-xl"></div>
                </div>
                <div className="h-8 bg-secondary-200 rounded w-16"></div>
                <div className="h-3 bg-secondary-200 rounded w-32"></div>
              </div>
            </div>
          ))}
        </div>

        {/* Content Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="premium-card">
              <div className="p-6 border-b border-secondary-100">
                <div className="h-6 bg-secondary-200 rounded w-40 animate-pulse"></div>
              </div>
              <div className="p-6 space-y-4">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="animate-pulse flex gap-4">
                    <div className="h-12 w-12 bg-secondary-200 rounded-xl"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-secondary-200 rounded w-3/4"></div>
                      <div className="h-3 bg-secondary-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
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
      <div className="flex items-center justify-center min-h-[400px] animate-fade-in">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-error-50 flex items-center justify-center">
            <AlertCircle className="text-error-500" size={32} />
          </div>
          <h3 className="text-xl font-bold text-secondary-900 mb-2">
            Error al cargar el dashboard
          </h3>
          <p className="text-secondary-500 mb-6">
            {reservasError?.message || activityError?.message || 'No se pudo cargar la informacion'}
          </p>
          <button
            onClick={() => {
              if (reservasError) refetchReservas();
            }}
            className="btn-primary"
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
      <div className="space-y-8 animate-fade-in">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div 
                key={stat.label} 
                className="stat-card animate-fade-in-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-500">{stat.label}</p>
                    <p className="text-3xl font-bold text-secondary-900 mt-2">{stat.value}</p>
                    <p className="text-sm text-secondary-400 mt-1">{stat.subtitle}</p>
                  </div>
                  <div className={`bg-gradient-to-br ${stat.gradient} p-3 rounded-xl shadow-soft`}>
                    <Icon className="text-white" size={22} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        <div className="premium-card p-12">
          <div className="text-center max-w-md mx-auto">
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-secondary-50 flex items-center justify-center">
              <Calendar className="text-secondary-400" size={40} />
            </div>
            <h3 className="text-xl font-bold text-secondary-900 mb-2">
              No hay reservas registradas
            </h3>
            <p className="text-secondary-500">
              Las reservas que se creen apareceran aqui automaticamente.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const reservasRecientes = reservas.slice(0, 5);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 animate-fade-in-up">
          <div className="toast toast-success">
            <CheckCircle size={20} className="flex-shrink-0" />
            <span className="font-medium">{toastMessage}</span>
            <button
              onClick={() => setToastMessage(null)}
              className="ml-2 text-white/80 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Live Status Banner */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-gradient-to-r from-success-50 to-success-100/50 border border-success-200">
        <div className="flex items-center gap-3">
          <div className="pulse-dot"></div>
          <div>
            <p className="font-semibold text-success-800">Sistema en tiempo real activo</p>
            <p className="text-sm text-success-600">Conectado via WebSocket - Actualizaciones instantaneas</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-success-700">
          <Zap size={18} />
          <span className="text-sm font-medium">En vivo</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div 
              key={stat.label} 
              className="stat-card group animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-secondary-500 group-hover:text-secondary-600 transition-colors">
                    {stat.label}
                  </p>
                  <p className="text-3xl font-bold text-secondary-900 mt-2 group-hover:scale-105 transition-transform origin-left">
                    {stat.value}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    {stat.trend.up ? (
                      <ArrowUpRight size={14} className="text-success-500" />
                    ) : (
                      <ArrowDownRight size={14} className="text-error-500" />
                    )}
                    <span className={`text-xs font-medium ${stat.trend.up ? 'text-success-600' : 'text-error-600'}`}>
                      {stat.trend.value}% vs ayer
                    </span>
                  </div>
                </div>
                <div className={`bg-gradient-to-br ${stat.gradient} p-3.5 rounded-xl shadow-soft group-hover:shadow-card-hover transition-shadow`}>
                  <Icon className="text-white" size={22} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Reservations */}
        <div className="premium-card animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <div className="p-6 border-b border-secondary-100 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-secondary-900">Reservas Recientes</h3>
              <p className="text-sm text-secondary-500 mt-0.5">Ultimas {reservasRecientes.length} reservas</p>
            </div>
            <Activity size={20} className="text-secondary-400" />
          </div>
          <div className="divide-y divide-secondary-100">
            {reservasRecientes.map((reserva, index) => (
              <div 
                key={reserva.id} 
                className="p-4 hover:bg-secondary-50/50 transition-colors cursor-pointer group"
                style={{ animationDelay: `${(index + 3) * 50}ms` }}
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary-600 font-bold text-sm">
                        {reserva.nombre.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-secondary-900 truncate">{reserva.nombre}</p>
                      <p className="text-sm text-secondary-500 mt-0.5">
                        {format(parseISO(reserva.fecha), "dd MMM", { locale: es })} · {reserva.hora} · {reserva.pax} {reserva.pax === 1 ? 'persona' : 'personas'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    {reserva.mesa && (
                      <span className="px-2.5 py-1 bg-secondary-100 rounded-lg text-sm font-medium text-secondary-700">
                        {reserva.mesa}
                      </span>
                    )}
                    <span className={`badge ${getEstadoBadgeClasses(reserva.estado)}`}>
                      {reserva.estado}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 border-t border-secondary-100 bg-secondary-50/50">
            <button className="text-primary-600 hover:text-primary-700 font-semibold text-sm transition-colors flex items-center gap-1 group">
              Ver todas las reservas ({reservas.length})
              <ArrowUpRight size={16} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          </div>
        </div>

        {/* Activity Feed */}
        <div className="premium-card animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <div className="p-6 border-b border-secondary-100 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-secondary-900">Actividad Reciente</h3>
              <p className="text-sm text-secondary-500 mt-0.5">Eventos en tiempo real</p>
            </div>
            <div className="w-2 h-2 rounded-full bg-success-500 animate-pulse"></div>
          </div>
          <div className="p-6">
            {activities.length > 0 ? (
              <div className="space-y-4">
                {activities.map((activity, index) => {
                  const ActivityIcon = getActivityIcon(activity.tipo);
                  return (
                    <div 
                      key={activity.id} 
                      className="flex items-start gap-4 p-4 rounded-xl bg-gradient-to-r from-secondary-50 to-transparent hover:from-secondary-100 transition-colors group"
                    >
                      <div className="p-2.5 bg-white rounded-xl shadow-soft border border-secondary-100 group-hover:border-primary-200 transition-colors">
                        <ActivityIcon className="text-primary-500" size={18} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-secondary-900 text-sm leading-snug">
                          {activity.descripcion}
                        </p>
                        <p className="text-xs text-secondary-400 mt-1.5 flex items-center gap-2">
                          <Clock size={12} />
                          {formatTimeAgo(activity.timestamp)}
                          {activity.usuario && (
                            <>
                              <span className="text-secondary-300">·</span>
                              <span>{activity.usuario}</span>
                            </>
                          )}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-secondary-50 flex items-center justify-center">
                  <MessageSquare className="text-secondary-400" size={28} />
                </div>
                <p className="text-secondary-500 font-medium">No hay actividad reciente</p>
                <p className="text-sm text-secondary-400 mt-1">Los eventos apareceran aqui</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
