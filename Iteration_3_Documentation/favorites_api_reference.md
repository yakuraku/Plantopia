# Favorites API Reference

All routes are prefixed with `/api/v1`. Favorites are user-scoped and identified by user email in the request body where needed.

## 1) GET /favorites — Get User Favorites
- Purpose: Return all favorite plants for a user.
- Query Parameters:
  - `email` (required): user email
- Response (200):
```json
[
  {
    "id": 12,
    "plant_id": 456,
    "plant_name": "Cherry Tomato",
    "plant_category": "vegetable",
    "notes": "Tasty",
    "priority_level": 0,
    "created_at": "2025-01-10T12:00:00"
  }
]
```

## 2) POST /favorites — Add Favorite
- Purpose: Add a plant to user's favorites (idempotent upsert by user_id + plant_id).
- Request Body:
```json
{ "email": "user@example.com", "plant_id": 456, "notes": "Tasty" }
```
- Required: `email`, `plant_id`
- Optional: `notes`
- Response (200):
```json
{
  "id": 12,
  "plant_id": 456,
  "plant_name": "Cherry Tomato",
  "plant_category": "vegetable",
  "notes": "Tasty",
  "priority_level": 0,
  "created_at": "2025-01-10T12:00:00"
}
```

## 3) DELETE /favorites/{plant_id} — Remove Favorite
- Purpose: Remove a plant from user's favorites.
- Path: `plant_id` (required)
- Query Parameters:
  - `email` (required): user email
- Response (200):
```json
{ "removed": true }
```

## 4) POST /favorites/sync — Sync Favorites
- Purpose: Merge localStorage favorites into server without removing existing entries.
- Request Body:
```json
{ "email": "user@example.com", "favorite_plant_ids": [ 1, 2, 3 ] }
```
- Response (200): returns all favorites after sync
```json
[
  {
    "id": 21,
    "plant_id": 1,
    "plant_name": "Basil",
    "plant_category": "herb",
    "notes": "Synced from localStorage",
    "priority_level": 0,
    "created_at": "2025-01-10T12:00:00"
  }
]
```

## 5) GET /favorites/check/{plant_id} — Check Favorite
- Purpose: Check whether a plant is in user's favorites.
- Path: `plant_id` (required)
- Query Parameters:
  - `email` (required): user email
- Response (200):
```json
{ "is_favorite": true }
```

---

### Errors
- 422: Validation errors (missing email/plant_id, wrong types)
- 404: Plant not found (when validating plant existence on add)
- 500: Internal errors (database issues)
