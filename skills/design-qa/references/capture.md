# Capturing the build and the design

## The design

With the Figma MCP server connected:

- `get_screenshot` on the frame's node for the picture
- `get_design_context` on the node for layout, spacing and component names
- `get_variable_defs` for the variables (tokens) the frame uses

Take the node ID from the Figma URL (`node-id=12-345` becomes `12:345`). Without a connected tool, ask for an exported PNG of each frame and the token file.

## The build

Any browser tool works. With Playwright available:

```python
from playwright.sync_api import sync_playwright

WIDTHS = [390, 768, 1440]
with sync_playwright() as p:
    browser = p.chromium.launch()
    for width in WIDTHS:
        page = browser.new_page(viewport={"width": width, "height": 900})
        page.goto("http://localhost:3000/checkout")
        page.screenshot(path=f"qa/checkout-{width}.png", full_page=True)
    browser.close()
```

To render states, drive the page into them: hover and focus elements (`page.hover`, `page.focus`), submit an empty form, block a request with `page.route` to force the error state, or pass mock data that is empty or very long.

Read computed values instead of guessing:

```javascript
const el = document.querySelector('.card');
const s = getComputedStyle(el);
[s.paddingTop, s.gap, s.fontSize, s.fontFamily, s.color, s.borderRadius];
```

## Side by side

When you have both pictures, compare them at the same width and scale. Note where the frame was drawn at a width the build does not use, and compare at the nearest breakpoint. Keep the screenshot paths in the punch list so the developer can see each issue.
