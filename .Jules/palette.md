## 2025-02-17 - Accessible Icon Buttons
**Learning:** Icon-only buttons (e.g., microphone, TTS) are invisible to screen readers without labels, creating a major accessibility gap in interactive apps.
**Action:** Always add state-aware `aria-label` attributes to icon-only buttons (e.g., "Parar leitura" vs "Ler pergunta").

## 2025-02-17 - Accessible Icon Button Pattern
**Learning:** Icon-only buttons benefit from both `aria-label` (for screen readers) and `title` (for mouse hover tooltips), ensuring coverage for different user types without custom CSS tooltips.
**Action:** Add both attributes to future icon-only buttons.
