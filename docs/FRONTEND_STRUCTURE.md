# Frontend Structure

Overview of the frontend folder organization and component architecture.

## 📁 Directory Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router (Pages)
│   │   ├── layout.tsx         # Root layout component
│   │   ├── page.tsx           # Homepage
│   │   ├── chat/              # Chat interface
│   │   │   └── page.tsx
│   │   └── funds/             # Fund explorer
│   │       ├── page.tsx       # Fund list
│   │       └── [fundId]/      # Dynamic route
│   │           └── page.tsx   # Fund details
│   │
│   ├── components/            # React Components
│   │   ├── Header.tsx        # Main navigation
│   │   ├── chat/             # Chat-related components
│   │   └── layout/           # Layout components
│   │
│   ├── lib/                   # Utility Libraries
│   │   ├── api.ts            # API client functions
│   │   └── utils.ts          # Utility functions
│   │
│   ├── types/                 # TypeScript Types
│   │   └── index.ts
│   │
│   └── hooks/                 # Custom React Hooks
│       └── index.ts
│
├── public/                    # Static assets
├── package.json              # Dependencies
└── Configuration files       # Next.js, TypeScript, Tailwind
```

---

## 📦 Core Components

### `src/app/` - Next.js App Router

Next.js 16+ App Router structure with file-based routing.

#### `layout.tsx`
- Root layout component
- Wraps all pages
- Providers (React Query, Theme, etc.)
- Global navigation

#### `page.tsx` (Homepage)
- Landing page
- Welcome message
- Navigation to chat/funds
- Hero section

#### `chat/page.tsx`
- Main chat interface
- Chat message list
- Input component
- Search mode selector
- Fund analysis results display

**Purpose:** Primary user interface for RAG queries

#### `funds/page.tsx`
- Fund explorer list view
- Filters (category, risk level)
- Grid/card layout
- Fund metrics preview

#### `funds/[fundId]/page.tsx`
- Individual fund detail page
- Full fund metrics
- Performance charts
- Fund information display

**Purpose:** Detailed fund information view

---

### `src/components/` - React Components

#### `Header.tsx`
- Main navigation bar
- Links to pages
- Theme toggle (if implemented)
- User menu (if implemented)

#### `components/chat/`
Chat-specific components:

- **`ChatInput.tsx`**:
  - Text input for queries
  - Search mode selector dropdown
  - Submit button
  - Input validation

- **`ChatMessage.tsx`**:
  - Individual chat message display
  - User vs assistant styling
  - Markdown rendering
  - Loading states

- **`CitationChip.tsx`**:
  - Source citation badge
  - Clickable source links
  - Source type indicator (FAQ/Fund)

- **`FundAnalysisResults.tsx`**:
  - Grid display of fund metrics
  - Fund cards from query results
  - Metrics visualization

- **`FundInsightCard.tsx`**:
  - Individual fund card component
  - Key metrics display
  - Visual indicators (risk level, performance)

- **`FundMetricsUtils.ts`**:
  - Utility functions for fund metrics
  - Formatting helpers
  - Calculation helpers

- **`WelcomeMessage.tsx`**:
  - Welcome screen when chat is empty
  - Example queries
  - Instructions

**Purpose:** Modular, reusable chat interface components

#### `components/layout/`
Layout-related components:

- **`ConditionalLayout.tsx`**:
  - Conditional layout wrapper
  - Different layouts for different pages

- **`Header.tsx`**:
  - Alternative header component (if different from main)

- **`Sidebar.tsx`**:
  - Sidebar navigation (if used)

**Purpose:** Layout and navigation components

---

### `src/lib/` - Utility Libraries

#### `lib/api.ts`
API client functions:

- **`checkHealth()`**: Health check API call
- **`sendQuery()`**: RAG query API call
- **`getFunds()`**: List funds API call
- **`getFundById()`**: Get fund details API call
- **`getSearchModes()`**: Get available search modes

**Purpose:** Centralized API communication layer

**Features:**
- Error handling
- Request/response typing
- Base URL configuration
- JSON serialization

#### `lib/utils.ts`
Utility functions:

- Date formatting
- Number formatting
- String helpers
- Common transformations

**Purpose:** Shared utility functions

---

### `src/types/` - TypeScript Types

#### `types/index.ts`
Type definitions matching backend schemas:

- `QueryRequest`, `QueryResponse`
- `FundInfo`, `FundDetail`
- `HealthResponse`
- `SearchMode`
- Component prop types

**Purpose:** Type safety across frontend

---

### `src/hooks/` - Custom React Hooks

#### `hooks/index.ts`
Custom hooks:

- **`useChat()`**: Chat state management
  - Message history
  - Loading states
  - Error handling
  - Query submission

- **`useFunds()`**: Fund data fetching
  - Fund list fetching
  - Filtering
  - Pagination (if implemented)

- **`useQuery()`**: React Query wrapper for RAG queries

**Purpose:** Reusable state management and data fetching logic

---

## 🎨 Styling

### Tailwind CSS
- Utility-first CSS framework
- Custom theme configuration
- Responsive design utilities

### Global Styles
- `app/globals.css`: Global CSS variables, base styles

### Component Styling
- Inline Tailwind classes
- Component-level styles where needed

---

## 🔄 Data Flow

### Query Flow

1. **User Input** (`ChatInput.tsx`):
   - User types query
   - Selects search mode
   - Submits form

2. **State Management** (`useChat` hook):
   - Updates message history
   - Sets loading state
   - Calls API

3. **API Call** (`lib/api.ts`):
   - Sends POST to `/api/v1/query`
   - Handles errors
   - Returns response

4. **Response Handling** (`ChatMessage.tsx`):
   - Displays answer
   - Shows fund results
   - Renders sources

5. **UI Update**:
   - Adds message to chat
   - Shows fund cards
   - Displays citations

---

### Fund Explorer Flow

1. **Page Load** (`funds/page.tsx`):
   - Fetches fund list
   - Applies filters (if any)

2. **API Call** (`lib/api.ts`):
   - GET `/api/v1/funds`
   - Query parameters for filtering

3. **Display** (`funds/page.tsx`):
   - Renders fund grid
   - Shows metrics
   - Links to detail pages

4. **Navigation**:
   - Click fund → navigate to detail
   - Detail page fetches full fund data

---

## 🛠️ Technology Stack

### Core
- **Next.js 16**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Type safety

### UI Components
- **Radix UI**: Accessible component primitives
- **Lucide React**: Icon library
- **Tailwind CSS**: Styling

### State & Data
- **React Query (TanStack Query)**: Server state management
- **React Hook Form**: Form handling

### Visualization
- **Recharts**: Charts and graphs
- **Tremor**: Dashboard components

### Utilities
- **Zod**: Schema validation
- **date-fns**: Date formatting
- **clsx**: Conditional class names

---

## 📝 Key Files Reference

| File | Purpose | Key Features |
|------|---------|--------------|
| `app/layout.tsx` | Root layout | Providers, global nav |
| `app/chat/page.tsx` | Chat interface | Main RAG UI |
| `components/chat/ChatInput.tsx` | Query input | Form, mode selector |
| `components/chat/ChatMessage.tsx` | Message display | Markdown, styling |
| `components/chat/FundAnalysisResults.tsx` | Fund results | Metrics grid |
| `lib/api.ts` | API client | All API calls |
| `hooks/index.ts` | Custom hooks | State management |
| `types/index.ts` | Type definitions | TypeScript types |

---

## 🎯 Design Principles

### Component-Based Architecture
- Small, reusable components
- Single responsibility principle
- Props-based composition

### Type Safety
- Full TypeScript coverage
- Types match backend schemas
- Compile-time error checking

### User Experience
- Loading states
- Error handling
- Responsive design
- Accessible components (Radix UI)

### Performance
- React Query for caching
- Code splitting (Next.js automatic)
- Optimized re-renders

---

For data flow diagrams, see [Data Flow](data-flow.md).

