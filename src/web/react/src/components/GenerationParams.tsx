/**
 * Generation parameters component for the sidebar
 */

import React from 'react';
import { GenerationParams, DEFAULT_GENERATION_PARAMS } from '../types';

export interface GenerationParamsProps {
  params: GenerationParams;
  onChange: (params: GenerationParams) => void;
}

// Parameter descriptions
const PARAM_DESCRIPTIONS: Record<keyof GenerationParams, string> = {
  max_new_tokens: 'Maximum new tokens to generate (higher = longer responses)',
  temperature: 'Randomness: 0.0=deterministic, 1.0+ = more creative/random',
  do_sample: 'Enable sampling (False = greedy/argmax decoding)',
  top_k: 'Keep only top-k highest probability tokens for sampling',
  top_p: 'Nucleus sampling: keep tokens with cumulative probability > p',
  repetition_penalty: 'Penalty for repeated tokens (1.0=no penalty, >1.0=discourage repetition)',
  num_return_sequences: 'Number of response sequences to generate',
};

export function GenerationParamsComponent({ params, onChange }: GenerationParamsProps) {
  // Handle parameter change
  const handleChange = (key: keyof GenerationParams, value: number | boolean) => {
    onChange({
      ...params,
      [key]: value,
    });
  };

  // Reset to defaults
  const handleReset = () => {
    onChange(DEFAULT_GENERATION_PARAMS);
  };

  return (
    <div className="mb-6">
      <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
        Generation Parameters
      </h2>

      <div className="space-y-4">
        {/* Float parameters (sliders) */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-gray-600">max_new_tokens</label>
            <span className="text-xs font-medium">{params.max_new_tokens}</span>
          </div>
          <input
            type="range"
            min={16}
            max={2048}
            step={16}
            value={params.max_new_tokens}
            onChange={(e) => handleChange('max_new_tokens', Number(e.target.value))}
            className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="text-xs text-gray-400 mt-1">{PARAM_DESCRIPTIONS.max_new_tokens}</div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-gray-600">temperature</label>
            <span className="text-xs font-medium">{params.temperature.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0}
            max={2}
            step={0.05}
            value={params.temperature}
            onChange={(e) => handleChange('temperature', Number(e.target.value))}
            className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="text-xs text-gray-400 mt-1">{PARAM_DESCRIPTIONS.temperature}</div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-gray-600">top_p</label>
            <span className="text-xs font-medium">{params.top_p.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={params.top_p}
            onChange={(e) => handleChange('top_p', Number(e.target.value))}
            className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="text-xs text-gray-400 mt-1">{PARAM_DESCRIPTIONS.top_p}</div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-gray-600">repetition_penalty</label>
            <span className="text-xs font-medium">{params.repetition_penalty.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0.5}
            max={2}
            step={0.1}
            value={params.repetition_penalty}
            onChange={(e) => handleChange('repetition_penalty', Number(e.target.value))}
            className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="text-xs text-gray-400 mt-1">{PARAM_DESCRIPTIONS.repetition_penalty}</div>
        </div>

        {/* Integer parameters (sliders) */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-gray-600">top_k</label>
            <span className="text-xs font-medium">{params.top_k}</span>
          </div>
          <input
            type="range"
            min={1}
            max={200}
            step={1}
            value={params.top_k}
            onChange={(e) => handleChange('top_k', Number(e.target.value))}
            className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="text-xs text-gray-400 mt-1">{PARAM_DESCRIPTIONS.top_k}</div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-gray-600">num_return_sequences</label>
            <span className="text-xs font-medium">{params.num_return_sequences}</span>
          </div>
          <input
            type="range"
            min={1}
            max={5}
            step={1}
            value={params.num_return_sequences}
            onChange={(e) => handleChange('num_return_sequences', Number(e.target.value))}
            className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="text-xs text-gray-400 mt-1">{PARAM_DESCRIPTIONS.num_return_sequences}</div>
        </div>

        {/* Boolean parameter (checkbox) */}
        <div>
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={params.do_sample}
              onChange={(e) => handleChange('do_sample', e.target.checked)}
              className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-gray-700">do_sample</span>
          </label>
          <div className="text-xs text-gray-400 mt-1">{PARAM_DESCRIPTIONS.do_sample}</div>
        </div>

        {/* Reset button */}
        <button
          onClick={handleReset}
          className="w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors"
        >
          Reset to Defaults
        </button>
      </div>
    </div>
  );
}

export default GenerationParamsComponent;
