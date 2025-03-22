import React, { useState, useRef } from 'react';
import { FilePond, registerPlugin } from 'react-filepond';
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
import 'filepond/dist/filepond.min.css';
import axios from 'axios';
import Header from './components/Header';
import TranscriptionView from './components/TranscriptionView';
import Footer from './components/Footer';
import { FiUpload, FiCpu, FiCheck, FiX } from 'react-icons/fi';

// Register FilePond plugins
registerPlugin(FilePondPluginFileValidateType);

// Configure axios for larger files and longer timeouts
axios.defaults.maxContentLength = 200 * 1024 * 1024; // 200MB
axios.defaults.timeout = 1800000; // 30 minutes

function App() {
  // State variables
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [error, setError] = useState(null);
  const [processId, setProcessId] = useState(null);
  const [transcription, setTranscription] = useState(null);
  const [originalFilename, setOriginalFilename] = useState(null); // Guardar el nombre original del archivo
  
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

      setProcessing(true);
      setProgress(10);
      setError(null);
      setProgressMessage('Preparando archivo para subir...');
      setOriginalFilename(currentFile.name); // Guardar el nombre original del archivo

      const formData = new FormData();
      formData.append('file', currentFile);

      const response = await axios.post('http://localhost:8000/upload-file/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 30) / progressEvent.total
          );
          setProgress(Math.min(30 + percentCompleted, 60)); // Cap at 60%
          setProgressMessage(`Subiendo archivo: ${percentCompleted < 100 ? percentCompleted : 100}%`);
        },
      });

      const jobId = response.data.process_id;
      setProcessId(jobId);
      
      setProgress(65);
      setProgressMessage('Archivo subido. Procesando audio...');
      
      const statusInterval = setInterval(async () => {
        try {
          const statusResponse = await axios.get(`http://localhost:8000/status/${jobId}`);
          const status = statusResponse.data.status;
            
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
              setProgressMessage('¡Transcripción completada!');
              setProgress(100);
                
              const resultsResponse = await axios.get(`http://localhost:8000/results/${jobId}`);
                
              setTranscription(resultsResponse.data.transcription);
              setProcessing(false);
                
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
        }
      }, 5000); // Verificar cada 5 segundos

    } catch (error) {
      console.error('Error processing file:', error);
      setProcessing(false);
    }
  };

  // Function to handle file download
  const handleDownload = async () => {
    if (!processId) return;
    
    try {
      const response = await axios.get(
        `http://localhost:8000/download/${processId}?format=txt`, 
        { responseType: 'blob' }
      );
      
      let filename = '';
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }
      
      if (!filename && originalFilename) {
        const nameWithoutExt = originalFilename.split('.').slice(0, -1).join('.');
        filename = nameWithoutExt ? `${nameWithoutExt}.txt` : `${originalFilename}.txt`;
      } else if (!filename) {
        filename = `transcripcion_${new Date().toISOString().slice(0, 10)}.txt`;
      }
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      
      link.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading file:', error);
      setError('Error al descargar el archivo.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">Cargar Archivo de Audio</h1>
          
          <div className="mb-6">
            {!transcription && (
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
            )}
            
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
          
          <div className="mb-4">
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
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4 flex items-center">
              <FiX className="text-red-500 mr-2" />
              {error}
            </div>
          )}
          
          {transcription && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative mb-4 flex items-center">
              <FiCheck className="text-green-500 mr-2" />
              Transcripción completada con éxito.
            </div>
          )}
        </div>
        
        {transcription && (
          <TranscriptionView 
            transcription={transcription} 
            onDownload={handleDownload} 
          />
        )}
      </main>
      
      <Footer />
    </div>
  );
}

export default App;
