import { useState } from 'react';
import { Search, Filter, Phone, MessageSquare, Calendar, Users } from 'lucide-react';
import { RESERVAS_EJEMPLO } from '../types';

export default function Reservas() {
  const [filtroEstado, setFiltroEstado] = useState<string>('todos');
  const [busqueda, setBusqueda] = useState('');

  const reservasFiltradas = RESERVAS_EJEMPLO.filter(reserva => {
    const matchEstado = filtroEstado === 'todos' || reserva.estado.toLowerCase() === filtroEstado;
    const matchBusqueda = reserva.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                         reserva.telefono.includes(busqueda);
    return matchEstado && matchBusqueda;
  });

  return (
    <div className="space-y-6">
      {/* Filtros y Búsqueda */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex flex-col md:flex-row gap-4 justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por nombre o teléfono..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          <div className="flex gap-2">
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="todos">Todos los estados</option>
              <option value="pendiente">Pendiente</option>
              <option value="confirmada">Confirmada</option>
              <option value="cancelada">Cancelada</option>
              <option value="completada">Completada</option>
            </select>
            
            <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
              <Calendar size={18} />
              Nueva Reserva
            </button>
          </div>
        </div>
      </div>

      {/* Tabla de Reservas */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Cliente</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Fecha y Hora</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Personas</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Mesa</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Estado</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Origen</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {reservasFiltradas.map((reserva) => (
              <tr key={reserva.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <p className="font-medium text-gray-900">{reserva.nombre}</p>
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                      <Phone size={14} />
                      {reserva.telefono}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-gray-400" />
                    <span>{reserva.fecha} • {reserva.hora}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Users size={16} className="text-gray-400" />
                    {reserva.personas}
                  </div>
                </td>
                <td className="px-6 py-4">
                  {reserva.mesa ? (
                    <span className="px-3 py-1 bg-gray-100 rounded-full text-sm">{reserva.mesa}</span>
                  ) : (
                    <span className="text-gray-400">Sin asignar</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    reserva.estado === 'Confirmada' ? 'bg-green-100 text-green-700' :
                    reserva.estado === 'Pendiente' ? 'bg-yellow-100 text-yellow-700' :
                    reserva.estado === 'Cancelada' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {reserva.estado}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    reserva.origen === 'VAPI' ? 'bg-purple-100 text-purple-700' :
                    reserva.origen === 'WhatsApp' ? 'bg-green-100 text-green-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {reserva.origen}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    <button className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg" title="Editar">
                      ✏️
                    </button>
                    <button className="p-2 text-green-600 hover:bg-green-50 rounded-lg" title="Confirmar">
                      ✅
                    </button>
                    <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg" title="Cancelar">
                      ❌
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
