## 2025-02-17 - Accessible Icon Buttons
**Learning:** Icon-only buttons (e.g., microphone, TTS) are invisible to screen readers without labels, creating a major accessibility gap in interactive apps.
**Action:** Always add state-aware `aria-label` attributes to icon-only buttons (e.g., "Parar leitura" vs "Ler pergunta").

## 2025-05-21 - Visibility on Focus
**Learning:** Interactive elements that are hidden by default (e.g., show on hover) create "ghost focus" traps for keyboard users who tab to them but see nothing.
**Action:** Always add `focus:opacity-100` (or equivalent) to elements that use `group-hover:opacity-100`, ensuring they become visible when focused.
