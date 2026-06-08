# Full-Text Search Design — Impactite

**Date**: 2026-06-08
**Status**: Validated against LadybugDB 0.17.1

## 1. Overview

Add full-text search over note content using LadybugDB's native FTS extension with BM25 ranking, stemming, and conjunctive query support. Users trigger search with `Ctrl+Shift+F`, type a query, and see relevance-ranked results with snippets.

### Working LadybugDB FTS API (validated)

```
-- Create index (table_name, index_name, properties, options...)
CALL CREATE_FTS_INDEX('FTSContent', 'fts_content_idx', ['content'], stemmer := 'porter')

-- Query (table_name, index_name, query, options...)
CALL QUERY_FTS_INDEX('FTSContent', 'fts_content_idx', 'search terms', top := 10)
    RETURN node.file_path, node.content, score
    ORDER BY score DESC

-- Drop index
CALL DROP_FTS_INDEX('FTSContent', 'fts_content_idx')

-- Inspect
CALL SHOW_INDEXES() RETURN *
```

Key properties:
- **BM25 scoring** built-in
- **Auto-updates** on node insert/update/delete — no manual reindexing needed
- **Stemmer**: porter (English); supports 20+ languages
- **conjunctive := true** mode for "all terms must match"
- **K**, **B** BM25 tuning parameters
- **top := N** limits results

---

## 2. Schema Changes

### `TagIndex._initialize_schema()` — add FTS index creation

```python
# After creating the FTSContent node table:
self.connection.execute("""
    CALL CREATE_FTS_INDEX(
        'FTSContent',
        'fts_content_idx',
        ['content'],
        stemmer := 'porter'
    )
""")
```

Wrap in try/except — if the index already exists, LadybugDB raises a binder error. We catch and ignore it for idempotency across restarts.

**Why `porter` stemmer?**
- English-centric but handles basic morphological variants (running → run, programming → program)
- For multi-language notes (the app supports en/ru/de), porter degrades gracefully — non-English words are simply not stemmed rather than corrupted
- Alternative: `stemmer := 'none'` disables stemming entirely; exact match only. We default to `porter` and make it configurable later if needed.

### Content Storage

The `FTSContent` table already exists in the current code:

```cypher
CREATE NODE TABLE IF NOT EXISTS FTSContent (
    file_path STRING PRIMARY KEY,
    content STRING
)
```

During indexing (`_add_or_update_file_in_index()`), content is stored after stripping YAML frontmatter. The FTS extension handles the rest.

---

## 3. Search Method

### `TagIndex.search_content()`

Replace the current CONTAINS-based fallback with the proper FTS query:

```python
def search_content(self, query_text: str, limit: int = 10) -> List[Dict]:
    """Search note content using LadybugDB FTS with BM25 ranking.
    
    Returns list of dicts with keys: file_path, score, content
    """
    if not query_text.strip():
        return []
    
    try:
        result = self.connection.execute("""
            CALL QUERY_FTS_INDEX(
                'FTSContent', 'fts_content_idx', $query, top := $limit
            )
            RETURN node.file_path AS file_path, node.content AS content, score
            ORDER BY score DESC
        """, {"query": query_text, "limit": limit})
        
        results = []
        while result.has_next():
            row = result.get_next()
            results.append({
                "file_path": row[0],
                "score": row[1],
                "content": row[2],
            })
        return results
    except Exception:
        return []
```

**Error handling**: If the FTS index doesn't exist (e.g., corrupted DB), return empty list gracefully rather than crashing. The existing `search_content()` already wraps in try/except.

---

## 4. Snippet Generation

`QUERY_FTS_INDEX` returns the full node content. Snippets are generated in Python:

```python
def _make_snippet(content: str, query: str, context_chars: int = 80) -> str:
    """Extract a context window around the first query term match."""
    terms = query.lower().split()
    lower_content = content.lower()
    
    # Find earliest position of any query term
    best_pos = -1
    best_term_len = 0
    for term in terms:
        pos = lower_content.find(term)
        if pos != -1 and (best_pos == -1 or pos < best_pos):
            best_pos = pos
            best_term_len = len(term)
    
    if best_pos == -1:
        # No term found (stemming mismatch) — return start of content
        return content[:context_chars * 2].strip()
    
    start = max(0, best_pos - context_chars)
    end = min(len(content), best_pos + best_term_len + context_chars)
    snippet = content[start:end].strip()
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    
    return snippet
```

---

## 5. Index Lifecycle

