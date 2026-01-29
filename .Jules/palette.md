## 2025-02-17 - Accessible Icon Buttons
**Learning:** Icon-only buttons (e.g., microphone, TTS) are invisible to screen readers without labels, creating a major accessibility gap in interactive apps.
**Action:** Always add state-aware `aria-label` attributes to icon-only buttons (e.g., "Parar leitura" vs "Ler pergunta").

## 2025-02-18 - Nested Interactive Controls
**Learning:** Placing a delete button inside a clickable list item (`<button>...<button>`) creates invalid HTML and strict mode violations in testing tools like Playwright.
**Action:** Use a layout where the primary action (select) and secondary action (delete) are siblings, or apply `role="button"` to the content container instead of the parent wrapper.
