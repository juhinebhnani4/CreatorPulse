# CreatorPulse Frontend - Next.js 14

Modern Next.js frontend for the CreatorPulse AI Newsletter Generator.

## Features

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Radix UI** components (via shadcn/ui pattern)
- **Zustand** for state management
- **Axios** with authentication interceptor

## Quick Start

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Environment variables are already configured in .env.local
```

### Development

```bash
# Start dev server
npm run dev

# Open http://localhost:3000
```

## Project Structure

```
frontend-nextjs/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx            # Landing page
│   │   ├── login/              # Login page
│   │   ├── register/           # Register page
│   │   └── app/                # Protected dashboard
│   │
│   ├── components/
│   │   └── ui/                 # UI components (Button, Card, Input, etc.)
│   │
│   ├── lib/
│   │   ├── api/                # API client & endpoints
│   │   ├── stores/             # Zustand stores
│   │   └── utils.ts            # Utility functions
│   │
│   └── types/                  # TypeScript types
│
└── .env.local                  # Environment variables
```

## Pages

- **`/`** - Landing page
- **`/login`** - Login
- **`/register`** - Register
- **`/app`** - Dashboard (protected)

## Current Status

✅ **Completed:**
- Next.js 14 setup with TypeScript
- Tailwind CSS + shadcn/ui components
- API client with authentication
- Auth store with Zustand
- Landing page
- Login/Register pages
- Basic dashboard page

🚧 **Next Steps:**
- Full dashboard with newsletter preview
- Settings page
- Modals for draft editing
- History page
- Loading states
- Mobile responsive

## Environment Variables

Configured in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key
```

## Tech Stack

- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI
- **State:** Zustand
- **HTTP Client:** Axios
