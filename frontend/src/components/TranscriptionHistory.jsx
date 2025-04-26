import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { FiRefreshCw, FiFileText, FiTrash2, FiAlertCircle, FiChevronUp, FiChevronDown, FiChevronsLeft, FiChevronsRight, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import { API_URL } from '../config';

const ITEMS_PER_PAGE = 15;

const TranscriptionHistory = ({ onSelectTranscription }) => {
  const [transcriptions, setTranscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token, logout } = useAuth();
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'descending' });

  const fetchTranscriptions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!token) {
        console.error('No hay token de autenticación disponible');
        setError('Debes iniciar sesión para ver tu historial de transcripciones');
        setLoading(false);
        return;
      }
      
      console.log('Haciendo solicitud con token:', token.substring(0, 15) + '...');
      
      // [IV] Corregir URL - quitar el /api duplicado
      const response = await axios.get(`${API_URL}/transcriptions/`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      console.log('Transcripciones recibidas:', response.data);
      setTranscriptions(response.data);
    } catch (error) {
      console.error('Error al obtener transcripciones:', error);
      
      if (error.response?.status === 401) {
        setError('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
      } else {
        setError('No se pudieron cargar las transcripciones. Intenta nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) { // Solo llamar si hay token
      fetchTranscriptions();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]); // Dependencia: token

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
        day: 'numeric',
        month: 'long'
      });
    } catch (error) {
      return 'Fecha inválida';
    }
  };

  const sortedTranscriptions = useMemo(() => {
    let sortableItems = [...transcriptions];
    if (sortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        if (sortConfig.key === 'title') {
          aValue = aValue || '';
          bValue = bValue || '';
        }

        if (sortConfig.key === 'created_at') {
          aValue = aValue ? new Date(aValue).getTime() : 0;
          bValue = bValue ? new Date(bValue).getTime() : 0;
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [transcriptions, sortConfig]);

  const totalPages = Math.ceil(sortedTranscriptions.length / ITEMS_PER_PAGE);
  const currentTranscriptions = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    return sortedTranscriptions.slice(startIndex, endIndex);
  }, [sortedTranscriptions, currentPage]);

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    } else if (sortConfig.key === key && sortConfig.direction === 'descending') {
      direction = 'ascending';
    }
    setSortConfig({ key, direction });
    setCurrentPage(1);
  };

  const goToPage = (pageNumber) => {
    setCurrentPage(Math.max(1, Math.min(pageNumber, totalPages)));
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? <FiChevronUp className="inline ml-1"/> : <FiChevronDown className="inline ml-1"/>;
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
        <>
          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/2 cursor-pointer hover:bg-gray-100"
                    onClick={() => requestSort('title')}
                  >
                    Título {getSortIcon('title')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/4 cursor-pointer hover:bg-gray-100"
                    onClick={() => requestSort('created_at')}
                  >
                    Fecha {getSortIcon('created_at')}
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-auto">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentTranscriptions.map((transcription) => (
                  <tr key={transcription.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 truncate max-w-md"> 
                      <button
                        onClick={() => onSelectTranscription(transcription)}
                        className="text-primary-600 hover:text-primary-800 font-medium"
                      >
                        {transcription.title || 'Sin título'}
                      </button>
                    </td>
                    <td className="px-6 py-4 text-gray-700">
                      {formatDate(transcription.created_at)}
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
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
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 border-t border-gray-200 pt-4">
              <span className="text-sm text-gray-700">
                Página <span className="font-medium">{currentPage}</span> de <span className="font-medium">{totalPages}</span>
              </span>
              <div className="flex items-center space-x-1">
                <button 
                  onClick={() => goToPage(1)} 
                  disabled={currentPage === 1}
                  className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-gray-500 hover:bg-gray-100"
                  title="Primera página"
                >
                  <FiChevronsLeft />
                </button>
                <button 
                  onClick={() => goToPage(currentPage - 1)} 
                  disabled={currentPage === 1}
                  className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-gray-500 hover:bg-gray-100"
                  title="Página anterior"
                >
                  <FiChevronLeft />
                </button>
                <button 
                  onClick={() => goToPage(currentPage + 1)} 
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-gray-500 hover:bg-gray-100"
                  title="Página siguiente"
                >
                  <FiChevronRight />
                </button>
                <button 
                  onClick={() => goToPage(totalPages)} 
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-gray-500 hover:bg-gray-100"
                  title="Última página"
                >
                  <FiChevronsRight />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TranscriptionHistory;
