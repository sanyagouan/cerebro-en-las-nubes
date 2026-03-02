import axios from 'axios';

// En desarrollo, baseURL vacío → el proxy de Vite redirige /api/* al backend (vite.config.ts)
// En producción, Vite inyecta VITE_API_URL durante el build (debe estar configurada como buildtime en Coolify)
// Fallback hardcodeado a la URL del backend en Coolify por si acaso
const VITE_API_URL = (import.meta as any).env?.VITE_API_URL;
const isDev = (import.meta as any).env?.DEV === true;
export const API_BASE_URL = VITE_API_URL || (isDev ? '' : 'https://go84sgscs4ckcs08wog84o0o.app.generaia.site');

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

// Crear instancia de axios con interceptores JWT
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor de REQUEST: inyecta el token JWT en cada petición
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de RESPONSE: redirige a login en caso de 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default config;
