import React, { useState, useEffect } from 'react';
import { FiCopy, FiDownload, FiCheck, FiPlay } from 'react-icons/fi';

/**
 * Formatea segundos a formato [mm:ss]
 * @param {number} seconds - Tiempo en segundos 
 * @returns {string} - Tiempo formateado [mm:ss]
 */
const formatTimestamp = (seconds) => {
  if (!seconds && seconds !== 0) return '[--:--]';
  
  // Redondear a 2 decimales
  seconds = Math.round(seconds * 100) / 100;
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  // Formatear como [mm:ss]
  return `[${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}]`;
};

const TranscriptionView = ({ transcription, onDownload }) => {
  const [copySuccess, setCopySuccess] = useState(false);
  const [utterances, setUtterances] = useState([]);
  const [showTimestamps, setShowTimestamps] = useState(true);

  // Función para crear un utterance de respaldo con toda la transcripción
  const createFallbackUtterance = () => {
    const text = typeof transcription === 'object' 
      ? transcription.transcription || transcription.content || ''
      : String(transcription || '');
    
    return [{
      start: 0,
      end: 0,
      transcript: text,
      id: 'single-utterance'
    }];
  };

  useEffect(() => {
    // Extraer utterances de la transcripción
    if (transcription && typeof transcription === 'object') {
      // Si tenemos utterances_json y es un array no vacío, usamos esos datos
      if (transcription.utterances_json && 
          Array.isArray(transcription.utterances_json) && 
          transcription.utterances_json.length > 0) {
        
        // Ordenamos por tiempo de inicio
        const sortedUtterances = [...transcription.utterances_json]
          .sort((a, b) => a.start - b.start);
        setUtterances(sortedUtterances);
        
      } else if (transcription.utterances_json && 
                typeof transcription.utterances_json === 'object' && 
                !Array.isArray(transcription.utterances_json)) {
        
        // Si es un objeto individual, lo convertimos a array
        setUtterances([transcription.utterances_json]);
        
      } else {
        // [SF] Si no hay utterances válidos, creamos un utterance único con toda la transcripción
        setUtterances(createFallbackUtterance());
      }
    } else if (typeof transcription === 'string') {
      // Si es una cadena, creamos un utterance único
      setUtterances([{
        start: 0,
        end: 0,
        transcript: transcription,
        id: 'single-utterance'
      }]);
    } else {
      setUtterances([]);
    }
  }, [transcription]);

  const handleCopyClick = async () => {
    try {
      // Verificar si transcription es un objeto o una cadena
      const textToCopy = typeof transcription === 'object' ? 
        transcription.transcription || transcription.content || 'No hay transcripción disponible' : 
        transcription;
      
      await navigator.clipboard.writeText(textToCopy);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Error al copiar texto: ', err);
    }
  };

  const toggleTimestamps = () => {
    setShowTimestamps(!showTimestamps);
  };

  // Si no hay transcripción, mostramos un mensaje
  if (!transcription || (typeof transcription === 'object' && !transcription.transcription && !transcription.content)) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-semibold text-gray-800">Transcripción</h2>
        <div className="border border-gray-200 rounded-md p-4 mt-4 bg-gray-50">
          <p className="text-gray-500 italic">No hay transcripción disponible</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-800">Transcripción</h2>
        <div className="flex space-x-2">
          <button
            onClick={toggleTimestamps}
            className={`flex items-center px-3 py-2 ${showTimestamps ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-700'} rounded-md transition-colors duration-200`}
            title={showTimestamps ? "Ocultar timestamps" : "Mostrar timestamps"}
          >
            <FiPlay className="mr-1" />
            {showTimestamps ? 'Ocultar timestamps' : 'Mostrar timestamps'}
          </button>
          <button
            onClick={handleCopyClick}
            className="flex items-center px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-gray-700 transition-colors duration-200"
            title="Copiar transcripción"
          >
            {copySuccess ? <FiCheck className="mr-1" /> : <FiCopy className="mr-1" />}
            {copySuccess ? 'Copiado' : 'Copiar'}
          </button>
          <button
            onClick={onDownload}
            className="flex items-center px-3 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-md transition-colors duration-200"
            title="Descargar como TXT"
          >
            <FiDownload className="mr-1" />
            TXT
          </button>
        </div>
      </div>
      
      <div className="border border-gray-200 rounded-md overflow-auto p-4 max-h-96 bg-gray-50">
        {utterances.length > 0 ? (
          <div className="space-y-2">

            
            {utterances.map((utterance, index) => (
              <div key={utterance.id || index} className="pb-2 last:pb-0">
                {showTimestamps && (
                  <span className="text-primary-700 font-mono mr-2">
                    {formatTimestamp(utterance.start)}
                  </span>
                )}
                <span>{utterance.transcript}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">No hay segmentos disponibles</p>
        )}
      </div>
    </div>
  );
};

export default TranscriptionView;
