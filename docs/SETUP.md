# Quick Setup Guide

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager

## Step-by-Step Setup

### 1. Clean Install
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

### 3. Ensure Backend is Running
In another terminal:
```bash
cd ../backend
# Activate your Python virtual environment
source venv/bin/activate  # or your venv activation command
uvicorn main:app --reload
```

Backend should be running on [http://localhost:8000](http://localhost:8000)

### 4. Test the Application
1. Open [http://localhost:3000](http://localhost:3000)
2. Type a message in the chat
3. Verify the message is sent to the backend
4. Check that responses appear in the chat

## What's New?

### Modern UI Components
- **Card components** for structured layouts
- **Button components** with multiple variants
- **Textarea** with improved styling
- **Loading indicators** with animations
- **Badge components** for status indicators

### TypeScript Support
All files are now `.ts` or `.tsx` with proper type checking.

### Dark Theme
Beautiful dark theme with:
- Slate/gray backgrounds
- Blue accent colors
- Smooth animations
- Professional spacing

### Responsive Design
Works perfectly on:
- Desktop (1920px+)
- Laptop (1024px+)
- Tablet (768px+)
- Mobile (375px+)

## Common Issues

### Port 3000 already in use?
```bash
# Use a different port
PORT=3001 npm run dev
```

### Backend connection refused?
Make sure backend is running on port 8000:
```bash
curl http://localhost:8000/api/chat/conversations/
```

### TypeScript errors?
```bash
# Reinstall dependencies
rm -rf node_modules .next
npm install
```

## Development Tips

### Hot Reload
Changes to any file automatically reload the page. No need to restart the dev server!

### Code Organization
- Put new pages in `src/app/`
- Put new components in `src/components/`
- Put API calls in `src/api/`
- Put utilities in `src/lib/`

### Adding Components
Install shadcn/ui components as needed:
```bash
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add table
```

### Styling Guidelines
- Use Tailwind classes: `className="flex items-center gap-4"`
- Use the `cn()` utility for conditional classes
- Follow the existing color scheme (slate + blue)
- Maintain consistent spacing (p-4, p-6, gap-4, gap-6)

## Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## File Structure Quick Reference

```
src/
├── app/
│   ├── layout.tsx       → Root layout, fonts, metadata
│   ├── page.tsx         → Home page with chat + sidebar
│   └── globals.css      → Tailwind + CSS variables
├── components/
│   ├── ChatWindow.tsx   → Main chat component
│   └── ui/              → Reusable UI components
├── api/
│   ├── axios.ts         → Axios config + interceptors
│   ├── chatApi.ts       → API functions
│   └── types.ts         → TypeScript interfaces
└── lib/
    └── utils.ts         → Helper functions (cn, etc.)
```

## Need Help?

Check these files:
- `MIGRATION_GUIDE.md` - Detailed migration information
- `README.md` - Project overview
- `next.config.js` - Next.js configuration
- `tailwind.config.ts` - Styling configuration

