## 2026-01-17 - Streamlit Radio Labels & Accessibility
**Learning:** `st.radio` (and other Streamlit widgets) supports Markdown in the `label` parameter. Using this instead of a separate `st.markdown` header ensures the question is programmatically associated with the input group, significantly improving accessibility for screen readers (which otherwise hear "Choose an option" without context).
**Action:** Always check if widget labels can carry the necessary context/formatting before using separate Markdown elements. Merge them when possible.
