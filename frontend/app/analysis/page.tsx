'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { analysisApi } from '@/lib/api';
import { FileCode2, Play, Loader2, CheckCircle, XCircle } from 'lucide-react';

const analysisTypes = [
  { id: 'complexity', label: 'Complexity Analysis', description: 'Cyclomatic complexity and maintainability' },
  { id: 'dependency', label: 'Dependency Tracking', description: 'Import graphs and circular dependencies' },
  { id: 'pattern', label: 'Pattern Detection', description: 'Design patterns and best practices' },
  { id: 'security', label: 'Security Scan', description: 'Vulnerability detection' },
  { id: 'performance', label: 'Performance', description: 'Optimization suggestions' },
];

export default function AnalysisPage() {
  const [targetPath, setTargetPath] = useState('sample_repos/sample_python_project/main.py');
  const [selectedTypes, setSelectedTypes] = useState(['complexity', 'pattern']);
  const [asyncMode, setAsyncMode] = useState(false);
  const [result, setResult] = useState<any>(null);

  const analysisMutation = useMutation({
    mutationFn: async () => {
      return await analysisApi.analyze(targetPath, selectedTypes, asyncMode);
    },
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleAnalyze = () => {
    setResult(null);
    analysisMutation.mutate();
  };

  const toggleAnalysisType = (typeId: string) => {
    setSelectedTypes(prev =>
      prev.includes(typeId)
        ? prev.filter(id => id !== typeId)
        : [...prev, typeId]
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold mb-6">Code Analysis</h1>
        
        {/* Input Section */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target File or Directory
            </label>
            <input
              type="text"
              value={targetPath}
              onChange={(e) => setTargetPath(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter file path or directory"
            />
          </div>

          {/* Analysis Types */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Types
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {analysisTypes.map((type) => (
                <div
                  key={type.id}
                  onClick={() => toggleAnalysisType(type.id)}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedTypes.includes(type.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{type.label}</span>
                    {selectedTypes.includes(type.id) && (
                      <CheckCircle className="h-4 w-4 text-blue-500" />
                    )}
                  </div>
                  <p className="text-xs text-gray-600">{type.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Options */}
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={asyncMode}
                onChange={(e) => setAsyncMode(e.target.checked)}
                className="rounded text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">Async Mode</span>
            </label>
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={analysisMutation.isPending || selectedTypes.length === 0}
            className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analysisMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
          
          {/* Task Info */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Task ID:</span>
                <p className="font-mono text-xs">{result.task_id}</p>
              </div>
              <div>
                <span className="text-gray-600">Status:</span>
                <p className="font-semibold">{result.status}</p>
              </div>
              <div>
                <span className="text-gray-600">Elements:</span>
                <p className="font-semibold">{result.result?.elements_count || 0}</p>
              </div>
              <div>
                <span className="text-gray-600">File:</span>
                <p className="font-semibold truncate">{result.result?.file_info?.name}</p>
              </div>
            </div>
          </div>

          {/* Analysis Results */}
          {result.result?.analysis && (
            <div className="space-y-4">
              {Object.entries(result.result.analysis).map(([type, data]: [string, any]) => (
                <div key={type} className="border rounded-lg p-4">
                  <h3 className="font-semibold mb-2 capitalize">{type} Analysis</h3>
                  {data.error ? (
                    <div className="flex items-center space-x-2 text-red-600">
                      <XCircle className="h-4 w-4" />
                      <span className="text-sm">{data.error}</span>
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded p-3">
                      <pre className="text-xs overflow-x-auto">
                        {JSON.stringify(data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {analysisMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 text-red-600">
            <XCircle className="h-5 w-5" />
            <span>Analysis failed. Please check your input and try again.</span>
          </div>
        </div>
      )}
    </div>
  );
}