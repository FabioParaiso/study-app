## 2026-01-17 - Streamlit Radio Labels & Accessibility
**Learning:** `st.radio` (and other Streamlit widgets) supports Markdown in the `label` parameter. Using this instead of a separate `st.markdown` header ensures the question is programmatically associated with the input group, significantly improving accessibility for screen readers (which otherwise hear "Choose an option" without context).
**Action:** Always check if widget labels can carry the necessary context/formatting before using separate Markdown elements. Merge them when possible.

## 2026-02-17 - Icon-Only Buttons and Hidden Inputs
**Learning:** The React frontend heavily relies on icon-only buttons (using `lucide-react`) and hidden file inputs for custom styling. These elements were completely invisible to screen readers, lacking `aria-label` or `title`.
**Action:** Always verify `aria-label` is present on `button` elements that contain only icons. Ensure hidden `input` elements have accessible names via `aria-label` or linked labels.
