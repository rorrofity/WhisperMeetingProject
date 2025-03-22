import React, { useState } from 'react';
import { FiCopy, FiDownload, FiCheck } from 'react-icons/fi';

const TranscriptionView = ({ transcription, onDownload }) => {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyClick = async () => {
    try {
      await navigator.clipboard.writeText(transcription);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Error al copiar texto: ', err);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-800">Transcripción</h2>
        <div className="flex space-x-2">
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
        <p className="whitespace-pre-line">{transcription || 'No hay transcripción disponible'}</p>
      </div>
    </div>
  );
};

export default TranscriptionView;
