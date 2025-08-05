# Code Documentation Assistant - Frontend

A modern, responsive web interface for the Code Documentation Assistant API, built with Next.js 14+, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Dashboard**: Overview of system status and quick access to all features
- **Code Analysis**: Analyze code complexity, dependencies, patterns, and security
- **Semantic Search**: Natural language code search with syntax highlighting
- **Documentation Generator**: AI-powered documentation generation with multiple styles
- **Metrics Visualization**: Interactive charts for code quality metrics
- **Real-time Updates**: Live status updates for async operations

## 🛠️ Tech Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Charts**: Recharts
- **Icons**: Lucide React
- **Code Highlighting**: React Syntax Highlighter

## 📦 Installation

```bash
# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🏗️ Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home/Dashboard
│   ├── providers.tsx      # React Query provider
│   ├── analysis/          # Analysis page
│   ├── search/            # Search page
│   ├── documentation/     # Documentation generator
│   └── metrics/           # Metrics visualization
├── components/            # Reusable components
│   └── layout/           
│       └── Header.tsx    # Navigation header
├── lib/                   # Utilities
│   └── api.ts            # API client
└── public/               # Static assets
```

## 🎨 Pages

### Dashboard (`/`)
- System status indicator
- API connection status
- Quick stats (indexed chunks, languages, etc.)
- Feature cards with navigation

### Analysis (`/analysis`)
- File/directory path input
- Multiple analysis type selection
- Async/sync mode toggle
- Results display with error handling

### Search (`/search`)
- Natural language query input
- Configurable max results
- Syntax-highlighted code results
- Similarity scores

### Documentation (`/documentation`)
- Code input area
- Documentation style selection (Google, NumPy, Sphinx)
- Live preview
- Copy to clipboard

### Metrics (`/metrics`)
- Project path input
- Overview cards (files, lines, complexity, maintainability)
- Documentation coverage visualization
- Detailed metrics display

## 🔧 Configuration

### Environment Variables

```bash
# API endpoint (required)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Integration

The frontend connects to the backend API through the `lib/api.ts` client:

```typescript
import { api } from '@/lib/api';

// Example usage
const result = await api.post('/api/v1/analysis/', {
  target: 'path/to/file.py',
  analysis_types: ['complexity', 'pattern']
});
```

## 🚀 Development

```bash
# Start backend API server first
cd .. && python api_server.py

# In another terminal, start frontend
cd frontend && npm run dev

# Access at http://localhost:3000
```

## 📝 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

## 🎯 Features in Detail

### Real-time Status Updates
- API connection monitoring
- Task progress tracking
- Error handling with user-friendly messages

### Responsive Design
- Mobile-first approach
- Adaptive layouts for all screen sizes
- Touch-friendly interactions

### Performance Optimizations
- Code splitting
- Lazy loading
- React Query caching
- Optimistic updates

## 🔮 Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Dark mode toggle
- [ ] Export functionality (PDF, Markdown)
- [ ] Batch operations
- [ ] User preferences persistence
- [ ] Keyboard shortcuts
- [ ] Advanced filtering options

## 📄 License

MIT