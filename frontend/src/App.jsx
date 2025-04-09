import React, { useState, useRef, useEffect } from 'react';
import { FilePond, registerPlugin } from 'react-filepond';
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
import 'filepond/dist/filepond.min.css';
import axios from 'axios';
import Header from './components/Header';
import TranscriptionView from './components/TranscriptionView';
import TranscriptionHistory from './components/TranscriptionHistory';
import Auth from './components/Auth';
import Footer from './components/Footer';
import { FiUpload, FiCpu, FiCheck, FiX, FiLogOut } from 'react-icons/fi';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { API_URL } from './config';

// Register FilePond plugins
registerPlugin(FilePondPluginFileValidateType);

// Configure axios for larger files and longer timeouts
axios.defaults.maxContentLength = 200 * 1024 * 1024; // 200MB
axios.defaults.timeout = 1800000; // 30 minutes

function AppContent() {
  // State variables
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [error, setError] = useState(null);
  const [processId, setProcessId] = useState(null);
  const [transcription, setTranscription] = useState(null);
  const [originalFilename, setOriginalFilename] = useState(null); // Guardar el nombre original del archivo
  const [showHistory, setShowHistory] = useState(false);
  const [selectedTranscriptionTitle, setSelectedTranscriptionTitle] = useState(null);
  const [success, setSuccess] = useState(false); // Estado para mostrar mensaje de éxito
  const [showCompleted, setShowCompleted] = useState(false); // Estado para mostrar la vista de transcripción completada
  
  const { currentUser, logout, token } = useAuth();
  const filePondRef = useRef(null);

  // Function to handle file upload and processing
  const handleProcessFile = async () => {
    try {
      const currentFile = file || (filePondRef.current?.getFiles()[0]?.file);
      
      if (!currentFile) {
        setError('Por favor, selecciona un archivo de audio primero.');
        return;
      }

      if (!['audio/mp3', 'audio/wav', 'video/mp4', 'audio/x-m4a', 'audio/m4a', 'audio/mpeg'].includes(currentFile.type)) {
        setError('Formato de archivo no soportado. Utiliza MP3, WAV, MP4 o M4A.');
        return;
      }

      if (currentFile.size > 200 * 1024 * 1024) { // 200MB
        setError('El archivo es demasiado grande. El tamaño máximo es 200MB.');
        return;
      }

      // Limpiar cualquier transcripción anterior y reiniciar estados
      setTranscription(null);
      setSuccess(false);
      setShowCompleted(false);
      setSelectedTranscriptionTitle(null);
      
      setProcessing(true);
      setProgress(10);
      setError(null);
      setProgressMessage('Preparando archivo para subir...');
      setOriginalFilename(currentFile.name); // Guardar el nombre original del archivo

      const formData = new FormData();
      formData.append('file', currentFile);

      const response = await axios.post(`${API_URL}/api/upload-file/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 30) / progressEvent.total
          );
          setProgress(Math.min(30 + percentCompleted, 60)); // Cap at 60%
          setProgressMessage(`Subiendo archivo: ${percentCompleted < 100 ? percentCompleted : 100}%`);
        },
      });

      console.log('Respuesta del servidor:', response.data);
      
      // Intentar extraer el process_id de diferentes maneras
      let jobId = null;
      
      if (response.data && typeof response.data === 'object') {
        // Intentar obtener con el nuevo nombre job_id
        if (response.data.job_id) {
          jobId = response.data.job_id;
        } 
        // Intentar con el nombre anterior por compatibilidad
        else if (response.data.process_id) {
          jobId = response.data.process_id;
        } 
        // Si no está directamente accesible, verificar si está en alguna propiedad anidada
        else if (response.data.data && (response.data.data.job_id || response.data.data.process_id)) {
          jobId = response.data.data.job_id || response.data.data.process_id;
        }
        // Mostrar todas las propiedades para diagnóstico
        console.log('Propiedades de la respuesta:', Object.keys(response.data));
      }
      
      if (!jobId) {
        console.error('No se recibió un ID de proceso válido del servidor', response.data);
        setError('No se pudo obtener un ID de proceso válido del servidor');
        setProcessing(false);
        return;
      }
      
      console.log('ID del proceso recibido:', jobId);
      setProcessId(jobId);
      
      setProgress(65);
      setProgressMessage('Archivo subido. Procesando audio...');
      
      let statusCheckAttempts = 0;
      const MAX_STATUS_CHECK_ATTEMPTS = 3;
      let completedDetected = false;

      const statusInterval = setInterval(async () => {
        try {
          // Verificar que jobId exista y no sea undefined antes de consultar
          if (!jobId) {
            console.error('No hay un ID de proceso válido');
            clearInterval(statusInterval);
            setProcessing(false);
            setError('No se pudo obtener un ID de proceso válido');
            return;
          }

          // Si ya detectamos que está completado, no hacemos más consultas
          if (completedDetected) {
            console.log('Transcripción ya completada, no se consultará más el estado');
            clearInterval(statusInterval);
            return;
          }

          console.log(`Consultando estado del proceso: ${jobId}`);
          const statusResponse = await axios.get(`${API_URL}/api/status/${jobId}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          console.log('Estado del proceso:', statusResponse.data);
          const status = statusResponse.data.status;
          
          // Reiniciar contador de intentos cuando hay una respuesta exitosa
          statusCheckAttempts = 0;
            
          switch(status) {
            case 'processing_audio':
              setProgressMessage('Procesando audio para transcripción...');
              setProgress(70);
              break;
            case 'transcribing':
              setProgressMessage('Transcribiendo audio con Deepgram (esto puede tomar varios minutos)...');
              setProgress(80);
              break;
            case 'completed':
              setProgressMessage('Transcripción completada. Los resultados están disponibles.');
              setProgress(100);
              completedDetected = true;
                
              try {
                console.log(`Obteniendo resultados del proceso: ${jobId}`);
                const resultsResponse = await axios.get(`${API_URL}/api/results/${jobId}`, {
                  headers: {
                    'Authorization': `Bearer ${token}`
                  }
                });
                console.log("Resultados recibidos:", resultsResponse.data);
                
                if (resultsResponse.data && resultsResponse.data.transcription) {
                  // Usar la nueva función unificada
                  const title = file && file.name 
                    ? `Transcripción de ${file.name}` 
                    : "Transcripción completada";
                  
                  handleTranscriptionCompleted(
                    resultsResponse.data.transcription,
                    title
                  );
                  
                  console.log("Transcripción y vista actualizadas correctamente");
                } else {
                  throw new Error("La respuesta no contiene datos de transcripción");
                }
              } catch (resultError) {
                console.error('Error al obtener resultados:', resultError);
                console.error('Detalles del error:', resultError.response ? resultError.response.data : 'No hay detalles');
                
                // No establecer un mensaje de error visible aquí, simplemente cambiar el mensaje de progreso
                setProgressMessage('Buscando transcripción en el historial...');
                setProcessing(false);
                
                // Intentar obtener los resultados del historial en segundo plano - se manejará automáticamente por el useEffect
                console.log("Intentando obtener resultados desde el historial a través del useEffect...");
              }
                
              clearInterval(statusInterval);
              break;
            case 'error':
              setError(`Error en el procesamiento: ${statusResponse.data.error || 'Error desconocido'}`);
              setProcessing(false);
              clearInterval(statusInterval);
              break;
          }
            
        } catch (error) {
          console.error('Error al verificar estado:', error);
          
          // Incrementar contador de intentos fallidos
          statusCheckAttempts++;
          
          // Si hay demasiados intentos fallidos consecutivos, verificar directamente en la base de datos
          if (statusCheckAttempts >= MAX_STATUS_CHECK_ATTEMPTS) {
            console.log(`Demasiados errores consecutivos (${statusCheckAttempts}). Verificando en la base de datos...`);
            try {
              // Verificar en el historial si la transcripción está completada
              const historyResponse = await axios.get(`${API_URL}/api/transcriptions/user`, {
                headers: {
                  'Authorization': `Bearer ${token}`
                }
              });
              
              // Buscar si el job_id actual está en el historial y está completado
              const transcriptionItem = historyResponse.data.find(
                t => t.job_id === jobId && t.status === 'completed'
              );
              
              if (transcriptionItem) {
                console.log('Transcripción encontrada en el historial como completada');
                setProgressMessage('¡Transcripción completada! Disponible en el historial.');
                setProgress(100);
                setProcessing(false);
                completedDetected = true;
                clearInterval(statusInterval);
              }
            } catch (historyError) {
              console.error('Error al verificar el historial:', historyError);
            }
          }
        }
      }, 5000); // Verificar cada 5 segundos

    } catch (error) {
      console.error('Error processing file:', error);
      setError('Error al procesar el archivo: ' + (error.response?.data?.detail || error.message));
      setProcessing(false);
    }
  };

  // Esta función se ejecuta cuando se detecta que una transcripción ha sido completada
  const handleTranscriptionCompleted = (transcriptionText, title) => {
    // Limpiar cualquier estado de error previo
    setError(null);
    
    // Establecer los datos de la transcripción
    setTranscription(transcriptionText);
    setSelectedTranscriptionTitle(title);
    
    // Detener la animación de procesamiento y mostrar éxito
    setProcessing(false);
    setSuccess(true);
    setShowCompleted(true);
    
    // Log para debug
    console.log("[handleTranscriptionCompleted] Transcripción cargada correctamente");
  };

  // Function to handle file download
  const handleDownload = async () => {
    try {
      if (!processId) {
        setError('No hay transcripción disponible para descargar.');
        return;
      }
      
      setProgressMessage('Preparando archivo para descarga...');
      
      // Obtener el blob del archivo
      const response = await axios.get(`${API_URL}/api/download/${processId}?format=txt`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      });
      
      // Crear URL para el blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // Crear elemento de enlace para la descarga
      const link = document.createElement('a');
      link.href = url;
      
      // Nombre del archivo
      const filename = originalFilename 
        ? `Transcripcion_${originalFilename.replace(/\.[^/.]+$/, '')}.txt` 
        : `Transcripcion_${new Date().toISOString().slice(0, 10)}.txt`;
      
      link.setAttribute('download', filename);
      
      // Añadir al DOM, hacer clic y eliminar
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Liberar URL
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error al descargar la transcripción:', error);
      setError('Error al descargar la transcripción. Intenta nuevamente.');
    }
  };

  const handleSelectHistoryTranscription = (selectedTranscription) => {
    // Usar nuestra función unificada para manejar la selección del historial
    handleTranscriptionCompleted(selectedTranscription.content, selectedTranscription.title);
    
    // Guardar el ID de la transcripción seleccionada del historial
    setProcessId(selectedTranscription.id);
    
    // Cerrar la vista de historial
    setShowHistory(false);
  };

  // Limpiar completamente el estado y reiniciar para una nueva transcripción
  const clearTranscription = () => {
    setTranscription(null);
    setFile(null);
    setProcessId(null);
    setProgress(0);
    setProgressMessage('');
    setError(null); // Reiniciar el estado de error
    setSuccess(false); // Reiniciar el estado de éxito
    setShowCompleted(false); // Reiniciar la vista de transcripción completada
    setSelectedTranscriptionTitle(null);
    
    // Limpiar FilePond
    if (filePondRef.current) {
      filePondRef.current.removeFiles();
    }
  };

  const handleLogout = () => {
    logout();
    clearTranscription();
  };

  const toggleHistory = () => {
    setShowHistory(!showHistory);
  };

  // Añadir un useEffect que verifique el estado cuando processId cambia
  useEffect(() => {
    // Solo verificar cuando hay un processId válido
    if (processId && progress === 100) {
      // Limpiar cualquier mensaje de error previo
      setError(null);
      
      const fetchTranscriptionData = async () => {
        if (!processId) return;
        
        try {
          // Verificar el estado primero
          const statusResponse = await axios.get(`${API_URL}/api/status/${processId}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          console.log('Estado de la transcripción:', statusResponse.data);
          
          if (statusResponse.data.status === 'completed') {
            // Si está completo, obtener los resultados
            const resultsResponse = await axios.get(`${API_URL}/api/results/${processId}`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            console.log('Resultados de la transcripción:', resultsResponse.data);
            
            // Actualizar el estado con la transcripción
            if (resultsResponse.data.transcription) {
              setTranscription(resultsResponse.data.transcription);
              handleTranscriptionCompleted(
                resultsResponse.data.transcription,
                `Transcripción de ${originalFilename || 'audio'}`
              );
            } else {
              setError('La transcripción no contiene texto.');
            }
            
            setProcessing(false);
            setProgress(100);
            setProgressMessage('Transcripción completada');
            setSuccess(true);
            setShowCompleted(true);
            
            // Limpiar el intervalo
            return true;
          } else if (statusResponse.data.status === 'error') {
            setError(`Error en la transcripción: ${statusResponse.data.error || 'Error desconocido'}`);
            setProcessing(false);
            return true;
          } else {
            // Actualizar progreso
            setProgress(Math.min(60 + Math.random() * 20, 95)); // Random progress between 60-95%
            setProgressMessage('Procesando audio y generando transcripción...');
            return false;
          }
        } catch (error) {
          console.error('Error al verificar el estado de la transcripción:', error);
          setError('Error al verificar el estado de la transcripción. Intenta nuevamente.');
          setProcessing(false);
          return true;
        }
      };

      fetchTranscriptionData();
    }
  }, [processId, progress, token]);

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        
        <main className="flex-grow container mx-auto px-4 py-8 flex flex-col items-center justify-center">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-4">Bienvenido a la App de Transcripción</h1>
            <p className="text-gray-600 mb-8">Inicia sesión o regístrate para comenzar a transcribir tus archivos de audio.</p>
          </div>
          
          <Auth />
        </main>
        
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      <div className="bg-primary-600 text-white py-2 px-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center">
            <span className="font-medium">Usuario: {currentUser.username}</span>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={toggleHistory}
              className="text-white hover:text-gray-200 text-sm font-medium flex items-center"
            >
              {showHistory ? 'Nueva Transcripción' : 'Ver Historial'}
            </button>
            <button
              onClick={handleLogout}
              className="text-white hover:text-gray-200 text-sm font-medium flex items-center"
            >
              <FiLogOut className="mr-1" /> Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
      
      <main className="container max-w-4xl mx-auto px-4 py-8 flex-grow">
        {showHistory ? (
          <TranscriptionHistory onSelectTranscription={handleSelectHistoryTranscription} />
        ) : (
          <>
            {transcription || showCompleted ? (
              <>
                {/* Mensaje de éxito verde */}
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative mb-4 flex items-center">
                  <FiCheck className="text-green-500 mr-2" />
                  Transcripción completada con éxito.
                </div>
                
                {/* Botón iniciar nueva transcripción */}
                <div className="mb-4">
                  <button
                    onClick={clearTranscription}
                    className="text-primary-600 hover:text-primary-800 font-medium"
                  >
                    Iniciar nueva transcripción
                  </button>
                </div>
                
                {/* Vista de transcripción */}
                {transcription && (
                  <TranscriptionView 
                    transcription={transcription} 
                    title={selectedTranscriptionTitle}
                    onDownload={handleDownload} 
                  />
                )}
              </>
            ) : (
              <>
                <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                  <h1 className="text-3xl font-bold text-gray-800 mb-6">Cargar Archivo de Audio</h1>
                  
                  <div className="mb-6">
                    <FilePond
                      ref={filePondRef}
                      allowFileTypeValidation={true}
                      acceptedFileTypes={['audio/mp3', 'audio/wav', 'video/mp4', 'audio/x-m4a', 'audio/m4a', 'audio/mpeg']}
                      labelFileTypeNotAllowed="Formato de archivo inválido"
                      fileValidateTypeLabelExpectedTypes="Se esperan archivos de audio (MP3, WAV, MP4, M4A)"
                      labelIdle='Arrastra y suelta tu archivo de audio aquí o <span class="filepond--label-action">Selecciona</span>'
                      oninit={() => console.log('FilePond instance initialized')}
                      onupdatefiles={(fileItems) => {
                        console.log('Archivos actualizados', fileItems);
                        setFile(fileItems.length > 0 ? fileItems[0].file : null);
                      }}
                      disabled={processing}
                    />
                  </div>
                  
                  <button
                    onClick={handleProcessFile}
                    disabled={(!file && !filePondRef.current?.getFiles().length) || processing}
                    className={`w-full flex items-center justify-center py-3 px-4 rounded-md font-medium text-white ${
                      (!file && !filePondRef.current?.getFiles().length) || processing
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-primary-600 hover:bg-primary-700'
                    }`}
                  >
                    {processing ? (
                      <>
                        <FiCpu className="animate-spin mr-2" />
                        Procesando...
                      </>
                    ) : (
                      <>
                        <FiUpload className="mr-2" />
                        Transcribir Audio
                      </>
                    )}
                  </button>
                </div>
                
                {/* Barra de progreso solo visible durante el procesamiento */}
                {processing && (
                  <div className="bg-gray-100 rounded-lg p-4 mt-4">
                    <div className="mb-2 flex justify-between items-center">
                      <span className="text-gray-700">{progressMessage}</span>
                      <span className="text-gray-700">{progress}%</span>
                    </div>
                    <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-600 transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </main>
      
      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
