import { useState } from 'react';
import { useActivity, type ActivityEvent } from '../hooks/useActivity';
import {
  Activity as ActivityIcon,
  Calendar,
  User,
  Clock,
  Filter,
  Search,
  CheckCircle2,
  XCircle,
  Edit3,
  UserPlus,
  Utensils,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';

const EVENT_TYPE_CONFIG = {
  reservation_created: {
    icon: UserPlus,
    label: 'Reserva Creada',
    color: 'bg-green-500/10 text-green-600 border-green-500/20',
    iconBg: 'bg-green-500/10',
    iconColor: 'text-green-600',
  },
  reservation_updated: {
    icon: Edit3,
    label: 'Reserva Actualizada',
    color: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    iconBg: 'bg-blue-500/10',
    iconColor: 'text-blue-600',
  },
  reservation_cancelled: {
    icon: XCircle,
    label: 'Reserva Cancelada',
    color: 'bg-red-500/10 text-red-600 border-red-500/20',
    iconBg: 'bg-red-500/10',
    iconColor: 'text-red-600',
  },
  table_assigned: {
    icon: CheckCircle2,
    label: 'Mesa Asignada',
    color: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
    iconBg: 'bg-purple-500/10',
    iconColor: 'text-purple-600',
  },
  customer_seated: {
    icon: Utensils,
    label: 'Cliente Sentado',
    color: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
    iconBg: 'bg-amber-500/10',
    iconColor: 'text-amber-600',
  },
} as const;

export default function Activity() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEventType, setSelectedEventType] = useState<string>('all');
  const [selectedUser, setSelectedUser] = useState<string>('all');

  const { data, isLoading, error, refetch, isRefetching } = useActivity();

  // Filter logic
  const filteredEvents = data?.events.filter((event) => {
    const matchesSearch =
      searchQuery === '' ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.user.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesEventType =
      selectedEventType === 'all' || event.event_type === selectedEventType;

    const matchesUser = selectedUser === 'all' || event.user === selectedUser;

    return matchesSearch && matchesEventType && matchesUser;
  }) || [];

  // Extract unique users for filter
  const uniqueUsers = Array.from(
    new Set(data?.events.map((e) => e.user) || [])
  ).sort();

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Justo ahora';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;

    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg shadow-purple-500/25">
              <ActivityIcon className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Registro de Actividad
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                Monitoreo en tiempo real de eventos del sistema
              </p>
            </div>
          </div>

          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="px-4 py-2 bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-xl hover:bg-slate-50 transition-all shadow-sm hover:shadow-md flex items-center gap-2 text-slate-700 font-medium disabled:opacity-50"
          >
            <RefreshCw
              className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`}
            />
            {isRefetching ? 'Actualizando...' : 'Actualizar'}
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-slate-500/10 rounded-xl">
                <ActivityIcon className="w-6 h-6 text-slate-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">
                  Total Eventos
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {data?.total || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <UserPlus className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">Creadas</p>
                <p className="text-2xl font-bold text-slate-900">
                  {data?.events.filter((e) => e.event_type === 'reservation_created')
                    .length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-amber-500/10 rounded-xl">
                <Utensils className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">Sentados</p>
                <p className="text-2xl font-bold text-slate-900">
                  {data?.events.filter((e) => e.event_type === 'customer_seated')
                    .length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-red-500/10 rounded-xl">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600 font-medium">
                  Canceladas
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {data?.events.filter(
                    (e) => e.event_type === 'reservation_cancelled'
                  ).length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar en actividad..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-slate-50/80 border border-slate-200/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500/40 transition-all text-slate-900 placeholder:text-slate-400"
              />
            </div>

            {/* Event Type Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <select
                value={selectedEventType}
                onChange={(e) => setSelectedEventType(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-slate-50/80 border border-slate-200/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500/40 transition-all text-slate-900 appearance-none cursor-pointer"
              >
                <option value="all">Todos los eventos</option>
                <option value="reservation_created">Reservas Creadas</option>
                <option value="reservation_updated">
                  Reservas Actualizadas
                </option>
                <option value="reservation_cancelled">
                  Reservas Canceladas
                </option>
                <option value="table_assigned">Mesas Asignadas</option>
                <option value="customer_seated">Clientes Sentados</option>
              </select>
            </div>

            {/* User Filter */}
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <select
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-slate-50/80 border border-slate-200/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500/40 transition-all text-slate-900 appearance-none cursor-pointer"
              >
                <option value="all">Todos los usuarios</option>
                {uniqueUsers.map((user) => (
                  <option key={user} value={user}>
                    {user}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Active Filters Summary */}
          {(searchQuery || selectedEventType !== 'all' || selectedUser !== 'all') && (
            <div className="mt-4 pt-4 border-t border-slate-200/60">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-slate-600 font-medium">
                  Filtros activos:
                </span>
                {searchQuery && (
                  <span className="px-3 py-1 bg-purple-500/10 text-purple-600 text-xs rounded-lg border border-purple-500/20 font-medium">
                    Búsqueda: "{searchQuery}"
                  </span>
                )}
                {selectedEventType !== 'all' && (
                  <span className="px-3 py-1 bg-blue-500/10 text-blue-600 text-xs rounded-lg border border-blue-500/20 font-medium">
                    Tipo:{' '}
                    {
                      EVENT_TYPE_CONFIG[
                        selectedEventType as keyof typeof EVENT_TYPE_CONFIG
                      ].label
                    }
                  </span>
                )}
                {selectedUser !== 'all' && (
                  <span className="px-3 py-1 bg-slate-500/10 text-slate-600 text-xs rounded-lg border border-slate-500/20 font-medium">
                    Usuario: {selectedUser}
                  </span>
                )}
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedEventType('all');
                    setSelectedUser('all');
                  }}
                  className="ml-2 text-xs text-slate-500 hover:text-slate-700 underline"
                >
                  Limpiar filtros
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Activity Timeline */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center py-24">
              <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-purple-500/20 border-t-purple-600 rounded-full animate-spin"></div>
                <p className="text-slate-600 font-medium">
                  Cargando actividad...
                </p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-24">
              <div className="flex flex-col items-center gap-4 max-w-md text-center">
                <div className="p-4 bg-red-500/10 rounded-2xl">
                  <AlertCircle className="w-12 h-12 text-red-600" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-slate-900 mb-2">
                    Error al cargar actividad
                  </p>
                  <p className="text-sm text-slate-600">
                    {error instanceof Error
                      ? error.message
                      : 'Ha ocurrido un error inesperado'}
                  </p>
                </div>
                <button
                  onClick={() => refetch()}
                  className="mt-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg shadow-purple-500/25 font-medium"
                >
                  Reintentar
                </button>
              </div>
            </div>
          ) : filteredEvents.length === 0 ? (
            <div className="flex items-center justify-center py-24">
              <div className="flex flex-col items-center gap-4 max-w-md text-center">
                <div className="p-4 bg-slate-100 rounded-2xl">
                  <ActivityIcon className="w-12 h-12 text-slate-400" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-slate-900 mb-2">
                    {searchQuery || selectedEventType !== 'all' || selectedUser !== 'all'
                      ? 'No se encontraron eventos'
                      : 'No hay actividad reciente'}
                  </p>
                  <p className="text-sm text-slate-600">
                    {searchQuery || selectedEventType !== 'all' || selectedUser !== 'all'
                      ? 'Intenta ajustar los filtros de búsqueda'
                      : 'Los eventos del sistema aparecerán aquí'}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {filteredEvents.map((event) => {
                const config =
                  EVENT_TYPE_CONFIG[
                    event.event_type as keyof typeof EVENT_TYPE_CONFIG
                  ];
                const Icon = config.icon;

                return (
                  <div
                    key={event.id}
                    className="p-6 hover:bg-slate-50/50 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      {/* Icon */}
                      <div className={`p-3 ${config.iconBg} rounded-xl`}>
                        <Icon className={`w-5 h-5 ${config.iconColor}`} />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-slate-900 mb-1">
                              {event.description}
                            </p>
                            <div className="flex items-center gap-3 flex-wrap">
                              <span
                                className={`px-2.5 py-1 text-xs rounded-lg border font-medium ${config.color}`}
                              >
                                {config.label}
                              </span>
                              <div className="flex items-center gap-1.5 text-xs text-slate-600">
                                <User className="w-3.5 h-3.5" />
                                <span>{event.user}</span>
                              </div>
                              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                                <Clock className="w-3.5 h-3.5" />
                                <span>{formatTimestamp(event.timestamp)}</span>
                              </div>
                            </div>
                          </div>

                          {/* Timestamp */}
                          <div className="text-xs text-slate-500 whitespace-nowrap">
                            {new Date(event.timestamp).toLocaleTimeString(
                              'es-ES',
                              {
                                hour: '2-digit',
                                minute: '2-digit',
                              }
                            )}
                          </div>
                        </div>

                        {/* Metadata */}
                        {event.metadata && Object.keys(event.metadata).length > 0 && (
                          <div className="mt-3 p-3 bg-slate-50/80 rounded-xl">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                              {Object.entries(event.metadata).map(
                                ([key, value]) => (
                                  <div key={key}>
                                    <p className="text-xs text-slate-500 mb-0.5 capitalize">
                                      {key.replace(/_/g, ' ')}
                                    </p>
                                    <p className="text-sm text-slate-900 font-medium">
                                      {typeof value === 'object'
                                        ? JSON.stringify(value)
                                        : String(value)}
                                    </p>
                                  </div>
                                )
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Results Footer */}
        {filteredEvents.length > 0 && (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-4 shadow-sm">
            <div className="flex items-center justify-between text-sm">
              <p className="text-slate-600">
                Mostrando{' '}
                <span className="font-semibold text-slate-900">
                  {filteredEvents.length}
                </span>{' '}
                de{' '}
                <span className="font-semibold text-slate-900">
                  {data?.total || 0}
                </span>{' '}
                eventos
              </p>
              <p className="text-slate-500 text-xs">
                Actualización automática cada 5 segundos
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
