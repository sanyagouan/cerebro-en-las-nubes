import { useState } from 'react';
import { CheckCircle, XCircle, MapPin, Users, Plus, Edit2, Trash2, Grid3X3, LayoutGrid, ArrowUpRight } from 'lucide-react';
import {
  useTables,
  useCreateTable,
  useUpdateTable,
  useDeleteTable,
  useUpdateTableStatus,
  useTableStats,
  Table,
  TableStatus,
} from '../hooks/useTables';
import MesaForm from './MesaForm';

interface MesaCardProps {
  mesa: Table;
  onEdit: (mesa: Table) => void;
  onDelete: (mesa: Table) => void;
  onToggleStatus: (mesa: Table) => void;
}

// Modern MesaCard with glassmorphism and premium design
function MesaCard({ mesa, onEdit, onDelete, onToggleStatus }: MesaCardProps) {
  const getEstadoStyles = (estado: TableStatus) => {
    switch (estado) {
      case 'Libre':
        return {
          card: 'border-success-200 bg-gradient-to-br from-success-50 to-white hover:border-success-300',
          icon: { bg: 'bg-success-100', color: 'text-success-600' },
          button: 'bg-success-600 hover:bg-success-700',
        };
      case 'Ocupada':
        return {
          card: 'border-error-200 bg-gradient-to-br from-error-50 to-white hover:border-error-300',
          icon: { bg: 'bg-error-100', color: 'text-error-600' },
          button: 'bg-error-600 hover:bg-error-700',
        };
      case 'Reservada':
        return {
          card: 'border-warning-200 bg-gradient-to-br from-warning-50 to-white hover:border-warning-300',
          icon: { bg: 'bg-warning-100', color: 'text-warning-600' },
          button: 'bg-warning-600 hover:bg-warning-700',
        };
      default:
        return {
          card: 'border-secondary-200 bg-white hover:border-secondary-300',
          icon: { bg: 'bg-secondary-100', color: 'text-secondary-600' },
          button: 'bg-secondary-600 hover:bg-secondary-700',
        };
    }
  };

  const getEstadoIcon = (estado: TableStatus) => {
    switch (estado) {
      case 'Libre':
        return CheckCircle;
      case 'Ocupada':
        return XCircle;
      case 'Reservada':
        return CheckCircle;
      default:
        return CheckCircle;
    }
  };

  const styles = getEstadoStyles(mesa.estado);
  const IconComponent = getEstadoIcon(mesa.estado);

  return (
    <div className={`relative overflow-hidden rounded-2xl border-2 transition-all duration-300 group ${styles.card}`}>
      {/* Card Content */}
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className="text-lg font-bold text-secondary-900">{mesa.numero}</h4>
            <div className="flex items-center gap-1.5 text-sm text-secondary-500 mt-1">
              <MapPin size={14} />
              {mesa.ubicacion}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className={`p-2.5 rounded-xl ${styles.icon.bg}`}>
              <IconComponent size={20} className={styles.icon.color} />
            </div>

            {/* Action buttons - visible on hover */}
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => onEdit(mesa)}
                className="p-2 bg-white/80 backdrop-blur-sm rounded-lg hover:bg-white transition-colors shadow-sm"
                title="Editar mesa"
              >
                <Edit2 size={14} className="text-secondary-600" />
              </button>
              <button
                onClick={() => onDelete(mesa)}
                className="p-2 bg-white/80 backdrop-blur-sm rounded-lg hover:bg-error-50 transition-colors shadow-sm"
                title="Eliminar mesa"
              >
                <Trash2 size={14} className="text-error-600" />
              </button>
            </div>
          </div>
        </div>

        <div className="mt-4 space-y-2">
          <div className="flex items-center gap-2 text-sm text-secondary-600">
            <Users size={16} className="text-secondary-400" />
            <span>
              <strong className="text-secondary-900">{mesa.capacidad}</strong> personas
              {mesa.capacidad_max && (
                <span className="text-secondary-400"> (max: {mesa.capacidad_max})</span>
              )}
            </span>
          </div>

          {mesa.notas && (
            <p className="text-xs text-secondary-500 bg-secondary-50 rounded-lg px-3 py-2 mt-2">
              {mesa.notas}
            </p>
          )}
        </div>

        {/* Status Button */}
        <div className="mt-5 pt-4 border-t border-secondary-100">
          <button
            onClick={() => onToggleStatus(mesa)}
            className={`w-full py-2.5 rounded-xl font-semibold text-white transition-colors ${styles.button}`}
          >
            {mesa.estado === 'Libre' ? 'Marcar Ocupada' : 
             mesa.estado === 'Ocupada' ? 'Liberar Mesa' : 'Cambiar Estado'}
          </button>
        </div>
      </div>

      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/50 to-transparent pointer-events-none" />
    </div>
  );
}

