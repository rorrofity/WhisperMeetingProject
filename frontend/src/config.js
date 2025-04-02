// Configuración de la API
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'http://134.199.218.48/api'  // URL de producción (servidor) con ruta /api para usar el proxy de Nginx
  : 'http://localhost:8000';       // URL de desarrollo (local)

export { API_URL };
