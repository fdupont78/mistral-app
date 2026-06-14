/**
 * Model controls component for the sidebar
 */

import React from 'react';
import { ModelStatus, QuantizationMethod, QUANTIZATION_OPTIONS } from '../types';

export interface ModelControlsProps {
  status: ModelStatus;
  quantizationMethod: QuantizationMethod;
  autoLoadModel: boolean;
  onLoad: (quantMethod: QuantizationMethod) => void;
  onUnload: () => void;
  onToggleAutoLoad: (value: boolean) => void;
}

export function ModelControls({
  status,
  quantizationMethod,
  autoLoadModel,
  onLoad,
  onUnload,
  onToggleAutoLoad,
}: ModelControlsProps) {
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  // Handle load model
  const handleLoadModel = async (quantMethod: QuantizationMethod) => {
    setIsLoading(true);
    try {
      await onLoad(quantMethod);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle unload model
  const handleUnloadModel = async () => {
    setIsLoading(true);
    try {
      await onUnload();
    } finally {
      setIsLoading(false);
    }
  };

  // Get status color
  const getStatusColor = (): string => {
    if (status.loading) return 'text-yellow-500';
    if (status.loaded) return 'text-green-500';
    return 'text-gray-500';
  };

  // Get status text
  const getStatusText = (): string => {
    if (status.loading) return 'Loading...';
    if (status.loaded) return 'Loaded ✓';
    return 'Not loaded';
  };

  // Check if model is loading or loaded
  const isModelBusy = status.loading || status.loaded;

  return (
    <div className="mb-6">
      <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
          <rect x="2" y="2" width="20" height="20" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="2" y1="10" x2="22" y2="10"></line>
        </svg>
        Model
      </h2>

      {/* Status */}
      <div className="mb-3">
        <div className="text-xs text-gray-500 mb-1">Status</div>
        <div className={`text-sm font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </div>
      </div>

      {/* Quantization */}
      <div className="mb-3">
        <div className="text-xs text-gray-500 mb-1">Quantization</div>
        <select
          value={quantizationMethod}
          onChange={(e) => onToggleAutoLoad(false)} // Disable auto-load when manually changing
          disabled={isModelBusy}
          className="w-full px-2 py-1 border rounded text-sm bg-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {QUANTIZATION_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div className="text-xs text-gray-400 mt-1">
          {QUANTIZATION_OPTIONS.find(o => o.value === quantizationMethod)?.description}
        </div>
      </div>

      {/* Auto-load checkbox */}
      <div className="mb-3">
        <label className="flex items-center text-sm">
          <input
            type="checkbox"
            checked={autoLoadModel}
            onChange={(e) => onToggleAutoLoad(e.target.checked)}
            disabled={isModelBusy}
            className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
          />
          <span className="text-gray-700">Auto-load on startup</span>
        </label>
      </div>

      {/* Action buttons */}
      <div className="flex space-x-2">
        <button
          onClick={() => handleLoadModel(quantizationMethod)}
          disabled={isModelBusy || isLoading}
          className="flex-1 flex items-center justify-center px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
              <polyline points="22 6 12 14 2 6"></polyline>
              <path d="M2 6l6 6 6-6"></path>
              <path d="M12 14v7"></path>
            </svg>
          )}
          Load Model
        </button>
        
        <button
          onClick={handleUnloadModel}
          disabled={!status.loaded || isLoading}
          className="flex-1 flex items-center justify-center px-3 py-2 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
            <rect x="2" y="6" width="20" height="12" rx="2"></rect>
            <path d="M12 16v4"></path>
            <path d="M8 16h8"></path>
            <path d="M6 10h12"></path>
          </svg>
          Unload
        </button>
      </div>

      {/* Dry-run notice */}
      {import.meta.env.VITE_DRY_RUN === 'true' && (
        <div className="mt-3 p-2 bg-green-100 text-green-700 text-xs rounded">
          🎭 Dry-run mode: Mock responses only (no model loading)
        </div>
      )}
    </div>
  );
}

export default ModelControls;
