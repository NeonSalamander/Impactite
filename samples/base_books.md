---
type: base
query: |
  FROM notes/books
  SELECT title, author, genre, year, pages, rating, tags
  ORDER BY year
filters:
  - title: [string]
  - genre: [multi-select, [sci-fi, fantasy, dystopia, tech]]
  - year: [integer]
  - tags: [multi-select, tags]
---

# Books base view

This is a base note with filters and query results.
