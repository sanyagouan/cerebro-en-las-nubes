// Configuración de la API
// @ts-ignore - Vite env vars
// In development, use empty string to trigger Vite proxy (configured to forward /api to localhost:8000)
// In production, use the full production URL
const isDevelopment = (import.meta as any).env?.MODE === 'development';
const API_BASE_URL = isDevelopment ? '' : ((import.meta as any).env?.VITE_API_URL || 'https://go84sgscs4ckcs08wog84o0o.app.generaia.site');

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
