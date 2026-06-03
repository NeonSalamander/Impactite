---
type: form
destination: note
catalog: reviews
fields:
  - book: ["Book", string, 80]
  - reviewer: ["Reviewer", string, 40]
  - rating: ["Rating (1-5)", list, select, [1, 2, 3, 4, 5]]
  - recommend: ["Recommend", boolean, 0]
  - mood: ["Mood", list, multi-select, [inspiring, sad, fun, thought-provoking]]
  - comment: ["Comment", text, 0]
---

<!--
This is a form (type: form) that saves data to the DATABASE.

destination: database -> saving appends a record to the form_records table
                         inside .tag_index.db (the same DB as the tag index).
catalog: reviews      -> the catalog label of the record; you can filter
                         queries by it:  FROM database/reviews

Fill in the form in view mode and press "Save" — then open queries_database.md
to see the record in the query results.
-->
