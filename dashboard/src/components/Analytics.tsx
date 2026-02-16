import { useState, useMemo } from 'react';
import { Download, TrendingUp, Users, Calendar, XCircle, CheckCircle } from 'lucide-react';
import { useReservations } from '../hooks/useReservations';
import { useTables } from '../hooks/useTables';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, subDays, startOfDay, endOfDay, eachDayOfInterval, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

type DateRange = '7d' | '30d' | '90d';

const COLORS = {
  primary: '#4F46E5',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6',
  purple: '#8B5CF6',
};

export default function Analytics() {
  const { data: reservationsData } = useReservations();
  const { data: tablesData } = useTables();
  const [dateRange, setDateRange] = useState<DateRange>('30d');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Calculate date range
  const rangeConfig = {
    '7d': { days: 7, label: '7 días' },
    '30d': { days: 30, label: '30 días' },
    '90d': { days: 90, label: '90 días' },
  };

  const startDate = useMemo(() => {
    return startOfDay(subDays(new Date(), rangeConfig[dateRange].days));
  }, [dateRange]);

  const endDate = useMemo(() => endOfDay(new Date()), []);

  // Filter reservations by date range
  const filteredReservations = useMemo(() => {
    if (!reservationsData?.reservations) return [];

    return reservationsData.reservations.filter(r => {
      const reservaDate = parseISO(r.fecha);
      return reservaDate >= startDate && reservaDate <= endDate;
    });
  }, [reservationsData, startDate, endDate]);

  // Calculate metrics
  const metrics = useMemo(() => {
    const total = filteredReservations.length;
    const confirmadas = filteredReservations.filter(r => r.estado === 'Confirmada').length;
    const completadas = filteredReservations.filter(r => r.estado === 'Completada').length;
    const canceladas = filteredReservations.filter(r => r.estado === 'Cancelada').length;
    const totalPersonas = filteredReservations.reduce((sum, r) => sum + r.pax, 0);
    const avgPax = total > 0 ? (totalPersonas / total).toFixed(1) : '0';
    const tasaCancelacion = total > 0 ? ((canceladas / total) * 100).toFixed(1) : '0';
    const tasaCompletadas = total > 0 ? ((completadas / total) * 100).toFixed(1) : '0';

    return {
      total,
      confirmadas,
      completadas,
      canceladas,
      totalPersonas,
      avgPax,
      tasaCancelacion,
      tasaCompletadas,
    };
  }, [filteredReservations]);

  // Reservations by day chart data
  const reservationsByDay = useMemo(() => {
    const days = eachDayOfInterval({ start: startDate, end: endDate });

    return days.map(day => {
      const dayReservations = filteredReservations.filter(r => {
        const reservaDate = parseISO(r.fecha);
        return format(reservaDate, 'yyyy-MM-dd') === format(day, 'yyyy-MM-dd');
      });

      return {
        date: format(day, 'dd MMM', { locale: es }),
        total: dayReservations.length,
        completadas: dayReservations.filter(r => r.estado === 'Completada').length,
        canceladas: dayReservations.filter(r => r.estado === 'Cancelada').length,
        personas: dayReservations.reduce((sum, r) => sum + r.pax, 0),
      };
    });
  }, [filteredReservations, startDate, endDate]);

  // Status distribution pie chart
  const statusDistribution = useMemo(() => {
    const pendientes = filteredReservations.filter(r => r.estado === 'Pendiente').length;
    const confirmadas = filteredReservations.filter(r => r.estado === 'Confirmada').length;
    const sentadas = filteredReservations.filter(r => r.estado === 'Sentada').length;
    const completadas = filteredReservations.filter(r => r.estado === 'Completada').length;
    const canceladas = filteredReservations.filter(r => r.estado === 'Cancelada').length;

    return [
      { name: 'Pendientes', value: pendientes, color: COLORS.warning },
      { name: 'Confirmadas', value: confirmadas, color: COLORS.success },
      { name: 'Sentadas', value: sentadas, color: COLORS.info },
      { name: 'Completadas', value: completadas, color: COLORS.primary },
      { name: 'Canceladas', value: canceladas, color: COLORS.danger },
    ].filter(item => item.value > 0);
  }, [filteredReservations]);

  // Channel distribution
  const channelDistribution = useMemo(() => {
    const byChannel = filteredReservations.reduce((acc, r) => {
      acc[r.canal] = (acc[r.canal] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(byChannel).map(([channel, count]) => ({
      name: channel,
      value: count,
    }));
  }, [filteredReservations]);

  // Peak hours analysis
  const peakHours = useMemo(() => {
    const hourCounts: Record<number, number> = {};

    filteredReservations.forEach(r => {
      const hour = parseInt(r.hora.split(':')[0], 10);
      hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    });

    return Object.entries(hourCounts)
      .map(([hour, count]) => ({
        hora: `${hour}:00`,
        reservas: count,
      }))
      .sort((a, b) => parseInt(a.hora) - parseInt(b.hora));
  }, [filteredReservations]);

  // Table occupancy (if tables data available)
  const tableOccupancy = useMemo(() => {
    if (!tablesData?.tables) return null;

    const total = tablesData.tables.length;
    const ocupadas = tablesData.tables.filter(t => t.estado === 'Ocupada').length;
    const reservadas = tablesData.tables.filter(t => t.estado === 'Reservada').length;
    const libres = tablesData.tables.filter(t => t.estado === 'Libre').length;

    return [
      { name: 'Ocupadas', value: ocupadas, color: COLORS.danger },
      { name: 'Reservadas', value: reservadas, color: COLORS.warning },
      { name: 'Libres', value: libres, color: COLORS.success },
    ];
  }, [tablesData]);

  // Export to CSV
  const handleExportAnalytics = () => {
    const headers = ['Fecha', 'Total Reservas', 'Completadas', 'Canceladas', 'Personas'];
    const rows = reservationsByDay.map(d => [
      d.date,
      d.total.toString(),
      d.completadas.toString(),
      d.canceladas.toString(),
      d.personas.toString(),
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute(
      'download',
      `analytics_${format(new Date(), 'yyyy-MM-dd_HH-mm', { locale: es })}.csv`
    );
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setToast({ message: 'Analytics exportado exitosamente', type: 'success' });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Toast Notifications */}
      {toast && (
        <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
          <div
            className={`flex items-center gap-3 px-6 py-4 rounded-lg shadow-lg ${
              toast.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
            }`}
          >
            {toast.type === 'success' ? (
              <CheckCircle size={20} className="flex-shrink-0" />
            ) : (
              <XCircle size={20} className="flex-shrink-0" />
            )}
            <span className="font-medium">{toast.message}</span>
          </div>
        </div>
      )}

      {/* Header with Date Range and Export */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Analytics y Reportes</h2>

        <div className="flex items-center gap-3">
          {/* Date Range Filter */}
          <div className="flex gap-1 border rounded-lg p-1 bg-gray-50">
            {(['7d', '30d', '90d'] as DateRange[]).map(range => (
              <button
                key={range}
                onClick={() => setDateRange(range)}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  dateRange === range
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                {rangeConfig[range].label}
              </button>
            ))}
          </div>

          {/* Export Button */}
          <button
            onClick={handleExportAnalytics}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download size={20} />
            <span>Exportar CSV</span>
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Calendar size={24} className="text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Reservas</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle size={24} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Tasa Completadas</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.tasaCompletadas}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-100 rounded-lg">
              <XCircle size={24} className="text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Tasa Cancelación</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.tasaCancelacion}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users size={24} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Promedio Personas</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.avgPax}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Reservations by Day - Area Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Reservas por Día</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={reservationsByDay}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" style={{ fontSize: '12px' }} />
              <YAxis style={{ fontSize: '12px' }} />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="total"
                stackId="1"
                stroke={COLORS.primary}
                fill={COLORS.primary}
                name="Total"
              />
              <Area
                type="monotone"
                dataKey="completadas"
                stackId="2"
                stroke={COLORS.success}
                fill={COLORS.success}
                name="Completadas"
              />
              <Area
                type="monotone"
                dataKey="canceladas"
                stackId="3"
                stroke={COLORS.danger}
                fill={COLORS.danger}
                name="Canceladas"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution - Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Distribución por Estado</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Peak Hours - Bar Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Horarios Pico</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={peakHours}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hora" style={{ fontSize: '12px' }} />
              <YAxis style={{ fontSize: '12px' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="reservas" fill={COLORS.purple} name="Reservas" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Channel Distribution - Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Canales de Reserva</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={channelDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {channelDistribution.map((entry, index) => {
                  const colors = [COLORS.info, COLORS.success, COLORS.purple];
                  return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                })}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table Occupancy (if available) */}
      {tableOccupancy && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Ocupación de Mesas (Actual)</h3>
          <div className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={tableOccupancy}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) =>
                    `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {tableOccupancy.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <TrendingUp size={20} className="text-primary-600" />
          Resumen del Periodo
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Reservas Totales</p>
            <p className="text-xl font-bold text-gray-900">{metrics.total}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Confirmadas</p>
            <p className="text-xl font-bold text-green-600">{metrics.confirmadas}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Canceladas</p>
            <p className="text-xl font-bold text-red-600">{metrics.canceladas}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Personas</p>
            <p className="text-xl font-bold text-blue-600">{metrics.totalPersonas}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
