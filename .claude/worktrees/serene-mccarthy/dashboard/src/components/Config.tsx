import { useState } from 'react';
import {
  useConfig,
  useUpdateHorarios,
  useCreateFestivo,
  useUpdateFestivo,
  useDeleteFestivo,
  useUpdateCapacidad,
  useUpdateTiemposReserva,
  useStaff,
  useCreateUsuarioStaff,
  useUpdateUsuarioStaff,
  useDeleteUsuarioStaff,
  type HorarioConfig,
  type FestivoConfig,
  type CapacidadConfig,
  type TiempoReservaConfig,
  type UsuarioStaff,
} from '../hooks/useConfig';
import {
  Clock,
  Calendar,
  Users,
  Settings,
  MapPin,
  Timer,
  UserCog,
  Plus,
  Edit,
  Trash2,
  Save,
  X,
  AlertCircle,
  CheckCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
  Shield,
  Mail,
  Phone,
  Key,
} from 'lucide-react';

const DIAS_SEMANA = [
  { key: 'lunes', label: 'Lunes' },
  { key: 'martes', label: 'Martes' },
  { key: 'miercoles', label: 'Miércoles' },
  { key: 'jueves', label: 'Jueves' },
  { key: 'viernes', label: 'Viernes' },
  { key: 'sabado', label: 'Sábado' },
  { key: 'domingo', label: 'Domingo' },
] as const;

const ROLES_CONFIG = {
  admin: {
    label: 'Administrador',
    color: 'bg-purple-500/10 text-purple-700 border-purple-500/20',
    icon: Shield,
  },
  manager: {
    label: 'Encargado',
    color: 'bg-blue-500/10 text-blue-700 border-blue-500/20',
    icon: Settings,
  },
  waiter: {
    label: 'Camarero',
    color: 'bg-green-500/10 text-green-700 border-green-500/20',
    icon: Users,
  },
  cook: {
    label: 'Cocinero',
    color: 'bg-orange-500/10 text-orange-700 border-orange-500/20',
    icon: Clock,
  },
};

type Section = 'horarios' | 'festivos' | 'capacidad' | 'tiempos' | 'staff';

