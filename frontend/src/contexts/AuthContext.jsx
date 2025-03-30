import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

// Crear el contexto de autenticación
const AuthContext = createContext();

// Hook personalizado para usar el contexto de autenticación
export const useAuth = () => useContext(AuthContext);

// Proveedor del contexto de autenticación
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  
  // Configurar axios para usar el token en todas las solicitudes y manejar errores de autenticación
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Intentar obtener información del usuario
      fetchUserInfo();
    } else {
      delete axios.defaults.headers.common['Authorization'];
      setCurrentUser(null);
    }
    
    // Configurar interceptor para manejar errores de autenticación
    const interceptorId = axios.interceptors.response.use(
      response => response,
      error => {
        // Si obtenemos un error 401 (No autorizado), cerramos la sesión automáticamente
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          console.log('Sesión expirada o token inválido. Redirigiendo a inicio de sesión...');
          logout();
        }
        return Promise.reject(error);
      }
    );
    
    setLoading(false);
    
    // Limpiar el interceptor al desmontar
    return () => {
      axios.interceptors.response.eject(interceptorId);
    };
  }, [token]);
  
  // Función para obtener información del usuario
  const fetchUserInfo = async () => {
    try {
      // En un sistema real, tendrías un endpoint para obtener info del usuario 
      // Por ahora, solo configuramos el usuario basado en el token
      if (token) {
        // Extraer el username del token (decodificar sin verificar)
        const payload = JSON.parse(atob(token.split('.')[1]));
        setCurrentUser({
          username: payload.sub,
          // Otros datos de usuario se obtendrían de la API
        });
      }
    } catch (error) {
      console.error('Error al obtener información del usuario:', error);
      logout();
    }
  };
  
  // Función para iniciar sesión
  const login = async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await axios.post('http://localhost:8000/users/token', formData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      return true;
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
      return false;
    }
  };
  
  // Función para registrarse
  const register = async (username, email, password) => {
    try {
      const response = await axios.post('http://localhost:8000/users/register', {
        username,
        email,
        password
      });
      
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error al registrarse:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al registrarse'
      };
    }
  };
  
  // Función para cerrar sesión
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCurrentUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };
  
  // Valor del contexto
  const value = {
    currentUser,
    token,
    login,
    register,
    logout,
    loading
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
