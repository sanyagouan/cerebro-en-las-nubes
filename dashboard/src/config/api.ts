// Configuración de la API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://go84sgscs4ckcs08wog84o0o.app.generaia.site';

export const config = {
  API_BASE_URL,
  API_ENDPOINTS: {
    HEALTH: `${API_BASE_URL}/health`,
    RESERVAS: `${API_BASE_URL}/api/reservas`,
    MESAS: `${API_BASE_URL}/api/mesas`,
    TURNOS: `${API_BASE_URL}/api/turnos`,
    STATS: `${API_BASE_URL}/api/stats`,
  }
};

export default config;
