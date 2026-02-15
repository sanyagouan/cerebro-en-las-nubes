import { useState, useEffect, useRef } from 'react';
import { X, AlertCircle } from 'lucide-react';
import { Table, TableLocation, TableStatus } from '../hooks/useTables';

interface MesaFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Table>) => Promise<void>;
  initialData?: Table | null;
  mode: 'create' | 'edit';
  existingTables?: Table[];
}

export default function MesaForm({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  mode,
  existingTables = [],
}: MesaFormProps) {
  const [formData, setFormData] = useState<Partial<Table>>({
    numero: '',
    capacidad: 2,
    capacidad_max: undefined,
    ubicacion: 'Interior' as TableLocation,
    estado: 'Libre' as TableStatus,
    notas: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const firstInputRef = useRef<HTMLInputElement>(null);

  // Reset form when modal opens/closes or initialData changes
  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && initialData) {
        setFormData({
          numero: initialData.numero,
          capacidad: initialData.capacidad,
          capacidad_max: initialData.capacidad_max,
          ubicacion: initialData.ubicacion,
          estado: initialData.estado,
          notas: initialData.notas || '',
        });
      } else {
        setFormData({
          numero: '',
          capacidad: 2,
          capacidad_max: undefined,
          ubicacion: 'Interior' as TableLocation,
          estado: 'Libre' as TableStatus,
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
  }, [isOpen, mode, initialData]);

  // ESC key handler
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent body scroll
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, isSubmitting, onClose]);

  // Validation
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Número validation
    if (!formData.numero?.trim()) {
      newErrors.numero = 'El número de mesa es requerido';
    } else {
      // Check uniqueness (exclude current table if editing)
      const isDuplicate = existingTables.some(
        (table) =>
          table.numero.toLowerCase() === formData.numero!.trim().toLowerCase() &&
          (mode === 'create' || table.id !== initialData?.id)
      );
      if (isDuplicate) {
        newErrors.numero = 'Ya existe una mesa con este número';
      }
    }

    // Capacidad validation
    if (!formData.capacidad || formData.capacidad < 1) {
      newErrors.capacidad = 'La capacidad mínima debe ser al menos 1';
    } else if (formData.capacidad > 20) {
      newErrors.capacidad = 'La capacidad máxima no puede exceder 20';
    }

    // Capacidad_max validation (if provided)
    if (
      formData.capacidad_max !== undefined &&
      formData.capacidad_max !== null &&
      formData.capacidad !== undefined &&
      formData.capacidad_max < formData.capacidad
    ) {
      newErrors.capacidad_max = 'La capacidad ampliada debe ser mayor a la capacidad base';
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
      onClose(); // Close on success
    } catch (error) {
      // Error will be shown via toast in parent component
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
            {mode === 'create' ? 'Nueva Mesa' : 'Editar Mesa'}
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
          {/* Número */}
          <div>
            <label htmlFor="numero" className="block text-sm font-medium text-gray-700 mb-2">
              Número de Mesa *
            </label>
            <input
              ref={firstInputRef}
              id="numero"
              type="text"
              value={formData.numero || ''}
              onChange={(e) => handleChange('numero', e.target.value)}
              disabled={isSubmitting}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                errors.numero ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Ej: Mesa 1, A1, VIP-1"
            />
            {errors.numero && (
              <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                <AlertCircle size={14} />
                <span>{errors.numero}</span>
              </div>
            )}
          </div>

          {/* Capacidad */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="capacidad" className="block text-sm font-medium text-gray-700 mb-2">
                Capacidad Base *
              </label>
              <input
                id="capacidad"
                type="number"
                min="1"
                max="20"
                value={formData.capacidad || ''}
                onChange={(e) => handleChange('capacidad', parseInt(e.target.value) || 0)}
                disabled={isSubmitting}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                  errors.capacidad ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.capacidad && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle size={14} />
                  <span>{errors.capacidad}</span>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="capacidad_max" className="block text-sm font-medium text-gray-700 mb-2">
                Capacidad Ampliada
              </label>
              <input
                id="capacidad_max"
                type="number"
                min="1"
                max="20"
                value={formData.capacidad_max || ''}
                onChange={(e) =>
                  handleChange('capacidad_max', e.target.value ? parseInt(e.target.value) : undefined)
                }
                disabled={isSubmitting}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                  errors.capacidad_max ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Opcional"
              />
              {errors.capacidad_max && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle size={14} />
                  <span>{errors.capacidad_max}</span>
                </div>
              )}
            </div>
          </div>

          {/* Ubicación y Estado */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="ubicacion" className="block text-sm font-medium text-gray-700 mb-2">
                Ubicación *
              </label>
              <select
                id="ubicacion"
                value={formData.ubicacion || 'Interior'}
                onChange={(e) => handleChange('ubicacion', e.target.value as TableLocation)}
                disabled={isSubmitting}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              >
                <option value="Interior">Interior</option>
                <option value="Terraza">Terraza</option>
              </select>
            </div>

            <div>
              <label htmlFor="estado" className="block text-sm font-medium text-gray-700 mb-2">
                Estado *
              </label>
              <select
                id="estado"
                value={formData.estado || 'Libre'}
                onChange={(e) => handleChange('estado', e.target.value as TableStatus)}
                disabled={isSubmitting}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              >
                <option value="Libre">Libre</option>
                <option value="Ocupada">Ocupada</option>
                <option value="Reservada">Reservada</option>
              </select>
            </div>
          </div>

          {/* Notas */}
          <div>
            <label htmlFor="notas" className="block text-sm font-medium text-gray-700 mb-2">
              Notas
            </label>
            <textarea
              id="notas"
              rows={3}
              value={formData.notas || ''}
              onChange={(e) => handleChange('notas', e.target.value)}
              disabled={isSubmitting}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
              placeholder="Ej: Vista ventana, acceso PMR, zona tranquila..."
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
                <span>{mode === 'create' ? 'Crear Mesa' : 'Guardar Cambios'}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
