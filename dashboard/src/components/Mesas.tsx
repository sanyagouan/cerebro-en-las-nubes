import { CheckCircle, XCircle, MapPin, Users } from 'lucide-react';
import { MESAS_EJEMPLO } from '../types';

export default function Mesas() {
  const mesasInterior = MESAS_EJEMPLO.filter(m => m.ubicacion === 'Interior');
  const mesasTerraza = MESAS_EJEMPLO.filter(m => m.ubicacion === 'Terraza');

  const MesaCard = ({ mesa }: { mesa: typeof MESAS_EJEMPLO[0] }) => (
    <div className={`p-4 rounded-xl border-2 transition-all ${
      mesa.disponible 
        ? 'border-green-200 bg-green-50 hover:border-green-300' 
        : 'border-red-200 bg-red-50 hover:border-red-300'
    }`}>
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-semibold text-gray-900">{mesa.nombre}</h4>
          <div className="flex items-center gap-1 text-sm text-gray-600 mt-1">
            <MapPin size={14} />
            {mesa.ubicacion}
          </div>
        </div>
        <div className={`p-2 rounded-full ${
          mesa.disponible ? 'bg-green-200' : 'bg-red-200'
        }`}>
          {mesa.disponible ? (
            <CheckCircle size={20} className="text-green-700" />
          ) : (
            <XCircle size={20} className="text-red-700" />
          )}
        </div>
      </div>
      
      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2 text-sm">
          <Users size={16} className="text-gray-400" />
          <span>
            Capacidad: <strong>{mesa.capacidad}</strong>
            {mesa.capacidadAmpliada && (
              <span className="text-gray-500"> (ampliada: {mesa.capacidadAmpliada})</span>
            )}
          </span>
        </div>
        
        {mesa.notas && (
          <p className="text-sm text-gray-600 mt-2">{mesa.notas}</p>
        )}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <button
          onClick={() => {}}
          className={`w-full py-2 rounded-lg font-medium transition-colors ${
            mesa.disponible
              ? 'bg-green-600 text-white hover:bg-green-700'
              : 'bg-red-600 text-white hover:bg-red-700'
          }`}
        >
          {mesa.disponible ? 'Marcar Ocupada' : 'Marcar Disponible'}
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Total de Mesas</p>
          <p className="text-3xl font-bold text-gray-900">{MESAS_EJEMPLO.length}</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Disponibles</p>
          <p className="text-3xl font-bold text-green-600">{MESAS_EJEMPLO.filter(m => m.disponible).length}</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Ocupadas</p>
          <p className="text-3xl font-bold text-red-600">{MESAS_EJEMPLO.filter(m => !m.disponible).length}</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-600">Capacidad Total</p>
          <p className="text-3xl font-bold text-primary-600">
            {MESAS_EJEMPLO.reduce((sum, m) => sum + m.capacidad, 0)}
          </p>
        </div>
      </div>

      {/* Mesas Interior */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Interior</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mesasInterior.map(mesa => (
            <MesaCard key={mesa.id} mesa={mesa} />
          ))}
        </div>
      </div>

      {/* Mesas Terraza */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Terraza</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mesasTerraza.map(mesa => (
            <MesaCard key={mesa.id} mesa={mesa} />
          ))}
        </div>
      </div>
    </div>
  );
}
