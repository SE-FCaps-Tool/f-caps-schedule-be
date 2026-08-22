## 2026-08-22 — Bilingual project titles

- Added nullable `projects.title_vi` and `projects.title_en` in migration
  `0038_project_bilingual_titles`; existing `title` remains as a compatibility
  fallback. Existing Excel staging rows are used for backfill when linked.
- Updated Excel importers, seed loader, project CRUD/import routes, group
  listings, leader dashboard, lecturer supervised-projects, and reports to
  preserve both values and prefer English for the primary display value.
- FE now displays English when available and uses the native browser tooltip
  to reveal the Vietnamese title. Vietnamese remains the fallback when English
  is empty.
- Verification: Python syntax/targeted Ruff checks pass; focused BE tests
  pass (17 tests); FE TypeScript, ESLint, and production build pass. The live
  database migration was intentionally not applied in this session.
