import { useState, useMemo } from 'react';
import {
  Users,
  User,
  Star,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Tag,
  FileText,
  AlertCircle,
  TrendingUp,
  Plus,
  Edit,
  Trash2,
  Merge,
  ChevronRight,
  X,
  Search,
  Filter,
  Clock,
  CheckCircle,
  XCircle,
  MessageSquare,
  Heart,
  AlertTriangle,
  Crown,
  Save,
  Ban,
  UserX,
} from 'lucide-react';
import {
  useClientes,
  useCliente,
  useClienteStats,
  useCreateCliente,
  useUpdateCliente,
  useAddClienteNota,
  useUpdateClientePreferencias,
  useMergeClientes,
  type Cliente,
  type ClienteNota,
  type ClientePreferencias,
} from '../hooks/useClients';

const TIPO_CONFIG = {
  regular: {
    label: 'Regular',
    color: 'bg-blue-500/10 text-blue-700 border-blue-500/20',
    icon: User,
  },
  vip: {
    label: 'VIP',
    color: 'bg-purple-500/10 text-purple-700 border-purple-500/20',
    icon: Crown,
  },
  nuevo: {
    label: 'Nuevo',
    color: 'bg-green-500/10 text-green-700 border-green-500/20',
    icon: Star,
  },
  problema: {
    label: 'Problema',
    color: 'bg-red-500/10 text-red-700 border-red-500/20',
    icon: AlertTriangle,
  },
};

const TIPO_NOTA_CONFIG = {
  general: {
    label: 'General',
    color: 'bg-slate-500/10 text-slate-700',
    icon: MessageSquare,
  },
  preferencia: {
    label: 'Preferencia',
    color: 'bg-blue-500/10 text-blue-700',
    icon: Heart,
  },
  queja: {
    label: 'Queja',
    color: 'bg-red-500/10 text-red-700',
    icon: AlertCircle,
  },
  elogio: {
    label: 'Elogio',
    color: 'bg-green-500/10 text-green-700',
    icon: CheckCircle,
  },
  vip: {
    label: 'VIP',
    color: 'bg-purple-500/10 text-purple-700',
    icon: Crown,
  },
};

