# Checks

## Accessibility thresholds (WCAG 2.2, level AA)

| Check | Threshold | Criterion |
| --- | --- | --- |
| Text contrast | 4.5:1, or 3:1 for large text (24 px regular, or 18.66 px bold and up) | 1.4.3 |
| Non-text contrast: control borders, icons, focus rings, chart marks | 3:1 against adjacent colours | 1.4.11 |
| Colour as the only signal | Never; pair it with text, shape or position | 1.4.1 |
| Focus visible | Every interactive element shows a visible focus state | 2.4.7 |
| Focus not obscured | Focused element not fully hidden by sticky headers, banners or overlays | 2.4.11 |
| Target size | At least 24 by 24 CSS px, or enough spacing around smaller targets | 2.5.8 |
| Reflow | Usable at 320 CSS px wide without horizontal scrolling | 1.4.10 |
| Text spacing | Layout survives larger line, letter and word spacing | 1.4.12 |
| Labels | Every input has a visible label; placeholder text is not a label | 3.3.2 |
| Errors | Error identified in text, near the field, with how to fix it | 3.3.1, 3.3.3 |
| Redundant entry | Do not make people re-enter information already given in the same process | 3.3.7 |
| Accessible authentication | No memory or puzzle test to sign in without an alternative | 3.3.8 |
| Motion | Respect reduced motion; nothing flashes more than three times a second | 2.3.1, 2.3.3 |

Recommended beyond the minimum: 44 by 44 px touch targets, 16 px body text on web, line length 45 to 80 characters.

## State checklist

For each screen, ask which of these apply and whether the design covers them:

- **Empty**: first use, no results, cleared filters. Does it explain and offer a next step?
- **Loading**: initial load, slow network, partial results. Does layout hold steady?
- **Error**: validation, server failure, timeout, permission denied. Does it say what happened and what to do?
- **Partial or degraded**: some data missing, offline, stale data.
- **Overflow**: long names, long numbers, many items, translated text 30 to 40 percent longer.
- **Quantity**: zero, one, many, too many.
- **First run and returning**: what changes after the first visit?
- **Destructive actions**: confirmation or undo, and what is lost.
- **Success**: does the user know it worked, and what happens next?

## Signs of generic AI-generated design

Not failures in themselves, but each one is worth asking "was this chosen for this product?":

- a centred hero with a gradient headline and two buttons, followed by three equal cards with icons
- purple to blue gradients with no link to the brand
- glass effects, glows or heavy shadows on everything
- emoji standing in for icons
- one typeface at one weight with hierarchy carried only by size
- copy that could belong to any product ("Unlock your potential", "Built for the future")
- uniform radius and spacing everywhere, with no grouping

If several appear together, say the design reads as templated and point to the decisions that would make it specific to this product.
