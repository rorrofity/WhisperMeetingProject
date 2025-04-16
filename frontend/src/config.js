// Configuración de la API
const API_URL = import.meta.env.VITE_API_URL;
// Ahora API_URL será https://www.rocketflow.cl/api/ en producción y http://localhost:8000/api/ en desarrollo, según el archivo .env
export { API_URL };
