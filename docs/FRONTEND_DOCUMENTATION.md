# Frontend Folder Structure & Implementation Documentation

## 📁 Complete Frontend Architecture

This document provides an in-depth analysis of every file in the frontend folder, explaining what each component does, why it exists, and its impact on the overall system.

---

## 📂 Folder Structure

```
frontend/
├── src/                          # Source code directory
│   ├── app/                      # Next.js App Router (Pages)
│   │   ├── layout.tsx           # Root layout component
│   │   ├── page.tsx             # Homepage (Landing page)
│   │   ├── globals.css          # Global styles
│   │   ├── chat/
│   │   │   └── page.tsx         # Chat interface page
│   │   └── funds/
│   │       ├── page.tsx         # Fund Explorer (list)
│   │       └── [fundId]/
│   │           └── page.tsx     # Fund detail page
│   │
│   ├── components/              # React Components
│   │   ├── Header.tsx           # Main navigation header
│   │   └── chat/                # Chat-related components
│   │       ├── ChatInput.tsx    # Chat input with search mode
│   │       ├── ChatMessage.tsx  # Individual chat message
│   │       ├── CitationChip.tsx # Source citation badge
│   │       ├── FundAnalysisResults.tsx # Fund metrics grid
│   │       ├── FundInsightCard.tsx     # Individual fund card
│   │       ├── FundMetricsUtils.ts     # Metric utility functions
│   │       ├── WelcomeMessage.tsx # Welcome screen
│   │       └── index.ts         # Component exports
│   │
│   ├── lib/                     # Utility Libraries
│   │   ├── api.ts               # API client functions
│   │   └── utils.ts             # Utility functions
│   │
│   ├── types/                   # TypeScript Type Definitions
│   │   └── index.ts             # All type definitions
│   │
│   └── hooks/                   # Custom React Hooks
│       └── index.ts             # Custom hooks (useChat, useFunds, etc.)
│
├── public/                      # Static assets (if any)
├── node_modules/                # Dependencies
├── package.json                 # Dependencies & scripts
├── package-lock.json            # Dependency lock file
├── tsconfig.json                # TypeScript configuration
├── tailwind.config.ts           # Tailwind CSS configuration
├── next.config.js               # Next.js configuration
├── postcss.config.js            # PostCSS configuration
└── next-env.d.ts                # Next.js TypeScript declarations
```

---

## 📄 File-by-File Documentation

### 🔷 **Configuration Files**

#### `frontend/package.json`
- **Path:** `frontend/package.json`
- **Purpose:** Project dependencies, scripts, and metadata
- **What it contains:**
  - Project name, version, description
  - Dependencies (React, Next.js, UI libraries)
  - DevDependencies (TypeScript, ESLint, Prettier)
  - Scripts (dev, build, start, lint)
  - Engine requirements (Node >= 20.0.0)
- **Key Dependencies:**
  - **Framework:** `next@^16.0.5`, `react@18.3.1`
  - **UI Libraries:** `lucide-react` (icons), `@radix-ui/*` (UI primitives), `@tremor/react` (charts)
  - **State Management:** `@tanstack/react-query@5.62.8` (server state)
  - **Styling:** `tailwindcss@3.4.17`, `tailwind-merge`, `clsx`
  - **Forms:** `react-hook-form@7.54.2`, `zod@3.24.1`
  - **Charts:** `recharts@2.15.0`
  - **API:** `axios@^1.13.2`
- **Scripts:**
  - `npm run dev` - Start development server
  - `npm run build` - Production build
  - `npm run start` - Start production server
  - `npm run lint` - Lint code
  - `npm run type-check` - TypeScript type checking
- **Why it exists:**
  - Dependency management
  - Script automation
  - Project metadata
- **Impact:**
  - **Critical** - Defines all dependencies
  - Centralized script management
  - Ensures consistent environment
- **Lines:** ~78

---

#### `frontend/tsconfig.json`
- **Path:** `frontend/tsconfig.json`
- **Purpose:** TypeScript compiler configuration
- **What it contains:**
  - Compiler options (strict mode, JSX, module resolution)
  - Path aliases (`@/*` → `./src/*`)
  - Include/exclude patterns
- **Key Settings:**
  - `strict: true` - Strict type checking
  - `moduleResolution: "bundler"` - Modern module resolution
  - `jsx: "react-jsx"` - New JSX transform
  - Path alias: `@/*` maps to `./src/*`
- **Why it exists:**
  - Type safety across the codebase
  - Consistent TypeScript settings
  - Path alias configuration (clean imports)
- **Impact:**
  - **High** - Type safety prevents bugs
  - Clean import paths (`@/components` vs `../../components`)
  - Strict mode catches errors early
- **Lines:** ~42

---

#### `frontend/next.config.js`
- **Path:** `frontend/next.config.js`
- **Purpose:** Next.js framework configuration
- **What it contains:**
  - React strict mode
  - Image domain configuration
  - API rewrites (proxy to backend)
- **Key Features:**
  - **API Rewrites:** Proxies `/api/*` requests to backend
  - Environment-based API URL (`NEXT_PUBLIC_API_URL`)
  - React strict mode enabled
