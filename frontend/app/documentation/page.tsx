'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { documentationApi } from '@/lib/api';
import { FileText, Wand2, Loader2, Copy, Check } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const docStyles = [
  { id: 'google', label: 'Google Style', description: 'Google Python style guide format' },
  { id: 'numpy', label: 'NumPy Style', description: 'NumPy documentation format' },
  { id: 'sphinx', label: 'Sphinx Style', description: 'reStructuredText format' },
];

const docTypes = [
  { id: 'function', label: 'Function' },
  { id: 'class', label: 'Class' },
  { id: 'module', label: 'Module' },
];

export default function DocumentationPage() {
  const [code, setCode] = useState(`def calculate_total(items, tax_rate=0.1):
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax`);
  const [docType, setDocType] = useState('function');
  const [docStyle, setDocStyle] = useState('google');
  const [generatedDoc, setGeneratedDoc] = useState('');
  const [copied, setCopied] = useState(false);

  const generateMutation = useMutation({
    mutationFn: async () => {
      return await documentationApi.generate(code, docType, docStyle);
    },
    onSuccess: (data) => {
      setGeneratedDoc(data.documentation);
    },
  });

  const handleGenerate = () => {
    generateMutation.mutate();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedDoc);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold mb-6">Documentation Generator</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code Input
              </label>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-64 px-3 py-2 font-mono text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Paste your code here..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Documentation Type
                </label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  {docTypes.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Style
                </label>
                <select
                  value={docStyle}
                  onChange={(e) => setDocStyle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  {docStyles.map(style => (
                    <option key={style.id} value={style.id}>
                      {style.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={generateMutation.isPending || !code.trim()}
              className="w-full flex items-center justify-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generateMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Wand2 className="h-4 w-4" />
                  <span>Generate Documentation</span>
                </>
              )}
            </button>
          </div>

          {/* Output Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-gray-700">
                Generated Documentation
              </label>
              {generatedDoc && (
                <button
                  onClick={handleCopy}
                  className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  {copied ? (
                    <>
                      <Check className="h-3 w-3 text-green-600" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              )}
            </div>

            <div className="h-64 border border-gray-300 rounded-md overflow-auto bg-gray-50">
              {generatedDoc ? (
                <pre className="p-4 text-sm whitespace-pre-wrap">
                  {generatedDoc}
                </pre>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400">
                  Generated documentation will appear here
                </div>
              )}
            </div>

            {generateMutation.data?.suggestions && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                <h3 className="text-sm font-semibold text-yellow-800 mb-2">Suggestions</h3>
                <ul className="text-sm text-yellow-700 space-y-1">
                  {generateMutation.data.suggestions.map((suggestion: string, index: number) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Examples Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Style Examples</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {docStyles.map(style => (
            <div key={style.id} className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">{style.label}</h3>
              <p className="text-sm text-gray-600 mb-3">{style.description}</p>
              <div className="bg-gray-900 rounded p-3 overflow-x-auto">
                <pre className="text-xs text-gray-300">
                  {style.id === 'google' ? `"""Brief description.

Args:
    param1: Description
    param2: Description

Returns:
    Description
"""` : style.id === 'numpy' ? `"""
Brief description.

Parameters
----------
param1 : type
    Description
param2 : type
    Description

Returns
-------
type
    Description
"""` : `"""
Brief description.

:param param1: Description
:type param1: type
:param param2: Description
:type param2: type
:return: Description
:rtype: type
"""`}
                </pre>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}