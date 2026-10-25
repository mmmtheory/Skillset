---
name: Tally
colors:
  primary: "#1a3a52"
  primary-hover: "#24506f"
  on-primary: "#ffffff"
  surface: "#f7f3ec"
  ink: "#141414"
  muted: "#5c5c58"
  border: "#d9d4ca"
typography:
  title:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: 600
    lineHeight: 32px
  body:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
rounded:
  md: 8px
  lg: 12px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
---

## Overview
Tally is invoicing for sole traders. Calm, exact, no decoration.

## Colors
Use `ink` for primary text and `muted` for secondary text, both on `surface`. Buttons use `primary` with `on-primary` text and `primary-hover` on hover.

## Typography
Public Sans only. `title` for card headings, `body` for everything else.

## Layout
Breakpoints: 390 px (one column), 768 px (two columns), 1280 px (three columns). Gaps between cards use `lg`. Padding inside cards uses `lg`.

## Components
Primary button: full width in cards, `rounded.md`, padding `sm` vertical and `md` horizontal. Required states: hover (`primary-hover`), focus (2 px `ink` outline, 2 px offset), disabled (40% opacity, not clickable). Cards: `surface` background, 1 px `border` border, `rounded.lg`.