- **Why it exists:**
  - Configures Next.js behavior
  - API proxying avoids CORS issues
  - Environment-specific settings
- **Impact:**
  - **High** - API proxying is critical
  - Enables seamless backend communication
  - Handles environment differences
- **Important:** The API rewrite allows frontend to call `/api/v1/query` which gets proxied to `http://localhost:8000/api/v1/query`
- **Lines:** ~20

---

#### `frontend/tailwind.config.ts`
- **Path:** `frontend/tailwind.config.ts`
- **Purpose:** Tailwind CSS configuration
- **What it contains:**
  - Content paths (where Tailwind scans for classes)
  - Theme extensions (colors, borders)
  - Plugins (@tailwindcss/typography, @tailwindcss/forms)
- **Key Settings:**
  - Content paths: `./src/**/*.{js,ts,jsx,tsx,mdx}`
  - Custom colors from CSS variables
  - Border radius variables
  - Typography and forms plugins
- **Why it exists:**
  - Configures Tailwind CSS utility classes
  - Custom theme values
  - Plugin configuration
- **Impact:**
  - **High** - All styling depends on this
  - Defines design system colors
  - Enables typography and form styling
- **Lines:** ~58

---

#### `frontend/postcss.config.js`
- **Path:** `frontend/postcss.config.js`
- **Purpose:** PostCSS configuration (processes CSS)
- **What it contains:**
  - Tailwind CSS plugin
  - Autoprefixer plugin
- **Why it exists:**
  - Required by Next.js for CSS processing
  - Processes Tailwind directives
  - Adds vendor prefixes
- **Impact:**
  - **Medium** - Required for Tailwind to work
  - Automatic vendor prefixing

---

### 🔷 **App Router (`src/app/`)**

#### `frontend/src/app/layout.tsx`
- **Path:** `frontend/src/app/layout.tsx`
- **Purpose:** Root layout component (wraps all pages)
- **What it contains:**
  - HTML structure
  - Font loading (Inter from Google Fonts)
  - Global CSS import
  - Header component
  - Metadata (SEO)
- **Key Features:**
  - **Font:** Inter font from Google Fonts
  - **Metadata:** Page title and description for SEO
  - **Layout:** Header component on all pages
  - **Styling:** Dark theme base (`bg-slate-950`)
- **Why it exists:**
  - Shared layout for all pages
  - Global styles and fonts
  - SEO metadata
  - Consistent header across app
- **Impact:**
  - **Critical** - All pages use this layout
  - Defines global appearance
  - SEO metadata
- **Lines:** ~27

---

#### `frontend/src/app/globals.css`
- **Path:** `frontend/src/app/globals.css`
- **Purpose:** Global CSS styles and Tailwind directives
- **What it contains:**
  - Tailwind directives (`@tailwind base/components/utilities`)
  - CSS custom properties (CSS variables)
  - Custom scrollbar styles
  - Animation utilities
- **Key Features:**
  - **CSS Variables:** Color system (HSL values)
  - **Scrollbar:** Custom scrollbar styling (thin, dark)
  - **Base Styles:** Global body and element styles
- **Why it exists:**
  - Global styling
  - Design system variables
  - Custom utilities
- **Impact:**
  - **High** - Defines global appearance
  - Design system consistency
  - Custom scrollbar aesthetic
- **Lines:** ~93+

---

#### `frontend/src/app/page.tsx`
- **Path:** `frontend/src/app/page.tsx`
- **Purpose:** Homepage/Landing page
- **What it contains:**
  - Hero section with title
  - Search input box (glass morphism design)
  - Quick action suggestions
  - Background effects (gradient blobs)
- **Key Features:**
  - **Glass Morphism UI:** Backdrop blur, transparent backgrounds
  - **Interactive Input:** Large search box with "Get Started" button
  - **Quick Actions:** Pre-filled query suggestions
  - **Background Effects:** Gradient blobs for visual appeal
  - **Navigation:** Redirects to `/chat` with or without query
- **Component Structure:**
  - Hero title with gradient text
  - Description paragraph
  - Search form with textarea
  - Quick action buttons
  - Background gradient effects
- **Why it exists:**
  - First impression for users
  - Entry point to chat interface
  - Quick access to common queries
- **Impact:**
  - **High** - User's first interaction
  - Brand impression
  - Navigation hub
- **Key Implementation Details:**
  - Uses `useRouter` for navigation
  - Supports query parameter passing (`/chat?q=query`)
  - Keyboard support (Enter to submit)
  - Responsive design (mobile/desktop)
- **Lines:** ~102

---

#### `frontend/src/app/chat/page.tsx`
- **Path:** `frontend/src/app/chat/page.tsx`
- **Purpose:** Main chat interface - core of the application
- **What it contains:**
  - Chat message list
  - Welcome message (when no messages)
  - Chat input component
  - Scroll management
  - Query parameter handling (pre-filled queries)
  - Loading states
  - Error handling
