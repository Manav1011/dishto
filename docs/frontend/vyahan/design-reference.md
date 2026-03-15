# Vyahan Frontend Design Reference

This document outlines the core colors, typographies, layout structures, and styling techniques used across the Vyahan tracking and logistics frontend to achieve its premium glassmorphic aesthetic.

## 1. Color Palette

The project primarily utilizes a blend of Tailwind's Slate and Orange color scales, paired with custom CSS variables for essential brand elements.

### Brand Colors
- **Brand Orange (Primary)** 
  - **Hex**: `#F97316` (`orange-500` in Tailwind)
  - **Hover variant**: `#EA580C` (`orange-600`)
  - **Usage**: Primary call-to-action buttons, active navigation items, icon highlights, dynamic glows, and primary gradients.

### Background Colors
- **Deep Slate (Global Background)**
  - **Hex**: `#F8FAFC` (`slate-50`)
  - **Usage**: The main application canvas background (`--bg-deep`).
- **Surface / Card Background**
  - **Hex**: `rgba(255, 255, 255, 0.8)` (`--bg-card`)
  - **Usage**: Used inside elements sporting the `.glass` class.
- **Premium Hero Dark Background**
  - **Hex**: `#020617` / `#0F172A` (`slate-950` / `slate-900`)
  - **Usage**: Used primarily for Hero banners and contrast elements like action shortcut buttons, often paired with bright orange glows.

### Typography Colors
- **Text Primary**
  - **Hex**: `#0F172A` (`slate-900` / `--text-primary`)
  - **Usage**: Main headings, bold text, primary reading content.
- **Text Secondary / Muted**
  - **Hex**: `#64748B` (`slate-500` / `slate-400` / `--text-secondary`)
  - **Usage**: Subtitles, body descriptions, table headers, metadata.

### Status Indicators
- **Arrived (Success)**
  - Background: Emerald-500/10 (`bg-emerald-500/10`)
  - Text: Emerald-600 (`text-emerald-600`)
  - Border: Emerald-500/20
- **In Transit (Progress)**
  - Background: Sky-500/10 (`bg-sky-500/10`)
  - Text: Sky-600 (`text-sky-600`)
  - Border: Sky-500/20
- **Booked / Pending (Neutral)**
  - Background: Slate-100 (`bg-slate-100`)
  - Text: Slate-500 (`text-slate-500`)
  - Border: Slate-200

---

## 2. Typography Constraints
Two primary Google Fonts are imported via `index.html`:

- **Inter (`font-sans`)**: The system default font for the entire body. It provides excellent readability for dense logistics text and data.
- **Outfit (`font-brand`)**: Assigned to classes like `.font-brand` alongside headings (`h1` through `h6`). This font offers a premium, modern geometrical feel, primarily focused on displaying titles, labels, tracking IDs, and uppercase taglines.

---

## 3. Card Layouts & Glassmorphism

The application distinctly defines its premium aesthetic via dynamic card containers:

### Universal Container / Component Block
- **Container Structure**: 
  - Uses classes like `bg-white rounded-xl sm:rounded-2xl md:rounded-[2.5rem] overflow-hidden border border-slate-200 shadow-xl`.
  - The card headers generally sit on a distinct subtle slate background like `bg-slate-50/50` bordering the primary content.
- **Interactions**: Elements consistently use `transition-all duration-300 active:scale-95` to yield tactile, native-app-like interaction behaviors.

### Premium Status Cards (Dashboards)
The individual statistic cards (`StatCard`) follow a very tight signature layout:
- **Base Background**: `bg-white` 
- **Border Mechanics**: `border border-slate-200` with heavily rounded corners (`rounded-xl` going up to `rounded-[1.5rem]` on large viewports).
- **Hover Transitions**: Elevated on hover using `hover:shadow-2xl hover:bg-slate-50` with an accompanying subtle scale via `active:scale-[0.98]`.
- **Top Right Ambience Glow**: Achieved via an `absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full blur-2xl` div with a background of `bg-orange-500/5`, brightening to `/10` on group-hover.
- **Icon Blocks**: Floating gradient icon blocks (`bg-gradient-to-br from-orange-500 to-orange-600`) that include shadow (`shadow-orange-500/20`) and scale up (`group-hover:scale-110`) during user hover.

### Hero Overviews (Premium Contrast Blocks)
- Large top-level introduction components break the light theme rhythm using dark slate backgrounds (`bg-slate-900`) combined with intense blurred orb backgrounds (e.g., `bg-orange-500 rounded-full blur-[120px] opacity-20`) pushing from absolute corners. This creates an immersive, spotlighted view. 

### Glassmorphism Utility Classes (CSS)
Defined in `index.html`:
- **`.glass`**: A standard translucent layer applying a `rgba(255, 255, 255, 0.8)` background complemented by `backdrop-filter: blur(12px)` and a subtle light slate border. Generally utilized for Sticky Top Navbars.
- **`.glass-dark`**: A slightly less translucent variant utilizing `rgba(255, 255, 255, 0.95)` and `backdrop-filter: blur(20px)` mapped heavily to sidebars to establish strong visual hierarchy while sustaining the unified blur mechanic behind it.
- **`.orange-glow`**: Readily applies a tailored box-shadow `box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3)` to icons or active state buttons.

---

## 4. Layout Metrics & Spacing
- **Corner Radii (`border-radius`)**: Heavily relied upon to soften aesthetics. Core cards use between `24px` (`rounded-3xl` or `rounded-[1.5rem]`) and `40px` (`rounded-[2.5rem]`). Inner interactive elements like icons or table lines use `12px` (`rounded-xl`) or completely pill-shaped `rounded-full` boundaries.
- **Padding constraints**: Emphasizes spacious, breathable padding (e.g., `p-4 sm:p-6 md:p-8 lg:p-10`) using a mobile-first approach. Max widths on views are generally constrained to `max-w-[1600px] mx-auto w-full`.
