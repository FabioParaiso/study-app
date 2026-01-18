## 2025-02-19 - String Concatenation Optimization
**Learning:** Python string concatenation (`+=`) in a loop is $O(N^2)$ because strings are immutable. For PDF text extraction with `pypdf`, this caused noticeable overhead (90%+ slower in benchmarks compared to `list.join`) when processing many pages.
**Action:** Always use `list.append()` and `"".join(list)` for accumulating text in loops.