- **Key Features:**
  - **Suspense Wrapper:** Handles Next.js navigation loading
  - **URL Query Parameters:** Supports `/chat?q=query` for pre-filled queries
  - **Double-Run Prevention:** Uses `useRef` to prevent double execution in React StrictMode
  - **Message Management:** Uses `useChat()` hook for state management
  - **Auto-scroll:** Automatically scrolls to bottom on new messages
  - **Background Effects:** Ambient gradient blobs
- **Component Structure:**
  ```typescript
  ChatContent (main component)
    ├── WelcomeMessage (if no messages)
    ├── ChatMessage (for each message)
    └── ChatInput (fixed at bottom)
  ```
- **State Management:**
  - Uses `useChat()` hook from `@/hooks`
  - `messages` - Array of chat messages (from hook)
  - `isLoading` - Loading state for API calls (from hook)
  - `sendMessage()` - Function to send queries (from hook)
  - `hasProcessedQuery` - Ref to prevent double execution
- **Key Functions:**
  - `sendMessage()` - Sends query to backend API (from useChat hook)
  - URL query handling with `useSearchParams`
- **Why it exists:**
  - Main user interface for RAG queries
  - Displays AI responses
  - Manages conversation state
- **Impact:**
  - **CRITICAL** - Core user interaction
  - All chat functionality flows through here
- **Key Implementation Details:**
  - ✅ Uses `useChat()` hook for state management and API calls
  - ✅ Prevents double-execution with `useRef`
  - ✅ Supports URL query parameters
  - ✅ Error handling with user-friendly messages
  - ✅ Loading states with spinner
  - ✅ Auto-scrolling chat container
  - ✅ Suspense boundary for Next.js navigation
- **Lines:** ~120

---

#### `frontend/src/app/funds/page.tsx`
- **Path:** `frontend/src/app/funds/page.tsx`
- **Purpose:** Fund Explorer - Browse and filter mutual funds
- **What it contains:**
  - Fund list display (cards)
  - Search functionality
  - Category filters (Large Cap, Hybrid, Flexi, Debt, Index, ELS, Small Cap)
  - Fund cards with metrics
  - "Ask AI" button for each fund
  - Loading and error states
- **Key Features:**
  - **Search:** Real-time filtering by fund name, category, fund house
  - **Filters:** Category-based filtering (7 predefined categories)
  - **Fund Cards:** Display key metrics (CAGR, Sharpe, Volatility)
  - **Ask AI Integration:** Links to chat with pre-filled query
  - **Responsive Grid:** 1 column mobile, 2-3 columns desktop
- **State Management:**
  - `funds` - Fund list from API
  - `searchQuery` - Search input value
  - `selectedFilter` - Active category filter
  - `isLoading` - Loading state
  - `error` - Error state
- **Key Functions:**
  - `fetchFunds()` - Loads funds from API
  - `filteredFunds` - Computed filtered list
  - `handleAskAI()` - Navigates to chat with fund query
- **Why it exists:**
  - Allows users to browse all funds
  - Quick access to fund information
  - Integration with chat (Ask AI)
- **Impact:**
  - **High** - Key feature for fund exploration
  - Enables discovery of funds
  - Bridges to chat interface
- **Filter Categories:**
  - Large Cap, Hybrid, Flexi, Debt, Index, ELS, Small Cap
- **Key Implementation Details:**
  - ✅ Client-side filtering (fast, no API calls)
  - ✅ Case-insensitive search
  - ✅ Partial category matching
  - ✅ Empty state handling
  - ✅ Error state with retry
- **Lines:** ~264

---

#### `frontend/src/app/funds/[fundId]/page.tsx`
- **Path:** `frontend/src/app/funds/[fundId]/page.tsx`
- **Purpose:** Fund detail page - comprehensive fund information
- **What it contains:**
  - Detailed fund information
  - All performance metrics
  - Risk metrics
  - Fund details (AUM, NAV, Expense Ratio)
  - "Ask AI" button
  - Back navigation
- **Key Features:**
  - **Dynamic Routing:** Uses Next.js dynamic route `[fundId]`
  - **Comprehensive Metrics:** All available fund data
  - **Organized Metrics Display:** Structured fund data presentation
  - **Risk Badges:** Color-coded risk levels
  - **AI Integration:** Direct link to chat about fund
- **State Management:**
  - Uses `useFundDetail()` hook
  - Loads fund data on mount
- **Why it exists:**
  - Detailed view of individual funds
  - Complete metric display
  - Deep dive into fund performance
- **Impact:**
  - **Medium-High** - Provides detailed fund analysis
  - Complements fund list
  - Rich information display
- **Key Implementation Details:**
  - ✅ Dynamic route parameter handling
  - ✅ Loading state with spinner
  - ✅ Error handling with back button
  - ✅ Comprehensive metric display
  - ✅ Formatting utilities (percentage, currency)
- **Lines:** ~220

---

### 🔷 **Components (`src/components/`)**

#### `frontend/src/components/Header.tsx`
- **Path:** `frontend/src/components/Header.tsx`
- **Purpose:** Main navigation header component
- **What it contains:**
  - Logo (Qonfido branding)
  - Navigation links (AI Co-Pilot, Fund Explorer)
  - Active route highlighting
  - Conditional display (shows nav only on homepage)
