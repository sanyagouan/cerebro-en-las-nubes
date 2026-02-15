import { useState } from 'react';
import { CheckCircle, XCircle, MapPin, Users, Plus, Edit2, Trash2 } from 'lucide-react';
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

// Componente MesaCard con acciones CRUD
function MesaCard({ mesa, onEdit, onDelete, onToggleStatus }: MesaCardProps) {
  const getEstadoColor = (estado: TableStatus) => {
    switch (estado) {
      case 'Libre':
        return 'border-green-200 bg-green-50 hover:border-green-300';
      case 'Ocupada':
        return 'border-red-200 bg-red-50 hover:border-red-300';
      case 'Reservada':
        return 'border-yellow-200 bg-yellow-50 hover:border-yellow-300';
      default:
        return 'border-gray-200 bg-gray-50 hover:border-gray-300';
    }
  };

  const getEstadoIcon = (estado: TableStatus) => {
    switch (estado) {
      case 'Libre':
        return { icon: CheckCircle, bg: 'bg-green-200', color: 'text-green-700' };
      case 'Ocupada':
        return { icon: XCircle, bg: 'bg-red-200', color: 'text-red-700' };
      case 'Reservada':
        return { icon: CheckCircle, bg: 'bg-yellow-200', color: 'text-yellow-700' };
      default:
        return { icon: CheckCircle, bg: 'bg-gray-200', color: 'text-gray-700' };
    }
  };

  const estadoInfo = getEstadoIcon(mesa.estado);
  const IconComponent = estadoInfo.icon;

  return (
    <div className={`p-4 rounded-xl border-2 transition-all ${getEstadoColor(mesa.estado)}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900">{mesa.numero}</h4>
          <div className="flex items-center gap-1 text-sm text-gray-600 mt-1">
            <MapPin size={14} />
            {mesa.ubicacion}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-full ${estadoInfo.bg}`}>
            <IconComponent size={20} className={estadoInfo.color} />
          </div>

          {/* Action buttons */}
          <div className="flex gap-1">
            <button
              onClick={() => onEdit(mesa)}
              className="p-1.5 hover:bg-white/50 rounded-lg transition-colors"
              title="Editar mesa"
            >
              <Edit2 size={16} className="text-gray-600" />
            </button>
            <button
              onClick={() => onDelete(mesa)}
              className="p-1.5 hover:bg-white/50 rounded-lg transition-colors"
              title="Eliminar mesa"
            >
              <Trash2 size={16} className="text-red-600" />
            </button>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2 text-sm">
          <Users size={16} className="text-gray-400" />
          <span>
            Capacidad: <strong>{mesa.capacidad}</strong>
            {mesa.capacidad_max && (
              <span className="text-gray-500"> (máx: {mesa.capacidad_max})</span>
            )}
          </span>
        </div>

        {mesa.notas && <p className="text-sm text-gray-600 mt-2">{mesa.notas}</p>}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <button
          onClick={() => onToggleStatus(mesa)}
          className={`w-full py-2 rounded-lg font-medium transition-colors ${
            mesa.estado === 'Libre'
              ? 'bg-green-600 text-white hover:bg-green-700'
              : mesa.estado === 'Ocupada'
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-yellow-600 text-white hover:bg-yellow-700'
          }`}
        >
          {mesa.estado === 'Libre'
            ? 'Marcar Ocupada'
            : mesa.estado === 'Ocupada'
            ? 'Liberar Mesa'
            : 'Cambiar Estado'}
        </button>
      </div>
    </div>
  );
}

// Confirm Dialog Component
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
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isDestructive
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// Toast Notification (simple inline implementation)
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
      showToast(`Mesa "${tableToDelete.numero}" eliminada exitosamente`, 'success');
      setDeleteConfirmOpen(false);
      setTableToDelete(null);
    } catch (error) {
      showToast(`Error al eliminar mesa: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleToggleStatus = async (mesa: Table) => {
    const newEstado: TableStatus = mesa.estado === 'Libre' ? 'Ocupada' : 'Libre';

    try {
      await updateStatusMutation.mutateAsync({ id: mesa.id, estado: newEstado });
      showToast(`Mesa "${mesa.numero}" actualizada a ${newEstado}`, 'success');
    } catch (error) {
      showToast(`Error al cambiar estado: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleFormSubmit = async (data: Partial<Table>) => {
    try {
      if (formMode === 'create') {
        await createMutation.mutateAsync(data);
        showToast(`Mesa "${data.numero}" creada exitosamente`, 'success');
      } else if (selectedTable) {
        await updateMutation.mutateAsync({ id: selectedTable.id, data });
        showToast(`Mesa "${data.numero}" actualizada exitosamente`, 'success');
      }
      setIsFormOpen(false);
    } catch (error) {
      showToast(
        `Error al ${formMode === 'create' ? 'crear' : 'actualizar'} mesa: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        'error'
      );
      throw error; // Re-throw to keep form open
    }
  };

  // Filter tables by location
  const mesasInterior = tables.filter((m) => m.ubicacion === 'Interior');
  const mesasTerraza = tables.filter((m) => m.ubicacion === 'Terraza');

  return (
    <div className="space-y-8">
      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-3 rounded-lg shadow-lg text-white animate-fade-in ${
              toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Header with Create Button */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Gestión de Mesas</h2>
        <button
          onClick={handleCreateClick}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={20} />
          <span>Nueva Mesa</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Total de Mesas</p>
          <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Disponibles</p>
          <p className="text-3xl font-bold text-green-600">{stats.libres}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Ocupadas</p>
          <p className="text-3xl font-bold text-red-600">{stats.ocupadas}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Reservadas</p>
          <p className="text-3xl font-bold text-yellow-600">{stats.reservadas}</p>
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
          Error al cargar mesas: {error.message}
        </div>
      )}

      {/* Tables List */}
      {!isLoading && !error && (
        <>
          {/* Mesas Interior */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Interior ({mesasInterior.length})
            </h3>
            {mesasInterior.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No hay mesas en el interior</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
          </div>

          {/* Mesas Terraza */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Terraza ({mesasTerraza.length})
            </h3>
            {mesasTerraza.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No hay mesas en la terraza</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
          </div>
        </>
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
        message={`¿Estás seguro de que deseas eliminar la mesa "${tableToDelete?.numero}"? Esta acción no se puede deshacer.`}
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
