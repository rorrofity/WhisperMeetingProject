// Configuración de la API
const rawApiUrl = import.meta.env.VITE_API_URL;

// [SF] Simplicity First: Normaliza la URL para evitar slashes duplicados
// Si la URL termina con /, lo quitamos para evitar dobles slashes al construir rutas
const API_URL = rawApiUrl.endsWith('/') 
  ? rawApiUrl.slice(0, -1) // Quitar el último slash
  : rawApiUrl;

// Función de utilidad para construir URLs de API de forma segura
const buildApiUrl = (endpoint) => {
  // Asegurarnos que el endpoint comience con /
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_URL}${normalizedEndpoint}`;
};

export { API_URL, buildApiUrl };
