import { Check, X, Edit3, Download, Filter, CalendarDays, AlertCircle, Plus, ArrowUpRight } from 'lucide-react';
import { useState, useMemo } from 'react';
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
import { format, startOfDay, endOfDay, startOfWeek, endOfWeek, startOfMonth, endOfMonth } from 'date-fns';
import { es } from 'date-fns/locale';

type DateFilter = 'todos' | 'hoy' | 'semana' | 'mes';

// Status badge styles using the new design system
function getStatusBadge(estado: Reservation['estado']): string {
  switch (estado) {
    case 'Confirmada':
      return 'badge-success';
    case 'Pendiente':
      return 'badge-warning';
    case 'Cancelada':
      return 'badge-error';
    case 'Completada':
      return 'badge-info';
    case 'Sentada':
      return 'bg-purple-50 text-purple-700 border-purple-200';
    default:
      return 'bg-secondary-100 text-secondary-700 border-secondary-200';
  }
}

// Channel badge styles
function getChannelBadge(canal: string): string {
  switch (canal) {
    case 'VAPI':
      return 'bg-violet-50 text-violet-700 border-violet-200';
    case 'WhatsApp':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    default:
      return 'bg-blue-50 text-blue-700 border-blue-200';
  }
}

export default function Reservas() {
  const { token } = useAuth();
  const [filtroEstado, setFiltroEstado] = useState<string>('todos');
  const [filtroFecha, setFiltroFecha] = useState<DateFilter>('hoy');
  const [busqueda, setBusqueda] = useState('');
  const [selectedReserva, setSelectedReserva] = useState<Reservation | null>(null);
  const [isDetalleOpen, setIsDetalleOpen] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedReservaForEdit, setSelectedReservaForEdit] = useState<Reservation | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

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

  // Filter by search term AND date (client-side filtering)
  const reservasFiltradas = useMemo(() => {
    if (!data?.reservations) return [];

    return data.reservations.filter(reserva => {
      // Search filter
      const matchBusqueda = reserva.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                           reserva.telefono.includes(busqueda);
      if (!matchBusqueda) return false;

      // Date filter
      if (filtroFecha === 'todos') return true;

      const reservaDate = new Date(reserva.fecha);
      const today = new Date();

      if (filtroFecha === 'hoy') {
        return reservaDate >= startOfDay(today) && reservaDate <= endOfDay(today);
      } else if (filtroFecha === 'semana') {
        return reservaDate >= startOfWeek(today, { locale: es }) && 
               reservaDate <= endOfWeek(today, { locale: es });
      } else if (filtroFecha === 'mes') {
        return reservaDate >= startOfMonth(today) && reservaDate <= endOfMonth(today);
      }

      return true;
    });
  }, [data?.reservations, busqueda, filtroFecha]);

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
        setToast({ message: 'Reserva creada exitosamente', type: 'success' });
      } else if (selectedReservaForEdit) {
        await updateMutation.mutateAsync({ id: selectedReservaForEdit.id, data });
        setToast({ message: 'Reserva actualizada exitosamente', type: 'success' });
      }
      setIsFormOpen(false);
      setTimeout(() => setToast(null), 3000);
    } catch (error) {
      console.error('Form submission error:', error);
      setToast({ message: 'Error al guardar la reserva', type: 'error' });
      setTimeout(() => setToast(null), 3000);
      throw error; // Re-throw to keep form open on error
    }
  };

  const handleExportCSV = () => {
    if (!reservasFiltradas.length) {
      setToast({ message: 'No hay reservas para exportar', type: 'error' });
      setTimeout(() => setToast(null), 3000);
      return;
    }

    const headers = ['ID', 'Nombre', 'Telefono', 'Fecha', 'Hora', 'Personas', 'Mesa', 'Estado', 'Canal', 'Notas'];
    const rows = reservasFiltradas.map(r => [
      r.id,
      r.nombre,
      r.telefono,
      r.fecha,
      r.hora,
      r.pax.toString(),
      r.mesa || 'Sin asignar',
      r.estado,
      r.canal,
      r.notas || ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `reservas_${format(new Date(), 'yyyy-MM-dd_HH-mm', { locale: es })}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setToast({ message: `${reservasFiltradas.length} reservas exportadas`, type: 'success' });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Filters Bar */}
      <div className="premium-card p-4">
        <div className="flex flex-col lg:flex-row gap-4 justify-between">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-secondary-400" size={18} />
            <input
              type="text"
              placeholder="Buscar por nombre o telefono..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="input-search"
            />
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            {/* Date Filter */}
            <div className="flex bg-secondary-100 rounded-xl p-1">
              {[
                { key: 'todos', label: 'Todos' },
                { key: 'hoy', label: 'Hoy' },
                { key: 'semana', label: 'Semana' },
                { key: 'mes', label: 'Mes' },
              ].map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setFiltroFecha(key as DateFilter)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    filtroFecha === key
                      ? 'bg-white text-primary-600 shadow-sm'
                      : 'text-secondary-600 hover:text-secondary-800'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* Status Filter */}
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="input-field w-auto min-w-[160px]"
            >
              <option value="todos">Todos los estados</option>
              <option value="pendiente">Pendiente</option>
              <option value="confirmada">Confirmada</option>
              <option value="cancelada">Cancelada</option>
              <option value="completada">Completada</option>
            </select>

            {/* Export Button */}
            <button
              onClick={handleExportCSV}
              disabled={!reservasFiltradas.length}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download size={18} />
              <span className="hidden sm:inline">Exportar</span>
            </button>
            
            {/* Create Button */}
            <button 
              onClick={handleCreateClick}
              className="btn-primary"
            >
              <Plus size={18} />
              <span>Nueva Reserva</span>
            </button>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      {!isLoading && !error && (
        <div className="flex items-center justify-between text-sm">
          <p className="text-secondary-500">
            <span className="font-semibold text-secondary-900">{reservasFiltradas.length}</span> reservas encontradas
          </p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="premium-card p-12">
          <div className="flex flex-col items-center justify-center">
            <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
            <p className="text-secondary-500 font-medium">Cargando reservas...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="premium-card p-8">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-error-50 flex items-center justify-center mb-4">
              <AlertCircle className="text-error-500" size={28} />
            </div>
            <h3 className="text-lg font-bold text-secondary-900 mb-2">Error al cargar</h3>
            <p className="text-secondary-500">{error.message}</p>
          </div>
        </div>
      )}

      {/* Table */}
      {!isLoading && !error && (
        <div className="premium-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Fecha y Hora</th>
                  <th>Personas</th>
                  <th>Mesa</th>
                  <th>Estado</th>
                  <th>Origen</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {reservasFiltradas.map((reserva) => (
                  <tr 
                    key={reserva.id} 
                    className="cursor-pointer group"
                    onClick={() => handleRowClick(reserva)}
                  >
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center flex-shrink-0">
                          <span className="text-primary-600 font-bold text-sm">
                            {reserva.nombre.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-semibold text-secondary-900">{reserva.nombre}</p>
                          <div className="flex items-center gap-1.5 text-sm text-secondary-500">
                            <Phone size={12} />
                            {reserva.telefono}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <Calendar size={16} className="text-secondary-400" />
                        <div>
                          <p className="font-medium text-secondary-900">{reserva.fecha}</p>
                          <p className="text-sm text-secondary-500">{reserva.hora}</p>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <Users size={16} className="text-secondary-400" />
                        <span className="font-medium text-secondary-900">{reserva.pax}</span>
                      </div>
                    </td>
                    <td>
                      {reserva.mesa ? (
                        <span className="px-3 py-1.5 bg-secondary-100 rounded-lg text-sm font-medium text-secondary-700">
                          {reserva.mesa}
                        </span>
                      ) : (
                        <span className="text-secondary-400 text-sm">Sin asignar</span>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${getStatusBadge(reserva.estado)}`}>
                        {reserva.estado}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getChannelBadge(reserva.canal)}`}>
                        {reserva.canal}
                      </span>
                    </td>
                    <td>
                      <div className="flex gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditClick(reserva);
                          }}
                          className="p-2 text-secondary-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                          title="Editar"
                          disabled={updateStatusMutation.isPending || createMutation.isPending || updateMutation.isPending}
                        >
                          <Edit3 size={16} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleConfirm(reserva);
                          }}
                          className="p-2 text-secondary-400 hover:text-success-600 hover:bg-success-50 rounded-lg transition-colors disabled:opacity-50"
                          title="Confirmar"
                          disabled={reserva.estado === 'Confirmada' || updateStatusMutation.isPending}
                        >
                          <Check size={16} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCancel(reserva);
                          }}
                          className="p-2 text-secondary-400 hover:text-error-600 hover:bg-error-50 rounded-lg transition-colors disabled:opacity-50"
                          title="Cancelar"
                          disabled={reserva.estado === 'Cancelada' || updateStatusMutation.isPending}
                        >
                          <X size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {reservasFiltradas.length === 0 && (
                  <tr>
                    <td colSpan={7} className="py-12">
                      <div className="text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-secondary-50 flex items-center justify-center">
                          <CalendarDays className="text-secondary-400" size={28} />
                        </div>
                        <p className="text-secondary-500 font-medium">No se encontraron reservas</p>
                        <p className="text-sm text-secondary-400 mt-1">Prueba con otros filtros</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modals */}
      <ReservaForm
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={selectedReservaForEdit}
        mode={formMode}
      />

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

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 animate-fade-in-up">
          <div className={`toast ${toast.type === 'success' ? 'toast-success' : 'toast-error'}`}>
            {toast.type === 'success' ? (
              <Check size={18} className="flex-shrink-0" />
            ) : (
              <AlertCircle size={18} className="flex-shrink-0" />
            )}
            <span className="font-medium">{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  );
}
