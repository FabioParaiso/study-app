## 2026-01-17 - Streamlit Radio Labels & Accessibility
**Learning:** `st.radio` (and other Streamlit widgets) supports Markdown in the `label` parameter. Using this instead of a separate `st.markdown` header ensures the question is programmatically associated with the input group, significantly improving accessibility for screen readers (which otherwise hear "Choose an option" without context).
**Action:** Always check if widget labels can carry the necessary context/formatting before using separate Markdown elements. Merge them when possible.

## 2025-02-18 - Hidden File Input Focus
**Learning:** Hidden file inputs (`opacity: 0`) used for "drag and drop" zones often break keyboard accessibility because the default focus ring becomes invisible.
**Action:** When creating custom file upload components with hidden inputs, always apply `focus-within` styles to the visible parent container to ensure keyboard users receive visual feedback.
