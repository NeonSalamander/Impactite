# Connecting an LLM to Impactite's LadybugDB Database

Impactite uses LadybugDB as its underlying database for storing tag indices, form records, and favorites. The database file is stored at `.ladybug_index.lbug` in the notes directory.

This document explains how to connect an LLM (Language Model) to this database to enable querying and potentially updating the knowledge base.

## Overview

The Impactite application provides a `TagIndex` class (in `src/impactite/core.py`) that manages the LadybugDB connection and provides methods for common operations. We have extended this class with a `run_read_cypher` method to allow executing read-only Cypher queries.

There are two main approaches to connect an LLM to the database:

1. **Direct Database Access**: Connect directly to the LadybugDB file using the LadybugDB driver.
2. **Via the TagIndex Class**: Use the existing `TagIndex` instance (or create one) to run queries through its `run_read_cypher` method.

## Approach 1: Using the TagIndex Class (Recommended)

If you have access to the Impactite codebase, you can create a `TagIndex` instance and use its `run_read_cypher` method.

### Example Usage

```python
from impactite.core import TagIndex
from pathlib import Path

# Initialize the TagIndex with the path to your notes directory
notes_dir = Path("/path/to/your/notes")
tag_index = TagIndex(notes_dir)

# Now you can run read-only Cypher queries
query = """
MATCH (t:Tag)-[r:HAS_TAG_FRONTMatter|HAS_TAG_BODY]-(f:File)
RETURN t.name AS tag, collect(f.path) AS files
ORDER BY tag
"""
results = tag_index.run_read_cypher(query)

# Process the results
for row in results:
    print(f"Tag: {row['tag']}")
    for file_path in row['files']:
        print(f"  - {file_path}")
```

### Available Methods in TagIndex

Besides `run_read_cypher`, the `TagIndex` class provides several useful methods:

- `get_tag_files()`: Returns a dictionary mapping tag names to lists of file paths.
- `get_tag_counts()`: Returns a dictionary mapping tag names to the number of files associated with each tag.
- `get_tag_colors()`: Returns a dictionary mapping tag names to their deterministic colors.
- `get_form_records(catalog=None)`: Returns form records, optionally filtered by catalog.
- `is_favorite(file_path)`: Checks if a file is marked as a favorite.
- `get_favorites()`: Returns a list of favorite file paths.

These methods can be used directly for common operations without writing Cypher queries.

## Approach 2: Direct LadybugDB Connection

You can also connect directly to the LadybugDB file using the official LadybugDB driver.

### Example Usage

```python
from ladybug import Database
from pathlib import Path

# Path to the database file
db_path = Path("/path/to/your/notes/.ladybug_index.lbug")

# Create a database connection
db = Database(str(db_path))

# Now you can execute Cypher queries
query = """
MATCH (t:Tag)
WHERE t.name STARTS WITH 'py'
RETURN t.name AS tag, t.color AS color
ORDER BY tag
"""
result = db.execute(query)

# Process the result
while result.has_next():
    row = result.get_next()
    print(f"Tag: {row[0]}, Color: {row[1]}")

# Don't forget to close the connection when done
db.close()
```

### Important Notes

1. **Read-Only vs Write Operations**: 
   - For read-only operations, either approach is safe.
   - For write operations, exercise caution as concurrent writes from the Impactite application and your LLM agent could lead to conflicts.
   - It is generally recommended to perform only read operations via direct database access while the Impactite application is running.

2. **Database Schema**:
   - **Nodes**:
     - `(t:Tag)`: Represents a tag with properties `name` and `color`.
     - `(f:File)`: Represents a markdown file with properties `path` and `mtime`.
     - `(fr:Favorite)`: Represents a favorite file with property `file_path`.
     - `(fr:FormRecord)`: Represents a form record with properties `file_path`, `catalog`, `data` (as JSON), and `created_at`.
   - **Relationships**:
     - `(f)-[:HAS_TAG_FRONTMatter]->(t)`: Tag extracted from frontmatter.
     - `(f)-[:HAS_TAG_BODY]->(t)`: Tag extracted from the body of the file.
     - `(f)-[:IS_FAVORITE]->(fr:Favorite)`: Favorite relationship.
     - `(f)-[:RECORD_FROM_FILE]->(fr:FormRecord)`: Form record relationship.

3. **Deterministic Tag Colors**:
   - Tag colors are generated deterministically from the tag name using the same algorithm in both the original SQLite implementation and the LadybugDB version.
   - The algorithm is available in the `_generate_deterministic_color` method of the `TagIndex` class.

## Security Considerations

- The `run_read_cypher` method does not validate that the query is read-only. It is the caller's responsibility to ensure that the query does not modify the database.
- Avoid executing untrusted Cypher queries directly. If you need to allow user-provided queries, consider implementing a query validator or using a whitelist of allowed operations.

## Performance Tips

- For frequent queries, consider caching results if the underlying data doesn't change often.
- Use appropriate Cypher query patterns to leverage LadybugDB's indexing (though note that the current implementation does not create explicit indexes beyond the implicit ones from the node and relationship patterns).

## Example Queries for an LLM

Here are some example Cypher queries that an LLM might find useful:

### Get all tags and their associated files
```cypher
MATCH (t:Tag)-[r:HAS_TAG_FRONTMatter|HAS_TAG_BODY]-(f:File)
RETURN t.name AS tag, collect(f.path) AS files
ORDER BY tag
```

### Get files that contain a specific tag
```cypher
MATCH (t:Tag {name: $tag_name})<-[r:HAS_TAG_FRONTMatter|HAS_TAG_BODY]-(f:File)
RETURN f.path AS file
ORDER BY f.path
```

### Get the count of files per tag
```cypher
MATCH (t:Tag)-[r:HAS_TAG_FRONTMatter|HAS_TAG_BODY]-(f:File)
RETURN t.name AS tag, count(DISTINCT f) AS file_count
ORDER BY file_count DESC
```

### Get all form records in a specific catalog
```cypher
MATCH (fr:FormRecord {catalog: $catalog})
RETURN fr.file_path AS file, fr.data AS data, fr.created_at AS created_at
ORDER BY fr.created_at DESC
```

### Get all favorite files
```cypher
MATCH (f:File)-[:IS_FAVORITE]->(:Favorite)
RETURN f.path AS file
ORDER BY f.path
```

### Search for tags by name pattern
```cypher
MATCH (t:Tag)
WHERE t.name CONTAINS $search_term
RETURN t.name AS tag, t.color AS color
ORDER BY t.name
```

## Integration with LLM Agents

When integrating with an LLM agent (like those in the pi agent framework), you can:

1. Provide the `TagIndex.run_read_cypher` method as a tool that the LLM can call.
2. Create a natural language interface that converts user questions into Cypher queries (using prompt engineering or a dedicated query generation component).
3. Use the results to inform the LLM's responses or to trigger further actions.

## Conclusion

By exposing the `run_read_cypher` method (or using direct database access), you can enable LLMs to query Impactite's knowledge base, opening up possibilities for intelligent note exploration, automated tagging, content recommendations, and more.

For write operations, consider using the Impactite application's existing API (via the `TagIndex` class methods) to ensure data consistency and avoid conflicts.