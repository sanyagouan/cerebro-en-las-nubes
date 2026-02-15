import { useState, useEffect, useRef } from 'react';
import { X, AlertCircle, Calendar, Clock, User, Phone, Users, FileText } from 'lucide-react';
import { Reservation, ReservationStatus } from '../hooks/useReservations';

interface ReservaFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Reservation>) => Promise<void>;
  initialData?: Reservation | null;
  mode: 'create' | 'edit';
}

export default function ReservaForm({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  mode,
}: ReservaFormProps) {
  const [formData, setFormData] = useState<Partial<Reservation>>({
    nombre: '',
    telefono: '',
    fecha: '',
    hora: '',
    pax: 2,
    estado: 'Pendiente' as ReservationStatus,
    notas: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const firstInputRef = useRef<HTMLInputElement>(null);

  // Get today's date in YYYY-MM-DD format for min date validation
  const today = new Date().toISOString().split('T')[0];

  // Reset form when modal opens/closes or initialData changes
  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && initialData) {
        setFormData({
          nombre: initialData.nombre,
          telefono: initialData.telefono,
          fecha: initialData.fecha,
          hora: initialData.hora,
          pax: initialData.pax,
          estado: initialData.estado,
          notas: initialData.notas || '',
        });
      } else {
        // Default to today's date and current hour + 2
        const now = new Date();
        const defaultHour = (now.getHours() + 2) % 24;
        const defaultTime = `${defaultHour.toString().padStart(2, '0')}:00`;
        
        setFormData({
          nombre: '',
          telefono: '',
          fecha: today,
          hora: defaultTime,
          pax: 2,
          estado: 'Pendiente' as ReservationStatus,
          notas: '',
        });
      }
      setErrors({});
      setIsSubmitting(false);

      // Auto-focus first input
      setTimeout(() => {
        firstInputRef.current?.focus();
      }, 100);
    }
  }, [isOpen, mode, initialData, today]);

  // ESC key handler
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, isSubmitting, onClose]);

  // Validation
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Nombre validation
    if (!formData.nombre?.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    } else if (formData.nombre.trim().length < 2) {
      newErrors.nombre = 'El nombre debe tener al menos 2 caracteres';
    }

    // Teléfono validation (Spanish format)
    if (!formData.telefono?.trim()) {
      newErrors.telefono = 'El teléfono es requerido';
    } else {
      const phoneRegex = /^(\+34|0034|34)?[6789]\d{8}$/;
      const cleanPhone = formData.telefono.replace(/[\s-]/g, '');
      if (!phoneRegex.test(cleanPhone)) {
        newErrors.telefono = 'Formato de teléfono inválido (ej: 612345678)';
      }
    }

    // Fecha validation
    if (!formData.fecha) {
      newErrors.fecha = 'La fecha es requerida';
    } else {
      const selectedDate = new Date(formData.fecha);
      const todayDate = new Date(today);
      if (selectedDate < todayDate) {
        newErrors.fecha = 'No se pueden crear reservas en fechas pasadas';
      }
    }

    // Hora validation
    if (!formData.hora) {
      newErrors.hora = 'La hora es requerida';
    } else {
      const [hours, minutes] = formData.hora.split(':').map(Number);
      if (hours < 12 || hours > 23) {
        newErrors.hora = 'Horario de servicio: 12:00 - 23:59';
      }
    }

    // Pax validation
    if (!formData.pax || formData.pax < 1) {
      newErrors.pax = 'Mínimo 1 persona';
    } else if (formData.pax > 20) {
      newErrors.pax = 'Máximo 20 personas (contacte para grupos mayores)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate() || isSubmitting) return;

    setIsSubmitting(true);

    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Form submission error:', error);
      setIsSubmitting(false);
    }
  };

  const handleChange = (
    field: keyof typeof formData,
    value: string | number | undefined
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field on change
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 transition-opacity"
        onClick={() => !isSubmitting && onClose()}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'create' ? 'Nueva Reserva' : 'Editar Reserva'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X size={24} className="text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Nombre y Teléfono */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <User size={16} />
                  Nombre Completo *
                </div>
              </label>
              <input
                ref={firstInputRef}
                id="nombre"
                type="text"
                value={formData.nombre || ''}
                onChange={(e) => handleChange('nombre', e.target.value)}
                disabled={isSubmitting}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                  errors.nombre ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ej: Juan Pérez García"
              />
              {errors.nombre && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle size={14} />
                  <span>{errors.nombre}</span>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="telefono" className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <Phone size={16} />
                  Teléfono *
                </div>
              </label>
              <input
                id="telefono"
                type="tel"
                value={formData.telefono || ''}
                onChange={(e) => handleChange('telefono', e.target.value)}
                disabled={isSubmitting}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                  errors.telefono ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="612345678"
              />
              {errors.telefono && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle size={14} />
                  <span>{errors.telefono}</span>
                </div>
              )}
            </div>
          </div>

          {/* Fecha y Hora */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="fecha" className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <Calendar size={16} />
                  Fecha *
                </div>
              </label>
              <input
                id="fecha"
                type="date"
                min={today}
                value={formData.fecha || ''}
                onChange={(e) => handleChange('fecha', e.target.value)}
                disabled={isSubmitting}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                  errors.fecha ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.fecha && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle size={14} />
                  <span>{errors.fecha}</span>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="hora" className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <Clock size={16} />
                  Hora *
                </div>
              </label>
              <input
                id="hora"
                type="time"
                value={formData.hora || ''}
                onChange={(e) => handleChange('hora', e.target.value)}
                disabled={isSubmitting}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                  errors.hora ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.hora && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle size={14} />
                  <span>{errors.hora}</span>
                </div>
              )}
              <p className="text-xs text-gray-500 mt-1">Horario de servicio: 12:00 - 23:59</p>
            </div>
          </div>

          {/* Personas */}
          <div>
            <label htmlFor="pax" className="block text-sm font-medium text-gray-700 mb-2">
              <div className="flex items-center gap-2">
                <Users size={16} />
                Número de Personas *
              </div>
            </label>
            <input
              id="pax"
              type="number"
              min="1"
              max="20"
              value={formData.pax || ''}
              onChange={(e) => handleChange('pax', parseInt(e.target.value) || 0)}
              disabled={isSubmitting}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                errors.pax ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.pax && (
              <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                <AlertCircle size={14} />
                <span>{errors.pax}</span>
              </div>
            )}
          </div>

          {/* Estado (solo en modo edición) */}
          {mode === 'edit' && (
            <div>
              <label htmlFor="estado" className="block text-sm font-medium text-gray-700 mb-2">
                Estado
              </label>
              <select
                id="estado"
                value={formData.estado || 'Pendiente'}
                onChange={(e) => handleChange('estado', e.target.value as ReservationStatus)}
                disabled={isSubmitting}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              >
                <option value="Pendiente">Pendiente</option>
                <option value="Confirmada">Confirmada</option>
                <option value="Sentada">Sentada</option>
                <option value="Completada">Completada</option>
                <option value="Cancelada">Cancelada</option>
              </select>
            </div>
          )}

          {/* Notas */}
          <div>
            <label htmlFor="notas" className="block text-sm font-medium text-gray-700 mb-2">
              <div className="flex items-center gap-2">
                <FileText size={16} />
                Solicitudes Especiales
              </div>
            </label>
            <textarea
              id="notas"
              rows={3}
              value={formData.notas || ''}
              onChange={(e) => handleChange('notas', e.target.value)}
              disabled={isSubmitting}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
              placeholder="Ej: Silla para bebé, mesa cerca ventana, alergias alimentarias..."
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Guardando...</span>
                </>
              ) : (
                <span>{mode === 'create' ? 'Crear Reserva' : 'Guardar Cambios'}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
