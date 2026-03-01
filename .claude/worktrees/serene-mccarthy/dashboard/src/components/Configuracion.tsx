import { useState, useMemo } from 'react';
import {
  Calendar,
  Clock,
  Users,
  Settings,
  Shield,
  AlertCircle,
  Plus,
  Edit2,
  Trash2,
  Save,
  X,
  CheckCircle,
} from 'lucide-react';
import {
  useSchedule,
  useUpdateSchedule,
  useHolidays,
  useCreateHoliday,
  useUpdateHoliday,
  useDeleteHoliday,
  useShifts,
  useUpdateShift,
  useCapacity,
  useUpdateCapacity,
  useReservationTimings,
  useUpdateReservationTimings,
  useUsers,
  useCreateUser,
  useUpdateUser,
  useDeleteUser,
  DaySchedule,
  Holiday,
  Shift,
  CapacityConfig,
  ReservationTiming,
  StaffUser,
} from '../hooks/useConfig';

// ==================== TYPES ====================

type TabType = 'horarios' | 'festivos' | 'turnos' | 'capacidad' | 'tiempos' | 'usuarios';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

interface HolidayFormData {
  date: string;
  name: string;
  is_closed: boolean;
  special_hours?: {
    lunch_start?: string;
    lunch_end?: string;
    dinner_start?: string;
    dinner_end?: string;
  };
}

interface UserFormData {
  name: string;
  email: string;
  phone: string;
  role: 'Waiter' | 'Cook' | 'Manager' | 'Admin';
  is_active: boolean;
}

// ==================== UTILS ====================

let toastId = 0;

const validateTime = (time: string): boolean => {
  return /^([01]\d|2[0-3]):([0-5]\d)$/.test(time);
};

const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

const validatePhone = (phone: string): boolean => {
  const cleanPhone = phone.replace(/[\s-]/g, '');
  return /^(\+34|0034|34)?[6789]\d{8}$/.test(cleanPhone);
};

const daysOfWeek: Array<'lunes' | 'martes' | 'miércoles' | 'jueves' | 'viernes' | 'sábado' | 'domingo'> = [
  'lunes',
  'martes',
  'miércoles',
  'jueves',
  'viernes',
  'sábado',
  'domingo',
];

const dayLabels: Record<string, string> = {
  lunes: 'Lunes',
  martes: 'Martes',
  miércoles: 'Miércoles',
  jueves: 'Jueves',
  viernes: 'Viernes',
  sábado: 'Sábado',
  domingo: 'Domingo',
};

// ==================== MAIN COMPONENT ====================

