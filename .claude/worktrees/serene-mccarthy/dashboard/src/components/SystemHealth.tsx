import { useState } from 'react';
import {
  useSystemHealth,
  useSystemMetrics,
  useErrorLogs,
  useUptimeStatus,
  type HealthCheck,
  type ErrorLog,
} from '../hooks/useSystemHealth';
import {
  Activity,
  Server,
  Database,
  Wifi,
  Cloud,
  AlertTriangle,
  CheckCircle,
  XCircle,
  AlertCircle,
  Cpu,
  HardDrive,
  Clock,
  TrendingUp,
  RefreshCw,
  Filter,
  X,
  Calendar,
  Zap,
  Radio,
} from 'lucide-react';

const SERVICE_CONFIG = {
  backend: {
    label: 'Backend API',
    icon: Server,
    color: 'blue',
  },
  redis: {
    label: 'Redis Cache',
    icon: Database,
    color: 'red',
  },
  airtable: {
    label: 'Airtable DB',
    icon: Cloud,
    color: 'yellow',
  },
  vapi: {
    label: 'VAPI Voice',
    icon: Wifi,
    color: 'purple',
  },
  twilio: {
    label: 'Twilio SMS',
    icon: Radio,
    color: 'green',
  },
};

const HEALTH_STATUS_CONFIG = {
  healthy: {
    icon: CheckCircle,
    label: 'Saludable',
    color: 'bg-green-500/10 text-green-600 border-green-500/20',
    iconBg: 'bg-green-500/10',
    iconColor: 'text-green-600',
    dotColor: 'bg-green-500',
  },
  degraded: {
    icon: AlertCircle,
    label: 'Degradado',
    color: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
    iconBg: 'bg-yellow-500/10',
    iconColor: 'text-yellow-600',
    dotColor: 'bg-yellow-500',
  },
  unhealthy: {
    icon: XCircle,
    label: 'No Disponible',
    color: 'bg-red-500/10 text-red-600 border-red-500/20',
    iconBg: 'bg-red-500/10',
    iconColor: 'text-red-600',
    dotColor: 'bg-red-500',
  },
};

const ERROR_LEVEL_CONFIG = {
  critical: {
    label: 'Crítico',
    color: 'bg-red-500/10 text-red-700 border-red-500/20',
    icon: XCircle,
    iconColor: 'text-red-600',
  },
  error: {
    label: 'Error',
    color: 'bg-orange-500/10 text-orange-700 border-orange-500/20',
    icon: AlertTriangle,
    iconColor: 'text-orange-600',
  },
  warning: {
    label: 'Advertencia',
    color: 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20',
    icon: AlertCircle,
    iconColor: 'text-yellow-600',
  },
};

