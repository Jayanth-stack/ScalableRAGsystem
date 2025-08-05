'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { searchApi } from '@/lib/api';
import { Search, Loader2, FileCode2, Hash } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [results, setResults] = useState<any>(null);

  const searchMutation = useMutation({
    mutationFn: async () => {
      return await searchApi.search(query, maxResults);
    },
    onSuccess: (data) => {
      setResults(data);
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchMutation.mutate();
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold mb-6">Semantic Code Search</h1>
        
        {/* Search Form */}
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., calculate total price, handle user authentication"
              />
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Max Results:</label>
              <input
                type="number"
                min="1"
                max="50"
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                className="w-20 px-2 py-1 border border-gray-300 rounded-md"
              />
            </div>

            <button
              type="submit"
              disabled={searchMutation.isPending || !query.trim()}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {searchMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  <span>Search</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Search Results */}
      {results && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">
              Results ({results.total_results})
            </h2>
            <span className="text-sm text-gray-600">
              Query time: {results.query_time_ms?.toFixed(2)}ms
            </span>
          </div>

          {results.results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No results found. Try a different query or index more code.
            </div>
          ) : (
            <div className="space-y-4">
              {results.results.map((result: any, index: number) => (
                <div key={index} className="border rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-2 border-b">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <FileCode2 className="h-4 w-4 text-gray-600" />
                        <span className="font-mono text-sm">
                          {result.chunk?.file_path}
                        </span>
                        <span className="text-xs text-gray-500">
                          Lines {result.chunk?.start_line}-{result.chunk?.end_line}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Hash className="h-3 w-3 text-gray-400" />
                        <span className="text-sm font-medium">
                          {(result.similarity_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-0">
                    <SyntaxHighlighter
                      language={result.chunk?.language || 'python'}
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        fontSize: '0.875rem',
                        maxHeight: '300px',
                      }}
                      showLineNumbers
                      startingLineNumber={result.chunk?.start_line || 1}
                    >
                      {result.chunk?.content || ''}
                    </SyntaxHighlighter>
                  </div>

                  {result.chunk?.element_name && (
                    <div className="px-4 py-2 bg-gray-50 border-t">
                      <span className="text-xs text-gray-600">
                        Element: <span className="font-semibold">{result.chunk.element_name}</span>
                        {result.chunk.element_type && (
                          <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                            {result.chunk.element_type}
                          </span>
                        )}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}