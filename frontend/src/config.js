// Configuración de la API
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'http://134.199.218.48:8000'  // URL de producción (servidor)
  : 'http://localhost:8000';       // URL de desarrollo (local)

export { API_URL };
