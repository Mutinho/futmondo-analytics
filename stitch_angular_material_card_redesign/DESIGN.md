---
name: Pro League Matrix
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#baccaf'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#84967c'
  outline-variant: '#3b4b35'
  surface-tint: '#12e600'
  primary: '#ebffdf'
  on-primary: '#023a00'
  primary-container: '#14ff00'
  on-primary-container: '#067100'
  inverse-primary: '#066e00'
  secondary: '#4ae183'
  on-secondary: '#003919'
  secondary-container: '#06bb63'
  on-secondary-container: '#00431f'
  tertiary: '#fff7f7'
  on-tertiary: '#65002f'
  tertiary-container: '#ffd0da'
  on-tertiary-container: '#ae2e5f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#77ff5f'
  primary-fixed-dim: '#12e600'
  on-primary-fixed: '#012200'
  on-primary-fixed-variant: '#035300'
  secondary-fixed: '#6bfe9c'
  secondary-fixed-dim: '#4ae183'
  on-secondary-fixed: '#00210c'
  on-secondary-fixed-variant: '#005228'
  tertiary-fixed: '#ffd9e1'
  tertiary-fixed-dim: '#ffb1c5'
  on-tertiary-fixed: '#3f001b'
  on-tertiary-fixed-variant: '#8b0e45'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '800'
    lineHeight: 16px
    letterSpacing: 0.05em
  stat-value:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '800'
    lineHeight: 22px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '800'
    lineHeight: 34px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 16px
  gutter: 12px
---

## Brand & Style

The design system is engineered for a high-performance sports management environment. It targets a competitive audience that demands real-time data clarity and rapid actionability. The aesthetic is a fusion of **Modern Corporate** precision and **High-Contrast Bold** energy, utilizing a dark-themed "command center" approach.

The interface evokes a sense of urgency and elite status. It relies on deep tonal layering to separate analytical data from interactive surfaces, ensuring that the "Neon Kinetic" primary accents drive user focus toward critical market movements and transactional buttons. 

Key visual principles:
- **Athletic Precision:** Use of rigid grids and bold typography to reflect the intensity of professional sports.
- **Data Dominance:** Priority is given to numerical values and performance indicators through high-contrast color coding.
- **Tactical Depth:** Subtle elevation and glassmorphic touches are used to indicate state changes without breaking the dark, focused environment.

## Colors

The color system is built on a "Pitch Black" foundation to maximize the vibrance of data visualization. 

- **Primary (Neon Kinetic):** Used exclusively for primary calls to action (e.g., "Pujar" buttons) and positive market trends. It must maintain a high luminance to pop against the dark background.
- **Secondary (Turf Green):** Used for auxiliary positive indicators, badges, and secondary stats (e.g., Sofascore ratings).
- **Tertiary (Position Accents):** Softened pastels like muted pink or cyan are reserved for player position tags (DL, MC, DF) to differentiate them from functional data.
- **Neutrals:** The background uses a true charcoal (#121212), while surface cards use a slightly lighter elevation (#1E1E1E). Text alternates between Pure White for values and Muted Grey for labels.

## Typography

This design system utilizes **Inter** for its mathematical precision and exceptional legibility in data-dense layouts. 

- **Numerical Priority:** All currency and performance values use `stat-value` or `headline-sm` with extra-bold weights to ensure they are the first thing a user scans.
- **Labels:** Meta-information (e.g., "PRECIO MERCADO") always uses `label-caps`. This creates a clear stylistic distinction between the "Category" and the "Data."
- **Scale:** On mobile devices, headlines scale down slightly, but the weight remains heavy to maintain the athletic brand voice.

## Layout & Spacing

The layout follows a **Fluid Grid** model optimized for high-density information. 

- **Rhythm:** A 4px baseline grid ensures tight, disciplined alignment.
- **Cards:** Content within player cards uses a 16px internal padding. Related data points (e.g., Market Price and Suggested Price) are grouped with 8px spacing, while distinct sections (Header vs. Stats vs. Actions) are separated by 16px or 24px vertical margins.
- **Responsive Behavior:** 
  - **Mobile:** 1-column layout with 16px side margins. 
  - **Tablet/Desktop:** Cards transition to a multi-column grid (up to 3 columns) depending on screen width.
- **Dividers:** Use subtle 1px horizontal lines in `#333333` to separate player headers from statistical grids.

## Elevation & Depth

Hierarchy is established through **Tonal Layers** and **Low-Contrast Outlines** rather than heavy shadows, keeping the UI feeling fast and "digital-first."

- **Level 0 (Background):** Deep charcoal (#121212), used for the application canvas.
- **Level 1 (Cards):** Slightly elevated surface (#1E1E1E) with a subtle 1px border (#333333).
- **Level 2 (Overlays/Modals):** Lighter surface (#2C2C2C) with a soft 15% opacity black shadow to provide focus.
- **Interaction:** Active states for cards or inputs use a thin Neon Green (#14FF00) border glow or an increase in border opacity.

## Shapes

The shape language is **Rounded**, balancing the aggressive typography with accessible, modern container shapes.

- **Cards:** Use `rounded-lg` (16px) to create a clear container identity.
- **Buttons & Inputs:** Use `rounded-xl` (24px) for a "pill" feel that invites interaction.
- **Badges/Tags:** Small status tags (Position, Rating) use `rounded-sm` (4px) to remain distinct from larger action elements.
- **Avatars:** Player photos are always circular to provide a soft counterpoint to the rigid grid.

## Components

### Buttons
- **Primary:** Neon Green background (#14FF00), Black text (Inter Bold). Pill-shaped.
- **Secondary:** Transparent background, Neon Green border (1px), Neon Green text.
- **Ghost:** White text with no background, used for "Cancel" or "Close" actions.

### Player Cards
- **Header:** Contains Avatar, Name, and Team Logo. Includes a position badge (DL, MC, etc.) in the top right.
- **Data Grid:** Two-column layout for "VALOR" and "TENDENCIA". Positive trends include a "▲" icon in Neon Green.
- **Rating Badges:** Compact pills with a solid green background and white text for Sofascore/Titularity ratings.

### Input Fields
- Dark background (#121212), 1px border (#333333).
- On focus: Border changes to Neon Green (#14FF00).
- Text: Pure White for input, Muted Grey for placeholders.

### Chips & Badges
- Used for player positions. Each category (Forward, Midfield, Defense) should have a unique, muted pastel background to allow for instant visual categorization without competing with action colors.

### Progress Bars
- Linear bars for "Titular" percentage, using a Neon Green fill against a dark grey track.