// Confirm Dialog Component with modern design
interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
}

function ConfirmDialog({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  isDestructive = false,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="absolute inset-0 bg-secondary-900/50 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-scale-in">
        <h3 className="text-xl font-bold text-secondary-900 mb-2">{title}</h3>
        <p className="text-secondary-600 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="btn-secondary"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`btn-primary ${isDestructive ? '!bg-error-600 hover:!bg-error-700' : ''}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// Toast Notification
interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

let toastId = 0;

export default function Mesas() {
  const { data: tables = [], isLoading, error } = useTables();
  const createMutation = useCreateTable();
  const updateMutation = useUpdateTable();
  const deleteMutation = useDeleteTable();
  const updateStatusMutation = useUpdateTableStatus();
  const stats = useTableStats();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedTable, setSelectedTable] = useState<Table | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [tableToDelete, setTableToDelete] = useState<Table | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'compact'>('grid');

  const showToast = (message: string, type: 'success' | 'error') => {
    const id = toastId++;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // Handlers
  const handleCreateClick = () => {
    setFormMode('create');
    setSelectedTable(null);
    setIsFormOpen(true);
  };

  const handleEditClick = (mesa: Table) => {
    setFormMode('edit');
    setSelectedTable(mesa);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (mesa: Table) => {
    setTableToDelete(mesa);
    setDeleteConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!tableToDelete) return;

    try {
      await deleteMutation.mutateAsync(tableToDelete.id);
      showToast(`Mesa "${tableToDelete.numero}" eliminada`, 'success');
      setDeleteConfirmOpen(false);
      setTableToDelete(null);
    } catch (error) {
      showToast(`Error al eliminar: ${error instanceof Error ? error.message : 'Error'}`, 'error');
    }
  };

  const handleToggleStatus = async (mesa: Table) => {
    const newEstado: TableStatus = mesa.estado === 'Libre' ? 'Ocupada' : 'Libre';

    try {
      await updateStatusMutation.mutateAsync({ id: mesa.id, estado: newEstado });
      showToast(`Mesa "${mesa.numero}" actualizada`, 'success');
    } catch (error) {
      showToast(`Error: ${error instanceof Error ? error.message : 'Error'}`, 'error');
    }
  };

  const handleFormSubmit = async (data: Partial<Table>) => {
    try {
      if (formMode === 'create') {
        await createMutation.mutateAsync(data);
        showToast(`Mesa "${data.numero}" creada`, 'success');
      } else if (selectedTable) {
        await updateMutation.mutateAsync({ id: selectedTable.id, data });
        showToast(`Mesa "${data.numero}" actualizada`, 'success');
      }
      setIsFormOpen(false);
    } catch (error) {
      showToast(
        `Error: ${error instanceof Error ? error.message : 'Error'}`,
        'error'
      );
      throw error;
    }
  };

  // Filter tables by location
  const mesasInterior = tables.filter((m) => m.ubicacion === 'Interior');
  const mesasTerraza = tables.filter((m) => m.ubicacion === 'Terraza');

  // Stats cards data
  const statsData = [
    { label: 'Total', value: stats.total, icon: Grid3X3, color: 'text-secondary-700', bg: 'bg-secondary-100' },
    { label: 'Libres', value: stats.libres, icon: CheckCircle, color: 'text-success-600', bg: 'bg-success-100' },
    { label: 'Ocupadas', value: stats.ocupadas, icon: XCircle, color: 'text-error-600', bg: 'bg-error-100' },
    { label: 'Reservadas', value: stats.reservadas, icon: MapPin, color: 'text-warning-600', bg: 'bg-warning-100' },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Toast Notifications */}
      <div className="fixed top-6 right-6 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`toast ${toast.type === 'success' ? 'toast-success' : 'toast-error'} animate-fade-in-up`}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-secondary-900">Gestion de Mesas</h2>
          <p className="text-secondary-500 mt-1">Controla el estado de las mesas en tiempo real</p>
        </div>
        <div className="flex items-center gap-3">
          {/* View Mode Toggle */}
          <div className="flex bg-secondary-100 rounded-xl p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-white shadow-sm text-primary-600' : 'text-secondary-500 hover:text-secondary-700'}`}
            >
              <LayoutGrid size={18} />
            </button>
            <button
              onClick={() => setViewMode('compact')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'compact' ? 'bg-white shadow-sm text-primary-600' : 'text-secondary-500 hover:text-secondary-700'}`}
            >
              <Grid3X3 size={18} />
            </button>
          </div>
          <button
            onClick={handleCreateClick}
            className="btn-primary"
          >
            <Plus size={18} />
            <span>Nueva Mesa</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statsData.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="stat-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-secondary-500">{stat.label}</p>
                  <p className={`text-3xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
                </div>
                <div className={`p-3 rounded-xl ${stat.bg}`}>
                  <Icon size={22} className={stat.color} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="premium-card p-12">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
            <p className="text-secondary-500 font-medium">Cargando mesas...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="premium-card p-8">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-error-50 flex items-center justify-center mb-4">
              <XCircle className="text-error-500" size={28} />
            </div>
            <h3 className="text-lg font-bold text-secondary-900 mb-2">Error al cargar</h3>
            <p className="text-secondary-500">{error.message}</p>
          </div>
        </div>
      )}

      {/* Tables List */}
      {!isLoading && !error && (
        <div className="space-y-10">
          {/* Interior Section */}
          <section className="animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center">
                <MapPin size={18} className="text-primary-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-secondary-900">Interior</h3>
                <p className="text-sm text-secondary-500">{mesasInterior.length} mesas</p>
              </div>
            </div>
            
            {mesasInterior.length === 0 ? (
              <div className="premium-card p-8 text-center">
                <p className="text-secondary-400">No hay mesas en el interior</p>
              </div>
            ) : (
              <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'grid-cols-2 md:grid-cols-4 lg:grid-cols-6'}`}>
                {mesasInterior.map((mesa) => (
                  <MesaCard
                    key={mesa.id}
                    mesa={mesa}
                    onEdit={handleEditClick}
                    onDelete={handleDeleteClick}
                    onToggleStatus={handleToggleStatus}
                  />
                ))}
              </div>
            )}
          </section>

          {/* Terraza Section */}
          <section className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-success-100 to-success-50 flex items-center justify-center">
                <MapPin size={18} className="text-success-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-secondary-900">Terraza</h3>
                <p className="text-sm text-secondary-500">{mesasTerraza.length} mesas</p>
              </div>
            </div>
            
            {mesasTerraza.length === 0 ? (
              <div className="premium-card p-8 text-center">
                <p className="text-secondary-400">No hay mesas en la terraza</p>
              </div>
            ) : (
              <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'grid-cols-2 md:grid-cols-4 lg:grid-cols-6'}`}>
                {mesasTerraza.map((mesa) => (
                  <MesaCard
                    key={mesa.id}
                    mesa={mesa}
                    onEdit={handleEditClick}
                    onDelete={handleDeleteClick}
                    onToggleStatus={handleToggleStatus}
                  />
                ))}
              </div>
            )}
          </section>
        </div>
      )}

      {/* Mesa Form Modal */}
      <MesaForm
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={selectedTable}
        mode={formMode}
        existingTables={tables}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirmOpen}
        title="Eliminar Mesa"
        message={`Estas seguro de que deseas eliminar la mesa "${tableToDelete?.numero}"? Esta accion no se puede deshacer.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => {
          setDeleteConfirmOpen(false);
          setTableToDelete(null);
        }}
        confirmLabel="Eliminar"
        cancelLabel="Cancelar"
        isDestructive
      />
    </div>
  );
}
