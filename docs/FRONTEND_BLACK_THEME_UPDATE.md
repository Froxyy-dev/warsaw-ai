# Frontend Update: True Black Theme (Cursor-Style)

## Summary
Zmieniono cały motyw z niebieskiego na prawdziwie czarny w stylu Cursor - minimalistyczny, grafitowy z subtelnym kontrastem.

## Paleta Kolorów

### Główne Tła
- **Główne tło**: `#0a0a0a` (prawie czarne)
- **Panele/karty**: `#1a1a1a` (ciemny grafitowy)
- **Ciemniejsze sekcje**: `#0a0a0a` (najciemniejszy)
- **Podniesione elementy**: `#2a2a2a` (jaśniejszy grafitowy)

### Bordy i Separatory
- **Główne bordy**: `border-white/[0.06]` (6% opacity)
- **Subtelne bordy**: `border-white/[0.08]` (8% opacity)
- **Hover bordy**: `border-white/[0.1]` (10% opacity)

### Tekst
- **Główny tekst**: `text-neutral-100` / `text-neutral-200`
- **Drugorzędny**: `text-neutral-300` / `text-neutral-400`
- **Wyciszony**: `text-neutral-500` / `text-neutral-600`
- **Bardzo wyciszony**: `text-neutral-700`

### Akcenty
- **Success/Completed**: `emerald-500` (zielony dla ukończonych kroków)
- **Error/Rejected**: `red-500` / `red-400`
- **Neutral active**: `neutral-400` (zamiast niebieskiego)

## Szczegółowe Zmiany

### 1. Main Page (`app/page.tsx`)

#### Tło
```typescript
// Było: bg-gradient-to-b from-[#050816] via-[#050816] to-[#020617]
// Jest: bg-[#0a0a0a]
```

#### Header
```typescript
// Było: bg-white/5 border-white/10
// Jest: bg-[#1a1a1a]/80 border-white/[0.06]
```

#### Logo/Ikona
- Zmieniono z niebieskiego gradientu na `bg-[#2a2a2a]` z subtelnym bordem
- Ikona w kolorze `text-neutral-400`

#### Chat Panel Card
```typescript
// Było: bg-slate-900/60 border-white/10 backdrop-blur-md
// Jest: bg-[#1a1a1a] border-white/[0.06]
```

### 2. Chat Messages (`ChatMessage.tsx`)

#### Awatary
```typescript
// Było: bg-gradient-to-br from-sky-500 to-indigo-600
// Jest: bg-[#2a2a2a] border border-white/[0.08] text-neutral-400
```

#### AI Message Bubble
```typescript
// Było: bg-slate-900/70 border-white/10 backdrop-blur-md
// Jest: bg-[#1a1a1a] border-white/[0.06]
```

#### User Message Bubble
```typescript
// Było: bg-sky-500 (niebieski)
// Jest: bg-[#2a2a2a] border-white/[0.08] text-neutral-100
```

#### Code Blocks
```typescript
// Było: bg-slate-900/50 text-sky-300
// Jest: bg-[#0a0a0a] text-neutral-300 border border-white/[0.06]
```

#### Linki i Bold
- Bold: `text-neutral-200` (zamiast `text-sky-300`)
- Linki: `text-neutral-400` hover `text-neutral-300`

### 3. Chat Window (`ChatWindow.tsx`)

#### Welcome Screen
```typescript
// Emoji opacity: 0.3 (zamiast 0.5)
// Tytuł: text-neutral-200
// Opis: text-neutral-500
```

#### Loading State
```typescript
// Avatar: bg-[#2a2a2a] border border-white/[0.08]
// Bubble: bg-[#1a1a1a] border-white/[0.06]
// Spinner: text-neutral-400
```

#### Input Area
```typescript
// Input: bg-[#0a0a0a] border-white/[0.06]
// Focus ring: focus-visible:ring-1 ring-neutral-700
// Button: bg-[#2a2a2a] hover:bg-[#333333]
```

### 4. Pipeline View (`PipelineView.tsx`)

#### Card
```typescript
// Było: bg-slate-900/60 border-white/10 backdrop-blur-md
// Jest: bg-[#1a1a1a] border-white/[0.06]
```

#### Status Icons
- **Completed**: `text-emerald-500` (zielony)
- **In Progress**: `text-neutral-400` (szary zamiast niebieskiego)
- **Pending**: `text-neutral-800`

#### Active Step
```typescript
// Było: bg-sky-500/10 border-sky-500/30 (niebieski)
// Jest: bg-neutral-800/30 border-neutral-700/50 (grafitowy)
```

#### Badges
- Success: `bg-emerald-500/20 text-emerald-400 border-emerald-500/30`
- Rejected: `bg-red-500/20 text-red-400 border-red-500/30`
- No Answer: `bg-neutral-800/50 text-neutral-400`

#### Task Results Cards
```typescript
// Card: bg-[#0a0a0a] border-white/[0.06]
// Icon container: bg-[#2a2a2a] border-white/[0.08]
// Button: bg-[#2a2a2a] hover:bg-[#333333]
```

### 5. Global Styles (`globals.css`)

#### Scrollbar
```css
/* Było: rgb(51 65 85 / 0.5) - niebieski */
/* Jest: rgb(64 64 64 / 0.3) - grafitowy */
```

## Usunięte Efekty

❌ **Backdrop blur** - usunięty z większości miejsc (niepotrzebny na solidnym tle)
❌ **Shadows** - usunięte glow shadows (np. `shadow-sky-500/20`)
❌ **Niebieskie gradienty** - zamienione na solid grafitowe kolory
❌ **Niebieskie akcenty** - zamienione na neutralne szare

## Zachowane Efekty

✅ **Emerald green** dla success states
✅ **Smooth transitions** na hover
✅ **Border radius** (rounded-xl, rounded-2xl)
✅ **Opacity states** dla disabled/completed items
✅ **Animate pulse** dla loading states

## Filozofia Designu

### Minimalizm
- Brak zbędnych kolorów
- Subtelny kontrast
- Czyste, proste formy

### Hierarchy przez Brightness
- Najważniejsze: neutral-100/200
- Średnio: neutral-400/500
- Tło: neutral-700/800

### Subtle Borders
- Wszystkie bordy bardzo subtelne (6-10% opacity)
- Separacja przez odcienie czerni, nie przez kolor

### Cursor-Style
- True black background (#0a0a0a)
- Graphite panels (#1a1a1a, #2a2a2a)
- Minimal color accents (tylko emerald dla success)
- Ultra-subtle borders
- No unnecessary blur/shadows

## Rezultat

Interfejs teraz wygląda jak:
- ✅ Cursor IDE
- ✅ Linear app
- ✅ Raycast
- ✅ Premium dark mode 2025

**Czarny, minimalistyczny, profesjonalny, bez rozpraszających kolorów.**

## Pliki Zmodyfikowane
1. `/frontend/src/app/page.tsx`
2. `/frontend/src/components/ChatMessage.tsx`
3. `/frontend/src/components/ChatWindow.tsx`
4. `/frontend/src/components/PipelineView.tsx`
5. `/frontend/src/app/globals.css`

## Brak Błędów
✅ Zero linting errors
✅ Wszystkie zmiany tylko wizualne
✅ Żadna logika biznesowa nie została zmieniona

