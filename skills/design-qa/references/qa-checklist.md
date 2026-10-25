# QA passes

Run each pass on every screen and viewport in scope. Each pass asks one question.

## 1. Layout and spacing

Does every element sit where the design puts it?

- Grid: column count, gutters and margins per breakpoint; content aligns to the same edges as the frame
- Spacing between groups versus inside them; the build often flattens these into one value
- Container widths and max widths; does content stop growing where the design says
- Alignment: baselines of adjacent text, icon centred on text, numbers right-aligned in tables
- Element order, including order for screen readers and keyboard (DOM order), not only visual order

## 2. Typography

- Font family actually loaded (check computed style and the network, not the CSS declaration; a fallback font is a common silent failure)
- Size, weight, line height and letter spacing per text style
- Text styles map to the system's named styles, not one-off values
- Truncation and wrapping: where it truncates, with what, and whether the full text is reachable
- Numerals: tabular figures in tables and amounts if the system specifies them

## 3. Colour

- Every colour comes from a token, in light and dark themes if both exist
- Text and icon contrast measured, including on hover, disabled and selected states
- Colour is never the only signal (error fields have an icon or text too)

## 4. Components

- The system component is used, not a lookalike rebuilt from divs
- Correct variant and size (secondary versus tertiary button, small versus medium input)
- Component props match the design (icon position, full width, loading state)

## 5. Content

- Copy matches the design or the copy doc word for word, including capitalisation and punctuation
- Placeholder or lorem text left in, test data, developer strings
- Number, date and currency formats match the locale

## 6. Icons and images

- Right icon from the system set, right size, aligned to the text
- Images: aspect ratio, cropping, focal point, resolution on high-density screens, alt text
- Empty and failed image states

## 7. States

For each component and screen, render: default, hover, focus, active or pressed, disabled, loading, empty, error, success, selected, and read-only where relevant. Then the content states: one item, many items, very long text, missing optional data. A state that was designed but never rendered in QA is unchecked, not passed.

## 8. Interaction

- Keyboard: every action reachable with Tab, Enter and Space; focus order follows reading order; focus is visible; Escape closes overlays and returns focus to the trigger
- Pointer targets at least 24 by 24 px (44 by 44 recommended on touch)
- Forms: validation timing, error placement, what happens to entered data on error
- Destructive actions: confirmation or undo as designed
- Links and buttons go where the design says

## 9. Motion

- Duration and easing match the system's motion tokens
- Nothing animates layout in a way that shifts content under the pointer
- `prefers-reduced-motion` respected

## 10. Responsive

- Every breakpoint the design defines, plus the widths between them (a layout that works at 768 and 1024 can break at 900)
- 320 px width without horizontal scrolling
- Zoom to 200 percent; text spacing increased
- Touch versus pointer differences (hover-only affordances on touch screens)

## 11. Accessibility basics

Not a full audit, but QA should catch: missing labels, images without alt text, headings out of order, buttons built from non-button elements, focus traps, and contrast failures. Cite the WCAG 2.2 criterion when you report one.
