import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LayoutDashboard, Calendar, Table, Settings, Users, LogOut } from 'lucide-react';
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

  if (!isAuthenticated) {
    return <Login onLogin={login} />;
  }

  const menuItems = [
    { id: 'dashboard' as Vista, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'reservas' as Vista, label: 'Reservas', icon: Calendar },
    { id: 'mesas' as Vista, label: 'Mesas', icon: Table },
    { id: 'clientes' as Vista, label: 'Clientes', icon: Users },
    { id: 'config' as Vista, label: 'Configuración', icon: Settings },
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
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-primary-600">En Las Nubes</h1>
          <p className="text-sm text-gray-500">Panel de Administración</p>
        </div>
        <nav className="p-4 flex-1">
          <ul className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setVistaActual(item.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      vistaActual === item.id
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
        
        {/* Logout Button */}
        <div className="p-4 border-t">
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 hover:bg-red-50 hover:text-red-600 transition-colors"
          >
            <LogOut size={20} />
            <span className="font-medium">Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="bg-white shadow-sm px-8 py-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold text-gray-800">
              {menuItems.find(item => item.id === vistaActual)?.label}
            </h2>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">{new Date().toLocaleDateString('es-ES', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}</span>
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-semibold">
                A
              </div>
            </div>
          </div>
        </header>

        <div className="p-8">
          {renderVista()}
        </div>
      </main>
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
