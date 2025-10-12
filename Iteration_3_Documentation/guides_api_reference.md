# Guides API Reference

All routes are prefixed with `/api/v1/guides` unless noted. This reference covers listing guides, retrieving content, and managing guide favorites.

## 1) GET /guides — List All Guides
- Purpose: Return all available guides grouped by category.
- Params: none
- Response (200):
```json
{
  "categories": ["grow_guide", "pests-diseases"],
  "guides": [
    { "title": "Composting Basics", "category": "grow_guide", "name": "Composting Basics.md", "path": "grow_guide/Composting Basics.md" }
  ]
}
```

## 2) GET /guides/categories — List Categories
- Purpose: Return list of all guide categories.
- Response (200):
```json
{ "categories": ["grow_guide", "pests-diseases", "informational"] }
```

## 3) GET /guides/{category} — List Guides By Category
- Purpose: Return guides within a specific category.
- Path: `category` (required)
- Response (200):
```json
{
  "category": "grow_guide",
  "guides": [
    { "title": "Basil Growing Guide", "name": "Basil Growing Guide.md", "path": "grow_guide/Basil Growing Guide.md" }
  ]
}
```

## 4) GET /guides/{category}/{guide_name} — Get Guide Content
- Purpose: Return full markdown content for a specific guide.
- Path: `category`, `guide_name` (required)
- Response (200):
```json
{
  "title": "Basil Growing Guide",
  "category": "grow_guide",
  "name": "Basil Growing Guide.md",
  "content": "# Basil...",
  "path": "grow_guide/Basil Growing Guide.md"
}
```

## 5) POST /guides/favorites — Add Guide To Favorites
- Purpose: Add a guide to a user's favorites (idempotent).
- Request Body:
```json
{ "email": "user@example.com", "guide_name": "Basil Growing Guide.md", "category": "grow_guide", "notes": "Useful" }
```
- Required: `email`, `guide_name`
- Optional: `category`, `notes`
- Response (201):
```json
{
  "id": 10,
  "guide_name": "Basil Growing Guide.md",
  "category": "grow_guide",
  "notes": "Useful",
  "created_at": "2025-01-10T12:00:00"
}
```

## 6) DELETE /guides/favorites/{guide_name} — Remove Guide From Favorites
- Purpose: Remove a guide from user's favorites.
- Path: `guide_name` (required)
- Query: `email` (required)
- Response (200):
```json
{ "removed": true }
```

## 7) GET /guides/favorites/user — Get User Guide Favorites
- Purpose: List user's guide favorites with enriched metadata.
- Query: `email` (required)
- Response (200):
```json
{
  "favorites": [
    { "id": 10, "guide_name": "Basil Growing Guide.md", "category": "grow_guide", "notes": "Useful", "created_at": "2025-01-10T12:00:00" }
  ]
}
```

## 8) GET /guides/favorites/check/{guide_name} — Check Favorite Status
- Purpose: Check whether a specific guide is favorited by the user.
- Path: `guide_name` (required)
- Query: `email` (required)
- Response (200):
```json
{ "is_favorite": true }
```

---

### Errors
- 422: Validation errors (missing email/guide_name, wrong types)
- 404: User or guide/favorite not found
- 400: Duplicate favorite when adding
- 500: Internal server error
