import { useState } from 'react';
import {
  useWaitlist,
  useAddToWaitlist,
  useNotifyWaitlist,
  useRemoveFromWaitlist,
  type WaitlistEntry
} from '../hooks/useWaitlist';
import { Clock, Users, Phone, MapPin, Bell, UserCheck, Trash2, Plus, Search, Filter } from 'lucide-react';

const ZONA_COLORS = {
  Interior: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
  Terraza: 'bg-green-500/10 text-green-600 border-green-500/20',
};

const STATUS_STYLES = {
  waiting: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
  notified: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
  seated: 'bg-green-500/10 text-green-600 border-green-500/20',
  cancelled: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
};

const STATUS_LABELS = {
  waiting: 'Esperando',
  notified: 'Notificado',
  seated: 'Sentado',
  cancelled: 'Cancelado',
};

export default function Waitlist() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterZone, setFilterZone] = useState<'all' | 'Interior' | 'Terraza'>('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    telefono: '',
    party_size: 2,
    zona_preferida: 'Interior' as 'Interior' | 'Terraza',
    notas: '',
  });

  const { data, isLoading, error } = useWaitlist();
  const addMutation = useAddToWaitlist();
  const notifyMutation = useNotifyWaitlist();
  const removeMutation = useRemoveFromWaitlist();

  const entries = data?.entries || [];
  const stats = data?.stats;

  // Filtrado
  const filteredEntries = entries.filter((entry) => {
    const matchesSearch =
      entry.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.telefono.includes(searchTerm);
    const matchesZone = filterZone === 'all' || entry.zona_preferida === filterZone;
    return matchesSearch && matchesZone && entry.status === 'waiting';
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await addMutation.mutateAsync({ data: formData });
    setShowAddModal(false);
    setFormData({
      nombre: '',
      telefono: '',
      party_size: 2,
      zona_preferida: 'Interior',
      notas: '',
    });
  };

  const handleNotify = async (id: string) => {
    if (confirm('¿Notificar al cliente que su mesa está lista?')) {
      await notifyMutation.mutateAsync({ entryId: id });
    }
  };

  const handleRemove = async (id: string) => {
    if (confirm('¿Eliminar esta entrada de la lista de espera?')) {
      await removeMutation.mutateAsync({ entryId: id });
    }
  };

  const formatWaitTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 backdrop-blur-sm">
            <p className="text-red-600 font-medium">Error al cargar lista de espera: {error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
              Lista de Espera
            </h1>
            <p className="text-slate-600 mt-1">Gestión de clientes esperando mesa</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:scale-105"
          >
            <Plus className="w-5 h-5" />
            <span className="font-medium">Agregar a Lista</span>
          </button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-amber-500/10 rounded-xl">
                  <Clock className="w-6 h-6 text-amber-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">En Espera</p>
                  <p className="text-2xl font-bold text-slate-900">{stats.total_waiting}</p>
                </div>
              </div>
            </div>

            <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-500/10 rounded-xl">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Personas Totales</p>
                  <p className="text-2xl font-bold text-slate-900">{stats.total_party_size}</p>
                </div>
              </div>
            </div>

            <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <Bell className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Notificados</p>
                  <p className="text-2xl font-bold text-slate-900">{stats.total_notified}</p>
                </div>
              </div>
            </div>

            <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-green-500/10 rounded-xl">
                  <Clock className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Tiempo Promedio</p>
                  <p className="text-2xl font-bold text-slate-900">{stats.avg_wait_time_minutes}m</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-4 shadow-sm">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar por nombre o teléfono..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-slate-400" />
              <select
                value={filterZone}
                onChange={(e) => setFilterZone(e.target.value as any)}
                className="px-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              >
                <option value="all">Todas las zonas</option>
                <option value="Interior">Interior</option>
                <option value="Terraza">Terraza</option>
              </select>
            </div>
          </div>
        </div>

        {/* Waitlist Table */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
              <p className="mt-4 text-slate-600">Cargando lista de espera...</p>
            </div>
          ) : filteredEntries.length === 0 ? (
            <div className="p-12 text-center">
              <Users className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <p className="text-lg font-medium text-slate-900">No hay clientes esperando</p>
              <p className="text-slate-600 mt-1">La lista de espera está vacía</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50/80 border-b border-slate-200">
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">Cliente</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">Personas</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">Zona</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">Tiempo Esperando</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">Estado</th>
                    <th className="text-right px-6 py-4 text-sm font-semibold text-slate-700">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredEntries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-slate-900">{entry.nombre}</p>
                          <div className="flex items-center gap-1.5 mt-1 text-sm text-slate-600">
                            <Phone className="w-3.5 h-3.5" />
                            <span>{entry.telefono}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1.5 text-slate-700">
                          <Users className="w-4 h-4 text-slate-400" />
                          <span className="font-medium">{entry.party_size}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-sm font-medium border ${ZONA_COLORS[entry.zona_preferida]}`}>
                          <MapPin className="w-3.5 h-3.5" />
                          {entry.zona_preferida}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1.5 text-slate-700">
                          <Clock className="w-4 h-4 text-slate-400" />
                          <span className="font-medium">{formatWaitTime(entry.wait_time_minutes)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-3 py-1 rounded-lg text-sm font-medium border ${STATUS_STYLES[entry.status]}`}>
                          {STATUS_LABELS[entry.status]}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleNotify(entry.id)}
                            disabled={notifyMutation.isPending}
                            className="p-2 text-purple-600 hover:bg-purple-500/10 rounded-lg transition-colors disabled:opacity-50"
                            title="Notificar cliente"
                          >
                            <Bell className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleRemove(entry.id)}
                            disabled={removeMutation.isPending}
                            className="p-2 text-red-600 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50"
                            title="Eliminar"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Add to Waitlist Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-slate-900">Agregar a Lista de Espera</h2>
              <p className="text-slate-600 mt-1">Complete los datos del cliente</p>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Nombre Completo *
                </label>
                <input
                  type="text"
                  required
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  placeholder="Ej: Juan Pérez"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Teléfono *
                </label>
                <input
                  type="tel"
                  required
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  placeholder="+34 600 000 000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Número de Personas *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  max="20"
                  value={formData.party_size}
                  onChange={(e) => setFormData({ ...formData, party_size: parseInt(e.target.value) })}
                  className="w-full px-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Zona Preferida *
                </label>
                <select
                  value={formData.zona_preferida}
                  onChange={(e) => setFormData({ ...formData, zona_preferida: e.target.value as any })}
                  className="w-full px-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                >
                  <option value="Interior">Interior</option>
                  <option value="Terraza">Terraza</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Notas (opcional)
                </label>
                <textarea
                  value={formData.notas}
                  onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none"
                  placeholder="Solicitudes especiales..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-6 py-3 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={addMutation.isPending}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/25 font-medium disabled:opacity-50"
                >
                  {addMutation.isPending ? 'Agregando...' : 'Agregar a Lista'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
