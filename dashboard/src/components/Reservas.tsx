import { Check, X, Edit3 } from 'lucide-react';
import { useState } from 'react';
import { Search, Phone, Calendar, Users } from 'lucide-react';
import {
  useReservations,
  useUpdateReservationStatus,
  useCreateReservation,
  useUpdateReservation,
  Reservation,
  ReservationStatus,
} from '../hooks/useReservations';
import { useAuth } from '../contexts/AuthContext';
import ReservaDetalle from './ReservaDetalle';
import ReservaForm from './ReservaForm';

export default function Reservas() {
  const { token } = useAuth();
  const [filtroEstado, setFiltroEstado] = useState<string>('todos');
  const [busqueda, setBusqueda] = useState('');
  const [selectedReserva, setSelectedReserva] = useState<Reservation | null>(null);
  const [isDetalleOpen, setIsDetalleOpen] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedReservaForEdit, setSelectedReservaForEdit] = useState<Reservation | null>(null);

  // Fetch reservations with filters
  const { data, isLoading, error } = useReservations(
    filtroEstado !== 'todos' ? { estado: filtroEstado as ReservationStatus } : undefined,
    0,
    100,
    token
  );
  const updateStatusMutation = useUpdateReservationStatus();
  const createMutation = useCreateReservation();
  const updateMutation = useUpdateReservation();

  // Filter by search term (client-side filtering for name/phone)
  const reservasFiltradas = data?.reservations.filter(reserva => {
    const matchBusqueda = reserva.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                         reserva.telefono.includes(busqueda);
    return matchBusqueda;
  }) || [];

  // Handlers
  const handleRowClick = (reserva: Reservation) => {
    setSelectedReserva(reserva);
    setIsDetalleOpen(true);
  };

  const handleConfirm = async (reserva: Reservation) => {
    if (reserva.estado === 'Confirmada') return;
    try {
      await updateStatusMutation.mutateAsync({ id: reserva.id, estado: 'Confirmada' });
      setIsDetalleOpen(false);
    } catch (error) {
      console.error('Error confirming reservation:', error);
    }
  };

  const handleSeat = async (reserva: Reservation) => {
    if (reserva.estado === 'Sentada') return;
    try {
      await updateStatusMutation.mutateAsync({ id: reserva.id, estado: 'Sentada' });
      setIsDetalleOpen(false);
    } catch (error) {
      console.error('Error seating reservation:', error);
    }
  };

  const handleComplete = async (reserva: Reservation) => {
    if (reserva.estado === 'Completada') return;
    try {
      await updateStatusMutation.mutateAsync({ id: reserva.id, estado: 'Completada' });
      setIsDetalleOpen(false);
    } catch (error) {
      console.error('Error completing reservation:', error);
    }
  };

  const handleCancel = async (reserva: Reservation) => {
    if (reserva.estado === 'Cancelada') return;
    try {
      await updateStatusMutation.mutateAsync({ id: reserva.id, estado: 'Cancelada' });
      setIsDetalleOpen(false);
    } catch (error) {
      console.error('Error cancelling reservation:', error);
    }
  };

  const handleCreateClick = () => {
    setFormMode('create');
    setSelectedReservaForEdit(null);
    setIsFormOpen(true);
  };

  const handleEditClick = (reserva: Reservation) => {
    setFormMode('edit');
    setSelectedReservaForEdit(reserva);
    setIsFormOpen(true);
  };

  const handleFormSubmit = async (data: Partial<Reservation>) => {
    try {
      if (formMode === 'create') {
        await createMutation.mutateAsync(data);
      } else if (selectedReservaForEdit) {
        await updateMutation.mutateAsync({ id: selectedReservaForEdit.id, data });
      }
      setIsFormOpen(false);
    } catch (error) {
      console.error('Form submission error:', error);
      throw error; // Re-throw to keep form open on error
    }
  };

  return (
    <div className="space-y-6">
      {/* Filtros y Búsqueda */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex flex-col md:flex-row gap-4 justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por nombre o teléfono..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          <div className="flex gap-2">
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="todos">Todos los estados</option>
              <option value="pendiente">Pendiente</option>
              <option value="confirmada">Confirmada</option>
              <option value="cancelada">Cancelada</option>
              <option value="completada">Completada</option>
            </select>
            
            <button 
              onClick={handleCreateClick}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Calendar size={18} />
              Nueva Reserva
            </button>
          </div>
        </div>
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
          Error al cargar reservas: {error.message}
        </div>
      )}

      {/* Tabla de Reservas */}
      {!isLoading && !error && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Cliente</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Fecha y Hora</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Personas</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Mesa</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Estado</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Origen</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {reservasFiltradas.map((reserva) => (
              <tr 
                key={reserva.id} 
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => handleRowClick(reserva)}
              >
                <td className="px-6 py-4">
                  <div>
                    <p className="font-medium text-gray-900">{reserva.nombre}</p>
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                      <Phone size={14} />
                      {reserva.telefono}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-gray-400" />
                    <span>{reserva.fecha} • {reserva.hora}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Users size={16} className="text-gray-400" />
                    {reserva.pax}
                  </div>
                </td>
                <td className="px-6 py-4">
                  {reserva.mesa ? (
                    <span className="px-3 py-1 bg-gray-100 rounded-full text-sm">{reserva.mesa}</span>
                  ) : (
                    <span className="text-gray-400">Sin asignar</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    reserva.estado === 'Confirmada' ? 'bg-green-100 text-green-700' :
                    reserva.estado === 'Pendiente' ? 'bg-yellow-100 text-yellow-700' :
                    reserva.estado === 'Cancelada' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {reserva.estado}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    reserva.canal === 'VAPI' ? 'bg-purple-100 text-purple-700' :
                    reserva.canal === 'WhatsApp' ? 'bg-green-100 text-green-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {reserva.canal}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditClick(reserva);
                      }}
                      className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                      title="Editar"
                      disabled={updateStatusMutation.isPending || createMutation.isPending || updateMutation.isPending}
                    >
                      <Edit3 size={18} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleConfirm(reserva);
                      }}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Confirmar"
                      disabled={reserva.estado === 'Confirmada' || updateStatusMutation.isPending}
                    >
                      <Check size={18} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCancel(reserva);
                      }}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Cancelar"
                      disabled={reserva.estado === 'Cancelada' || updateStatusMutation.isPending}
                    >
                      <X size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {reservasFiltradas.length === 0 && (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                  No se encontraron reservas con los filtros actuales
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      )}

      {/* Reservation Form Modal */}
      <ReservaForm
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={selectedReservaForEdit}
        mode={formMode}
      />

      {/* Reservation Detail Modal */}
      <ReservaDetalle
        isOpen={isDetalleOpen}
        onClose={() => setIsDetalleOpen(false)}
        reserva={selectedReserva}
        onConfirm={handleConfirm}
        onSeat={handleSeat}
        onComplete={handleComplete}
        onCancel={handleCancel}
        isUpdating={updateStatusMutation.isPending}
      />
    </div>
  );
}
