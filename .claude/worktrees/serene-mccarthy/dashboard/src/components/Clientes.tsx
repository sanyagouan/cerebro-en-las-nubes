import { useState, useMemo } from 'react';
import {
  User,
  Phone,
  Mail,
  Calendar,
  TrendingUp,
  Download,
  Search,
  Filter,
  X,
  Plus,
  Star,
  AlertCircle,
  CheckCircle,
  XCircle,
  MapPin,
  Users,
  Clock,
  FileText,
  Trash2,
} from 'lucide-react';
import {
  useCustomers,
  useCustomer,
  useCustomerReservations,
  useCustomerPreferences,
  useCustomerNotes,
  useAddCustomerPreference,
  useDeleteCustomerPreference,
  useAddCustomerNote,
  useDeleteCustomerNote,
  useToggleNoteImportance,
  useUpdateCustomer,
  useUpdateCustomerTier,
  useExportCustomers,
  Customer,
  CustomerTier,
  CustomerPreferenceType,
  CustomerSearchFilters,
} from '../hooks/useClientes';

// Toast notification system
interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

let toastId = 0;

// Cliente Detail Modal
interface ClienteDetalleModalProps {
  isOpen: boolean;
  onClose: () => void;
  clienteId: string | null;
  onToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

function ClienteDetalleModal({ isOpen, onClose, clienteId, onToast }: ClienteDetalleModalProps) {
  const { data: cliente, isLoading: loadingCliente } = useCustomer(clienteId || '');
  const { data: reservations = [], isLoading: loadingReservations } = useCustomerReservations(clienteId || '');
  const { data: preferences = [], isLoading: loadingPreferences } = useCustomerPreferences(clienteId || '');
  const { data: notes = [], isLoading: loadingNotes } = useCustomerNotes(clienteId || '');

  const addPreferenceMutation = useAddCustomerPreference();
  const deletePreferenceMutation = useDeleteCustomerPreference();
  const addNoteMutation = useAddCustomerNote();
  const deleteNoteMutation = useDeleteCustomerNote();
  const toggleNoteImportanceMutation = useToggleNoteImportance();
  const updateTierMutation = useUpdateCustomerTier();

  const [showAddPreference, setShowAddPreference] = useState(false);
  const [newPreferenceType, setNewPreferenceType] = useState<CustomerPreferenceType>('zona_favorita');
  const [newPreferenceValue, setNewPreferenceValue] = useState('');

  const [showAddNote, setShowAddNote] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [newNoteImportant, setNewNoteImportant] = useState(false);

  if (!isOpen || !clienteId) return null;

  const handleAddPreference = async () => {
    if (!newPreferenceValue.trim()) {
      onToast('El valor de la preferencia es requerido', 'error');
      return;
    }

    try {
      await addPreferenceMutation.mutateAsync({
        customer_id: clienteId,
        tipo: newPreferenceType,
        valor: newPreferenceValue,
      });
      onToast('Preferencia agregada exitosamente', 'success');
      setShowAddPreference(false);
      setNewPreferenceValue('');
    } catch (error) {
      onToast(`Error al agregar preferencia: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleDeletePreference = async (preferenceId: string) => {
    try {
      await deletePreferenceMutation.mutateAsync({ customer_id: clienteId, preference_id: preferenceId });
      onToast('Preferencia eliminada', 'success');
    } catch (error) {
      onToast(`Error al eliminar preferencia: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleAddNote = async () => {
    if (!newNoteContent.trim()) {
      onToast('El contenido de la nota es requerido', 'error');
      return;
    }

    try {
      await addNoteMutation.mutateAsync({
        customer_id: clienteId,
        contenido: newNoteContent,
        is_important: newNoteImportant,
      });
      onToast('Nota agregada exitosamente', 'success');
      setShowAddNote(false);
      setNewNoteContent('');
      setNewNoteImportant(false);
    } catch (error) {
      onToast(`Error al agregar nota: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    try {
      await deleteNoteMutation.mutateAsync({ customer_id: clienteId, note_id: noteId });
      onToast('Nota eliminada', 'success');
    } catch (error) {
      onToast(`Error al eliminar nota: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleToggleNoteImportance = async (noteId: string) => {
    try {
      await toggleNoteImportanceMutation.mutateAsync({ customer_id: clienteId, note_id: noteId });
    } catch (error) {
      onToast(`Error al actualizar nota: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleChangeTier = async (newTier: CustomerTier) => {
    try {
      await updateTierMutation.mutateAsync({ id: clienteId, tier: newTier });
      onToast(`Cliente actualizado a ${newTier}`, 'success');
    } catch (error) {
      onToast(`Error al actualizar tier: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const getTierColor = (tier: CustomerTier) => {
    switch (tier) {
      case 'Premium':
        return 'bg-purple-100 text-purple-700 border-purple-300';
      case 'VIP':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'Frecuente':
        return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'Regular':
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getPreferenceIcon = (tipo: CustomerPreferenceType) => {
    switch (tipo) {
      case 'zona_favorita':
        return MapPin;
      case 'solicitud_especial':
        return Star;
      case 'restriccion_dietetica':
        return AlertCircle;
      case 'ocasion_celebracion':
        return Calendar;
    }
  };

  const getPreferenceLabel = (tipo: CustomerPreferenceType) => {
    switch (tipo) {
      case 'zona_favorita':
        return 'Zona Favorita';
      case 'solicitud_especial':
        return 'Solicitud Especial';
      case 'restriccion_dietetica':
        return 'Restricción Dietética';
      case 'ocasion_celebracion':
        return 'Ocasión de Celebración';
    }
  };

  if (loadingCliente) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="absolute inset-0 bg-black/50" onClick={onClose} />
        <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl mx-4 p-8">
          <div className="flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  if (!cliente) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-5xl mx-4 my-8 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary-100 rounded-full">
                <User size={24} className="text-primary-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{cliente.nombre}</h2>
                <p className="text-sm text-gray-500">Cliente desde {new Date(cliente.primera_reserva).toLocaleDateString('es-ES')}</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <X size={24} className="text-gray-500" />
            </button>
          </div>

          {/* Tier Badge + Change Tier */}
          <div className="flex items-center gap-3 mt-4">
            <span className={`px-4 py-2 rounded-full text-sm font-medium border-2 ${getTierColor(cliente.tier)}`}>
              {cliente.tier}
            </span>
            <select
              value={cliente.tier}
              onChange={(e) => handleChangeTier(e.target.value as CustomerTier)}
              className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="Regular">Regular</option>
              <option value="Frecuente">Frecuente</option>
              <option value="VIP">VIP</option>
              <option value="Premium">Premium</option>
            </select>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Información Básica */}
          <div className="bg-gray-50 rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Información de Contacto</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <Phone size={20} className="text-gray-600" />
                <div>
                  <p className="text-sm text-gray-500">Teléfono</p>
                  <p className="font-medium text-gray-900">{cliente.telefono}</p>
                </div>
              </div>
              {cliente.email && (
                <div className="flex items-center gap-3">
                  <Mail size={20} className="text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-500">Email</p>
                    <p className="font-medium text-gray-900">{cliente.email}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Estadísticas */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-xl p-4">
              <p className="text-sm text-blue-600 mb-1">Total Reservas</p>
              <p className="text-2xl font-bold text-blue-700">{cliente.total_reservas}</p>
            </div>
            <div className="bg-green-50 rounded-xl p-4">
              <p className="text-sm text-green-600 mb-1">Completadas</p>
              <p className="text-2xl font-bold text-green-700">{cliente.reservas_completadas}</p>
            </div>
            <div className="bg-red-50 rounded-xl p-4">
              <p className="text-sm text-red-600 mb-1">Canceladas</p>
              <p className="text-2xl font-bold text-red-700">{cliente.reservas_canceladas}</p>
            </div>
            <div className="bg-yellow-50 rounded-xl p-4">
              <p className="text-sm text-yellow-600 mb-1">No Shows</p>
              <p className="text-2xl font-bold text-yellow-700">{cliente.no_shows}</p>
            </div>
          </div>

          {cliente.gasto_promedio && (
            <div className="bg-purple-50 rounded-xl p-4">
              <div className="flex items-center gap-2">
                <TrendingUp size={20} className="text-purple-600" />
                <div>
                  <p className="text-sm text-purple-600">Gasto Promedio</p>
                  <p className="text-xl font-bold text-purple-700">{cliente.gasto_promedio.toFixed(2)} €</p>
                </div>
              </div>
            </div>
          )}

          {/* Historial de Reservas */}
          <div className="bg-gray-50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Historial de Reservas</h3>
            {loadingReservations ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : reservations.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No hay reservas registradas</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-white">
                    <tr>
                      <th className="px-4 py-2 text-left">Fecha</th>
                      <th className="px-4 py-2 text-left">Hora</th>
                      <th className="px-4 py-2 text-left">Personas</th>
                      <th className="px-4 py-2 text-left">Mesa</th>
                      <th className="px-4 py-2 text-left">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reservations.slice(0, 10).map((reserva) => (
                      <tr key={reserva.id} className="border-t border-gray-200">
                        <td className="px-4 py-2">{reserva.fecha}</td>
                        <td className="px-4 py-2">{reserva.hora}</td>
                        <td className="px-4 py-2">{reserva.pax}</td>
                        <td className="px-4 py-2">{reserva.mesa || '-'}</td>
                        <td className="px-4 py-2">
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${
                              reserva.estado === 'Completada'
                                ? 'bg-green-100 text-green-700'
                                : reserva.estado === 'Cancelada'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }`}
                          >
                            {reserva.estado}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Preferencias */}
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Preferencias</h3>
              <button
                onClick={() => setShowAddPreference(!showAddPreference)}
                className="flex items-center gap-2 px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
              >
                <Plus size={16} />
                <span>Agregar</span>
              </button>
            </div>

            {showAddPreference && (
              <div className="bg-white rounded-lg p-4 mb-4 border-2 border-primary-200">
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Preferencia</label>
                    <select
                      value={newPreferenceType}
                      onChange={(e) => setNewPreferenceType(e.target.value as CustomerPreferenceType)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="zona_favorita">Zona Favorita</option>
                      <option value="solicitud_especial">Solicitud Especial</option>
                      <option value="restriccion_dietetica">Restricción Dietética</option>
                      <option value="ocasion_celebracion">Ocasión de Celebración</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Valor</label>
                    <input
                      type="text"
                      value={newPreferenceValue}
                      onChange={(e) => setNewPreferenceValue(e.target.value)}
                      placeholder="Ej: Terraza, Sin gluten, Cumpleaños..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleAddPreference}
                      disabled={addPreferenceMutation.isPending}
                      className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                    >
                      {addPreferenceMutation.isPending ? 'Guardando...' : 'Guardar'}
                    </button>
                    <button
                      onClick={() => {
                        setShowAddPreference(false);
                        setNewPreferenceValue('');
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              </div>
            )}

            {loadingPreferences ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : preferences.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No hay preferencias guardadas</p>
            ) : (
              <div className="space-y-2">
                {preferences.map((pref) => {
                  const Icon = getPreferenceIcon(pref.tipo);
                  return (
                    <div key={pref.id} className="flex items-center justify-between bg-white rounded-lg p-3 border border-gray-200">
                      <div className="flex items-center gap-3">
                        <Icon size={18} className="text-primary-600" />
                        <div>
                          <p className="text-xs text-gray-500">{getPreferenceLabel(pref.tipo)}</p>
                          <p className="font-medium text-gray-900">{pref.valor}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeletePreference(pref.id)}
                        disabled={deletePreferenceMutation.isPending}
                        className="p-1.5 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <Trash2 size={16} className="text-red-600" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Notas del Staff */}
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Notas del Staff</h3>
              <button
                onClick={() => setShowAddNote(!showAddNote)}
                className="flex items-center gap-2 px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
              >
                <Plus size={16} />
                <span>Agregar</span>
              </button>
            </div>

            {showAddNote && (
              <div className="bg-white rounded-lg p-4 mb-4 border-2 border-primary-200">
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Contenido de la Nota</label>
                    <textarea
                      value={newNoteContent}
                      onChange={(e) => setNewNoteContent(e.target.value)}
                      placeholder="Escribe una nota sobre el cliente..."
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 resize-none"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="importante"
                      checked={newNoteImportant}
                      onChange={(e) => setNewNoteImportant(e.target.checked)}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <label htmlFor="importante" className="text-sm text-gray-700">
                      Marcar como importante
                    </label>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleAddNote}
                      disabled={addNoteMutation.isPending}
                      className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                    >
                      {addNoteMutation.isPending ? 'Guardando...' : 'Guardar'}
                    </button>
                    <button
                      onClick={() => {
                        setShowAddNote(false);
                        setNewNoteContent('');
                        setNewNoteImportant(false);
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              </div>
            )}

            {loadingNotes ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : notes.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No hay notas registradas</p>
            ) : (
              <div className="space-y-3">
                {notes.map((note) => (
                  <div
                    key={note.id}
                    className={`bg-white rounded-lg p-4 border-2 ${
                      note.is_important ? 'border-yellow-300 bg-yellow-50/50' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <FileText size={16} className={note.is_important ? 'text-yellow-600' : 'text-gray-600'} />
                          <p className="text-xs text-gray-500">
                            {new Date(note.created_at).toLocaleString('es-ES')} • {note.staff_name}
                          </p>
                          {note.is_important && (
                            <span className="px-2 py-0.5 bg-yellow-200 text-yellow-700 text-xs font-medium rounded">
                              Importante
                            </span>
                          )}
                        </div>
                        <p className="text-gray-900">{note.contenido}</p>
                      </div>
                      <div className="flex gap-1 ml-4">
                        <button
                          onClick={() => handleToggleNoteImportance(note.id)}
                          disabled={toggleNoteImportanceMutation.isPending}
                          className="p-1.5 hover:bg-yellow-50 rounded-lg transition-colors disabled:opacity-50"
                          title={note.is_important ? 'Quitar importancia' : 'Marcar importante'}
                        >
                          <Star size={16} className={note.is_important ? 'text-yellow-600 fill-yellow-600' : 'text-gray-400'} />
                        </button>
                        <button
                          onClick={() => handleDeleteNote(note.id)}
                          disabled={deleteNoteMutation.isPending}
                          className="p-1.5 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                        >
                          <Trash2 size={16} className="text-red-600" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Notas del Cliente (campo texto libre) */}
          {cliente.notas_staff && (
            <div className="bg-blue-50 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <FileText size={20} className="text-blue-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">Notas Adicionales</p>
                  <p className="text-sm text-blue-700">{cliente.notas_staff}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Main Clientes Component
export default function Clientes() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<CustomerSearchFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedClienteId, setSelectedClienteId] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  const pageSize = 20;

  const activeFilters = useMemo(
    () => ({
      ...filters,
      query: searchQuery || undefined,
    }),
    [filters, searchQuery]
  );

  const { data, isLoading, error } = useCustomers(activeFilters, pageSize, currentPage * pageSize);
  const customers = data?.customers || [];
  const total = data?.total || 0;

  const { data: stats } = useCustomers({ tier: 'VIP' }, 1, 0);
  const { data: statsFrequent } = useCustomers({ tier: 'Frecuente' }, 1, 0);
  const { data: statsPremium } = useCustomers({ tier: 'Premium' }, 1, 0);

  const exportMutation = useExportCustomers();

  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    const id = toastId++;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleExport = async () => {
    try {
      await exportMutation.mutateAsync(activeFilters);
      showToast('Clientes exportados exitosamente', 'success');
    } catch (error) {
      showToast(`Error al exportar: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const totalPages = Math.ceil(total / pageSize);
  const hasFilters = searchQuery || filters.tier || filters.min_reservas || filters.has_notes !== undefined;

  return (
    <div className="space-y-6">
      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-3 rounded-lg shadow-lg text-white animate-fade-in ${
              toast.type === 'success' ? 'bg-green-600' : toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gestión de Clientes</h2>
          <p className="text-sm text-gray-600 mt-1">Sistema CRM para clientes recurrentes</p>
        </div>
        <button
          onClick={handleExport}
          disabled={exportMutation.isPending || customers.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download size={20} />
          <span>{exportMutation.isPending ? 'Exportando...' : 'Exportar CSV'}</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Total Clientes</p>
          <p className="text-3xl font-bold text-gray-900">{total}</p>
        </div>
        <div className="bg-purple-50 rounded-xl shadow-sm p-6">
          <p className="text-sm text-purple-600">Premium</p>
          <p className="text-3xl font-bold text-purple-700">{statsPremium?.total || 0}</p>
        </div>
        <div className="bg-yellow-50 rounded-xl shadow-sm p-6">
          <p className="text-sm text-yellow-600">VIP</p>
          <p className="text-3xl font-bold text-yellow-700">{stats?.total || 0}</p>
        </div>
        <div className="bg-blue-50 rounded-xl shadow-sm p-6">
          <p className="text-sm text-blue-600">Frecuentes</p>
          <p className="text-3xl font-bold text-blue-700">{statsFrequent?.total || 0}</p>
        </div>
        <div className="bg-gray-50 rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Regulares</p>
          <p className="text-3xl font-bold text-gray-700">
            {total - (statsPremium?.total || 0) - (stats?.total || 0) - (statsFrequent?.total || 0)}
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(0);
              }}
              placeholder="Buscar por nombre, teléfono o email..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
              hasFilters
                ? 'border-primary-600 text-primary-600 bg-primary-50'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Filter size={20} />
            <span>Filtros</span>
            {hasFilters && <span className="px-2 py-0.5 bg-primary-600 text-white text-xs rounded-full">!</span>}
          </button>
          {hasFilters && (
            <button
              onClick={() => {
                setSearchQuery('');
                setFilters({});
                setCurrentPage(0);
              }}
              className="flex items-center gap-2 px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors"
            >
              <X size={20} />
              <span>Limpiar</span>
            </button>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tier</label>
              <select
                value={filters.tier || ''}
                onChange={(e) => {
                  setFilters({ ...filters, tier: (e.target.value as CustomerTier) || undefined });
                  setCurrentPage(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Todos</option>
                <option value="Premium">Premium</option>
                <option value="VIP">VIP</option>
                <option value="Frecuente">Frecuente</option>
                <option value="Regular">Regular</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mínimo Reservas</label>
              <input
                type="number"
                min="0"
                value={filters.min_reservas || ''}
                onChange={(e) => {
                  setFilters({ ...filters, min_reservas: e.target.value ? parseInt(e.target.value) : undefined });
                  setCurrentPage(0);
                }}
                placeholder="Ej: 5"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Con Notas</label>
              <select
                value={filters.has_notes === undefined ? '' : filters.has_notes ? 'true' : 'false'}
                onChange={(e) => {
                  setFilters({
                    ...filters,
                    has_notes: e.target.value === '' ? undefined : e.target.value === 'true',
                  });
                  setCurrentPage(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Todos</option>
                <option value="true">Con notas</option>
                <option value="false">Sin notas</option>
              </select>
            </div>
          </div>
        )}
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
          Error al cargar clientes: {error.message}
        </div>
      )}

      {/* Customers Table */}
      {!isLoading && !error && (
        <>
          {customers.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <User size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No se encontraron clientes</p>
              {hasFilters && (
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setFilters({});
                    setCurrentPage(0);
                  }}
                  className="mt-4 text-primary-600 hover:text-primary-700 font-medium"
                >
                  Limpiar filtros
                </button>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cliente
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contacto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tier
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Reservas
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Última Visita
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {customers.map((cliente) => {
                      const getTierColor = (tier: CustomerTier) => {
                        switch (tier) {
                          case 'Premium':
                            return 'bg-purple-100 text-purple-700';
                          case 'VIP':
                            return 'bg-yellow-100 text-yellow-700';
                          case 'Frecuente':
                            return 'bg-blue-100 text-blue-700';
                          case 'Regular':
                            return 'bg-gray-100 text-gray-700';
                        }
                      };

                      const tasaCompletado =
                        cliente.total_reservas > 0
                          ? ((cliente.reservas_completadas / cliente.total_reservas) * 100).toFixed(0)
                          : '0';

                      return (
                        <tr key={cliente.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-3">
                              <div className="p-2 bg-primary-100 rounded-full">
                                <User size={18} className="text-primary-600" />
                              </div>
                              <div>
                                <p className="font-medium text-gray-900">{cliente.nombre}</p>
                                <p className="text-sm text-gray-500">
                                  Cliente desde {new Date(cliente.primera_reserva).toLocaleDateString('es-ES')}
                                </p>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2 text-sm text-gray-600">
                                <Phone size={14} />
                                <span>{cliente.telefono}</span>
                              </div>
                              {cliente.email && (
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                  <Mail size={14} />
                                  <span>{cliente.email}</span>
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTierColor(cliente.tier)}`}>
                              {cliente.tier}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="space-y-1">
                              <p className="text-sm font-medium text-gray-900">{cliente.total_reservas} total</p>
                              <div className="flex items-center gap-2 text-xs text-gray-600">
                                <CheckCircle size={12} className="text-green-600" />
                                <span>{tasaCompletado}% completadas</span>
                              </div>
                              {cliente.no_shows > 0 && (
                                <div className="flex items-center gap-2 text-xs text-red-600">
                                  <XCircle size={12} />
                                  <span>{cliente.no_shows} no-shows</span>
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Clock size={14} />
                              <span>
                                {cliente.ultima_reserva
                                  ? new Date(cliente.ultima_reserva).toLocaleDateString('es-ES')
                                  : 'Nunca'}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <button
                              onClick={() => setSelectedClienteId(cliente.id)}
                              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
                            >
                              Ver Detalle
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Mostrando {currentPage * pageSize + 1} - {Math.min((currentPage + 1) * pageSize, total)} de {total}{' '}
                    clientes
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
                      disabled={currentPage === 0}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    <span className="text-sm text-gray-600">
                      Página {currentPage + 1} de {totalPages}
                    </span>
                    <button
                      onClick={() => setCurrentPage((p) => Math.min(totalPages - 1, p + 1))}
                      disabled={currentPage >= totalPages - 1}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Siguiente
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Cliente Detail Modal */}
      <ClienteDetalleModal
        isOpen={!!selectedClienteId}
        onClose={() => setSelectedClienteId(null)}
        clienteId={selectedClienteId}
        onToast={showToast}
      />
    </div>
  );
}
