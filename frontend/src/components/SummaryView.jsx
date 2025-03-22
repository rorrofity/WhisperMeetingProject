import React from 'react';
import { FiDownload, FiRefreshCw } from 'react-icons/fi';

const SummaryView = ({ summaries, onDownload, onCleanup }) => {
  const { short, detailed } = summaries;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-800">Resúmenes</h2>
        <div className="flex space-x-2">
          <button
            onClick={onDownload}
            className="flex items-center px-3 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-md transition-colors duration-200"
            title="Descargar como PDF"
          >
            <FiDownload className="mr-1" />
            PDF
          </button>
          <button
            onClick={onCleanup}
            className="flex items-center px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-md transition-colors duration-200"
            title="Limpiar y empezar de nuevo"
          >
            <FiRefreshCw className="mr-1" />
            Nuevo
          </button>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-800 mb-2">Resumen Corto</h3>
        <div className="border border-gray-200 rounded-md p-4 bg-gray-50">
          <p className="text-gray-700">{short || 'No hay resumen disponible'}</p>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Resumen Detallado</h3>
        <div className="border border-gray-200 rounded-md p-4 bg-gray-50">
          <p className="text-gray-700 whitespace-pre-line">{detailed || 'No hay resumen disponible'}</p>
        </div>
      </div>
    </div>
  );
};

export default SummaryView;
