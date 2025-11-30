# Frontend Migration Guide

## Overview
This frontend has been migrated from Create React App (CRA) to Next.js 14 with TypeScript, Tailwind CSS, and shadcn/ui components.

## What Changed

### Technology Stack
- **Before**: CRA + JavaScript + Custom CSS
- **After**: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui

### Key Improvements
1. ✅ Modern 2025 SaaS design with clean, minimal aesthetics
2. ✅ TypeScript for type safety and better developer experience
3. ✅ Tailwind CSS for consistent, utility-first styling
4. ✅ shadcn/ui components for professional UI elements
5. ✅ Better build performance with Next.js
6. ✅ Improved code organization and maintainability

## Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run development server:**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

3. **Build for production:**
   ```bash
   npm run build
   npm start
   ```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app router
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Home page
│   │   └── globals.css   # Global styles with Tailwind
│   ├── components/
│   │   ├── ChatWindow.tsx    # Main chat component
│   │   └── ui/               # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── textarea.tsx
│   │       ├── badge.tsx
│   │       └── skeleton.tsx
│   ├── api/
│   │   ├── axios.ts      # Axios configuration
│   │   ├── chatApi.ts    # Chat API client
│   │   └── types.ts      # TypeScript types
│   └── lib/
│       └── utils.ts      # Utility functions
├── next.config.js        # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
├── components.json       # shadcn/ui configuration
└── package.json          # Dependencies
```

## Features

### Chat Interface
- Real-time messaging with auto-refresh
- Optimistic UI updates
- Loading states with animations
- Error handling with user feedback
- Responsive design (mobile-first)

### Design System
- **Colors**: Dark theme with blue accents
- **Typography**: Inter font family
- **Spacing**: Consistent padding and margins
- **Borders**: Rounded corners (rounded-xl, rounded-2xl)
- **Shadows**: Subtle shadows for depth

### API Integration
- All existing API calls preserved
- Backend proxy configured in `next.config.js`
- TypeScript types for all API responses

## Old Files

The old CRA files are still present in the repository:
- `src/App.js` (old)
- `src/App.css` (old)
- `src/components/ChatWindow.js` (old)
- `src/components/ChatWindow.css` (old)
- `src/index.js` (old)
- `src/index.css` (old)
- `src/setupProxy.js` (not needed in Next.js)
- `public/index.html` (not needed in Next.js)

**These can be safely deleted** once you verify the new Next.js version works correctly.

## Backend Compatibility

No changes required to the backend! The frontend still communicates with the same API endpoints:
- POST `/api/chat/conversations/`
- GET `/api/chat/conversations/`
- GET `/api/chat/conversations/{id}`
- POST `/api/chat/conversations/{id}/messages`

The Next.js `rewrites()` configuration in `next.config.js` proxies all `/api/*` requests to `http://localhost:8000/api/*`.

## Adding New Components

To add more shadcn/ui components:

```bash
npx shadcn-ui@latest add [component-name]
```

Examples:
```bash
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
```

## Customization

### Colors
Edit `tailwind.config.ts` and `src/app/globals.css` to modify the color scheme.

### Components
All shadcn/ui components are in `src/components/ui/` and can be customized directly.

### Layout
Edit `src/app/page.tsx` to modify the main layout structure.

## Troubleshooting

### Port conflicts
If port 3000 is already in use:
```bash
PORT=3001 npm run dev
```

### Build errors
Clear Next.js cache:
```bash
rm -rf .next
npm run dev
```

### Type errors
Ensure all dependencies are installed:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. ✅ Verify the app works with your backend
2. ✅ Test all chat functionality
3. ✅ Check responsive design on mobile devices
4. 🔲 Delete old CRA files (optional)
5. 🔲 Add more features (task list, venue search UI, etc.)
6. 🔲 Deploy to production (Vercel, etc.)

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [TypeScript](https://www.typescriptlang.org/docs/)

