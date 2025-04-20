import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import logo from '../assets/logo_rocketflow_colorTrans.png';

const Login = ({ onToggleForm }) => {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-primary-100 to-primary-50">
      <div className="flex flex-col items-center mb-0">
        <img src={logo} alt="Rocketflow Logo" className="h-56 mb-4 drop-shadow-lg select-none" style={{userSelect: 'none'}} />
      </div>
      <LoginCard onToggleForm={onToggleForm} />
    </div>
  );
};

// Tarjeta de login separada para claridad visual
const LoginCard = ({ onToggleForm }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('Por favor, completa todos los campos');
      return;
    }
    
    try {
      setError('');
      setLoading(true);
      const success = await login(username, password);
      
      if (!success) {
        setError('Usuario o contraseña incorrectos');
      }
    } catch (error) {
      setError('Error al iniciar sesión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-md">
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="username" className="block text-gray-700 font-medium mb-2">
            Nombre de Usuario
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500 placeholder-gray-400"
            placeholder="Ingresa tu nombre de usuario"
            required
          />
        </div>
        <div className="mb-6">
          <label htmlFor="password" className="block text-gray-700 font-medium mb-2">
            Contraseña
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500 placeholder-gray-400"
            placeholder="Ingresa tu contraseña"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-md font-medium text-white text-base shadow-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
            loading ? 'bg-primary-400 cursor-not-allowed' : 'bg-primary-600 hover:bg-primary-700'
          }`}
        >
          {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
        </button>
      </form>
      <div className="mt-4 text-center">
        <a href="#" className="text-sm text-primary-600 hover:text-primary-800">¿Olvidaste tu contraseña?</a>
      </div>
      <div className="mt-4 text-center">
        <p className="text-gray-600">
          ¿No tienes una cuenta?{' '}
          <button
            onClick={onToggleForm}
            className="text-primary-600 hover:text-primary-800 font-medium"
          >
            Regístrate
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
