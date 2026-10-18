# Raw Content

This folder holds raw source content from Jay and Chetna before it is processed into publishable formats.

## Structure

```
raw-content/
├── jay/        ← Jay's raw files (Excel, Word, text, images)
└── chetna/     ← Chetna's raw files
```

## What goes here

Drop any file in the correct owner subfolder:

- Excel spreadsheets with goal, habit, or lesson data
- Word documents with narrative drafts
- Plain text outlines
- Images (before illustration/formatting)
- Any other raw input format

## What happens next

JP-ContentLoader1 processes Jay's files → publishes to `goals-habits/` and `learning/`
CP-ContentLoader2 processes Chetna's files → same targets

Processed output lives in:
- `goals-habits/` — goal and habit content files
- `learning/` — lesson content files
- `links/` — goal-to-lesson mapping

Raw files are never deleted — they form the audit trail from source to published content.