export default function Config() {
  const [activeSection, setActiveSection] = useState<Section>('horarios');
  const [editingHorarios, setEditingHorarios] = useState(false);
  const [editingCapacidad, setEditingCapacidad] = useState(false);
  const [editingTiempos, setEditingTiempos] = useState(false);
  const [showFestivoModal, setShowFestivoModal] = useState(false);
  const [showStaffModal, setShowStaffModal] = useState(false);
  const [editingFestivo, setEditingFestivo] = useState<FestivoConfig | null>(null);
  const [editingStaff, setEditingStaff] = useState<UsuarioStaff | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ type: 'festivo' | 'staff'; id: string } | null>(null);

  const { data: configData, isLoading: configLoading, error: configError } = useConfig();
  const { data: staffData, isLoading: staffLoading } = useStaff();

  const updateHorariosMutation = useUpdateHorarios();
  const createFestivoMutation = useCreateFestivo();
  const updateFestivoMutation = useUpdateFestivo();
  const deleteFestivoMutation = useDeleteFestivo();
  const updateCapacidadMutation = useUpdateCapacidad();
  const updateTiemposMutation = useUpdateTiemposReserva();
  const createStaffMutation = useCreateUsuarioStaff();
  const updateStaffMutation = useUpdateUsuarioStaff();
  const deleteStaffMutation = useDeleteUsuarioStaff();

  const [horariosForm, setHorariosForm] = useState<HorarioConfig[]>([]);
  const [capacidadForm, setCapacidadForm] = useState<CapacidadConfig | null>(null);
  const [tiemposForm, setTiemposForm] = useState<TiempoReservaConfig | null>(null);
  const [festivoForm, setFestivoForm] = useState<Partial<FestivoConfig>>({
    nombre: '',
    fecha: '',
    cerrado: false,
  });
  const [staffForm, setStaffForm] = useState<Partial<UsuarioStaff & { password: string }>>({
    username: '',
    email: '',
    nombre_completo: '',
    rol: 'waiter',
    activo: true,
    password: '',
  });

  if (configLoading || staffLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-purple-600 animate-spin mx-auto mb-4" />
          <p className="text-slate-600 font-medium">Cargando configuración...</p>
        </div>
      </div>
    );
  }

  if (configError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 flex items-center justify-center p-6">
        <div className="bg-white/80 backdrop-blur-sm border border-red-200/60 rounded-2xl p-8 max-w-md w-full shadow-lg shadow-red-500/10">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-red-500/10 rounded-xl">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Error al cargar</h3>
          </div>
          <p className="text-slate-600 mb-6">No se pudo cargar la configuración del restaurante.</p>
        </div>
      </div>
    );
  }

  const config = configData!;
  const staff = staffData?.users || [];

  const handleSaveHorarios = () => {
    updateHorariosMutation.mutate(
      { horarios: horariosForm },
      {
        onSuccess: () => {
          setEditingHorarios(false);
        },
      }
    );
  };

  const handleSaveCapacidad = () => {
    if (!capacidadForm) return;
    updateCapacidadMutation.mutate(
      { capacidad: capacidadForm },
      {
        onSuccess: () => {
          setEditingCapacidad(false);
        },
      }
    );
  };

  const handleSaveTiempos = () => {
    if (!tiemposForm) return;
    updateTiemposMutation.mutate(
      { tiempos: tiemposForm },
      {
        onSuccess: () => {
          setEditingTiempos(false);
        },
      }
    );
  };

  const handleSaveFestivo = () => {
    if (editingFestivo) {
      updateFestivoMutation.mutate(
        {
          id: editingFestivo.id,
          festivo: festivoForm,
        },
        {
          onSuccess: () => {
            setShowFestivoModal(false);
            setEditingFestivo(null);
            setFestivoForm({ nombre: '', fecha: '', cerrado: false });
          },
        }
      );
    } else {
      createFestivoMutation.mutate(
        {
          festivo: festivoForm as Omit<FestivoConfig, 'id'>,
        },
        {
          onSuccess: () => {
            setShowFestivoModal(false);
            setFestivoForm({ nombre: '', fecha: '', cerrado: false });
          },
        }
      );
    }
  };

  const handleDeleteFestivo = (id: string) => {
    deleteFestivoMutation.mutate(
      { id },
      {
        onSuccess: () => {
          setDeleteConfirm(null);
        },
      }
    );
  };

  const handleSaveStaff = () => {
    if (editingStaff) {
      const { password, ...updateData } = staffForm;
      updateStaffMutation.mutate(
        {
          id: editingStaff.id,
          data: updateData,
        },
        {
          onSuccess: () => {
            setShowStaffModal(false);
            setEditingStaff(null);
            setStaffForm({ username: '', email: '', nombre_completo: '', rol: 'waiter', activo: true, password: '' });
          },
        }
      );
    } else {
      createStaffMutation.mutate(
        {
          data: staffForm as Omit<UsuarioStaff, 'id' | 'created_at' | 'last_login'> & { password: string },
        },
        {
          onSuccess: () => {
            setShowStaffModal(false);
            setStaffForm({ username: '', email: '', nombre_completo: '', rol: 'waiter', activo: true, password: '' });
          },
        }
      );
    }
  };

  const handleDeleteStaff = (id: string) => {
    deleteStaffMutation.mutate(
      { id },
      {
        onSuccess: () => {
          setDeleteConfirm(null);
        },
      }
    );
  };

  const sections = [
    { key: 'horarios' as Section, label: 'Horarios', icon: Clock, count: config.horarios.length },
    { key: 'festivos' as Section, label: 'Festivos', icon: Calendar, count: config.festivos.length },
    { key: 'capacidad' as Section, label: 'Capacidad', icon: MapPin, count: config.capacidad.capacidad_total },
    { key: 'tiempos' as Section, label: 'Tiempos', icon: Timer, count: null },
    { key: 'staff' as Section, label: 'Personal', icon: UserCog, count: staff.length },
  ];

  const formatTime = (time: string) => {
    return time.substring(0, 5);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-8 mb-6 shadow-lg shadow-purple-500/10">
          <div className="flex items-center gap-4 mb-2">
            <div className="p-4 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg shadow-purple-500/30">
              <Settings className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Configuración</h1>
              <p className="text-slate-600 mt-1">Gestiona la configuración del restaurante</p>
            </div>
          </div>
        </div>

        {/* Section Tabs */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-2 mb-6 shadow-lg shadow-purple-500/10">
          <div className="flex gap-2 overflow-x-auto">
            {sections.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.key;
              return (
                <button
                  key={section.key}
                  onClick={() => setActiveSection(section.key)}
                  className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg shadow-purple-500/30'
                      : 'text-slate-600 hover:bg-slate-50/50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="whitespace-nowrap">{section.label}</span>
                  {section.count !== null && (
                    <span
                      className={`px-2 py-0.5 rounded-lg text-xs font-semibold ${
                        isActive ? 'bg-white/20 text-white' : 'bg-purple-500/10 text-purple-600'
                      }`}
                    >
                      {section.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Horarios Section */}
        {activeSection === 'horarios' && (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-8 shadow-lg shadow-purple-500/10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <Clock className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Horarios de Apertura</h2>
                  <p className="text-sm text-slate-600">Configura los horarios por día de la semana</p>
                </div>
              </div>
              {!editingHorarios && (
                <button
                  onClick={() => {
                    setHorariosForm(config.horarios);
                    setEditingHorarios(true);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30"
                >
                  <Edit className="w-4 h-4" />
                  Editar
                </button>
              )}
            </div>

            <div className="space-y-4">
              {(editingHorarios ? horariosForm : config.horarios).map((horario, index) => {
                const diaLabel = DIAS_SEMANA.find((d) => d.key === horario.dia_semana)?.label || horario.dia_semana;
                return (
                  <div
                    key={horario.dia_semana}
                    className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-slate-900">{diaLabel}</h3>
                      {editingHorarios && (
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={horario.abierto}
                            onChange={(e) => {
                              const newHorarios = [...horariosForm];
                              newHorarios[index].abierto = e.target.checked;
                              setHorariosForm(newHorarios);
                            }}
                            className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500"
                          />
                          <span className="text-sm font-medium text-slate-700">Abierto</span>
                        </label>
                      )}
                      {!editingHorarios && (
                        <span
                          className={`px-3 py-1 rounded-lg text-xs font-semibold border ${
                            horario.abierto
                              ? 'bg-green-500/10 text-green-700 border-green-500/20'
                              : 'bg-slate-500/10 text-slate-700 border-slate-500/20'
                          }`}
                        >
                          {horario.abierto ? 'Abierto' : 'Cerrado'}
                        </span>
                      )}
                    </div>

                    {horario.abierto && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Almuerzo */}
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Almuerzo</label>
                          {editingHorarios ? (
                            <div className="flex gap-2">
                              <input
                                type="time"
                                value={horario.turnos.almuerzo?.inicio || ''}
                                onChange={(e) => {
                                  const newHorarios = [...horariosForm];
                                  if (!newHorarios[index].turnos.almuerzo) {
                                    newHorarios[index].turnos.almuerzo = { inicio: '', fin: '' };
                                  }
                                  newHorarios[index].turnos.almuerzo!.inicio = e.target.value;
                                  setHorariosForm(newHorarios);
                                }}
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              />
                              <span className="text-slate-500">-</span>
                              <input
                                type="time"
                                value={horario.turnos.almuerzo?.fin || ''}
                                onChange={(e) => {
                                  const newHorarios = [...horariosForm];
                                  if (!newHorarios[index].turnos.almuerzo) {
                                    newHorarios[index].turnos.almuerzo = { inicio: '', fin: '' };
                                  }
                                  newHorarios[index].turnos.almuerzo!.fin = e.target.value;
                                  setHorariosForm(newHorarios);
                                }}
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              />
                            </div>
                          ) : horario.turnos.almuerzo ? (
                            <div className="text-sm text-slate-600">
                              {formatTime(horario.turnos.almuerzo.inicio)} - {formatTime(horario.turnos.almuerzo.fin)}
                            </div>
                          ) : (
                            <div className="text-sm text-slate-400 italic">No configurado</div>
                          )}
                        </div>

                        {/* Cena */}
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-2">Cena</label>
                          {editingHorarios ? (
                            <div className="flex gap-2">
                              <input
                                type="time"
                                value={horario.turnos.cena?.inicio || ''}
                                onChange={(e) => {
                                  const newHorarios = [...horariosForm];
                                  if (!newHorarios[index].turnos.cena) {
                                    newHorarios[index].turnos.cena = { inicio: '', fin: '' };
                                  }
                                  newHorarios[index].turnos.cena!.inicio = e.target.value;
                                  setHorariosForm(newHorarios);
                                }}
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              />
                              <span className="text-slate-500">-</span>
                              <input
                                type="time"
                                value={horario.turnos.cena?.fin || ''}
                                onChange={(e) => {
                                  const newHorarios = [...horariosForm];
                                  if (!newHorarios[index].turnos.cena) {
                                    newHorarios[index].turnos.cena = { inicio: '', fin: '' };
                                  }
                                  newHorarios[index].turnos.cena!.fin = e.target.value;
                                  setHorariosForm(newHorarios);
                                }}
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              />
                            </div>
                          ) : horario.turnos.cena ? (
                            <div className="text-sm text-slate-600">
                              {formatTime(horario.turnos.cena.inicio)} - {formatTime(horario.turnos.cena.fin)}
                            </div>
                          ) : (
                            <div className="text-sm text-slate-400 italic">No configurado</div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {editingHorarios && (
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveHorarios}
                  disabled={updateHorariosMutation.isPending}
                  className="flex items-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30 disabled:opacity-50"
                >
                  {updateHorariosMutation.isPending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Save className="w-5 h-5" />
                  )}
                  Guardar Cambios
                </button>
                <button
                  onClick={() => setEditingHorarios(false)}
                  disabled={updateHorariosMutation.isPending}
                  className="flex items-center gap-2 px-6 py-3 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                  Cancelar
                </button>
              </div>
            )}
          </div>
        )}

        {/* Festivos Section */}
        {activeSection === 'festivos' && (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-8 shadow-lg shadow-purple-500/10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <Calendar className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Festivos y Días Especiales</h2>
                  <p className="text-sm text-slate-600">Gestiona los días festivos y horarios especiales</p>
                </div>
              </div>
              <button
                onClick={() => setShowFestivoModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30"
              >
                <Plus className="w-4 h-4" />
                Agregar Festivo
              </button>
            </div>

            {config.festivos.length === 0 ? (
              <div className="text-center py-12">
                <div className="p-4 bg-slate-100 rounded-2xl w-fit mx-auto mb-4">
                  <Calendar className="w-12 h-12 text-slate-400" />
                </div>
                <p className="text-slate-600 font-medium mb-2">No hay festivos configurados</p>
                <p className="text-sm text-slate-500">Agrega días festivos y horarios especiales</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {config.festivos.map((festivo) => (
                  <div
                    key={festivo.id}
                    className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="font-semibold text-slate-900">{festivo.nombre}</h3>
                      <div className="flex gap-1">
                        <button
                          onClick={() => {
                            setEditingFestivo(festivo);
                            setFestivoForm(festivo);
                            setShowFestivoModal(true);
                          }}
                          className="p-2 text-purple-600 hover:bg-purple-500/10 rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeleteConfirm({ type: 'festivo', id: festivo.id })}
                          className="p-2 text-red-600 hover:bg-red-500/10 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-slate-600">
                        <Calendar className="w-4 h-4" />
                        {formatDate(festivo.fecha)}
                      </div>

                      <span
                        className={`inline-block px-3 py-1 rounded-lg text-xs font-semibold border ${
                          festivo.cerrado
                            ? 'bg-red-500/10 text-red-700 border-red-500/20'
                            : 'bg-green-500/10 text-green-700 border-green-500/20'
                        }`}
                      >
                        {festivo.cerrado ? 'Cerrado' : 'Horario Especial'}
                      </span>

                      {festivo.horario_especial && (
                        <div className="text-sm text-slate-600">
                          <Clock className="w-4 h-4 inline mr-1" />
                          {formatTime(festivo.horario_especial.inicio)} - {formatTime(festivo.horario_especial.fin)}
                        </div>
                      )}

                      {festivo.notas && (
                        <p className="text-sm text-slate-500 italic mt-2">{festivo.notas}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Capacidad Section */}
        {activeSection === 'capacidad' && (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-8 shadow-lg shadow-purple-500/10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <MapPin className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Capacidad del Restaurante</h2>
                  <p className="text-sm text-slate-600">Configura la capacidad por zonas</p>
                </div>
              </div>
              {!editingCapacidad && (
                <button
                  onClick={() => {
                    setCapacidadForm(config.capacidad);
                    setEditingCapacidad(true);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30"
                >
                  <Edit className="w-4 h-4" />
                  Editar
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6">
                <label className="block text-sm font-medium text-slate-700 mb-2">Capacidad Total</label>
                {editingCapacidad ? (
                  <input
                    type="number"
                    value={capacidadForm?.capacidad_total || 0}
                    onChange={(e) =>
                      setCapacidadForm({ ...capacidadForm!, capacidad_total: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg font-semibold"
                  />
                ) : (
                  <p className="text-3xl font-bold text-slate-900">{config.capacidad.capacidad_total}</p>
                )}
                <p className="text-sm text-slate-500 mt-1">personas</p>
              </div>

              <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6">
                <label className="block text-sm font-medium text-slate-700 mb-2">Capacidad Interior</label>
                {editingCapacidad ? (
                  <input
                    type="number"
                    value={capacidadForm?.capacidad_interior || 0}
                    onChange={(e) =>
                      setCapacidadForm({ ...capacidadForm!, capacidad_interior: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg font-semibold"
                  />
                ) : (
                  <p className="text-3xl font-bold text-slate-900">{config.capacidad.capacidad_interior}</p>
                )}
                <p className="text-sm text-slate-500 mt-1">personas</p>
              </div>

              <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6">
                <label className="block text-sm font-medium text-slate-700 mb-2">Capacidad Terraza</label>
                {editingCapacidad ? (
                  <input
                    type="number"
                    value={capacidadForm?.capacidad_terraza || 0}
                    onChange={(e) =>
                      setCapacidadForm({ ...capacidadForm!, capacidad_terraza: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg font-semibold"
                  />
                ) : (
                  <p className="text-3xl font-bold text-slate-900">{config.capacidad.capacidad_terraza}</p>
                )}
                <p className="text-sm text-slate-500 mt-1">personas</p>
              </div>

              <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6">
                <label className="block text-sm font-medium text-slate-700 mb-2">Máximo por Reserva</label>
                {editingCapacidad ? (
                  <input
                    type="number"
                    value={capacidadForm?.max_por_reserva || 0}
                    onChange={(e) =>
                      setCapacidadForm({ ...capacidadForm!, max_por_reserva: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg font-semibold"
                  />
                ) : (
                  <p className="text-3xl font-bold text-slate-900">{config.capacidad.max_por_reserva}</p>
                )}
                <p className="text-sm text-slate-500 mt-1">personas</p>
              </div>
            </div>

            {editingCapacidad && (
              <div className="mt-6">
                <label className="flex items-center gap-3 bg-slate-50/50 border border-slate-200/60 rounded-xl p-4">
                  <input
                    type="checkbox"
                    checked={capacidadForm?.grupos_grandes_requieren_confirmacion || false}
                    onChange={(e) =>
                      setCapacidadForm({
                        ...capacidadForm!,
                        grupos_grandes_requieren_confirmacion: e.target.checked,
                      })
                    }
                    className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <div className="flex-1">
                    <span className="text-sm font-medium text-slate-700">
                      Grupos grandes requieren confirmación
                    </span>
                    <p className="text-xs text-slate-500 mt-1">
                      Los grupos de más de {capacidadForm?.umbral_grupo_grande || 0} personas necesitarán confirmación
                    </p>
                  </div>
                </label>

                <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-4 mt-4">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Umbral de Grupo Grande
                  </label>
                  <input
                    type="number"
                    value={capacidadForm?.umbral_grupo_grande || 0}
                    onChange={(e) =>
                      setCapacidadForm({ ...capacidadForm!, umbral_grupo_grande: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
            )}

            {editingCapacidad && (
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveCapacidad}
                  disabled={updateCapacidadMutation.isPending}
                  className="flex items-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30 disabled:opacity-50"
                >
                  {updateCapacidadMutation.isPending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Save className="w-5 h-5" />
                  )}
                  Guardar Cambios
                </button>
                <button
                  onClick={() => setEditingCapacidad(false)}
                  disabled={updateCapacidadMutation.isPending}
                  className="flex items-center gap-2 px-6 py-3 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                  Cancelar
                </button>
              </div>
            )}
          </div>
        )}

        {/* Tiempos Section */}
        {activeSection === 'tiempos' && (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-8 shadow-lg shadow-purple-500/10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <Timer className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Tiempos de Reserva</h2>
                  <p className="text-sm text-slate-600">Duración estimada por tamaño de grupo</p>
                </div>
              </div>
              {!editingTiempos && (
                <button
                  onClick={() => {
                    setTiemposForm(config.tiempos_reserva);
                    setEditingTiempos(true);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30"
                >
                  <Edit className="w-4 h-4" />
                  Editar
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { key: 'pax_1_2', label: '1-2 personas' },
                { key: 'pax_3_4', label: '3-4 personas' },
                { key: 'pax_5_6', label: '5-6 personas' },
                { key: 'pax_7_10', label: '7-10 personas' },
                { key: 'pax_11_plus', label: '11+ personas' },
              ].map((item) => (
                <div key={item.key} className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6">
                  <label className="block text-sm font-medium text-slate-700 mb-2">{item.label}</label>
                  {editingTiempos ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        value={tiemposForm?.[item.key as keyof TiempoReservaConfig] || 0}
                        onChange={(e) =>
                          setTiemposForm({
                            ...tiemposForm!,
                            [item.key]: parseInt(e.target.value),
                          })
                        }
                        className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg font-semibold"
                      />
                      <span className="text-slate-600">min</span>
                    </div>
                  ) : (
                    <div className="flex items-baseline gap-2">
                      <p className="text-3xl font-bold text-slate-900">
                        {config.tiempos_reserva[item.key as keyof TiempoReservaConfig]}
                      </p>
                      <span className="text-slate-500">minutos</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {editingTiempos && (
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveTiempos}
                  disabled={updateTiemposMutation.isPending}
                  className="flex items-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30 disabled:opacity-50"
                >
                  {updateTiemposMutation.isPending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Save className="w-5 h-5" />
                  )}
                  Guardar Cambios
                </button>
                <button
                  onClick={() => setEditingTiempos(false)}
                  disabled={updateTiemposMutation.isPending}
                  className="flex items-center gap-2 px-6 py-3 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                  Cancelar
                </button>
              </div>
            )}
          </div>
        )}

        {/* Staff Section */}
        {activeSection === 'staff' && (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-8 shadow-lg shadow-purple-500/10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/10 rounded-xl">
                  <UserCog className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Personal del Restaurante</h2>
                  <p className="text-sm text-slate-600">Gestiona los usuarios y sus roles</p>
                </div>
              </div>
              <button
                onClick={() => setShowStaffModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30"
              >
                <Plus className="w-4 h-4" />
                Agregar Usuario
              </button>
            </div>

            {staff.length === 0 ? (
              <div className="text-center py-12">
                <div className="p-4 bg-slate-100 rounded-2xl w-fit mx-auto mb-4">
                  <UserCog className="w-12 h-12 text-slate-400" />
                </div>
                <p className="text-slate-600 font-medium mb-2">No hay usuarios configurados</p>
                <p className="text-sm text-slate-500">Agrega usuarios del staff del restaurante</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {staff.map((user) => {
                  const roleConfig = ROLES_CONFIG[user.rol];
                  const RoleIcon = roleConfig.icon;
                  return (
                    <div
                      key={user.id}
                      className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-purple-500/10 rounded-lg">
                            <RoleIcon className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-slate-900">{user.nombre_completo}</h3>
                            <p className="text-sm text-slate-500">@{user.username}</p>
                          </div>
                        </div>
                        <div className="flex gap-1">
                          <button
                            onClick={() => {
                              setEditingStaff(user);
                              setStaffForm({
                                username: user.username,
                                email: user.email,
                                nombre_completo: user.nombre_completo,
                                rol: user.rol,
                                activo: user.activo,
                                password: '',
                              });
                              setShowStaffModal(true);
                            }}
                            className="p-2 text-purple-600 hover:bg-purple-500/10 rounded-lg transition-colors"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setDeleteConfirm({ type: 'staff', id: user.id })}
                            className="p-2 text-red-600 hover:bg-red-500/10 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <span className={`inline-block px-3 py-1 rounded-lg text-xs font-semibold border ${roleConfig.color}`}>
                          {roleConfig.label}
                        </span>

                        {user.email && (
                          <div className="flex items-center gap-2 text-sm text-slate-600">
                            <Mail className="w-4 h-4" />
                            {user.email}
                          </div>
                        )}

                        <div className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-200">
                          <span
                            className={`px-2 py-1 rounded text-xs font-semibold ${
                              user.activo
                                ? 'bg-green-500/10 text-green-700'
                                : 'bg-slate-500/10 text-slate-700'
                            }`}
                          >
                            {user.activo ? 'Activo' : 'Inactivo'}
                          </span>
                          {user.last_login && (
                            <span className="text-xs text-slate-500">
                              Último acceso: {formatDate(user.last_login)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Festivo Modal */}
        {showFestivoModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
              <h3 className="text-xl font-bold text-slate-900 mb-6">
                {editingFestivo ? 'Editar Festivo' : 'Nuevo Festivo'}
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Nombre</label>
                  <input
                    type="text"
                    value={festivoForm.nombre || ''}
                    onChange={(e) => setFestivoForm({ ...festivoForm, nombre: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Ej: Navidad"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Fecha</label>
                  <input
                    type="date"
                    value={festivoForm.fecha || ''}
                    onChange={(e) => setFestivoForm({ ...festivoForm, fecha: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={festivoForm.cerrado || false}
                    onChange={(e) => setFestivoForm({ ...festivoForm, cerrado: e.target.checked })}
                    className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <span className="text-sm font-medium text-slate-700">Cerrado todo el día</span>
                </label>

                {!festivoForm.cerrado && (
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Horario Especial</label>
                    <div className="flex gap-2">
                      <input
                        type="time"
                        value={festivoForm.horario_especial?.inicio || ''}
                        onChange={(e) =>
                          setFestivoForm({
                            ...festivoForm,
                            horario_especial: {
                              inicio: e.target.value,
                              fin: festivoForm.horario_especial?.fin || '',
                            },
                          })
                        }
                        className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                      <span className="text-slate-500">-</span>
                      <input
                        type="time"
                        value={festivoForm.horario_especial?.fin || ''}
                        onChange={(e) =>
                          setFestivoForm({
                            ...festivoForm,
                            horario_especial: {
                              inicio: festivoForm.horario_especial?.inicio || '',
                              fin: e.target.value,
                            },
                          })
                        }
                        className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Notas (opcional)</label>
                  <textarea
                    value={festivoForm.notas || ''}
                    onChange={(e) => setFestivoForm({ ...festivoForm, notas: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    rows={3}
                    placeholder="Información adicional sobre este día festivo"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveFestivo}
                  disabled={createFestivoMutation.isPending || updateFestivoMutation.isPending}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30 disabled:opacity-50"
                >
                  {(createFestivoMutation.isPending || updateFestivoMutation.isPending) ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Save className="w-5 h-5" />
                  )}
                  Guardar
                </button>
                <button
                  onClick={() => {
                    setShowFestivoModal(false);
                    setEditingFestivo(null);
                    setFestivoForm({ nombre: '', fecha: '', cerrado: false });
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Staff Modal */}
        {showStaffModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
              <h3 className="text-xl font-bold text-slate-900 mb-6">
                {editingStaff ? 'Editar Usuario' : 'Nuevo Usuario'}
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Nombre Completo</label>
                  <input
                    type="text"
                    value={staffForm.nombre_completo || ''}
                    onChange={(e) => setStaffForm({ ...staffForm, nombre_completo: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Juan Pérez"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Usuario</label>
                  <input
                    type="text"
                    value={staffForm.username || ''}
                    onChange={(e) => setStaffForm({ ...staffForm, username: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="jperez"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={staffForm.email || ''}
                    onChange={(e) => setStaffForm({ ...staffForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="juan@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Rol</label>
                  <select
                    value={staffForm.rol || 'waiter'}
                    onChange={(e) => setStaffForm({ ...staffForm, rol: e.target.value as any })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {Object.entries(ROLES_CONFIG).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.label}
                      </option>
                    ))}
                  </select>
                </div>

                {!editingStaff && (
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Contraseña</label>
                    <input
                      type="password"
                      value={staffForm.password || ''}
                      onChange={(e) => setStaffForm({ ...staffForm, password: e.target.value })}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="••••••••"
                    />
                  </div>
                )}

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={staffForm.activo || false}
                    onChange={(e) => setStaffForm({ ...staffForm, activo: e.target.checked })}
                    className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <span className="text-sm font-medium text-slate-700">Usuario activo</span>
                </label>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveStaff}
                  disabled={createStaffMutation.isPending || updateStaffMutation.isPending}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors shadow-lg shadow-purple-500/30 disabled:opacity-50"
                >
                  {(createStaffMutation.isPending || updateStaffMutation.isPending) ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Save className="w-5 h-5" />
                  )}
                  Guardar
                </button>
                <button
                  onClick={() => {
                    setShowStaffModal(false);
                    setEditingStaff(null);
                    setStaffForm({ username: '', email: '', nombre_completo: '', rol: 'waiter', activo: true, password: '' });
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-red-500/10 rounded-xl">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900">Confirmar Eliminación</h3>
              </div>
              <p className="text-slate-600 mb-6">
                ¿Estás seguro de que deseas eliminar este {deleteConfirm.type === 'festivo' ? 'festivo' : 'usuario'}?
                Esta acción no se puede deshacer.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    if (deleteConfirm.type === 'festivo') {
                      handleDeleteFestivo(deleteConfirm.id);
                    } else {
                      handleDeleteStaff(deleteConfirm.id);
                    }
                  }}
                  disabled={deleteFestivoMutation.isPending || deleteStaffMutation.isPending}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors shadow-lg shadow-red-500/30 disabled:opacity-50"
                >
                  {(deleteFestivoMutation.isPending || deleteStaffMutation.isPending) ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Trash2 className="w-5 h-5" />
                  )}
                  Eliminar
                </button>
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