- **Key Features:**
  - **Conditional Display:** Navigation only shows on homepage
  - **Active State:** Highlights current route
  - **Logo:** Gradient-styled logo with icon
  - **Responsive:** Hidden on mobile when not homepage
- **Navigation Items:**
  - AI Co-Pilot → `/chat`
  - Fund Explorer → `/funds`
- **Why it exists:**
  - Consistent navigation
  - Brand identity
  - Route awareness
- **Impact:**
  - **Medium** - Navigation structure
  - User orientation
- **Key Implementation Details:**
  - ✅ Uses `usePathname()` for route detection
  - ✅ Conditional rendering based on route
  - ✅ Active state styling
  - ✅ Responsive design
- **Lines:** ~77

---

#### `frontend/src/components/chat/ChatInput.tsx`
- **Path:** `frontend/src/components/chat/ChatInput.tsx`
- **Purpose:** Chat input component with search mode selection
- **What it contains:**
  - Text input area
  - Search mode selector (Lexical/Semantic/Hybrid)
  - Settings panel (collapsible)
  - Submit button
  - Loading state
  - Placeholder text
- **Key Features:**
  - **Search Mode Selection:** Toggle between Lexical, Semantic, Hybrid
  - **Settings Panel:** Collapsible panel with mode options
  - **Visual Mode Indicator:** Shows current mode with pulsing dot
  - **Keyboard Support:** Enter to submit, Shift+Enter for new line
  - **Loading State:** Disabled during API calls
- **State Management:**
  - `input` - Input text value
  - `searchMode` - Selected search mode ('lexical' | 'semantic' | 'hybrid')
  - `showSettings` - Settings panel visibility
- **Why it exists:**
  - User input interface
  - Search mode selection
  - Centralized input handling
- **Impact:**
  - **Critical** - All user queries go through here
  - Search mode affects query quality
- **Key Implementation Details:**
  - ✅ Mode indicator with animation
  - ✅ Settings panel stays open after selection
  - ✅ Visual feedback for active mode
  - ✅ Keyboard shortcuts
  - ✅ Auto-resize textarea
- **Lines:** ~150

---

#### `frontend/src/components/chat/ChatMessage.tsx`
- **Path:** `frontend/src/components/chat/ChatMessage.tsx`
- **Purpose:** Individual chat message display component
- **What it contains:**
  - User message bubble
  - AI message bubble with avatar
  - Loading state (spinner)
  - Error state
  - Fund analysis results (embedded)
  - Citations (source references)
- **Key Features:**
  - **Message Types:** User (right-aligned) and AI (left-aligned)
  - **AI Avatar:** Gradient icon with Sparkles
  - **Loading State:** Spinner while waiting for response
  - **Error Handling:** Displays error messages
  - **Embedded Components:** FundAnalysisResults, Citations
  - **Styling:** Glass morphism bubbles
- **Props:**
  - `message: ChatMessage` - Message data
- **Why it exists:**
  - Consistent message display
  - Reusable message component
  - Handles all message states
- **Impact:**
  - **High** - All messages rendered through this
  - Consistent UI across chat
- **Key Implementation Details:**
  - ✅ Conditional rendering (user vs AI)
  - ✅ Loading and error states
  - ✅ Embedded fund analysis
  - ✅ Citation chips
  - ✅ Glass morphism styling
- **Lines:** ~95

---

#### `frontend/src/components/chat/WelcomeMessage.tsx`
- **Path:** `frontend/src/components/chat/WelcomeMessage.tsx`
- **Purpose:** Welcome screen when chat has no messages
- **What it contains:**
  - Welcome text
  - Quick action buttons
  - AI avatar icon
- **Key Features:**
  - **Quick Actions:** Pre-defined query suggestions
  - **Animated Entrance:** Fade-in animation
  - **Consistent Styling:** Matches chat message style
- **Quick Actions:**
  - "Analyze Axis Bluechip"
  - "High Sharpe Funds"
  - "Safe Debt Funds"
- **Why it exists:**
  - First-time user guidance
  - Quick access to common queries
  - Reduces empty state friction
- **Impact:**
  - **Medium** - Improves UX for new users
  - Reduces blank screen feeling
- **Key Implementation Details:**
  - ✅ Fade-in animation
  - ✅ Clickable quick actions
  - ✅ Consistent with chat UI
- **Lines:** ~40

---

#### `frontend/src/components/chat/FundAnalysisResults.tsx`
- **Path:** `frontend/src/components/chat/FundAnalysisResults.tsx`
- **Purpose:** Displays grid of fund insight cards
- **What it contains:**
  - Grid layout (responsive)
  - FundInsightCard components
  - Limits to 4 funds
- **Key Features:**
  - **Grid Layout:** 1 column mobile, 2 columns desktop
  - **Fund Cards:** Uses FundInsightCard component
  - **Limit:** Shows top 4 funds only
- **Props:**
  - `funds: FundInfo[]` - Array of fund data
- **Why it exists:**
  - Organized fund display
  - Consistent grid layout
  - Reusable fund grid
- **Impact:**
  - **High** - Visual fund analysis in chat
  - Key feature for numerical queries
