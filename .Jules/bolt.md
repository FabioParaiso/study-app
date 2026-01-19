# Bolt's Journal

## 2024-05-22 - [Optimizing Topic Extraction]
**Learning:** String manipulation in loops can be optimized by combining operations. While `re.sub` is cleaner, ` " ".join(line.split())` proved faster for simple whitespace normalization in this Python version. Combining cleaning and processing loops (Loop Fusion) reduces memory overhead.
**Action:** Fuse loops where possible to avoid intermediate lists. Use `list(dict.fromkeys(x))` for fast, order-preserving deduplication.
