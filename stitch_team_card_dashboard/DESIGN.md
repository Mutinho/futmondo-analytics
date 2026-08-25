---
name: Obsidian Performance
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#bccbb9'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#869585'
  outline-variant: '#3d4a3d'
  surface-tint: '#4ae176'
  primary: '#4be277'
  on-primary: '#003915'
  primary-container: '#22c55e'
  on-primary-container: '#004b1e'
  inverse-primary: '#006e2f'
  secondary: '#ffb3ad'
  on-secondary: '#68000a'
  secondary-container: '#a40217'
  on-secondary-container: '#ffaea8'
  tertiary: '#afc7ff'
  on-tertiary: '#002e6a'
  tertiary-container: '#82abff'
  on-tertiary-container: '#003d88'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6bff8f'
  primary-fixed-dim: '#4ae176'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005321'
  secondary-fixed: '#ffdad7'
  secondary-fixed-dim: '#ffb3ad'
  on-secondary-fixed: '#410004'
  on-secondary-fixed-variant: '#930013'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a42'
  on-tertiary-fixed-variant: '#004395'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Hanken Grotesk
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
  label-caps:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 24px
  gutter: 16px
---

## Brand & Style

This design system is engineered for high-stakes data density and financial performance tracking. The brand personality is clinical, precise, and authoritative, drawing heavily from **Modern Minimalism** with a **Corporate** finish. It prioritizes legibility in low-light environments, using deep achromatic layers to make critical data points—represented by vivid semantic accents—immediately identifiable.

The visual mood is focused and "heads-down." It avoids decorative flourishes in favor of structural clarity, utilizing high-contrast data visualization against an obsidian-like backdrop to reduce eye strain during prolonged analysis.

## Colors

The palette is anchored by a true black background to maximize OLED efficiency and provide the deepest possible contrast. 

- **Primary (Success):** A vivid emerald green (#22C55E) used exclusively for positive financial deltas and "buy" signals.
- **Secondary (Danger):** A bright, high-chroma red (#EF4444) for negative values, deficits, and alerts.
- **Neutrals:** A scale of cool-toned greys. The core surface level is set at #121212, providing enough separation from the pure black background without introducing excessive glow.
- **Text:** Primary text uses Off-White (#F5F5F5) for high legibility, while secondary metadata uses Medium Grey (#A1A1AA).

## Typography

This system uses **Hanken Grotesk** for all primary UI and heading elements due to its sharp geometry and contemporary feel. To handle complex numerical data—specifically the large currency values shown in the reference—**JetBrains Mono** is employed for data-heavy table cells to ensure digit alignment and vertical scanning speed.

All financial values should use the `data-mono` style to prevent "shimmering" layout shifts when numbers update. Column headers use `label-caps` with increased tracking to create clear visual hierarchy against the data rows.

## Layout & Spacing

The layout follows a **Fixed Grid** approach for desktop dashboards to maintain strict data alignment, transitioning to a **Fluid Grid** for mobile.

- **Desktop (1440px+):** 12-column grid with a max-width of 1320px. 24px gutters.
- **Tablet (768px - 1024px):** 8-column grid with 16px gutters and margins.
- **Mobile (<768px):** 4-column fluid grid. Table data should reflow into card-style summaries.

Spacing is based on a **4px baseline scale**. Large data tables should utilize "Compact" vertical padding (8px top/bottom) to maximize information density, while container cards use "Standard" padding (24px) to provide visual breathing room.

## Elevation & Depth

This system rejects traditional shadows in favor of **Tonal Layers** and **Low-Contrast Outlines**. Depth is communicated through color luminance:

1.  **Level 0 (Base):** #050505 (Deepest black).
2.  **Level 1 (Cards/Tables):** #121212 with a 1px solid border of #2A2A2A.
3.  **Level 2 (Modals/Popovers):** #1E1E1E with a 1px solid border of #3F3F46.

Hover states on interactive rows should be signaled by a subtle background shift to #1A1A1A, rather than a shadow or glow. This maintains the "flat" professional aesthetic of the dashboard.

## Shapes

The shape language is **Soft (0.25rem)**. This slight rounding takes the edge off the high-contrast interface without making the UI feel overly casual or "bubbly."

- **Cards & Data Containers:** Use `rounded-lg` (0.5rem) to define clear boundaries.
- **Buttons & Inputs:** Use the base `rounded` (0.25rem).
- **Status Indicators (Pills):** Use `rounded-full` (999px) for chips representing categories or boolean states.

## Components

### Tables
The core component. Rows must have a bottom border of 1px (#1E1E1E). Numerical columns are right-aligned to allow for decimal comparison. Use semantic coloring (#22C55E or #EF4444) for the entire text string in financial columns when representing change or status.

### Cards
Card containers use a background of #121212. Title headers within cards use `label-caps` in a muted grey (#71717A). Ensure a consistent 24px internal padding.

### Buttons
- **Primary:** Background #F5F5F5, Text #050505 (High contrast).
- **Secondary:** Background transparent, 1px border #2A2A2A, Text #F5F5F5.
- **Ghost:** Background transparent, Text #A1A1AA.

### Input Fields
Inputs use a dark fill (#0A0A0A) with a 1px border (#2A2A2A). Focus states are indicated by a 1px border of #3B82F6 (Tertiary).

### Data Badges (Chips)
Small, low-profile indicators. For "Ops" or count-based data, use a subtle grey background (#2A2A2A) with white text. For performance, use the primary/secondary semantic colors with a 10% opacity background of the same hue.