- **Key Implementation Details:**
  - ✅ Responsive grid
  - ✅ Empty state handling (returns null)
  - ✅ Limits to 4 funds
- **Lines:** ~30

---

#### `frontend/src/components/chat/FundInsightCard.tsx`
- **Path:** `frontend/src/components/chat/FundInsightCard.tsx`
- **Purpose:** Individual fund metric card display
- **What it contains:**
  - Fund name and category
  - Three metric sections:
    - Returns (CAGR) - with icon and color coding
    - Sharpe Ratio - with progress bar and label
    - Volatility (Risk) - with icon and risk label
  - Hover effects
- **Key Features:**
  - **Three-Metric Grid:** CAGR, Sharpe, Volatility
  - **Color Coding:** Based on metric values (good/neutral/bad)
  - **Visual Indicators:** Icons, progress bars
  - **Contextual Labels:** "Excellent", "Good", "Low Risk", etc.
  - **Hover Effects:** Interactive feedback
- **Metrics Displayed:**
  1. **Returns:** 5Y CAGR (falls back to 3Y or 1Y)
  2. **Sharpe Ratio:** With progress bar and quality label
  3. **Volatility:** With risk level label
- **Why it exists:**
  - Compact fund metric display
  - Visual metric comparison
  - At-a-glance fund analysis
- **Impact:**
  - **High** - Core fund display component
  - Enables quick fund comparison
- **Key Implementation Details:**
  - ✅ Uses FundMetricsUtils for color coding
  - ✅ Fallback logic for CAGR (5Y → 3Y → 1Y)
  - ✅ Progress bar for Sharpe visualization
  - ✅ Conditional formatting (N/A handling)
- **Lines:** ~110

---

#### `frontend/src/components/chat/FundMetricsUtils.ts`
- **Path:** `frontend/src/components/chat/FundMetricsUtils.ts`
- **Purpose:** Utility functions for fund metric visualization
- **What it contains:**
  - `getSharpeContext()` - Sharpe ratio color/label
  - `getVolatilityContext()` - Volatility color/label
  - `getReturnColor()` - CAGR color coding
- **Functions:**

**`getSharpeContext(value)`**
- Returns: `{ label, color, bg }`
- Labels: "Excellent" (≥2.0), "Good" (≥1.0), "Average" (<1.0)
- Colors: emerald, blue, amber

**`getVolatilityContext(value)`**
- Returns: `{ label, color }`
- Labels: "Low Risk" (<10%), "Moderate" (10-15%), "High Volatility" (>15%)
- Colors: emerald, amber, rose