export default function Clients() {
  // Filters and search
  const [searchTerm, setSearchTerm] = useState('');
  const [tipoFilter, setTipoFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);

  // Modals and detail view
  const [selectedClienteId, setSelectedClienteId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showNotaModal, setShowNotaModal] = useState(false);
  const [showPreferenciasModal, setShowPreferenciasModal] = useState(false);
  const [showMergeModal, setShowMergeModal] = useState(false);

  // Forms
  const [clienteForm, setClienteForm] = useState<Partial<Cliente>>({
    nombre: '',
    telefono: '',
    email: '',
    tipo: 'nuevo',
    preferencias: {
      zona_favorita: undefined,
      solicitudes_especiales: [],
      alergias: [],
      ocasiones_especiales: [],
    },
    notas: [],
    tags: [],
    activo: true,
  });

  const [notaForm, setNotaForm] = useState<Partial<ClienteNota>>({
    contenido: '',
    autor: '',
    tipo: 'general',
    privada: false,
  });

  const [preferenciasForm, setPreferenciasForm] = useState<ClientePreferencias>({
    zona_favorita: undefined,
    solicitudes_especiales: [],
    alergias: [],
    ocasiones_especiales: [],
  });

  const [mergeForm, setMergeForm] = useState({
    clienteSecundarioId: '',
  });

  // Tags input
  const [newTag, setNewTag] = useState('');

  // Queries
  const { data: clientesData, isLoading: clientesLoading, error: clientesError } = useClientes(
    100,
    tipoFilter,
    searchTerm
  );

  const { data: statsData, isLoading: statsLoading } = useClienteStats();

  const { data: selectedCliente, isLoading: clienteLoading } = useCliente(
    selectedClienteId || '',
    undefined
  );

  // Mutations
  const createClienteMutation = useCreateCliente();
  const updateClienteMutation = useUpdateCliente();
  const addNotaMutation = useAddClienteNota();
  const updatePreferenciasMutation = useUpdateClientePreferencias();
  const mergeClientesMutation = useMergeClientes();

  const clientes = clientesData?.clientes || [];
  const stats = statsData || {
    total_clientes: 0,
    clientes_nuevos_mes: 0,
    clientes_vip: 0,
    clientes_regulares: 0,
    tasa_retencion: 0,
    clientes_con_problemas: 0,
    distribucion_por_tipo: {
      regular: 0,
      vip: 0,
      nuevo: 0,
      problema: 0,
    },
  };

  // Handlers
  const handleCreateCliente = () => {
    createClienteMutation.mutate(
      { data: clienteForm as any },
      {
        onSuccess: () => {
          setShowCreateModal(false);
          setClienteForm({
            nombre: '',
            telefono: '',
            email: '',
            tipo: 'nuevo',
            preferencias: {
              zona_favorita: undefined,
              solicitudes_especiales: [],
              alergias: [],
              ocasiones_especiales: [],
            },
            notas: [],
            tags: [],
            activo: true,
          });
        },
      }
    );
  };

  const handleUpdateCliente = () => {
    if (!selectedClienteId) return;
    updateClienteMutation.mutate(
      { clienteId: selectedClienteId, data: clienteForm },
      {
        onSuccess: () => {
          setShowEditModal(false);
        },
      }
    );
  };

  const handleAddNota = () => {
    if (!selectedClienteId) return;
    addNotaMutation.mutate(
      { clienteId: selectedClienteId, nota: notaForm as any },
      {
        onSuccess: () => {
          setShowNotaModal(false);
          setNotaForm({
            contenido: '',
            autor: '',
            tipo: 'general',
            privada: false,
          });
        },
      }
    );
  };

  const handleUpdatePreferencias = () => {
    if (!selectedClienteId) return;
    updatePreferenciasMutation.mutate(
      { clienteId: selectedClienteId, preferencias: preferenciasForm },
      {
        onSuccess: () => {
          setShowPreferenciasModal(false);
        },
      }
    );
  };

  const handleMergeClientes = () => {
    if (!selectedClienteId || !mergeForm.clienteSecundarioId) return;
    mergeClientesMutation.mutate(
      {
        clienteIdPrincipal: selectedClienteId,
        clienteIdSecundario: mergeForm.clienteSecundarioId,
      },
      {
        onSuccess: () => {
          setShowMergeModal(false);
          setSelectedClienteId(null);
          setMergeForm({ clienteSecundarioId: '' });
        },
      }
    );
  };

  const handleAddTag = () => {
    if (newTag.trim() && clienteForm.tags) {
      setClienteForm({
        ...clienteForm,
        tags: [...clienteForm.tags, newTag.trim()],
      });
      setNewTag('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    if (clienteForm.tags) {
      setClienteForm({
        ...clienteForm,
        tags: clienteForm.tags.filter((t) => t !== tag),
      });
    }
  };

  const handleAddSolicitudEspecial = (solicitud: string) => {
    if (preferenciasForm.solicitudes_especiales) {
      setPreferenciasForm({
        ...preferenciasForm,
        solicitudes_especiales: [...preferenciasForm.solicitudes_especiales, solicitud],
      });
    }
  };

  const handleAddAlergia = (alergia: string) => {
    if (preferenciasForm.alergias) {
      setPreferenciasForm({
        ...preferenciasForm,
        alergias: [...preferenciasForm.alergias, alergia],
      });
    }
  };

  const handleAddOcasionEspecial = (ocasion: string) => {
    if (preferenciasForm.ocasiones_especiales) {
      setPreferenciasForm({
        ...preferenciasForm,
        ocasiones_especiales: [...preferenciasForm.ocasiones_especiales, ocasion],
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (clientesLoading || statsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600 font-medium">Cargando clientes...</p>
        </div>
      </div>
    );
  }

  if (clientesError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 flex items-center justify-center p-6">
        <div className="bg-white/80 backdrop-blur-sm border border-red-200/60 rounded-2xl p-8 max-w-md w-full shadow-lg shadow-red-500/20">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="w-6 h-6 text-red-600" />
            <h3 className="text-xl font-bold text-slate-900">Error al cargar clientes</h3>
          </div>
          <p className="text-slate-600 mb-6">
            {clientesError instanceof Error ? clientesError.message : 'Error desconocido'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="w-full px-4 py-2 bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl font-medium hover:shadow-md transition-all"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 mb-6 shadow-lg shadow-teal-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl shadow-lg shadow-teal-500/30">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Gestión de Clientes</h1>
                <p className="text-slate-600 text-sm mt-1">CRM y base de datos de clientes</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-xl font-medium hover:shadow-md transition-all flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Nuevo Cliente
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center gap-3 mb-2">
              <Users className="w-5 h-5 text-teal-600" />
              <span className="text-sm font-medium text-slate-600">Total Clientes</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">{stats.total_clientes}</p>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm text-slate-600">
                {stats.clientes_nuevos_mes} nuevos este mes
              </span>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center gap-3 mb-2">
              <Crown className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-slate-600">Clientes VIP</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">{stats.clientes_vip}</p>
            <p className="text-sm text-slate-600 mt-2">
              {stats.clientes_regulares} clientes regulares
            </p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-slate-600">Tasa de Retención</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">{stats.tasa_retencion.toFixed(1)}%</p>
            <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
              <div
                className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all"
                style={{ width: `${stats.tasa_retencion}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <span className="text-sm font-medium text-slate-600">Con Problemas</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">{stats.clientes_con_problemas}</p>
            <p className="text-sm text-slate-600 mt-2">Requieren atención</p>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-6 mb-6 shadow-md">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar por nombre o teléfono..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 border rounded-xl font-medium transition-all flex items-center gap-2 ${
                showFilters
                  ? 'bg-teal-50 border-teal-300 text-teal-700'
                  : 'border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Filter className="w-4 h-4" />
              Filtros
            </button>
          </div>

          {showFilters && (
            <div className="mt-4 pt-4 border-t border-slate-200">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <button
                  onClick={() => setTipoFilter('')}
                  className={`px-4 py-2 rounded-xl font-medium transition-all ${
                    tipoFilter === ''
                      ? 'bg-gradient-to-br from-teal-500 to-teal-600 text-white shadow-md'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  Todos
                </button>
                {Object.entries(TIPO_CONFIG).map(([key, config]) => {
                  const Icon = config.icon;
                  return (
                    <button
                      key={key}
                      onClick={() => setTipoFilter(key)}
                      className={`px-4 py-2 rounded-xl font-medium transition-all flex items-center gap-2 justify-center ${
                        tipoFilter === key
                          ? 'bg-gradient-to-br from-teal-500 to-teal-600 text-white shadow-md'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {config.label}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Clientes List */}
        {clientes.length === 0 ? (
          <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-2xl p-12 text-center shadow-md">
            <Users className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">No hay clientes</h3>
            <p className="text-slate-600 mb-6">
              {searchTerm || tipoFilter
                ? 'No se encontraron clientes con los filtros aplicados'
                : 'Comienza agregando tu primer cliente'}
            </p>
            {!searchTerm && !tipoFilter && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-3 bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-xl font-medium hover:shadow-md transition-all inline-flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Agregar Cliente
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clientes.map((cliente) => {
              const tipoConfig = TIPO_CONFIG[cliente.tipo];
              const TipoIcon = tipoConfig.icon;
              return (
                <div
                  key={cliente.id}
                  onClick={() => setSelectedClienteId(cliente.id)}
                  className="bg-white/80 backdrop-blur-sm border border-slate-200/60 rounded-xl p-6 shadow-md hover:shadow-lg transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-900 group-hover:text-teal-600 transition-colors">
                          {cliente.nombre}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <Phone className="w-3 h-3 text-slate-400" />
                          <span className="text-sm text-slate-600">{cliente.telefono}</span>
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-teal-600 transition-colors" />
                  </div>

                  <div className="flex items-center gap-2 mb-3">
                    <span
                      className={`px-2 py-1 rounded-lg text-xs font-medium border flex items-center gap-1 ${tipoConfig.color}`}
                    >
                      <TipoIcon className="w-3 h-3" />
                      {tipoConfig.label}
                    </span>
                    {!cliente.activo && (
                      <span className="px-2 py-1 bg-slate-500/10 text-slate-700 rounded-lg text-xs font-medium border border-slate-500/20 flex items-center gap-1">
                        <UserX className="w-3 h-3" />
                        Inactivo
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Total Reservas</p>
                      <p className="text-lg font-bold text-slate-900">{cliente.total_reservas}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Completadas</p>
                      <p className="text-lg font-bold text-green-600">
                        {cliente.reservas_completadas}
                      </p>
                    </div>
                  </div>

                  {cliente.ultima_visita && (
                    <div className="flex items-center gap-2 text-xs text-slate-600 pt-3 border-t border-slate-200">
                      <Calendar className="w-3 h-3" />
                      Última visita: {formatDate(cliente.ultima_visita)}
                    </div>
                  )}

                  {cliente.tags && cliente.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {cliente.tags.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 bg-teal-500/10 text-teal-700 rounded-md text-xs font-medium"
                        >
                          {tag}
                        </span>
                      ))}
                      {cliente.tags.length > 3 && (
                        <span className="px-2 py-0.5 bg-slate-500/10 text-slate-600 rounded-md text-xs font-medium">
                          +{cliente.tags.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Cliente Detail Modal */}
        {selectedClienteId && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
              {clienteLoading ? (
                <div className="p-12 flex flex-col items-center gap-4">
                  <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-slate-600">Cargando detalles...</p>
                </div>
              ) : selectedCliente ? (
                <div>
                  {/* Detail Header */}
                  <div className="bg-gradient-to-br from-teal-500 to-teal-600 p-6 rounded-t-2xl text-white">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                          <User className="w-8 h-8" />
                        </div>
                        <div>
                          <h2 className="text-2xl font-bold">{selectedCliente.nombre}</h2>
                          <p className="text-teal-100 mt-1">{selectedCliente.telefono}</p>
                          {selectedCliente.email && (
                            <p className="text-teal-100 text-sm mt-1">{selectedCliente.email}</p>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedClienteId(null)}
                        className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                      >
                        <X className="w-6 h-6" />
                      </button>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {(() => {
                        const tipoConfig = TIPO_CONFIG[selectedCliente.tipo];
                        const TipoIcon = tipoConfig.icon;
                        return (
                          <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-lg text-sm font-medium flex items-center gap-2">
                            <TipoIcon className="w-4 h-4" />
                            {tipoConfig.label}
                          </span>
                        );
                      })()}
                      {!selectedCliente.activo && (
                        <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-lg text-sm font-medium flex items-center gap-2">
                          <UserX className="w-4 h-4" />
                          Inactivo
                        </span>
                      )}
                      {selectedCliente.tags?.map((tag) => (
                        <span
                          key={tag}
                          className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-lg text-sm font-medium"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="p-6">
                    {/* Quick Actions */}
                    <div className="flex flex-wrap gap-2 mb-6">
                      <button
                        onClick={() => {
                          setClienteForm(selectedCliente);
                          setShowEditModal(true);
                        }}
                        className="px-4 py-2 bg-teal-50 text-teal-700 border border-teal-200 rounded-xl font-medium hover:bg-teal-100 transition-all flex items-center gap-2"
                      >
                        <Edit className="w-4 h-4" />
                        Editar
                      </button>
                      <button
                        onClick={() => {
                          setPreferenciasForm(selectedCliente.preferencias);
                          setShowPreferenciasModal(true);
                        }}
                        className="px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-xl font-medium hover:bg-blue-100 transition-all flex items-center gap-2"
                      >
                        <Heart className="w-4 h-4" />
                        Preferencias
                      </button>
                      <button
                        onClick={() => setShowNotaModal(true)}
                        className="px-4 py-2 bg-purple-50 text-purple-700 border border-purple-200 rounded-xl font-medium hover:bg-purple-100 transition-all flex items-center gap-2"
                      >
                        <FileText className="w-4 h-4" />
                        Agregar Nota
                      </button>
                      <button
                        onClick={() => setShowMergeModal(true)}
                        className="px-4 py-2 bg-orange-50 text-orange-700 border border-orange-200 rounded-xl font-medium hover:bg-orange-100 transition-all flex items-center gap-2"
                      >
                        <Merge className="w-4 h-4" />
                        Fusionar
                      </button>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-4">
                        <p className="text-sm text-slate-600 mb-1">Total Reservas</p>
                        <p className="text-2xl font-bold text-slate-900">
                          {selectedCliente.total_reservas}
                        </p>
                      </div>
                      <div className="bg-green-50/50 border border-green-200/60 rounded-xl p-4">
                        <p className="text-sm text-green-700 mb-1">Completadas</p>
                        <p className="text-2xl font-bold text-green-900">
                          {selectedCliente.reservas_completadas}
                        </p>
                      </div>
                      <div className="bg-red-50/50 border border-red-200/60 rounded-xl p-4">
                        <p className="text-sm text-red-700 mb-1">Canceladas</p>
                        <p className="text-2xl font-bold text-red-900">
                          {selectedCliente.reservas_canceladas}
                        </p>
                      </div>
                      <div className="bg-orange-50/50 border border-orange-200/60 rounded-xl p-4">
                        <p className="text-sm text-orange-700 mb-1">No Shows</p>
                        <p className="text-2xl font-bold text-orange-900">
                          {selectedCliente.no_shows}
                        </p>
                      </div>
                    </div>

                    {/* Preferencias */}
                    <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6 mb-6">
                      <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                        <Heart className="w-5 h-5 text-teal-600" />
                        Preferencias
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {selectedCliente.preferencias.zona_favorita && (
                          <div>
                            <p className="text-sm text-slate-600 mb-1">Zona Favorita</p>
                            <p className="font-medium text-slate-900 flex items-center gap-2">
                              <MapPin className="w-4 h-4 text-teal-600" />
                              {selectedCliente.preferencias.zona_favorita}
                            </p>
                          </div>
                        )}
                        {selectedCliente.preferencias.alergias &&
                          selectedCliente.preferencias.alergias.length > 0 && (
                            <div>
                              <p className="text-sm text-slate-600 mb-1">Alergias</p>
                              <div className="flex flex-wrap gap-1">
                                {selectedCliente.preferencias.alergias.map((alergia) => (
                                  <span
                                    key={alergia}
                                    className="px-2 py-1 bg-red-100 text-red-700 rounded-md text-sm"
                                  >
                                    {alergia}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        {selectedCliente.preferencias.solicitudes_especiales &&
                          selectedCliente.preferencias.solicitudes_especiales.length > 0 && (
                            <div className="md:col-span-2">
                              <p className="text-sm text-slate-600 mb-1">Solicitudes Especiales</p>
                              <div className="flex flex-wrap gap-1">
                                {selectedCliente.preferencias.solicitudes_especiales.map(
                                  (solicitud) => (
                                    <span
                                      key={solicitud}
                                      className="px-2 py-1 bg-blue-100 text-blue-700 rounded-md text-sm"
                                    >
                                      {solicitud}
                                    </span>
                                  )
                                )}
                              </div>
                            </div>
                          )}
                      </div>
                    </div>

                    {/* Notas */}
                    <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6 mb-6">
                      <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-teal-600" />
                        Notas del Staff ({selectedCliente.notas.length})
                      </h3>
                      {selectedCliente.notas.length === 0 ? (
                        <p className="text-slate-600 text-center py-4">No hay notas registradas</p>
                      ) : (
                        <div className="space-y-3">
                          {selectedCliente.notas
                            .slice()
                            .reverse()
                            .map((nota) => {
                              const notaConfig = TIPO_NOTA_CONFIG[nota.tipo];
                              const NotaIcon = notaConfig.icon;
                              return (
                                <div
                                  key={nota.id}
                                  className="bg-white border border-slate-200/60 rounded-lg p-4"
                                >
                                  <div className="flex items-start justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                      <span
                                        className={`px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1 ${notaConfig.color}`}
                                      >
                                        <NotaIcon className="w-3 h-3" />
                                        {notaConfig.label}
                                      </span>
                                      {nota.privada && (
                                        <span className="px-2 py-1 bg-slate-500/10 text-slate-700 rounded-md text-xs font-medium">
                                          Privada
                                        </span>
                                      )}
                                    </div>
                                    <span className="text-xs text-slate-500">
                                      {formatDateTime(nota.timestamp)}
                                    </span>
                                  </div>
                                  <p className="text-slate-900 mb-2">{nota.contenido}</p>
                                  <p className="text-sm text-slate-600">Por: {nota.autor}</p>
                                </div>
                              );
                            })}
                        </div>
                      )}
                    </div>

                    {/* Historial */}
                    <div className="bg-slate-50/50 border border-slate-200/60 rounded-xl p-6">
                      <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-teal-600" />
                        Historial de Reservas ({selectedCliente.historial.length})
                      </h3>
                      {selectedCliente.historial.length === 0 ? (
                        <p className="text-slate-600 text-center py-4">
                          No hay reservas registradas
                        </p>
                      ) : (
                        <div className="space-y-3">
                          {selectedCliente.historial
                            .slice()
                            .reverse()
                            .slice(0, 10)
                            .map((reserva) => (
                              <div
                                key={reserva.id}
                                className="bg-white border border-slate-200/60 rounded-lg p-4"
                              >
                                <div className="flex items-start justify-between mb-2">
                                  <div>
                                    <p className="font-medium text-slate-900">
                                      {formatDate(reserva.fecha)} - {reserva.hora}
                                    </p>
                                    <p className="text-sm text-slate-600">
                                      {reserva.pax} personas
                                      {reserva.mesa_asignada && ` • Mesa ${reserva.mesa_asignada}`}
                                      {reserva.zona && ` • ${reserva.zona}`}
                                    </p>
                                  </div>
                                  <span
                                    className={`px-2 py-1 rounded-md text-xs font-medium ${
                                      reserva.estado === 'completada'
                                        ? 'bg-green-100 text-green-700'
                                        : reserva.estado === 'cancelada'
                                          ? 'bg-red-100 text-red-700'
                                          : 'bg-orange-100 text-orange-700'
                                    }`}
                                  >
                                    {reserva.estado === 'completada'
                                      ? 'Completada'
                                      : reserva.estado === 'cancelada'
                                        ? 'Cancelada'
                                        : 'No Show'}
                                  </span>
                                </div>
                                {reserva.notas && (
                                  <p className="text-sm text-slate-600 mt-2">{reserva.notas}</p>
                                )}
                              </div>
                            ))}
                          {selectedCliente.historial.length > 10 && (
                            <p className="text-sm text-slate-600 text-center pt-2">
                              Mostrando 10 de {selectedCliente.historial.length} reservas
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-12 text-center">
                  <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                  <p className="text-slate-600">Error al cargar cliente</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Create Cliente Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-2xl w-full shadow-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-slate-900">Nuevo Cliente</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-600" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Nombre Completo *
                  </label>
                  <input
                    type="text"
                    value={clienteForm.nombre}
                    onChange={(e) => setClienteForm({ ...clienteForm, nombre: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="Ej: Juan Pérez"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Teléfono *
                  </label>
                  <input
                    type="tel"
                    value={clienteForm.telefono}
                    onChange={(e) => setClienteForm({ ...clienteForm, telefono: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="+34 600 123 456"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={clienteForm.email}
                    onChange={(e) => setClienteForm({ ...clienteForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="ejemplo@email.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Tipo</label>
                  <select
                    value={clienteForm.tipo}
                    onChange={(e) =>
                      setClienteForm({
                        ...clienteForm,
                        tipo: e.target.value as 'regular' | 'vip' | 'nuevo' | 'problema',
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    {Object.entries(TIPO_CONFIG).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Tags</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleAddTag();
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Agregar tag..."
                    />
                    <button
                      onClick={handleAddTag}
                      className="px-4 py-2 bg-teal-500 text-white rounded-xl hover:bg-teal-600 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  {clienteForm.tags && clienteForm.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {clienteForm.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-3 py-1 bg-teal-100 text-teal-700 rounded-lg text-sm font-medium flex items-center gap-2"
                        >
                          {tag}
                          <button
                            onClick={() => handleRemoveTag(tag)}
                            className="hover:bg-teal-200 rounded-full p-0.5 transition-colors"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={clienteForm.activo}
                    onChange={(e) => setClienteForm({ ...clienteForm, activo: e.target.checked })}
                    className="w-4 h-4 text-teal-600 border-slate-300 rounded focus:ring-teal-500"
                  />
                  <span className="text-sm font-medium text-slate-700">Cliente activo</span>
                </label>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleCreateCliente}
                  disabled={
                    createClienteMutation.isPending || !clienteForm.nombre || !clienteForm.telefono
                  }
                  className="flex-1 px-6 py-3 bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-xl font-medium hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {createClienteMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Creando...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Crear Cliente
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  disabled={createClienteMutation.isPending}
                  className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-medium hover:bg-slate-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Ban className="w-4 h-4" />
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Cliente Modal */}
        {showEditModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-2xl w-full shadow-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-slate-900">Editar Cliente</h3>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-600" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Nombre Completo
                  </label>
                  <input
                    type="text"
                    value={clienteForm.nombre}
                    onChange={(e) => setClienteForm({ ...clienteForm, nombre: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Teléfono</label>
                  <input
                    type="tel"
                    value={clienteForm.telefono}
                    onChange={(e) => setClienteForm({ ...clienteForm, telefono: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={clienteForm.email}
                    onChange={(e) => setClienteForm({ ...clienteForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Tipo</label>
                  <select
                    value={clienteForm.tipo}
                    onChange={(e) =>
                      setClienteForm({
                        ...clienteForm,
                        tipo: e.target.value as 'regular' | 'vip' | 'nuevo' | 'problema',
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    {Object.entries(TIPO_CONFIG).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.label}
                      </option>
                    ))}
                  </select>
                </div>

                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={clienteForm.activo}
                    onChange={(e) => setClienteForm({ ...clienteForm, activo: e.target.checked })}
                    className="w-4 h-4 text-teal-600 border-slate-300 rounded focus:ring-teal-500"
                  />
                  <span className="text-sm font-medium text-slate-700">Cliente activo</span>
                </label>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleUpdateCliente}
                  disabled={updateClienteMutation.isPending}
                  className="flex-1 px-6 py-3 bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-xl font-medium hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {updateClienteMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Guardar Cambios
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowEditModal(false)}
                  disabled={updateClienteMutation.isPending}
                  className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-medium hover:bg-slate-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Ban className="w-4 h-4" />
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Add Nota Modal */}
        {showNotaModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-lg w-full shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-slate-900">Agregar Nota</h3>
                <button
                  onClick={() => setShowNotaModal(false)}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-600" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Tipo</label>
                  <select
                    value={notaForm.tipo}
                    onChange={(e) =>
                      setNotaForm({
                        ...notaForm,
                        tipo: e.target.value as
                          | 'general'
                          | 'preferencia'
                          | 'queja'
                          | 'elogio'
                          | 'vip',
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    {Object.entries(TIPO_NOTA_CONFIG).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Autor</label>
                  <input
                    type="text"
                    value={notaForm.autor}
                    onChange={(e) => setNotaForm({ ...notaForm, autor: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="Tu nombre"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Contenido
                  </label>
                  <textarea
                    value={notaForm.contenido}
                    onChange={(e) => setNotaForm({ ...notaForm, contenido: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[100px]"
                    placeholder="Escribe la nota aquí..."
                  />
                </div>

                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={notaForm.privada}
                    onChange={(e) => setNotaForm({ ...notaForm, privada: e.target.checked })}
                    className="w-4 h-4 text-teal-600 border-slate-300 rounded focus:ring-teal-500"
                  />
                  <span className="text-sm font-medium text-slate-700">Nota privada</span>
                </label>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleAddNota}
                  disabled={addNotaMutation.isPending || !notaForm.contenido || !notaForm.autor}
                  className="flex-1 px-6 py-3 bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-xl font-medium hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {addNotaMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Guardar Nota
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowNotaModal(false)}
                  disabled={addNotaMutation.isPending}
                  className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-medium hover:bg-slate-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Ban className="w-4 h-4" />
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Update Preferencias Modal */}
        {showPreferenciasModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-2xl w-full shadow-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-slate-900">Actualizar Preferencias</h3>
                <button
                  onClick={() => setShowPreferenciasModal(false)}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-600" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Zona Favorita
                  </label>
                  <select
                    value={preferenciasForm.zona_favorita || ''}
                    onChange={(e) =>
                      setPreferenciasForm({
                        ...preferenciasForm,
                        zona_favorita: e.target.value
                          ? (e.target.value as 'Interior' | 'Terraza')
                          : undefined,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="">Sin preferencia</option>
                    <option value="Interior">Interior</option>
                    <option value="Terraza">Terraza</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Alergias</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {preferenciasForm.alergias?.map((alergia) => (
                      <span
                        key={alergia}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm font-medium flex items-center gap-2"
                      >
                        {alergia}
                        <button
                          onClick={() => {
                            if (preferenciasForm.alergias) {
                              setPreferenciasForm({
                                ...preferenciasForm,
                                alergias: preferenciasForm.alergias.filter((a) => a !== alergia),
                              });
                            }
                          }}
                          className="hover:bg-red-200 rounded-full p-0.5 transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      id="new-alergia"
                      className="flex-1 px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Agregar alergia..."
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          const input = e.currentTarget;
                          if (input.value.trim()) {
                            handleAddAlergia(input.value.trim());
                            input.value = '';
                          }
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        const input = document.getElementById('new-alergia') as HTMLInputElement;
                        if (input && input.value.trim()) {
                          handleAddAlergia(input.value.trim());
                          input.value = '';
                        }
                      }}
                      className="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Solicitudes Especiales
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {preferenciasForm.solicitudes_especiales?.map((solicitud) => (
                      <span
                        key={solicitud}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium flex items-center gap-2"
                      >
                        {solicitud}
                        <button
                          onClick={() => {
                            if (preferenciasForm.solicitudes_especiales) {
                              setPreferenciasForm({
                                ...preferenciasForm,
                                solicitudes_especiales:
                                  preferenciasForm.solicitudes_especiales.filter(
                                    (s) => s !== solicitud
                                  ),
                              });
                            }
                          }}
                          className="hover:bg-blue-200 rounded-full p-0.5 transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      id="new-solicitud"
                      className="flex-1 px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Agregar solicitud..."
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          const input = e.currentTarget;
                          if (input.value.trim()) {
                            handleAddSolicitudEspecial(input.value.trim());
                            input.value = '';
                          }
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        const input = document.getElementById('new-solicitud') as HTMLInputElement;
                        if (input && input.value.trim()) {
                          handleAddSolicitudEspecial(input.value.trim());
                          input.value = '';
                        }
                      }}
                      className="px-4 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleUpdatePreferencias}
                  disabled={updatePreferenciasMutation.isPending}
                  className="flex-1 px-6 py-3 bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-xl font-medium hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {updatePreferenciasMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Guardar Preferencias
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowPreferenciasModal(false)}
                  disabled={updatePreferenciasMutation.isPending}
                  className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-medium hover:bg-slate-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Ban className="w-4 h-4" />
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Merge Clientes Modal */}
        {showMergeModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-lg w-full shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-slate-900">Fusionar Clientes</h3>
                <button
                  onClick={() => setShowMergeModal(false)}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-600" />
                </button>
              </div>

              <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 mb-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-orange-900 mb-1">Acción Permanente</p>
                    <p className="text-sm text-orange-700">
                      Esta acción fusionará el cliente seleccionado con el cliente principal. Todo
                      el historial y notas se transferirán y el cliente secundario se eliminará.
                      Esta acción no se puede deshacer.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Cliente Principal (Conservar)
                  </label>
                  <div className="px-4 py-3 bg-teal-50 border border-teal-200 rounded-xl">
                    <p className="font-medium text-teal-900">{selectedCliente?.nombre}</p>
                    <p className="text-sm text-teal-700">{selectedCliente?.telefono}</p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Cliente a Fusionar (Eliminar)
                  </label>
                  <select
                    value={mergeForm.clienteSecundarioId}
                    onChange={(e) =>
                      setMergeForm({ ...mergeForm, clienteSecundarioId: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="">Seleccionar cliente...</option>
                    {clientes
                      .filter((c) => c.id !== selectedClienteId)
                      .map((cliente) => (
                        <option key={cliente.id} value={cliente.id}>
                          {cliente.nombre} - {cliente.telefono}
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleMergeClientes}
                  disabled={mergeClientesMutation.isPending || !mergeForm.clienteSecundarioId}
                  className="flex-1 px-6 py-3 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl font-medium hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {mergeClientesMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Fusionando...
                    </>
                  ) : (
                    <>
                      <Merge className="w-4 h-4" />
                      Fusionar Clientes
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowMergeModal(false)}
                  disabled={mergeClientesMutation.isPending}
                  className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-medium hover:bg-slate-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Ban className="w-4 h-4" />
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
