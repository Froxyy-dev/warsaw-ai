# AI Chat Assistant - Frontend

A modern, beautiful frontend for the AI Chat Assistant built with Next.js 14, TypeScript, Tailwind CSS, and shadcn/ui.

![Tech Stack](https://img.shields.io/badge/Next.js-14-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8)
![React](https://img.shields.io/badge/React-18-61dafb)

## 🚀 Features

- **Modern SaaS Design**: Clean, minimal interface inspired by 2025 design trends
- **Real-time Chat**: Interactive chat interface with auto-refresh
- **TypeScript**: Full type safety throughout the application
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Dark Theme**: Beautiful dark mode with blue accents
- **Component Library**: Built with shadcn/ui components
- **Optimistic Updates**: Instant UI feedback for better UX
- **Loading States**: Smooth loading animations and skeletons
- **Error Handling**: Clear error messages and recovery

## 📦 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 3.4
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Utilities**: clsx, tailwind-merge, class-variance-authority

## 🎨 Design Philosophy

This frontend follows modern 2025 SaaS design patterns:

- **Whitespace**: Generous spacing for clarity
- **Consistency**: Unified padding (p-4, p-6), rounded corners (rounded-xl)
- **Hierarchy**: Clear visual hierarchy with typography scale
- **Shadows**: Subtle shadows for depth without clutter
- **Responsive**: Mobile-first approach with grid/flex layouts
- **Accessibility**: Semantic HTML, proper labels, good contrast

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout with fonts & metadata
│   │   ├── page.tsx           # Home page (main dashboard)
│   │   └── globals.css        # Global styles + Tailwind directives
│   │
│   ├── components/
│   │   ├── ChatWindow.tsx     # Main chat interface component
│   │   └── ui/                # shadcn/ui components
│   │       ├── button.tsx     # Button variants
│   │       ├── card.tsx       # Card components
│   │       ├── input.tsx      # Input field
│   │       ├── textarea.tsx   # Textarea field
│   │       ├── badge.tsx      # Badge component
│   │       └── skeleton.tsx   # Loading skeleton
│   │
│   ├── api/                   # API layer
│   │   ├── axios.ts          # Axios instance with config
│   │   ├── chatApi.ts        # Chat API functions
│   │   └── types.ts          # TypeScript interfaces
│   │
│   └── lib/
│       └── utils.ts          # Utility functions (cn, etc.)
│
├── next.config.js            # Next.js configuration
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
├── components.json           # shadcn/ui configuration
└── package.json              # Dependencies
```

## 🎯 Key Components

### ChatWindow
The main chat interface with:
- Message history display
- Real-time message sending
- Auto-refresh during backend processing
- Optimistic UI updates
- Loading indicators
- Error handling

### Page Layout
Dashboard-style layout with:
- Chat panel (2/3 width on desktop)
- Sidebar with quick actions (1/3 width)
- Status indicators
- Responsive grid system

### UI Components (shadcn/ui)
- **Card**: Container with header, content, footer
- **Button**: Multiple variants (default, outline, ghost, etc.)
- **Input/Textarea**: Form controls with focus states
- **Badge**: Status indicators
- **Skeleton**: Loading placeholders

## 🔧 Configuration

### Backend API Proxy
API calls are proxied through Next.js to avoid CORS issues:

```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ];
}
```

### Tailwind Theme
Custom color scheme defined in `tailwind.config.ts` and `globals.css`:
- Primary: Blue (#2563eb)
- Background: Slate/Gray dark tones
- Borders: Slate-800
- Text: Slate-100/400

## 📱 Responsive Design

Breakpoints:
- **Mobile**: < 768px (1 column)
- **Tablet**: 768px - 1024px (2 columns)
- **Desktop**: > 1024px (3 columns)

The layout automatically adjusts:
- Chat takes full width on mobile
- Sidebar moves below chat on tablet
- Side-by-side layout on desktop

## 🔄 State Management

Using React hooks for local state:
- `useState` for messages, input, loading states
- `useEffect` for initialization and auto-refresh
- `useRef` for DOM references and intervals

No global state management (Redux, Zustand) needed for this simple app.

## 🧪 Development

### Adding New Pages
Create a new folder in `src/app/`:
```bash
src/app/tasks/page.tsx      # /tasks route
src/app/venues/page.tsx     # /venues route
```

### Adding New Components
```bash
# Add shadcn/ui component
npx shadcn-ui@latest add dialog

# Create custom component
src/components/MyComponent.tsx
```

### Styling Guidelines
```tsx
// Use Tailwind utility classes
<div className="flex items-center gap-4 p-6 rounded-xl bg-slate-800">
  {/* content */}
</div>

// Use cn() for conditional classes
import { cn } from "@/lib/utils";

<div className={cn(
  "base-classes",
  condition && "conditional-classes"
)}>
```

## 🚦 API Integration

All API calls go through `/api/*` which proxies to the backend:

```typescript
// Example: Send a message
import { sendMessage } from '@/api/chatApi';

const response = await sendMessage(conversationId, content);
```

Available API functions:
- `createConversation()`: Create new conversation
- `getConversations()`: List all conversations
- `getConversation(id)`: Get conversation details
- `sendMessage(id, content)`: Send message
- `deleteConversation(id)`: Delete conversation

## 🎨 Customization

### Change Colors
Edit `tailwind.config.ts` and `src/app/globals.css`:
```css
:root {
  --primary: 221.2 83.2% 53.3%;  /* Modify hue/saturation/lightness */
  --background: 222.2 84% 4.9%;
  /* ... more variables */
}
```

### Change Fonts
Edit `src/app/layout.tsx`:
```typescript
import { Inter, Roboto } from "next/font/google";

const roboto = Roboto({ subsets: ["latin"], weight: ["400", "700"] });
```

### Change Layout
Edit `src/app/page.tsx` to modify the dashboard structure.

## 📄 Scripts

```bash
# Development (with hot reload)
npm run dev

# Production build
npm run build

# Run production build
npm start

# Lint code
npm run lint
```

## 🐛 Troubleshooting

**Port already in use?**
```bash
PORT=3001 npm run dev
```

**Backend not connecting?**
- Ensure backend is running on `http://localhost:8000`
- Check `next.config.js` proxy configuration

**TypeScript errors?**
```bash
rm -rf node_modules .next
npm install
```

**Styles not updating?**
- Clear Next.js cache: `rm -rf .next`
- Restart dev server

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Radix UI](https://www.radix-ui.com/)

## 📝 License

Part of the warsaw-ai project.

---

**Built with ❤️ using modern web technologies**

