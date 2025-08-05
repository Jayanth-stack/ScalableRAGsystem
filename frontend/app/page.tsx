'use client';

import { useState, useEffect } from 'react';
import { FileCode2, Search, FileText, BarChart3, Activity, Database } from 'lucide-react';
import Link from 'next/link';
import { searchApi } from '@/lib/api';

const features = [
  {
    icon: FileCode2,
    title: 'Code Analysis',
    description: 'Analyze code complexity, patterns, and dependencies',
    href: '/analysis',
    color: 'bg-blue-500',
  },
  {
    icon: Search,
    title: 'Semantic Search',
    description: 'Find code using natural language queries',
    href: '/search',
    color: 'bg-green-500',
  },
  {
    icon: FileText,
    title: 'Documentation',
    description: 'Generate AI-powered documentation',
    href: '/documentation',
    color: 'bg-purple-500',
  },
  {
    icon: BarChart3,
    title: 'Metrics',
    description: 'View code quality metrics and insights',
    href: '/metrics',
    color: 'bg-orange-500',
  },
];

export default function HomePage() {
  const [stats, setStats] = useState<any>(null);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setApiStatus('online');
        const statsData = await searchApi.getStats();
        setStats(statsData);
      } else {
        setApiStatus('offline');
      }
    } catch (error) {
      setApiStatus('offline');
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-white rounded-lg shadow-sm p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Code Documentation Assistant
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          AI-powered code analysis, documentation generation, and semantic search for your codebase
        </p>
        
        {/* API Status */}
        <div className="flex items-center space-x-2 mb-6">
          <Activity className={`h-5 w-5 ${apiStatus === 'online' ? 'text-green-500' : apiStatus === 'offline' ? 'text-red-500' : 'text-yellow-500'}`} />
          <span className="text-sm font-medium">
            API Status: {apiStatus === 'checking' ? 'Checking...' : apiStatus === 'online' ? 'Online' : 'Offline'}
          </span>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <Database className="h-8 w-8 text-blue-500 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.total_chunks || 0}</p>
              <p className="text-sm text-gray-600">Indexed Chunks</p>
            </div>
            <div className="text-center">
              <FileCode2 className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <p className="text-2xl font-bold">{Object.keys(stats.languages || {}).length}</p>
              <p className="text-sm text-gray-600">Languages</p>
            </div>
            <div className="text-center">
              <Search className="h-8 w-8 text-purple-500 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.distance_metric || 'cosine'}</p>
              <p className="text-sm text-gray-600">Distance Metric</p>
            </div>
          </div>
        )}
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.href}
              href={feature.href}
              className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
            >
              <div className={`${feature.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                <Icon className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </Link>
          );
        })}
      </div>

      {/* Quick Start */}
      <div className="bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-2xl font-bold mb-4">Quick Start</h2>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">1</span>
            <div>
              <h3 className="font-semibold">Start the API Server</h3>
              <code className="text-sm bg-gray-100 px-2 py-1 rounded">python api_server.py</code>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">2</span>
            <div>
              <h3 className="font-semibold">Index Your Code</h3>
              <p className="text-gray-600">Use the Analysis page to analyze and index your codebase</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">3</span>
            <div>
              <h3 className="font-semibold">Search & Generate</h3>
              <p className="text-gray-600">Search your code semantically and generate documentation</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}