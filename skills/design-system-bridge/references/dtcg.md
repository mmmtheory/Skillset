# DTCG 2025.10 in brief

The Design Tokens Community Group format reached its first stable version, 2025.10, in October 2025. Specification: designtokens.org/tr/2025.10.

## Token shape

Every token is an object with `$value` and usually `$type`. Groups are plain objects. Names may not start with `$` or contain `{`, `}` or `.`.

```json
{
  "colors": {
    "primary": {
      "$type": "color",
      "$value": { "colorSpace": "srgb", "components": [0.102, 0.2275, 0.3216], "alpha": 1, "hex": "#1a3a52" }
    },
    "action": { "$type": "color", "$value": "{colors.primary}" }
  },
  "rounded": {
    "md": { "$type": "dimension", "$value": { "value": 8, "unit": "px" } }
  },
  "typography": {
    "body": {
      "$type": "typography",
      "$value": {
        "fontFamily": "Public Sans",
        "fontSize": { "value": 16, "unit": "px" },
        "fontWeight": 400,
        "lineHeight": 1.5,
        "letterSpacing": { "value": 0, "unit": "px" }
      }
    }
  }
}
```

## Points that trip people up

- **Colours are objects, not strings.** `colorSpace` and `components` are required. `alpha` defaults to 1. `hex` is optional and always six digits.
- **Dimensions are objects** with `value` and `unit`, where `unit` is `px` or `rem`.
- **Line height is a number**, a multiple of the font size. `24px` on a `16px` font becomes `1.5`.
- **References** use the full dotted path in braces: `{colors.primary}`.
- **Modes and themes** (light and dark) are handled by the Resolver module, or by separate files per mode. Don't invent a `$modes` key.

## How tokens.py maps DESIGN.md

| DESIGN.md | DTCG |
| --- | --- |
| `colors.primary: "#1a3a52"` | colour object with `srgb` components and `hex` |
| `rounded.md: 8px` | dimension `{ "value": 8, "unit": "px" }` |
| `spacing.scale: [4, 8, 16]` | `spacing.scale-0`, `scale-1`, `scale-2` |
| `typography.body` | composite `typography` token |
| `components.button.backgroundColor: "{colors.primary}"` | `components.button.backgroundColor` with the reference kept |

Group names stay the same in both formats, so references read the same either way.
