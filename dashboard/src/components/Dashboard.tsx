import { TrendingUp, Users, Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { METRICAS_EJEMPLO, RESERVAS_EJEMPLO } from '../types';

export default function Dashboard() {
  const metricas = METRICAS_EJEMPLO;
  const reservasRecientes = RESERVAS_EJEMPLO.slice(0, 5);

  const statCards = [
    { 
      label: 'Reservas Hoy', 
      value: metricas.totalReservasHoy, 
      icon: Users, 
      color: 'bg-blue-500',
      trend: '+12% vs ayer'
    },
    { 
      label: 'Confirmadas', 
      value: metricas.reservasConfirmadas, 
      icon: CheckCircle, 
      color: 'bg-green-500',
      trend: '67% del total'
    },
    { 
      label: 'Pendientes', 
      value: metricas.reservasPendientes, 
      icon: Clock, 
      color: 'bg-yellow-500',
      trend: 'Requieren acción'
    },
    { 
      label: 'Ocupación', 
      value: `${metricas.ocupacion}%`, 
      icon: TrendingUp, 
      color: 'bg-primary-500',
      trend: 'Capacidad actual'
    },
  ];

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <p className="text-sm text-gray-500 mt-2">{stat.trend}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
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
        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-800">Reservas Recientes</h3>
          </div>
          <div className="divide-y">
            {reservasRecientes.map((reserva) => (
              <div key={reserva.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{reserva.nombre}</p>
                    <p className="text-sm text-gray-500">
                      {reserva.fecha} • {reserva.hora} • {reserva.pax} personas
                    </p>
                    {reserva.mesa && (
                      <p className="text-sm text-primary-600">{reserva.mesa}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      reserva.estado === 'Confirmada' ? 'bg-green-100 text-green-700' :
                      reserva.estado === 'Pendiente' ? 'bg-yellow-100 text-yellow-700' :
                      reserva.estado === 'Cancelada' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {reserva.estado}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 border-t">
            <button className="text-primary-600 hover:text-primary-700 font-medium">
              Ver todas las reservas →
            </button>
          </div>
        </div>

        {/* Alertas y Notificaciones */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-800">Alertas</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-start gap-4 p-4 bg-yellow-50 rounded-lg">
              <AlertCircle className="text-yellow-600 mt-0.5" size={20} />
              <div>
                <p className="font-medium text-yellow-800">Reservas pendientes de confirmación</p>
                <p className="text-sm text-yellow-700 mt-1">Tienes 3 reservas pendientes que requieren confirmación vía WhatsApp.</p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-blue-50 rounded-lg">
              <TrendingUp className="text-blue-600 mt-0.5" size={20} />
              <div>
                <p className="font-medium text-blue-800">Alta ocupación este fin de semana</p>
                <p className="text-sm text-blue-700 mt-1">El sábado tienes 85% de ocupación. Considera activar lista de espera.</p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-green-50 rounded-lg">
              <CheckCircle className="text-green-600 mt-0.5" size={20} />
              <div>
                <p className="font-medium text-green-800">Sistema funcionando correctamente</p>
                <p className="text-sm text-green-700 mt-1">Todos los servicios están operativos. Último check: hace 5 minutos.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