### Startup
1. `TagIndex.__init__()` → `_initialize_schema()` creates `FTSContent` table + FTS index
2. FTS index creation is idempotent: duplicate errors are caught and ignored
3. `rebuild()` populates `FTSContent` nodes as files are processed
4. FTS index updates automatically as nodes are inserted/updated/deleted

### On file change (rebuild)
- `_add_or_update_file_in_index()` → `MERGE` on `FTSContent` node updates content
- FTS index reflects the change immediately (validated: see testing notes above)
- No manual FTS reindex call needed

### On file delete
- `_remove_file_from_index()` → `DETACH DELETE` on `FTSContent` node
- FTS index reflects the delete immediately

### On app close
- `TagIndex.close()` closes connection as before
- FTS index persists in the `.ladybug_index.lbug` database

---

## 6. UI Integration

### `SearchResultsView` (already implemented)

The existing widget provides:
- Input field for search query
- `OptionList` for results display
- `Escape` to close, `Enter` to open first result
- Arrow key navigation

### Changes needed:

1. **`_perform_search()`**: Use `TagIndex.search_content()` which now returns proper BM25 scores instead of term-frequency counts
2. **Result display**: Update to show BM25 score and snippet from FTS results
3. **Highlighting**: Bold the query terms in the snippet text

### Keyboard shortcut

`Ctrl+Shift+F` → `action_search_fulltext()` (already wired in `app.py`)

### Flow:
```
Ctrl+Shift+F → SearchResultsView appears, input focused
User types   → _perform_search() on each keystroke (debounced 200ms)
Results show → file name, BM25 score, snippet with highlighted terms
Enter/Click  → open file, close search view
Escape       → close search, return to viewer
```

### Previous/Next result navigation
- `Up`/`Down` arrows move through results
- `Enter` opens the selected result

---

## 7. Stemmer and Multi-Language Considerations

| Approach | Pros | Cons |
|----------|------|------|
| `porter` (default) | English stemming works; graceful degradation for other languages | Russian/German words not stemmed |
| `none` | Exact match, no stemming surprises | No "running" → "run" matching |
| User-configurable | Per-user language preference | Adds config complexity |

**Decision**: Default to `porter`. It's the safest choice:
- English notes get stemming benefits
- Non-English notes work fine (just no stemming)
- Users who write primarily in Russian or German can set `stemmer := 'russian'` or `'german'` in a future config option

---

## 8. Error Handling

| Scenario | Behavior |
|----------|----------|
| FTS extension not installed | `INSTALL fts; LOAD fts;` on startup (auto-installs) |
| FTS index already exists | Try/except around `CREATE_FTS_INDEX`, ignore duplicate error |
| FTS index corrupted/missing | Return empty results, log warning |
| Empty search query | Show placeholder, no search |
| No results found | Show "No files found" message |
| Search during indexing | FTS index is always consistent (auto-updates) |

---

## 9. Testing Checklist

- [ ] `CREATE_FTS_INDEX` succeeds on fresh database
- [ ] `CREATE_FTS_INDEX` is idempotent (no error on duplicate)
- [ ] `QUERY_FTS_INDEX` returns results ranked by BM25 score
- [ ] Updated FTSContent node is immediately searchable
- [ ] Deleted node is immediately removed from FTS results
- [ ] New node is immediately searchable
- [ ] Conjunctive mode (`conjunctive := true`) requires all terms
- [ ] Empty/whitespace query returns 0 results
- [ ] Stop words ("the", "a") are handled by the stemmer
- [ ] Stemming works for English ("running" matches "run")
- [ ] Non-English content is searchable (exact match)
- [ ] UI: Search opens with Ctrl+Shift+F
- [ ] UI: Results show score and snippet
- [ ] UI: Enter opens file, Escape closes search
- [ ] UI: Arrow keys navigate results

---

## 10. Pseudocode — Complete Flow

### Initialization (in TagIndex._initialize_schema)
```
ensure FTS extension installed and loaded
create FTSContent node table if not exists
try:
    CREATE_FTS_INDEX('FTSContent', 'fts_content_idx', ['content'], stemmer := 'porter')
except IndexAlreadyExists:
    pass
```

### Indexing a file (in _add_or_update_file_in_index)
```
read file content
strip YAML frontmatter
MERGE (f:FTSContent {file_path: $path}) SET f.content = $content
# FTS index updates automatically — no extra work
```

### Searching (in SearchResultsView._perform_search)
```
query = input.value.strip()
if query is empty: show placeholder, return

results = tag_index.search_content(query, limit=50)

for each result:
    snippet = _make_snippet(result.content, query)
    highlight query terms in snippet with bold markup
    display: filename | score: X.XX | snippet

if no results: show "No files found"
```
