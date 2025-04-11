import React, { useState } from 'react';
import { FiRefreshCw, FiChevronDown, FiChevronUp } from 'react-icons/fi';

const SummaryView = ({ summaries, onCleanup }) => {
  // Controlar el estado de colapso de cada sección
  const [isSummaryExpanded, setSummaryExpanded] = useState(true);
  const [areKeyPointsExpanded, setKeyPointsExpanded] = useState(true);
  const [areActionItemsExpanded, setActionItemsExpanded] = useState(true);
  
  // Extraer los datos del resumen de la estructura mejorada
  const shortSummary = summaries?.short_summary || '';
  const keyPoints = Array.isArray(summaries?.key_points) ? summaries.key_points : [];
  const actionItems = Array.isArray(summaries?.action_items) ? summaries.action_items : [];
  
  // Verificar el estado del resumen
  const summaryStatus = summaries?.summary_status || 'pending';
  const isSummaryPending = summaryStatus === 'pending';
  
  // Verificar si hay algún resumen disponible
  const hasSummary = (shortSummary || keyPoints.length > 0 || actionItems.length > 0) && !isSummaryPending;

  // Componente reutilizable para secciones colapsables
  const CollapsibleSection = ({ title, isExpanded, setExpanded, content, isEmpty, emptyMessage }) => (
    <div className="mb-4 border border-gray-200 rounded-md overflow-hidden">
      <div 
        className="flex justify-between items-center p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={() => setExpanded(!isExpanded)}
      >
        <h3 className="text-lg font-medium text-gray-800">{title}</h3>
        <button className="text-gray-500 hover:text-gray-700">
          {isExpanded ? <FiChevronUp /> : <FiChevronDown />}
        </button>
      </div>
      
      {isExpanded && (
        <div className="p-4 bg-white">
          {isEmpty ? (
            <p className="text-gray-500 italic">{emptyMessage}</p>
          ) : content}
        </div>
      )}
    </div>
  );

  // Componente de indicador de carga para el resumen pendiente
  const LoadingIndicator = () => (
    <div className="flex flex-col items-center justify-center py-8 bg-gray-50 border border-gray-200 rounded-md">
      <div className="mb-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
      <p className="text-gray-600">Generando resumen de la reunión...</p>
      <p className="text-gray-500 text-sm mt-1">Esto puede tomar hasta 2 minutos dependiendo de la longitud del audio.</p>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-800">Resumen</h2>
        <div className="flex space-x-2">
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

      {!hasSummary && !isSummaryPending ? (
        <div className="text-center py-6 border border-gray-200 rounded-md bg-gray-50">
          <p className="text-gray-500">No hay resumen disponible para esta transcripción.</p>
        </div>
      ) : isSummaryPending ? (
        <LoadingIndicator />
      ) : (
        <div>
          <CollapsibleSection
            title="TL;DR (Resumen Corto)"
            isExpanded={isSummaryExpanded}
            setExpanded={setSummaryExpanded}
            content={<p className="text-gray-700">{shortSummary}</p>}
            isEmpty={!shortSummary}
            emptyMessage="No hay resumen corto disponible"
          />
          
          <CollapsibleSection
            title="Puntos Clave"
            isExpanded={areKeyPointsExpanded}
            setExpanded={setKeyPointsExpanded}
            content={
              <ul className="list-disc pl-5 text-gray-700 space-y-1">
                {keyPoints.map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
              </ul>
            }
            isEmpty={keyPoints.length === 0}
            emptyMessage="No hay puntos clave disponibles"
          />
          
          <CollapsibleSection
            title="Elementos de Acción"
            isExpanded={areActionItemsExpanded}
            setExpanded={setActionItemsExpanded}
            content={
              <ul className="list-disc pl-5 text-gray-700 space-y-1">
                {actionItems.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            }
            isEmpty={actionItems.length === 0}
            emptyMessage="No hay elementos de acción disponibles"
          />
        </div>
      )}
    </div>
  );
};

export default SummaryView;
