import { X, MapPin, Users, Calendar, Clock, Phone, User, FileText, CheckCircle } from 'lucide-react';
import { Reservation, ReservationStatus } from '../hooks/useReservations';

interface ReservaDetalleProps {
  isOpen: boolean;
  onClose: () => void;
  reserva: Reservation | null;
  onConfirm?: (reserva: Reservation) => void;
  onSeat?: (reserva: Reservation) => void;
  onComplete?: (reserva: Reservation) => void;
  onCancel?: (reserva: Reservation) => void;
  isUpdating?: boolean;
}

export default function ReservaDetalle({
  isOpen,
  onClose,
  reserva,
  onConfirm,
  onSeat,
  onComplete,
  onCancel,
  isUpdating = false,
}: ReservaDetalleProps) {
  if (!isOpen || !reserva) return null;

  const getEstadoColor = (estado: ReservationStatus) => {
    switch (estado) {
      case 'Confirmada':
        return 'bg-green-100 text-green-700 border-green-300';
      case 'Pendiente':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'Cancelada':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'Sentada':
        return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'Completada':
        return 'bg-gray-100 text-gray-700 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const canConfirm = reserva.estado === 'Pendiente';
  const canSeat = reserva.estado === 'Confirmada';
  const canComplete = reserva.estado === 'Sentada';
  const canCancel = !['Cancelada', 'Completada'].includes(reserva.estado);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 transition-opacity"
        onClick={() => !isUpdating && onClose()}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Detalle de Reserva</h2>
          <button
            type="button"
            onClick={onClose}
            disabled={isUpdating}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X size={24} className="text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Estado Badge */}
          <div className="flex items-center justify-between">
            <span className={`px-4 py-2 rounded-full text-sm font-medium border-2 ${getEstadoColor(reserva.estado)}`}>
              {reserva.estado}
            </span>
            <span className="text-sm text-gray-500">
              ID: {reserva.id.substring(0, 8)}...
            </span>
          </div>

          {/* Cliente Info */}
          <div className="bg-gray-50 rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Información del Cliente</h3>

            <div className="flex items-center gap-3">
              <div className="p-2 bg-white rounded-lg">
                <User size={20} className="text-gray-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Nombre</p>
                <p className="font-medium text-gray-900">{reserva.nombre}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 bg-white rounded-lg">
                <Phone size={20} className="text-gray-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Teléfono</p>
                <p className="font-medium text-gray-900">{reserva.telefono}</p>
              </div>
            </div>
          </div>

          {/* Reserva Info */}
          <div className="bg-gray-50 rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Detalles de la Reserva</h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  <Calendar size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Fecha</p>
                  <p className="font-medium text-gray-900">{reserva.fecha}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  <Clock size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Hora</p>
                  <p className="font-medium text-gray-900">{reserva.hora}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  <Users size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Personas</p>
                  <p className="font-medium text-gray-900">{reserva.pax}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg">
                  <MapPin size={20} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Mesa</p>
                  <p className="font-medium text-gray-900">
                    {reserva.mesa || 'Sin asignar'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Canal y Fecha de Creación */}
          <div className="flex items-center justify-between text-sm">
            <div>
              <span className="text-gray-500">Canal: </span>
              <span className={`px-3 py-1 rounded-full font-medium ${
                reserva.canal === 'VAPI' ? 'bg-purple-100 text-purple-700' :
                reserva.canal === 'WhatsApp' ? 'bg-green-100 text-green-700' :
                'bg-blue-100 text-blue-700'
              }`}>
                {reserva.canal}
              </span>
            </div>
            <div className="text-gray-500">
              Creada: {new Date(reserva.creado).toLocaleString('es-ES')}
            </div>
          </div>

          {/* Notas */}
          {reserva.notas && (
            <div className="bg-blue-50 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <FileText size={20} className="text-blue-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">Notas</p>
                  <p className="text-sm text-blue-700">{reserva.notas}</p>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
            {canConfirm && onConfirm && (
              <button
                onClick={() => onConfirm(reserva)}
                disabled={isUpdating}
                className="flex-1 min-w-[140px] flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <CheckCircle size={18} />
                <span>Confirmar</span>
              </button>
            )}

            {canSeat && onSeat && (
              <button
                onClick={() => onSeat(reserva)}
                disabled={isUpdating}
                className="flex-1 min-w-[140px] flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Users size={18} />
                <span>Sentar</span>
              </button>
            )}

            {canComplete && onComplete && (
              <button
                onClick={() => onComplete(reserva)}
                disabled={isUpdating}
                className="flex-1 min-w-[140px] flex items-center justify-center gap-2 px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <CheckCircle size={18} />
                <span>Completar</span>
              </button>
            )}

            {canCancel && onCancel && (
              <button
                onClick={() => onCancel(reserva)}
                disabled={isUpdating}
                className="flex-1 min-w-[140px] flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <X size={18} />
                <span>Cancelar</span>
              </button>
            )}

            <button
              onClick={onClose}
              disabled={isUpdating}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