export default function SystemHealth() {
  const [selectedService, setSelectedService] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'all'>('today');

  const { data: healthData, isLoading: healthLoading, error: healthError, refetch: refetchHealth, isRefetching: healthRefetching } = useSystemHealth();
  const { data: metricsData, isLoading: metricsLoading, error: metricsError } = useSystemMetrics();
  const { data: uptimeData, isLoading: uptimeLoading } = useUptimeStatus();
  const { data: logsData, isLoading: logsLoading, error: logsError, refetch: refetchLogs, isRefetching: logsRefetching } = useErrorLogs(
    100,
    selectedLevel !== 'all' ? selectedLevel : undefined,
    selectedService !== 'all' ? selectedService : undefined
  );

  const isLoading = healthLoading || metricsLoading || uptimeLoading || logsLoading;
  const hasError = healthError || metricsError || logsError;

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} MB`;
    return `${(bytes / 1024).toFixed(1)} GB`;
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 24) {
      return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
    if (hours > 0) return `Hace ${hours}h`;
    if (minutes > 0) return `Hace ${minutes}m`;
    return `Hace ${seconds}s`;
  };

  const logs = logsData?.logs || [];
  const filteredLogs = logs;

  const activeFiltersCount = [
    selectedService !== 'all',
    selectedLevel !== 'all',
  ].filter(Boolean).length;

  const clearFilters = () => {
    setSelectedService('all');
    setSelectedLevel('all');
  };

  if (isLoading && !healthData && !metricsData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-slate-600 font-medium">Cargando estado del sistema...</p>
        </div>
      </div>
    );
  }

  if (hasError && !healthData && !metricsData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 flex items-center justify-center p-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl shadow-red-500/20 p-8 max-w-md w-full border border-red-200/60">
          <div className="flex flex-col items-center text-center">
            <div className="p-4 bg-red-500/10 rounded-2xl mb-4">
              <AlertTriangle className="w-12 h-12 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">Error al cargar datos</h3>
            <p className="text-slate-600 mb-6">No se pudo conectar con el sistema de monitoreo</p>
            <button
              onClick={() => {
                refetchHealth();
                refetchLogs();
              }}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium shadow-lg shadow-blue-500/30"
            >
              <RefreshCw className="w-4 h-4" />
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  const overallStatus = healthData?.overall_status || 'unhealthy';
  const overallConfig = HEALTH_STATUS_CONFIG[overallStatus];
  const OverallIcon = overallConfig.icon;

  const services = healthData?.services || {};
  const metrics = metricsData || {};
  const uptime = uptimeData || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              Estado del Sistema
            </h1>
            <p className="text-slate-600">
              Monitoreo de salud, métricas y logs de errores
            </p>
          </div>
          <button
            onClick={() => {
              refetchHealth();
              refetchLogs();
            }}
            disabled={healthRefetching || logsRefetching}
            className="flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm border border-slate-200/60 text-slate-700 rounded-xl hover:bg-slate-50/50 transition-all shadow-lg shadow-blue-500/10 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${(healthRefetching || logsRefetching) ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>

        {/* Overall Health Status */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl shadow-blue-500/20 p-8 border border-slate-200/60">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className={`p-6 ${overallConfig.iconBg} rounded-2xl`}>
                <OverallIcon className={`w-12 h-12 ${overallConfig.iconColor}`} />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-1">
                  Estado General
                </p>
                <h2 className="text-3xl font-bold text-slate-900 mb-2">
                  {overallConfig.label}
                </h2>
                <p className="text-slate-600">
                  Todos los servicios funcionando correctamente
                </p>
              </div>
            </div>
            {uptimeData && (
              <div className="text-right">
                <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-1">
                  Uptime
                </p>
                <p className="text-3xl font-bold text-slate-900">
                  {formatUptime(uptime.uptime_seconds || 0)}
                </p>
                <p className="text-sm text-slate-600 mt-1">
                  Desde {new Date(uptime.started_at || '').toLocaleString('es-ES', {
                    day: '2-digit',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Services Health Grid */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-4">Servicios</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(services).map(([key, service]: [string, HealthCheck]) => {
              const config = SERVICE_CONFIG[key as keyof typeof SERVICE_CONFIG];
              const statusConfig = HEALTH_STATUS_CONFIG[service.status];
              const ServiceIcon = config?.icon || Server;
              const StatusIcon = statusConfig.icon;

              return (
                <div
                  key={key}
                  className="bg-white border border-slate-200/60 rounded-xl p-6 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 bg-${config?.color || 'blue'}-500/10 rounded-xl`}>
                      <ServiceIcon className={`w-6 h-6 text-${config?.color || 'blue'}-600`} />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${statusConfig.dotColor} animate-pulse`}></span>
                      <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${statusConfig.color}`}>
                        {statusConfig.label}
                      </span>
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {config?.label || service.service}
                  </h3>
                  {service.message && (
                    <p className="text-sm text-slate-600">{service.message}</p>
                  )}
                  {service.error && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-xs text-red-700 font-mono">{service.error}</p>
                    </div>
                  )}
                  <p className="text-xs text-slate-500 mt-3">
                    {formatTimestamp(service.timestamp)}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* System Metrics */}
        {metricsData && (
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-4">Métricas del Sistema</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* CPU Usage */}
              <div className="bg-white border border-slate-200/60 rounded-xl p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-purple-500/10 rounded-xl">
                    <Cpu className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                      CPU
                    </p>
                    <p className="text-2xl font-bold text-slate-900">
                      {metrics.cpu_usage_percent?.toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(metrics.cpu_usage_percent || 0, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Memory Usage */}
              <div className="bg-white border border-slate-200/60 rounded-xl p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-blue-500/10 rounded-xl">
                    <HardDrive className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                      Memoria
                    </p>
                    <p className="text-2xl font-bold text-slate-900">
                      {formatBytes(metrics.memory_usage_mb || 0)}
                    </p>
                  </div>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(metrics.memory_percent || 0, 100)}%` }}
                  ></div>
                </div>
                <p className="text-xs text-slate-600 mt-2">
                  {metrics.memory_percent?.toFixed(1)}% de {formatBytes(metrics.memory_total_mb || 0)}
                </p>
              </div>

              {/* Requests Per Minute */}
              <div className="bg-white border border-slate-200/60 rounded-xl p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-green-500/10 rounded-xl">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                      Requests/min
                    </p>
                    <p className="text-2xl font-bold text-slate-900">
                      {metrics.requests_per_minute || 0}
                    </p>
                    <p className="text-xs text-slate-600 mt-1">
                      {metrics.avg_response_time_ms?.toFixed(0)}ms promedio
                    </p>
                  </div>
                </div>
              </div>

              {/* WebSocket Connections */}
              <div className="bg-white border border-slate-200/60 rounded-xl p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-orange-500/10 rounded-xl">
                    <Zap className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                      WebSocket
                    </p>
                    <p className="text-2xl font-bold text-slate-900">
                      {metrics.active_websocket_connections || 0}
                    </p>
                    <p className="text-xs text-slate-600 mt-1">
                      Cache: {metrics.cache_hit_rate_percent?.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Logs */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-slate-900">Logs de Errores</h2>
            <div className="flex items-center gap-3">
              {activeFiltersCount > 0 && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg">
                  <span className="text-sm font-medium text-blue-700">
                    {activeFiltersCount} filtro{activeFiltersCount > 1 ? 's' : ''} activo{activeFiltersCount > 1 ? 's' : ''}
                  </span>
                  <button
                    onClick={clearFilters}
                    className="text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg shadow-blue-500/10 p-6 border border-slate-200/60 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Service Filter */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Servicio
                </label>
                <select
                  value={selectedService}
                  onChange={(e) => setSelectedService(e.target.value)}
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all bg-white"
                >
                  <option value="all">Todos los servicios</option>
                  {Object.entries(SERVICE_CONFIG).map(([key, config]) => (
                    <option key={key} value={key}>
                      {config.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Level Filter */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Nivel
                </label>
                <select
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all bg-white"
                >
                  <option value="all">Todos los niveles</option>
                  <option value="critical">Crítico</option>
                  <option value="error">Error</option>
                  <option value="warning">Advertencia</option>
                </select>
              </div>
            </div>
          </div>

          {/* Logs List */}
          {logsLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
              <p className="text-slate-600">Cargando logs...</p>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg shadow-green-500/10 p-12 text-center border border-slate-200/60">
              <div className="inline-block p-4 bg-green-500/10 rounded-2xl mb-4">
                <CheckCircle className="w-12 h-12 text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                ¡Sin errores!
              </h3>
              <p className="text-slate-600">
                No hay errores registrados en el sistema
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredLogs.map((log) => {
                const levelConfig = ERROR_LEVEL_CONFIG[log.level as keyof typeof ERROR_LEVEL_CONFIG];
                const serviceConfig = SERVICE_CONFIG[log.service as keyof typeof SERVICE_CONFIG];
                const LevelIcon = levelConfig?.icon || AlertTriangle;
                const ServiceIcon = serviceConfig?.icon || Server;

                return (
                  <div
                    key={log.id}
                    className="bg-white border border-slate-200/60 rounded-xl p-6 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start gap-4">
                      <div className={`p-3 ${levelConfig?.iconColor === 'text-red-600' ? 'bg-red-500/10' : levelConfig?.iconColor === 'text-orange-600' ? 'bg-orange-500/10' : 'bg-yellow-500/10'} rounded-xl`}>
                        <LevelIcon className={`w-6 h-6 ${levelConfig?.iconColor}`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${levelConfig?.color}`}>
                            {levelConfig?.label}
                          </span>
                          <span className="px-3 py-1 rounded-lg text-xs font-semibold bg-slate-500/10 text-slate-700">
                            <ServiceIcon className="w-3 h-3 inline mr-1" />
                            {serviceConfig?.label || log.service}
                          </span>
                          <span className="text-xs text-slate-500">
                            {formatTimestamp(log.timestamp)}
                          </span>
                        </div>
                        <p className="text-slate-900 font-medium mb-3">{log.message}</p>
                        {log.stack_trace && (
                          <details className="mt-3">
                            <summary className="cursor-pointer text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors mb-2">
                              Ver stack trace
                            </summary>
                            <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
                              <pre className="text-xs text-green-400 font-mono">{log.stack_trace}</pre>
                            </div>
                          </details>
                        )}
                        {log.metadata && Object.keys(log.metadata).length > 0 && (
                          <div className="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-lg">
                            <p className="text-xs font-semibold text-slate-600 mb-2">Metadata:</p>
                            <div className="space-y-1">
                              {Object.entries(log.metadata).map(([key, value]) => (
                                <div key={key} className="flex gap-2 text-xs">
                                  <span className="font-semibold text-slate-700">{key}:</span>
                                  <span className="text-slate-600">{JSON.stringify(value)}</span>
                                </div>
                              ))}
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

          {/* Results Footer */}
          {filteredLogs.length > 0 && (
            <div className="mt-6 text-center">
              <p className="text-sm text-slate-600">
                Mostrando <span className="font-semibold text-slate-900">{filteredLogs.length}</span> de{' '}
                <span className="font-semibold text-slate-900">{logsData?.total || 0}</span> errores
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Actualización automática cada 15 segundos
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