export default function Configuracion() {
  const [activeTab, setActiveTab] = useState<TabType>('horarios');
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [holidayModalOpen, setHolidayModalOpen] = useState(false);
  const [userModalOpen, setUserModalOpen] = useState(false);
  const [editingHoliday, setEditingHoliday] = useState<Holiday | null>(null);
  const [editingUser, setEditingUser] = useState<StaffUser | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'holiday' | 'user'; id: string } | null>(null);

  // Toast management
  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    const id = toastId++;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // Tab buttons
  const tabs: Array<{ key: TabType; label: string; icon: React.ElementType }> = [
    { key: 'horarios', label: 'Horarios', icon: Clock },
    { key: 'festivos', label: 'Festivos', icon: Calendar },
    { key: 'turnos', label: 'Turnos', icon: Settings },
    { key: 'capacidad', label: 'Capacidad', icon: Users },
    { key: 'tiempos', label: 'Tiempos', icon: AlertCircle },
    { key: 'usuarios', label: 'Usuarios', icon: Shield },
  ];

  return (
    <div className="space-y-6">
      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-3 rounded-lg shadow-lg text-white animate-fade-in flex items-center gap-2 ${
              toast.type === 'success'
                ? 'bg-green-600'
                : toast.type === 'error'
                ? 'bg-red-600'
                : 'bg-blue-600'
            }`}
          >
            {toast.type === 'success' && <CheckCircle size={18} />}
            {toast.type === 'error' && <AlertCircle size={18} />}
            {toast.type === 'info' && <AlertCircle size={18} />}
            <span>{toast.message}</span>
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Configuración del Sistema</h2>
      </div>

      {/* Tabs Navigation */}
      <div className="flex gap-2 border-b border-gray-200">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === key
                ? 'border-primary-600 text-primary-600 font-medium'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        {activeTab === 'horarios' && (
          <HorariosSection showToast={showToast} />
        )}
        {activeTab === 'festivos' && (
          <FestivosSection
            showToast={showToast}
            onEdit={(holiday) => {
              setEditingHoliday(holiday);
              setHolidayModalOpen(true);
            }}
            onDelete={(id) => {
              setDeleteTarget({ type: 'holiday', id });
              setDeleteConfirmOpen(true);
            }}
            onCreateNew={() => {
              setEditingHoliday(null);
              setHolidayModalOpen(true);
            }}
          />
        )}
        {activeTab === 'turnos' && (
          <TurnosSection showToast={showToast} />
        )}
        {activeTab === 'capacidad' && (
          <CapacidadSection showToast={showToast} />
        )}
        {activeTab === 'tiempos' && (
          <TiemposSection showToast={showToast} />
        )}
        {activeTab === 'usuarios' && (
          <UsuariosSection
            showToast={showToast}
            onEdit={(user) => {
              setEditingUser(user);
              setUserModalOpen(true);
            }}
            onDelete={(id) => {
              setDeleteTarget({ type: 'user', id });
              setDeleteConfirmOpen(true);
            }}
            onCreateNew={() => {
              setEditingUser(null);
              setUserModalOpen(true);
            }}
          />
        )}
      </div>

      {/* Holiday Modal */}
      {holidayModalOpen && (
        <HolidayFormModal
          holiday={editingHoliday}
          onClose={() => {
            setHolidayModalOpen(false);
            setEditingHoliday(null);
          }}
          onSuccess={(message) => {
            showToast(message, 'success');
            setHolidayModalOpen(false);
            setEditingHoliday(null);
          }}
          onError={(message) => showToast(message, 'error')}
        />
      )}

      {/* User Modal */}
      {userModalOpen && (
        <UserFormModal
          user={editingUser}
          onClose={() => {
            setUserModalOpen(false);
            setEditingUser(null);
          }}
          onSuccess={(message) => {
            showToast(message, 'success');
            setUserModalOpen(false);
            setEditingUser(null);
          }}
          onError={(message) => showToast(message, 'error')}
        />
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirmOpen && deleteTarget && (
        <DeleteConfirmDialog
          type={deleteTarget.type}
          onConfirm={async () => {
            // Handle deletion
            setDeleteConfirmOpen(false);
            setDeleteTarget(null);
          }}
          onCancel={() => {
            setDeleteConfirmOpen(false);
            setDeleteTarget(null);
          }}
        />
      )}
    </div>
  );
}

// ==================== HORARIOS SECTION ====================

function HorariosSection({ showToast }: { showToast: (msg: string, type: 'success' | 'error') => void }) {
  const { data, isLoading } = useSchedule();
  const updateMutation = useUpdateSchedule();
  const [schedule, setSchedule] = useState<DaySchedule[]>([]);
  const [hasChanges, setHasChanges] = useState(false);

  useMemo(() => {
    if (data?.schedule) {
      setSchedule(data.schedule);
    }
  }, [data]);

  const handleChange = (day: string, field: keyof DaySchedule, value: any) => {
    setSchedule((prev) =>
      prev.map((d) => (d.day === day ? { ...d, [field]: value } : d))
    );
    setHasChanges(true);
  };

  const handleSave = async () => {
    // Validar horarios
    for (const day of schedule) {
      if (!day.is_open) continue;
      
      if (day.lunch_start && day.lunch_end) {
        if (!validateTime(day.lunch_start) || !validateTime(day.lunch_end)) {
          showToast('Formato de hora inválido (usa HH:mm)', 'error');
          return;
        }
        if (day.lunch_start >= day.lunch_end) {
          showToast(`${dayLabels[day.day]}: Hora inicio almuerzo debe ser menor que hora fin`, 'error');
          return;
        }
      }
      
      if (day.dinner_start && day.dinner_end) {
        if (!validateTime(day.dinner_start) || !validateTime(day.dinner_end)) {
          showToast('Formato de hora inválido (usa HH:mm)', 'error');
          return;
        }
        if (day.dinner_start >= day.dinner_end) {
          showToast(`${dayLabels[day.day]}: Hora inicio cena debe ser menor que hora fin`, 'error');
          return;
        }
      }
    }

    try {
      await updateMutation.mutateAsync(schedule);
      showToast('Horarios actualizados exitosamente', 'success');
      setHasChanges(false);
    } catch (error) {
      showToast(`Error al actualizar horarios: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4, 5, 6, 7].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Horarios por Día de la Semana</h3>
        <button
          onClick={handleSave}
          disabled={!hasChanges || updateMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save size={18} />
          <span>{updateMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {daysOfWeek.map((day) => {
          const dayData = schedule.find((d) => d.day === day) || {
            day,
            is_open: false,
          };

          return (
            <div key={day} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium text-gray-900">{dayLabels[day]}</h4>
                <label className="flex items-center gap-2 cursor-pointer">
                  <span className="text-sm text-gray-600">Abierto</span>
                  <input
                    type="checkbox"
                    checked={dayData.is_open}
                    onChange={(e) => handleChange(day, 'is_open', e.target.checked)}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                </label>
              </div>

              {dayData.is_open && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Almuerzo Inicio</label>
                    <input
                      type="time"
                      value={dayData.lunch_start || ''}
                      onChange={(e) => handleChange(day, 'lunch_start', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Almuerzo Fin</label>
                    <input
                      type="time"
                      value={dayData.lunch_end || ''}
                      onChange={(e) => handleChange(day, 'lunch_end', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Cena Inicio</label>
                    <input
                      type="time"
                      value={dayData.dinner_start || ''}
                      onChange={(e) => handleChange(day, 'dinner_start', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Cena Fin</label>
                    <input
                      type="time"
                      value={dayData.dinner_end || ''}
                      onChange={(e) => handleChange(day, 'dinner_end', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ==================== FESTIVOS SECTION ====================

interface FestivosSectionProps {
  showToast: (msg: string, type: 'success' | 'error') => void;
  onEdit: (holiday: Holiday) => void;
  onDelete: (id: string) => void;
  onCreateNew: () => void;
}

function FestivosSection({ showToast, onEdit, onDelete, onCreateNew }: FestivosSectionProps) {
  const { data, isLoading } = useHolidays();

  const sortedHolidays = useMemo(() => {
    if (!data?.holidays) return [];
    return [...data.holidays].sort((a, b) => a.date.localeCompare(b.date));
  }, [data]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Calendario de Festivos</h3>
        <button
          onClick={onCreateNew}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={18} />
          <span>Nuevo Festivo</span>
        </button>
      </div>

      {sortedHolidays.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Calendar size={48} className="mx-auto mb-4 text-gray-300" />
          <p>No hay festivos configurados</p>
        </div>
      ) : (
        <div className="space-y-2">
          {sortedHolidays.map((holiday) => (
            <div
              key={holiday.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-gray-900">{holiday.name}</span>
                  <span className="text-sm text-gray-500">{holiday.date}</span>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      holiday.is_closed
                        ? 'bg-red-100 text-red-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {holiday.is_closed ? 'Cerrado' : 'Horario Especial'}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onEdit(holiday)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Editar"
                >
                  <Edit2 size={16} className="text-gray-600" />
                </button>
                <button
                  onClick={() => onDelete(holiday.id)}
                  className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                  title="Eliminar"
                >
                  <Trash2 size={16} className="text-red-600" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ==================== TURNOS SECTION ====================

function TurnosSection({ showToast }: { showToast: (msg: string, type: 'success' | 'error') => void }) {
  const { data, isLoading } = useShifts();
  const updateMutation = useUpdateShift();

  const handleUpdate = async (id: string, updates: Partial<Shift>) => {
    try {
      await updateMutation.mutateAsync({ id, data: updates });
      showToast('Turno actualizado exitosamente', 'success');
    } catch (error) {
      showToast(`Error al actualizar turno: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[1, 2].map((i) => (
          <div key={i} className="h-48 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Configuración de Turnos</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data?.shifts.map((shift) => (
          <div key={shift.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-medium text-gray-900 capitalize">{shift.name}</h4>
              <label className="flex items-center gap-2 cursor-pointer">
                <span className="text-sm text-gray-600">Activo</span>
                <input
                  type="checkbox"
                  checked={shift.is_active}
                  onChange={(e) => handleUpdate(shift.id, { is_active: e.target.checked })}
                  className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                />
              </label>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Hora Inicio</label>
                  <input
                    type="time"
                    value={shift.default_start}
                    onChange={(e) => handleUpdate(shift.id, { default_start: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Hora Fin</label>
                  <input
                    type="time"
                    value={shift.default_end}
                    onChange={(e) => handleUpdate(shift.id, { default_end: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-1">Capacidad Máxima</label>
                <input
                  type="number"
                  min="1"
                  value={shift.max_capacity}
                  onChange={(e) => handleUpdate(shift.id, { max_capacity: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ==================== CAPACIDAD SECTION ====================

function CapacidadSection({ showToast }: { showToast: (msg: string, type: 'success' | 'error') => void }) {
  const { data, isLoading } = useCapacity();
  const updateMutation = useUpdateCapacity();
  const [capacity, setCapacity] = useState<CapacityConfig | null>(null);
  const [hasChanges, setHasChanges] = useState(false);

  useMemo(() => {
    if (data) {
      setCapacity(data);
    }
  }, [data]);

  const handleChange = (field: keyof CapacityConfig, value: number) => {
    if (!capacity) return;
    setCapacity({ ...capacity, [field]: value });
    setHasChanges(true);
  };

  const handleSave = async () => {
    if (!capacity) return;

    // Validaciones
    if (capacity.overbooking_percentage < 0 || capacity.overbooking_percentage > 20) {
      showToast('El porcentaje de overbooking debe estar entre 0 y 20', 'error');
      return;
    }

    if (capacity.min_party_size >= capacity.max_party_size) {
      showToast('El tamaño mínimo debe ser menor que el tamaño máximo', 'error');
      return;
    }

    try {
      await updateMutation.mutateAsync(capacity);
      showToast('Capacidad actualizada exitosamente', 'success');
      setHasChanges(false);
    } catch (error) {
      showToast(`Error al actualizar capacidad: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  if (isLoading || !capacity) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Límites de Capacidad del Sistema</h3>
        <button
          onClick={handleSave}
          disabled={!hasChanges || updateMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save size={18} />
          <span>{updateMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Máximo de Reservas Simultáneas
          </label>
          <input
            type="number"
            min="1"
            value={capacity.max_simultaneous_reservations}
            onChange={(e) => handleChange('max_simultaneous_reservations', parseInt(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tamaño Máximo de Grupo
          </label>
          <input
            type="number"
            min="1"
            value={capacity.max_party_size}
            onChange={(e) => handleChange('max_party_size', parseInt(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tamaño Mínimo de Grupo
          </label>
          <input
            type="number"
            min="1"
            value={capacity.min_party_size}
            onChange={(e) => handleChange('min_party_size', parseInt(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Porcentaje de Overbooking (0-20%)
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="0"
              max="20"
              value={capacity.overbooking_percentage}
              onChange={(e) => handleChange('overbooking_percentage', parseInt(e.target.value))}
              className="flex-1"
            />
            <span className="text-lg font-medium text-gray-900 w-12 text-right">
              {capacity.overbooking_percentage}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ==================== TIEMPOS SECTION ====================

function TiemposSection({ showToast }: { showToast: (msg: string, type: 'success' | 'error') => void }) {
  const { data, isLoading } = useReservationTimings();
  const updateMutation = useUpdateReservationTimings();
  const [timings, setTimings] = useState<ReservationTiming[]>([]);
  const [hasChanges, setHasChanges] = useState(false);

  useMemo(() => {
    if (data?.timings) {
      setTimings(data.timings);
    }
  }, [data]);

  const handleChange = (index: number, field: keyof ReservationTiming, value: number) => {
    setTimings((prev) =>
      prev.map((t, i) => (i === index ? { ...t, [field]: value } : t))
    );
    setHasChanges(true);
  };

  const handleSave = async () => {
    // Validar rangos no solapados
    for (let i = 0; i < timings.length; i++) {
      if (timings[i].party_size_min >= timings[i].party_size_max) {
        showToast(`Rango ${i + 1}: El tamaño mínimo debe ser menor que el máximo`, 'error');
        return;
      }
    }

    try {
      await updateMutation.mutateAsync(timings);
      showToast('Tiempos de reserva actualizados exitosamente', 'success');
      setHasChanges(false);
    } catch (error) {
      showToast(`Error al actualizar tiempos: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Tiempos de Reserva por Tamaño de Grupo</h3>
        <button
          onClick={handleSave}
          disabled={!hasChanges || updateMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save size={18} />
          <span>{updateMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}</span>
        </button>
      </div>

      <div className="space-y-4">
        {timings.map((timing, index) => (
          <div key={index} className="grid grid-cols-3 gap-4 p-4 border border-gray-200 rounded-lg">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Tamaño Mínimo</label>
              <input
                type="number"
                min="1"
                value={timing.party_size_min}
                onChange={(e) => handleChange(index, 'party_size_min', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Tamaño Máximo</label>
              <input
                type="number"
                min="1"
                value={timing.party_size_max}
                onChange={(e) => handleChange(index, 'party_size_max', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Duración (minutos)</label>
              <input
                type="number"
                min="30"
                step="15"
                value={timing.duration_minutes}
                onChange={(e) => handleChange(index, 'duration_minutes', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ==================== USUARIOS SECTION ====================

interface UsuariosSectionProps {
  showToast: (msg: string, type: 'success' | 'error') => void;
  onEdit: (user: StaffUser) => void;
  onDelete: (id: string) => void;
  onCreateNew: () => void;
}

function UsuariosSection({ showToast, onEdit, onDelete, onCreateNew }: UsuariosSectionProps) {
  const { data, isLoading } = useUsers();
  const [roleFilter, setRoleFilter] = useState<'all' | 'Waiter' | 'Cook' | 'Manager' | 'Admin'>('all');

  const filteredUsers = useMemo(() => {
    if (!data?.users) return [];
    if (roleFilter === 'all') return data.users;
    return data.users.filter((u) => u.role === roleFilter);
  }, [data, roleFilter]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Usuarios del Staff</h3>
        <div className="flex items-center gap-3">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">Todos los Roles</option>
            <option value="Waiter">Camareros</option>
            <option value="Cook">Cocineros</option>
            <option value="Manager">Encargados</option>
            <option value="Admin">Administradores</option>
          </select>
          <button
            onClick={onCreateNew}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus size={18} />
            <span>Nuevo Usuario</span>
          </button>
        </div>
      </div>

      {filteredUsers.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Shield size={48} className="mx-auto mb-4 text-gray-300" />
          <p>No hay usuarios con este filtro</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nombre</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Email</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Teléfono</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Rol</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Estado</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{user.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{user.email}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{user.phone}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        user.role === 'Admin'
                          ? 'bg-purple-100 text-purple-700'
                          : user.role === 'Manager'
                          ? 'bg-blue-100 text-blue-700'
                          : user.role === 'Waiter'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-orange-100 text-orange-700'
                      }`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        user.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onEdit(user)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Editar"
                      >
                        <Edit2 size={16} className="text-gray-600" />
                      </button>
                      <button
                        onClick={() => onDelete(user.id)}
                        className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 size={16} className="text-red-600" />
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
  );
}

// ==================== MODALS ====================

interface HolidayFormModalProps {
  holiday: Holiday | null;
  onClose: () => void;
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

function HolidayFormModal({ holiday, onClose, onSuccess, onError }: HolidayFormModalProps) {
  const createMutation = useCreateHoliday();
  const updateMutation = useUpdateHoliday();
  const [formData, setFormData] = useState<HolidayFormData>(
    holiday || {
      date: '',
      name: '',
      is_closed: true,
    }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones
    if (!formData.name.trim()) {
      onError('El nombre es requerido');
      return;
    }
    if (!formData.date) {
      onError('La fecha es requerida');
      return;
    }

    try {
      if (holiday) {
        await updateMutation.mutateAsync({ id: holiday.id, data: formData });
        onSuccess('Festivo actualizado exitosamente');
      } else {
        await createMutation.mutateAsync(formData);
        onSuccess('Festivo creado exitosamente');
      }
    } catch (error) {
      onError(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {holiday ? 'Editar Festivo' : 'Nuevo Festivo'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="Ej: Navidad"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_closed}
                onChange={(e) => setFormData({ ...formData, is_closed: e.target.checked })}
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Restaurante cerrado este día</span>
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {createMutation.isPending || updateMutation.isPending
                ? 'Guardando...'
                : holiday
                ? 'Actualizar'
                : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface UserFormModalProps {
  user: StaffUser | null;
  onClose: () => void;
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

function UserFormModal({ user, onClose, onSuccess, onError }: UserFormModalProps) {
  const createMutation = useCreateUser();
  const updateMutation = useUpdateUser();
  const [formData, setFormData] = useState<UserFormData>(
    user
      ? {
          name: user.name,
          email: user.email,
          phone: user.phone,
          role: user.role,
          is_active: user.is_active,
        }
      : {
          name: '',
          email: '',
          phone: '',
          role: 'Waiter',
          is_active: true,
        }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones
    if (!formData.name.trim()) {
      onError('El nombre es requerido');
      return;
    }
    if (!validateEmail(formData.email)) {
      onError('Email inválido');
      return;
    }
    if (!validatePhone(formData.phone)) {
      onError('Teléfono inválido (formato: 612345678)');
      return;
    }

    try {
      if (user) {
        await updateMutation.mutateAsync({ id: user.id, data: formData });
        onSuccess('Usuario actualizado exitosamente');
      } else {
        await createMutation.mutateAsync(formData);
        onSuccess('Usuario creado exitosamente');
      }
    } catch (error) {
      onError(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {user ? 'Editar Usuario' : 'Nuevo Usuario'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="612345678"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Rol</label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="Waiter">Camarero</option>
              <option value="Cook">Cocinero</option>
              <option value="Manager">Encargado</option>
              <option value="Admin">Administrador</option>
            </select>
          </div>

          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Usuario activo</span>
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {createMutation.isPending || updateMutation.isPending
                ? 'Guardando...'
                : user
                ? 'Actualizar'
                : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface DeleteConfirmDialogProps {
  type: 'holiday' | 'user';
  onConfirm: () => void;
  onCancel: () => void;
}

function DeleteConfirmDialog({ type, onConfirm, onCancel }: DeleteConfirmDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          Confirmar Eliminación
        </h3>
        <p className="text-gray-600 mb-6">
          ¿Estás seguro de que deseas eliminar este {type === 'holiday' ? 'festivo' : 'usuario'}?
          Esta acción no se puede deshacer.
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>
  );
}
