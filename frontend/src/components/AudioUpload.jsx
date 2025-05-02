import React, { useState, useContext } from 'react';
import { FilePond, registerPlugin } from 'react-filepond';
import 'filepond/dist/filepond.min.css'; // Estilos base de FilePond
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
import 'filepond-plugin-file-validate-type/dist/filepond-plugin-file-validate-type.css'; // Estilos del plugin de validación
// No necesitamos importar FiUploadCloud explícitamente, FilePond maneja el icono.
import axios from 'axios';
import { AuthContext } from '../contexts/AuthContext'; // Asumiendo que usas AuthContext para el token
import { buildApiUrl } from '../config'; // [SF] Importamos buildApiUrl para normalizar las URL

// Registrar el plugin de validación de tipo de archivo
registerPlugin(FilePondPluginFileValidateType);

function AudioUpload() {
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState(''); // 'uploading', 'success', 'error'
  const [errorMessage, setErrorMessage] = useState('');
  const { token } = useContext(AuthContext); // Obtener token de autenticación

  // Función para manejar la subida real del archivo a través de FilePond
  const handleFileProcess = (fieldName, file, metadata, load, error, progress, abort) => {
    setUploadStatus('uploading');
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', file, file.name); // 'file' debe coincidir con el nombre esperado en el backend

    // [IV] Validación de entrada: FilePond ya valida el tipo con acceptedFileTypes.
    // Se podrían añadir validaciones de tamaño aquí si fuera necesario.

    axios.post(buildApiUrl('upload'), formData, { // [SF] Usamos buildApiUrl para evitar problemas con doble slash
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}` // Enviar token JWT
      },
      onUploadProgress: (progressEvent) => {
        // Actualizar barra de progreso de FilePond
        progress(true, progressEvent.loaded, progressEvent.total);
      }
    })
    .then(response => {
      console.log('Archivo subido con éxito:', response.data);
      setUploadStatus('success');
      // load() notifica a FilePond que la subida terminó. Se puede pasar un ID si el backend lo devuelve.
      load(response.data.job_id || file.name); // Usar job_id si está disponible, sino el nombre del archivo
      // Podrías querer actualizar el estado global o llamar a una función del padre aquí
      // Por ejemplo, para refrescar la lista de historial.
    })
    .catch(err => {
      console.error('Error en la subida:', err);
      // [IV] Mostrar error claro al usuario
      const apiError = err.response?.data?.detail || 'Error al subir el archivo.';
      setErrorMessage(apiError);
      setUploadStatus('error');
      // error() notifica a FilePond que hubo un fallo.
      error(apiError);
    });

    // Devolver un objeto con un método abort para permitir cancelación
    return {
      abort: () => {
        // Aquí podrías añadir lógica para cancelar la petición axios si es necesario
        console.log('Subida cancelada');
        setUploadStatus('');
        abort();
      }
    };
  };

  return (
    // Contenedor principal que centra y estiliza el área de carga
    <div className="flex justify-center items-start pt-10 min-h-screen bg-gray-100">
        <div className="w-full max-w-lg bg-white p-8 rounded-xl shadow-lg">
            {/* Encabezado similar a la imagen */}
             <div className="flex justify-between items-center mb-6 pb-4 border-b">
                 <div className="flex items-center space-x-2">
                    {/* Placeholder para el logo - Asegúrate de tener un logo SVG o imagen */}
                    <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /> {/* Ejemplo de icono tipo rayo */}
                    </svg>
                    <span className="text-2xl font-bold text-gray-800">ROCKETFLOW</span>
                 </div>
                 <div className="flex items-center space-x-4">
                     <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition duration-150 ease-in-out">Historial</button>
                     <button className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition duration-150 ease-in-out">
                         <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" /></svg>
                         Admin
                     </button>
                 </div>
             </div>

            {/* Contenedor para FilePond con el estilo deseado */}
            <div className="filepond-container mt-6 p-6 border-2 border-dashed border-blue-400 rounded-lg bg-blue-50 hover:bg-blue-100 transition duration-150 ease-in-out">
                <FilePond
                files={files}
                onupdatefiles={setFiles} // Actualiza el estado cuando los archivos cambian
                allowMultiple={false}    // Solo permitir un archivo a la vez
                maxFiles={1}
                server={{ process: handleFileProcess }} // Define cómo procesar (subir) los archivos
                name="file" // Nombre del campo que el backend espera para el archivo
                // Texto que se muestra cuando no hay archivos. Usa HTML para el enlace.
                labelIdle='Arrastra y suelta un archivo de audio aquí o <span class="filepond--label-action"> Seleccionar archivo </span>'
                // [IV] Tipos de archivo aceptados (mime types)
                acceptedFileTypes={['audio/*']}
                // Mensajes de error de validación en español
                labelFileTypeNotAllowed="Tipo de archivo no válido"
                fileValidateTypeLabelExpectedTypes="Se espera un archivo de audio (ej: MP3, WAV, M4A)"
                 // Detectar tipo de archivo para validación más robusta [IV]
                 fileValidateTypeDetectType={(source, type) => new Promise((resolve, reject) => {
                    // Lista explícita de tipos comunes + genérico 'audio/*'
                    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a', 'audio/aac', 'audio/flac', 'audio/webm', 'audio/amr'];
                     console.log("Detected MIME type:", type); // Log para depuración
                    if (allowedTypes.includes(type) || type.startsWith('audio/')) {
                        resolve(type);
                    } else {
                        console.warn(`Rejected type: ${type}`);
                        reject(type); // Rechaza si no es un tipo de audio conocido/genérico
                    }
                  })}
                credits={false} // Ocultar créditos de FilePond
                />
                {/* Mostrar estado de la subida o errores */}
                <div className="mt-4 text-center h-6"> {/* Altura fija para evitar saltos de layout */}
                    {uploadStatus === 'uploading' && <p className="text-sm text-blue-600 animate-pulse">Subiendo...</p>}
                    {uploadStatus === 'success' && <p className="text-sm text-green-600">¡Archivo subido con éxito!</p>}
                    {uploadStatus === 'error' && <p className="text-sm text-red-600">Error: {errorMessage}</p>}
                </div>
            </div>
        </div>
    </div>
  );
}

export default AudioUpload;
