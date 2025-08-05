'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { metricsApi } from '@/lib/api';
import { BarChart3, Loader2, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function MetricsPage() {
  const [targetPath, setTargetPath] = useState('sample_repos/sample_python_project');
  const [metrics, setMetrics] = useState<any>(null);

  const metricsMutation = useMutation({
    mutationFn: async () => {
      return await metricsApi.calculate(targetPath, ['complexity', 'quality']);
    },
    onSuccess: (data) => {
      setMetrics(data);
    },
  });

  const handleCalculate = () => {
    metricsMutation.mutate();
  };

  const getComplexityLevel = (score: number) => {
    if (score < 5) return { label: 'Low', color: 'text-green-600', icon: CheckCircle };
    if (score < 10) return { label: 'Medium', color: 'text-yellow-600', icon: AlertTriangle };
    return { label: 'High', color: 'text-red-600', icon: AlertTriangle };
  };

  const getMaintainabilityLevel = (score: number) => {
    if (score > 80) return { label: 'Excellent', color: 'text-green-600' };
    if (score > 60) return { label: 'Good', color: 'text-blue-600' };
    if (score > 40) return { label: 'Fair', color: 'text-yellow-600' };
    return { label: 'Poor', color: 'text-red-600' };
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold mb-6">Code Metrics</h1>
        
        {/* Input Section */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Path
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                value={targetPath}
                onChange={(e) => setTargetPath(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter project path"
              />
              <button
                onClick={handleCalculate}
                disabled={metricsMutation.isPending || !targetPath.trim()}
                className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {metricsMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Calculating...</span>
                  </>
                ) : (
                  <>
                    <BarChart3 className="h-4 w-4" />
                    <span>Calculate Metrics</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Display */}
      {metrics && (
        <>
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Files Analyzed</span>
                <BarChart3 className="h-4 w-4 text-blue-500" />
              </div>
              <p className="text-2xl font-bold">{metrics.file_count}</p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Total Lines</span>
                <TrendingUp className="h-4 w-4 text-green-500" />
              </div>
              <p className="text-2xl font-bold">{metrics.total_lines}</p>
            </div>

            {metrics.metrics?.complexity && (
              <div className="bg-white rounded-lg shadow-sm p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Avg Complexity</span>
                  {(() => {
                    const level = getComplexityLevel(metrics.metrics.complexity.total_cyclomatic);
                    const Icon = level.icon;
                    return <Icon className={`h-4 w-4 ${level.color}`} />;
                  })()}
                </div>
                <p className="text-2xl font-bold">
                  {metrics.metrics.complexity.total_cyclomatic?.toFixed(1) || 0}
                </p>
                <p className={`text-xs ${getComplexityLevel(metrics.metrics.complexity.total_cyclomatic).color}`}>
                  {getComplexityLevel(metrics.metrics.complexity.total_cyclomatic).label}
                </p>
              </div>
            )}

            {metrics.metrics?.complexity && (
              <div className="bg-white rounded-lg shadow-sm p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Maintainability</span>
                  <CheckCircle className="h-4 w-4 text-purple-500" />
                </div>
                <p className="text-2xl font-bold">
                  {metrics.metrics.complexity.average_maintainability?.toFixed(1) || 0}
                </p>
                <p className={`text-xs ${getMaintainabilityLevel(metrics.metrics.complexity.average_maintainability).color}`}>
                  {getMaintainabilityLevel(metrics.metrics.complexity.average_maintainability).label}
                </p>
              </div>
            )}
          </div>

          {/* Quality Metrics */}
          {metrics.metrics?.quality && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-4">Code Quality</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Documentation Coverage */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Documentation Coverage</h3>
                  <div className="relative pt-1">
                    <div className="flex mb-2 items-center justify-between">
                      <div>
                        <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                          Coverage
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-semibold inline-block text-blue-600">
                          {(metrics.metrics.quality.average_documentation_coverage * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
                      <div
                        style={{ width: `${metrics.metrics.quality.average_documentation_coverage * 100}%` }}
                        className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Code Elements */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Code Elements</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total Elements</span>
                      <span className="font-semibold">{metrics.metrics.quality.total_code_elements}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Detailed Metrics */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Detailed Analysis</h2>
            <div className="bg-gray-50 rounded p-4">
              <pre className="text-xs overflow-x-auto">
                {JSON.stringify(metrics.metrics, null, 2)}
              </pre>
            </div>
          </div>
        </>
      )}

      {/* Error Display */}
      {metricsMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            <span>Failed to calculate metrics. Please check your input and try again.</span>
          </div>
        </div>
      )}
    </div>
  );
}