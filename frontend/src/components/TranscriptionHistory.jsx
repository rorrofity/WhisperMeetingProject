import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FiRefreshCw, FiFileText, FiTrash2, FiAlertCircle } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import { API_URL } from '../config';

const TranscriptionHistory = ({ onSelectTranscription }) => {
  const [transcriptions, setTranscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token, logout } = useAuth();
  
  const fetchTranscriptions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Verificar que el token exista antes de hacer la solicitud
      if (!token) {
        console.error('No hay token de autenticación disponible');
        setError('Debes iniciar sesión para ver tu historial de transcripciones');
        setLoading(false);
        return;
      }
      
      console.log('Haciendo solicitud con token:', token.substring(0, 15) + '...');
      
      const response = await axios.get(`${API_URL}/transcriptions/`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setTranscriptions(response.data);
    } catch (error) {
      console.error('Error al obtener transcripciones:', error);
      
      // Mensajes de error más detallados según el tipo de error
      if (error.response?.status === 401) {
        setError('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
      } else {
        setError('No se pudieron cargar las transcripciones. Intenta nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Cargar transcripciones al montar el componente
  useEffect(() => {
    const fetchTranscriptions = async () => {
      try {
        setLoading(true);
        
        const response = await axios.get(`${API_URL}/transcriptions/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        setTranscriptions(response.data);
      } catch (error) {
        console.error('Error al cargar transcripciones:', error);
        
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          logout();
        } else {
          setError('Error al cargar las transcripciones');
        }
      } finally {
        setLoading(false);
      }
    };
    
    if (token) {
      fetchTranscriptions();
    }
  }, [token, logout]);

  const handleDelete = async (id) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta transcripción?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/transcriptions/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      // Actualizar la lista después de eliminar
      setTranscriptions(transcriptions.filter(t => t.id !== id));
    } catch (error) {
      console.error('Error al eliminar la transcripción:', error);
      
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        logout();
      } else {
        setError('Error al eliminar la transcripción');
      }
    }
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return 'Fecha desconocida';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Fecha inválida';
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          Mi Historial de Transcripciones
        </h2>
        <button 
          onClick={fetchTranscriptions}
          className="flex items-center text-primary-600 hover:text-primary-800"
        >
          <FiRefreshCw className="mr-1" /> Actualizar
        </button>
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded flex items-center">
          <FiAlertCircle className="mr-2" /> {error}
        </div>
      )}
      
      {loading ? (
        <div className="text-center py-6">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Cargando transcripciones...</p>
        </div>
      ) : transcriptions.length === 0 ? (
        <div className="text-center py-6 text-gray-500">
          No tienes transcripciones guardadas.
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Título
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Archivo Original
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transcriptions.map((transcription) => (
                <tr key={transcription.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => onSelectTranscription(transcription)}
                      className="text-primary-600 hover:text-primary-800 font-medium"
                    >
                      {transcription.title || 'Sin título'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                    {transcription.original_filename || 'Desconocido'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                    {formatDate(transcription.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button
                      onClick={() => onSelectTranscription(transcription)}
                      className="text-blue-600 hover:text-blue-800 mx-2"
                      title="Ver transcripción"
                    >
                      <FiFileText />
                    </button>
                    <button
                      onClick={() => handleDelete(transcription.id)}
                      className="text-red-600 hover:text-red-800 mx-2"
                      title="Eliminar transcripción"
                    >
                      <FiTrash2 />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TranscriptionHistory;