**`getReturnColor(value)`**
- Returns: CSS color class
- Colors: emerald (>15%), blue (10-15%), amber (0-10%), rose (<0)
- **Why it exists:**
  - Consistent metric visualization
  - DRY principle (don't repeat color logic)
  - Centralized metric interpretation
- **Impact:**
  - **Medium** - Enables consistent metric display
  - Used by FundInsightCard
- **Key Implementation Details:**
  - ✅ Threshold-based classification
  - ✅ Null/undefined handling
  - ✅ Consistent color scheme
- **Lines:** ~27

---

#### `frontend/src/components/chat/CitationChip.tsx`
- **Path:** `frontend/src/components/chat/CitationChip.tsx`
- **Purpose:** Source citation badge component
- **What it contains:**
  - Citation title
  - Optional page number
  - Optional score display
  - Clickable badge
- **Key Features:**
  - **Visual Badge:** Small, pill-shaped badge
  - **Score Display:** Shows relevance score
  - **Interactive:** Hover effects
- **Props:**
  - `title: string` - Citation title
  - `page?: number` - Page number
  - `score?: number` - Relevance score
- **Why it exists:**
  - Source transparency
  - User can see where answer came from
  - Trust building
- **Impact:**
  - **Medium** - Important for RAG transparency
  - Shows source provenance
- **Key Implementation Details:**
  - ✅ Conditional rendering (page, score)
  - ✅ Hover effects
  - ✅ Truncated title display
- **Lines:** ~30

---

#### `frontend/src/components/chat/index.ts`
- **Path:** `frontend/src/components/chat/index.ts`
- **Purpose:** Barrel export file for chat components
- **What it contains:**
  - Exports all chat components
  - Exports utility functions
- **Exports:**
  - ChatMessage, ChatInput, CitationChip
  - FundAnalysisResults, FundInsightCard
  - WelcomeMessage
  - FundMetricsUtils (all functions)
- **Why it exists:**
  - Clean imports (`@/components/chat` vs long paths)
  - Centralized exports
  - Easier refactoring
- **Impact:**
  - **Low-Medium** - Developer experience
  - Cleaner import statements

---

### 🔷 **Library (`src/lib/`)**

#### `frontend/src/lib/api.ts`
- **Path:** `frontend/src/lib/api.ts`
- **Purpose:** API client - all backend API calls
- **What it contains:**
  - Generic `fetchAPI` wrapper
  - All API functions:
    - `checkHealth()` - Health check
    - `sendQuery()` - RAG query
    - `getFunds()` - Fund list
    - `getFundById()` - Fund details
    - `getFundMetricsSummary()` - Metrics summary
    - `getSearchModes()` - Available search modes
- **Key Features:**
  - **Base URL:** Environment-based (`NEXT_PUBLIC_API_URL`)
  - **Error Handling:** Unified error handling
  - **Type Safety:** TypeScript types for all responses
  - **JSON Parsing:** Automatic JSON parsing
- **API Endpoints:**
  - `GET /api/v1/health`
  - `POST /api/v1/query`
  - `GET /api/v1/funds`
  - `GET /api/v1/funds/:id`
  - `GET /api/v1/funds/summary/metrics`
  - `GET /api/v1/search-modes`
- **Why it exists:**
  - Centralized API communication
  - Consistent error handling
  - Type-safe API calls
  - Reusable API functions
- **Impact:**
  - **Critical** - All backend communication goes through here
  - Single point for API changes
  - Type safety prevents errors
- **Key Implementation Details:**
  - ✅ Environment-based API URL
  - ✅ Generic fetch wrapper
  - ✅ Error handling with user-friendly messages
  - ✅ TypeScript generics for type safety
  - ✅ Query parameter building
- **Lines:** ~105

---

#### `frontend/src/lib/utils.ts`
- **Path:** `frontend/src/lib/utils.ts`
- **Purpose:** Utility functions used across the app
- **What it contains:**
  - `cn()` - Merge Tailwind classes
  - `formatPercent()` - Format percentage
  - `formatCurrency()` - Format currency (INR)
  - `formatNumber()` - Format number
  - `generateId()` - Generate unique ID
  - `truncate()` - Truncate text
  - `getRiskColor()` - Risk level color
  - `getRiskBadgeStyles()` - Risk badge styles
  - `debounce()` - Debounce function
- **Key Functions:**

**`cn(...inputs)`**
- Merges Tailwind classes (handles conflicts)
- Uses `clsx` and `tailwind-merge`
- Critical for conditional styling

**Formatting Functions:**
- `formatPercent()` - "12.50%"
- `formatCurrency()` - "₹1,23,456.78"
- `formatNumber()` - "123.45"

**Risk Functions:**
- `getRiskColor()` - Text color for risk level
- `getRiskBadgeStyles()` - Full badge styles (color + border + bg)

**`debounce()`**
- Delays function execution
- Useful for search inputs
- **Why it exists:**
  - Reusable utility functions
  - DRY principle
  - Consistent formatting
- **Impact:**
  - **Medium** - Used throughout the app
  - Consistent formatting
  - Cleaner code
- **Key Implementation Details:**
  - ✅ Class merging with conflict resolution
  - ✅ Null-safe formatting
  - ✅ Indian number formatting
  - ✅ Debounce for performance
- **Lines:** ~95

---

### 🔷 **Types (`src/types/`)**

#### `frontend/src/types/index.ts`
- **Path:** `frontend/src/types/index.ts`
- **Purpose:** All TypeScript type definitions
- **What it contains:**
  - Search modes type
  - API request/response types
  - Component prop types
  - Chat message types
  - Fund types
- **Key Types:**

**Search Modes:**
```typescript
type SearchMode = 'lexical' | 'semantic' | 'hybrid';
```

**API Types:**
- `QueryRequest` - RAG query request
- `QueryResponse` - RAG query response
- `FundSummary` - Fund list item
- `FundDetail` - Full fund details
- `SourceDocument` - RAG source document
- `FundInfo` - Fund info in responses

**Chat Types:**
- `ChatMessage` - Chat message structure
- `MessageData` - Message metadata
- `MessageMetric` - Metric display
- `MessageCitation` - Citation badge
- `ChartDataPoint` - Chart data structure

**Why it exists:**
- Type safety across the app
- Single source of truth for types
- API contract definition
- Component prop types
- **Impact:**
  - **Critical** - All components use these types
  - Prevents type errors
  - Self-documenting code
  - IDE autocomplete support
- **Key Implementation Details:**
  - ✅ Comprehensive type coverage
  - ✅ Optional properties marked correctly
  - ✅ Union types for enums
  - ✅ Extensible interfaces
- **Lines:** ~139

---

### 🔷 **Hooks (`src/hooks/`)**

#### `frontend/src/hooks/index.ts`
- **Path:** `frontend/src/hooks/index.ts`
- **Purpose:** Custom React hooks for data fetching and state management
- **What it contains:**
  - `useChat()` - Chat message management
  - `useFunds()` - Fund list fetching
  - `useFundDetail()` - Single fund fetching
  - `useHealth()` - Health check
- **Key Hooks:**

**`useChat()`**
- **Returns:** `{ messages, isLoading, error, sendMessage, clearMessages }`
- **Features:**
  - Message state management
  - API integration
  - Loading states
  - Error handling
  - Message transformation (funds → metrics, sources → citations)
- **Why it exists:**
  - Reusable chat logic
  - Separates UI from data logic
  - Consistent message handling

**`useFunds()`**
- **Returns:** `{ funds, isLoading, error, fetchFunds }`
- **Features:**
  - Fund list state
  - Filtering support
  - Error handling
- **Why it exists:**
  - Reusable fund fetching
  - Consistent state management

**`useFundDetail()`**
- **Returns:** `{ fund, isLoading, error, fetchFund }`
- **Features:**
  - Single fund state
  - Error handling
- **Why it exists:**
  - Reusable fund detail fetching

**`useHealth()`**
- **Returns:** `{ isHealthy, isChecking, checkAPI }`
- **Features:**
  - Backend health check
  - Boolean health status
- **Why it exists:**
  - API availability checking
- **Impact:**
  - **High** - Used by multiple components
  - Encapsulates data fetching logic
  - Consistent error handling
  - Reusable across components
- **Key Implementation Details:**
  - ✅ useState for state management
  - ✅ useCallback for stable functions
  - ✅ Error handling
  - ✅ Loading states
  - ✅ Type-safe return values
- **Lines:** ~239

---

## 🔄 Data Flow Through the System

### **Chat Flow:**
```
1. User types query → ChatInput.tsx
2. User submits → sendMessage() from useChat hook in chat/page.tsx
3. API call → lib/api.ts → sendQuery()
4. Backend processes → RAG pipeline
5. Response received → QueryResponse
6. Message created → ChatMessage component
7. Fund data extracted → FundAnalysisResults
8. Citations added → CitationChip components
9. UI updates → Message displayed
```

### **Fund Explorer Flow:**
```
1. Page loads → funds/page.tsx
2. useEffect triggers → fetchFunds() from hooks
3. API call → lib/api.ts → getFunds()
4. Response received → FundListResponse
5. Funds displayed → Fund cards
6. User filters → Client-side filtering
7. User clicks "Ask AI" → Navigate to /chat?q=...
```

### **Fund Detail Flow:**
```
1. User clicks fund → Navigate to /funds/[fundId]
2. Page loads → [fundId]/page.tsx
3. useEffect triggers → useFundDetail() hook
4. API call → lib/api.ts → getFundById()
5. Response received → FundDetail
6. Metrics displayed → Fund detail view
7. User clicks "Ask AI" → Navigate to /chat?q=...
```

---

## 🎯 Key Design Decisions & Their Impact

### **1. Next.js App Router (not Pages Router)**
- **Decision:** Use App Router (Next.js 13+)
- **Why:** Modern routing, Server Components, better performance
- **Impact:**
  - ✅ Server Components capability (future)
  - ✅ Better code splitting
  - ✅ Built-in Suspense support

### **2. Client Components (`'use client'`)**
- **Decision:** Most components are client-side
- **Why:** Interactive UI, state management, hooks
- **Impact:**
  - ✅ Full React interactivity
  - ✅ useState, useEffect, custom hooks
  - ⚠️ Slightly larger bundle (still optimized)

### **3. TypeScript Throughout**
- **Decision:** Full TypeScript coverage
- **Why:** Type safety, better DX, fewer bugs
- **Impact:**
  - ✅ Catch errors at compile time
  - ✅ IDE autocomplete
  - ✅ Self-documenting code
  - ✅ Refactoring safety

### **4. Tailwind CSS**
- **Decision:** Utility-first CSS framework
- **Why:** Rapid development, consistent design, small bundle
- **Impact:**
  - ✅ Fast styling
  - ✅ Consistent design system
  - ✅ Responsive by default
  - ✅ Dark theme support

### **5. Component Modularity**
- **Decision:** Small, focused components
- **Why:** Reusability, maintainability, testability
- **Impact:**
  - ✅ Easy to modify individual features
  - ✅ Reusable components
  - ✅ Clear separation of concerns
  - ✅ Easier testing (future)

### **6. Custom Hooks Pattern**
- **Decision:** Extract data fetching into hooks
- **Why:** Reusability, separation of concerns
- **Impact:**
  - ✅ Reusable data fetching logic
  - ✅ Cleaner component code
  - ✅ Consistent error handling

### **7. API Client Centralization**
- **Decision:** Single `lib/api.ts` for all API calls
- **Why:** Single source of truth, easy to modify
- **Impact:**
  - ✅ Easy to change API endpoints
  - ✅ Consistent error handling
  - ✅ Type safety

### **8. Glass Morphism Design**
- **Decision:** Modern glassmorphic UI
- **Why:** Modern aesthetic, depth perception
- **Impact:**
  - ✅ Modern, appealing UI
  - ✅ Good visual hierarchy
  - ✅ Consistent design language

---

## 📊 Component Dependencies

```
Root Layout (layout.tsx)
  └── Header.tsx
  └── Page Components
      ├── Homepage (page.tsx)
      ├── Chat (chat/page.tsx)
      │   ├── WelcomeMessage.tsx
      │   ├── ChatMessage.tsx
      │   │   ├── FundAnalysisResults.tsx
      │   │   │   └── FundInsightCard.tsx
      │   │   │       └── FundMetricsUtils.ts
      │   │   └── CitationChip.tsx
      │   └── ChatInput.tsx
      └── Funds (funds/page.tsx)
          └── Fund Detail ([fundId]/page.tsx)

All Components
  ├── lib/api.ts (API calls)
  ├── lib/utils.ts (Utilities)
  ├── hooks/index.ts (Custom hooks)
  └── types/index.ts (Type definitions)
```

---

## 🔧 Key Implementation Highlights

### **1. Double-Run Prevention in Chat**
- **File:** `chat/page.tsx`
- **Feature:** `hasProcessedQuery` ref prevents double execution
- **Why:** React StrictMode causes double renders in development
- **Impact:** Prevents duplicate API calls
- **Code:**
  ```typescript
  const { sendMessage } = useChat();
  const hasProcessedQuery = useRef(false);
  useEffect(() => {
    if (hasProcessedQuery.current || !urlQuery) return;
    hasProcessedQuery.current = true;
    sendMessage(urlQuery);
  }, [urlQuery]);
  ```

### **2. URL Query Parameter Support**
- **File:** `chat/page.tsx`, `page.tsx`
- **Feature:** Pre-filled queries via URL (`/chat?q=query`)
- **Why:** Deep linking, quick actions
- **Impact:** Enables "Ask AI" buttons from other pages
- **Usage:** `router.push('/chat?q=Tell me about Axis Bluechip')`

### **3. Client-Side Filtering**
- **File:** `funds/page.tsx`
- **Feature:** Filtering happens in browser (no API calls)
- **Why:** Fast, responsive, reduces server load
- **Impact:** Instant filter responses
- **Implementation:** Computed `filteredFunds` array

### **4. Responsive Grid Layouts**
- **Files:** `FundAnalysisResults.tsx`, `funds/page.tsx`
- **Feature:** CSS Grid with responsive breakpoints
- **Why:** Mobile-first design
- **Impact:** Works on all screen sizes
- **Pattern:** `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`

### **5. Glass Morphism Styling**
- **Pattern:** `backdrop-blur-md bg-slate-900/50 border-white/10`
- **Why:** Modern, depth, visual appeal
- **Impact:** Consistent design language
- **Usage:** Chat bubbles, input boxes, cards


### **7. Type-Safe API Client**
- **File:** `lib/api.ts`
- **Feature:** TypeScript generics for API responses
- **Why:** Type safety, autocomplete, error prevention
- **Impact:** Catches API errors at compile time
- **Pattern:** `fetchAPI<QueryResponse>(endpoint)`

---

## 📈 Performance Characteristics

### **Bundle Size:**
- Initial load: ~200-300KB (gzipped)
- Code splitting: Automatic with Next.js
- Lazy loading: Dynamic imports possible

### **API Calls:**
- Chat query: ~1.5-4 seconds (depends on backend)
- Fund list: ~100-500ms
- Fund detail: ~100-500ms

### **Rendering:**
- First Contentful Paint: ~1-2 seconds
- Time to Interactive: ~2-3 seconds
- Client-side navigation: Instant (Next.js prefetching)

---

## 🎯 Summary: Critical Files

### **Must Understand (Core Functionality):**
1. ✅ `app/chat/page.tsx` - Main chat interface
2. ✅ `app/page.tsx` - Homepage
3. ✅ `lib/api.ts` - All API calls
4. ✅ `components/chat/ChatInput.tsx` - User input
5. ✅ `components/chat/ChatMessage.tsx` - Message display

### **Important (Features & UX):**
1. ✅ `app/funds/page.tsx` - Fund explorer
2. ✅ `components/chat/FundAnalysisResults.tsx` - Fund display
3. ✅ `hooks/index.ts` - Data fetching logic
4. ✅ `types/index.ts` - Type definitions

### **Supporting (Infrastructure):**
1. ✅ `app/layout.tsx` - Root layout
2. ✅ `next.config.js` - Next.js configuration
3. ✅ `tailwind.config.ts` - Styling system
4. ✅ `lib/utils.ts` - Utility functions

---

## 🚀 Future Enhancements Ready

1. **Server Components** - Can migrate some components to Server Components
2. **React Query** - `@tanstack/react-query` already installed, can add caching
3. **Error Boundaries** - Can add error boundaries for better error handling
4. **Loading Skeletons** - Can add skeleton loaders for better UX
5. **Animations** - Can add more animations with Framer Motion
6. **PWA Support** - Can add service worker for offline support
7. **Dark/Light Theme** - `next-themes` installed, can add theme toggle
8. **Charts** - `recharts` installed, can add more visualizations

---

## 📝 Development Workflow

### **Adding a New Component:**
1. Create component file in `src/components/`
2. Export from `index.ts` (if in subdirectory)
3. Import and use in page/component

### **Adding a New Page:**
1. Create `page.tsx` in `src/app/[route]/`
2. Use `'use client'` if interactive
3. Import necessary components and hooks

### **Adding an API Endpoint:**
1. Add function to `lib/api.ts`
2. Add types to `types/index.ts`
3. Use in components via hooks or direct calls

### **Styling:**
1. Use Tailwind utility classes
2. Add custom styles to `globals.css` if needed
3. Use CSS variables for theming

---

This documentation provides a complete understanding of every file in the frontend. Each component is designed with clear responsibilities, proper separation of concerns, and modern React/Next.js best practices.

