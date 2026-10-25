# DESIGN.md format

This follows the shape of Google's DESIGN.md specification, which is still in alpha. Check the current spec at github.com/google-labs-code/design.md when something here looks out of date.

## Front matter

```yaml
---
name: Acme
colors:
  primary: "#1a3a52"
  on-primary: "#ffffff"
  surface: "#f7f3ec"
  ink: "#141414"
  muted: "#5c5c58"
typography:
  display:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 52px
    letterSpacing: -0.02em
  body:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
rounded:
  sm: 4px
  md: 8px
  full: 999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "#24506f"
---
```

Rules:

- Five token categories: `colors`, `typography`, `rounded`, `spacing`, `components`. Other top-level keys are allowed but most tools ignore them.
- Colours as CSS colour strings. Hex is safest.
- Dimensions with units (`8px`, `1rem`).
- Components map properties (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`) to literal values or references written `{category.token}`.
- States are separate entries with related names: `button-primary-hover`, `button-primary-disabled`.
- Keep the team's token names. Name colours by role (`surface`, `on-primary`) where the team does; don't rename `brand-blue` to `primary` without asking.

## Body sections

In this order, as `##` headings:

1. **Overview.** What the product is, who uses it, and the feel in two or three sentences.
2. **Colors.** The role of each colour, which pairs are allowed for text, and what never to combine.
3. **Typography.** Which style for which job, maximum line length, how hierarchy is built.
4. **Layout.** Grid, breakpoints, how spacing tokens are used (gaps between groups versus inside them).
5. **Elevation & Depth.** Shadows or borders, what is raised and why.
6. **Shapes.** Radius scale and where each step applies.
7. **Components.** Which component for which job, required states, and what not to build from scratch.
8. **Do's and Don'ts.** Mistakes this system keeps seeing, written as specific instructions. Proposals for missing tokens go here, clearly marked.

## Writing the body

- Lead each section with the rule, then the reason.
- Prefer instructions an agent can follow ("Use `muted` only for secondary text on `surface`") over descriptions ("Our palette is calm").
- Mark anything not read from a source as *Inferred*.
- State what is undefined. "No elevation tokens. Use a 1px `muted` border to separate surfaces" is more useful than silence.
