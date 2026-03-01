import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { 
  LayoutDashboard, 
  Calendar, 
  Table, 
  Settings, 
  Users, 
  LogOut,
  Menu,
  X,
  Bell,
  Cloud
} from 'lucide-react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Reservas from './components/Reservas';
import Mesas from './components/Mesas';
import Clientes from './components/Clientes';
import Configuracion from './components/Configuracion';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

type Vista = 'dashboard' | 'reservas' | 'mesas' | 'clientes' | 'config';

function AppContent() {
  const { isAuthenticated, login, logout } = useAuth();
  const [vistaActual, setVistaActual] = useState<Vista>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!isAuthenticated) {
    return <Login onLogin={login} />;
  }

  const menuItems = [
    { id: 'dashboard' as Vista, label: 'Dashboard', icon: LayoutDashboard, description: 'Vista general' },
    { id: 'reservas' as Vista, label: 'Reservas', icon: Calendar, description: 'Gestionar reservas' },
    { id: 'mesas' as Vista, label: 'Mesas', icon: Table, description: 'Estado de mesas' },
    { id: 'clientes' as Vista, label: 'Clientes', icon: Users, description: 'Base de datos' },
    { id: 'config' as Vista, label: 'Configuracion', icon: Settings, description: 'Ajustes' },
  ];

  const renderVista = () => {
    switch (vistaActual) {
      case 'dashboard':
        return <Dashboard />;
      case 'reservas':
        return <Reservas />;
      case 'mesas':
        return <Mesas />;
      case 'clientes':
        return <Clientes />;
      case 'config':
        return <Configuracion />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-secondary-50">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-72 flex flex-col
        bg-gradient-to-b from-secondary-900 via-secondary-900 to-secondary-950
        transform transition-transform duration-300 ease-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo Header */}
        <div className="p-6 border-b border-secondary-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-glow">
              <Cloud className="text-white" size={22} />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white font-display">En Las Nubes</h1>
              <p className="text-xs text-secondary-400">Panel de Administracion</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = vistaActual === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setVistaActual(item.id);
                  setSidebarOpen(false);
                }}
                className={`
                  w-full flex items-center gap-3 px-4 py-3.5 rounded-xl font-medium
                  transition-all duration-200 group
                  ${isActive 
                    ? 'bg-primary-600 text-white shadow-glow' 
                    : 'text-secondary-300 hover:bg-secondary-800 hover:text-white'
                  }
                `}
              >
                <Icon size={20} className={isActive ? 'text-white' : 'text-secondary-400 group-hover:text-primary-400'} />
                <div className="text-left">
                  <span className="block">{item.label}</span>
                  <span className={`text-xs ${isActive ? 'text-primary-100' : 'text-secondary-500'}`}>
                    {item.description}
                  </span>
                </div>
              </button>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-secondary-800">
          <div className="flex items-center gap-3 px-3 py-2 mb-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold text-sm">
              A
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">Administrador</p>
              <p className="text-xs text-secondary-400">admin@enlasnubes.com</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-secondary-300 hover:bg-error-600/10 hover:text-error-400 transition-all duration-200"
          >
            <LogOut size={18} />
            <span className="font-medium">Cerrar Sesion</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-secondary-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Mobile menu button */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-xl text-secondary-600 hover:bg-secondary-100"
              >
                <Menu size={24} />
              </button>

              <div>
                <h2 className="text-xl font-bold text-secondary-900 font-display">
                  {menuItems.find(item => item.id === vistaActual)?.label}
                </h2>
                <p className="text-sm text-secondary-500">
                  {new Date().toLocaleDateString('es-ES', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Notifications */}
              <button className="relative p-2.5 rounded-xl bg-secondary-50 text-secondary-600 hover:bg-secondary-100 transition-colors">
                <Bell size={20} />
                <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-primary-500 rounded-full border-2 border-white"></span>
              </button>

              {/* Live indicator */}
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-success-50 border border-success-200">
                <div className="pulse-dot"></div>
                <span className="text-sm font-medium text-success-700">En vivo</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6 lg:p-8">
          {renderVista()}
        </div>
      </main>

      {/* Mobile close button */}
      {sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(false)}
          className="fixed top-4 right-4 z-50 lg:hidden p-2 rounded-full bg-secondary-800 text-white"
        >
          <X size={24} />
        </button>
      )}
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
