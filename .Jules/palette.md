## 2025-02-17 - Accessible Icon Buttons
**Learning:** Icon-only buttons (e.g., microphone, TTS) are invisible to screen readers without labels, creating a major accessibility gap in interactive apps.
**Action:** Always add state-aware `aria-label` attributes to icon-only buttons (e.g., "Parar leitura" vs "Ler pergunta").

## 2025-02-18 - Terminology Consistency
**Learning:** Screen reader users benefit when `aria-label` terminology exactly matches visual labels/placeholders (e.g., "Chave de Acesso" instead of generic "Palavra-passe").
**Action:** Verify placeholders and nearby text before defining ARIA labels.
