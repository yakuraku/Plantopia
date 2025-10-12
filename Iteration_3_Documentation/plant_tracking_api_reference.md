# Plant Tracking API Reference

This document summarizes all endpoints under the plant-tracking feature, including purpose, required/optional parameters, and typical responses. All routes are prefixed with `/api/v1`.

## 1) POST /tracking/start — Start Plant Tracking
- Purpose: Create a user plant instance, generate growth data on first use, and initialize tracking.
- Request Body:
```json
{
  "user_data": {
    "email": "user@example.com",
    "name": "John Doe",
    "suburb_id": 123,
    "experience_level": "beginner",
    "garden_type": "balcony",
    "available_space": 5.0,
    "climate_goal": "sustainable gardening"
  },
  "plant_id": 456,
  "plant_nickname": "My First Tomato",
  "start_date": "2024-03-15",
  "location_details": "Balcony - South side"
}
```
- Required: `user_data`, `user_data.email`, `user_data.name`, `user_data.suburb_id`, `plant_id`, `plant_nickname`, `start_date`
- Optional: `location_details`; profile fields in `user_data` are optional but recommended
- Response (201):
```json
{
  "instance_id": 789,
  "plant_nickname": "My First Tomato",
  "start_date": "2024-03-15",
  "expected_maturity_date": "2024-07-13",
  "current_stage": "germination",
  "message": "Plant tracking started successfully"
}
```

## 2) GET /tracking/user/{email} — Get User Plant Instances
- Purpose: List a user's plant instances with pagination and summary fields.
- Query: `active_only` (default true), `page` (default 1), `limit` (default 20)
- Response (200):
```json
{
  "plants": [
    {
      "instance_id": 789,
      "plant_id": 456,
      "plant_name": "Cherry Tomato",
      "plant_nickname": "My First Tomato",
      "start_date": "2024-03-15",
      "expected_maturity_date": "2024-07-13",
      "current_stage": "flowering",
      "days_elapsed": 45,
      "progress_percentage": 60,
      "location_details": "Balcony - South side",
      "image_url": "https://storage.googleapis.com/plantopia/tomato.jpg"
    }
  ],
  "total_count": 3,
  "active_count": 2,
  "pagination": { "page": 1, "limit": 20, "total_pages": 1 }
}
```

## 3) GET /tracking/instance/{instance_id} — Get Plant Instance Details
- Purpose: Full details for a plant instance, including timeline and current tips.
- Response (200):
```json
{
  "instance_id": 789,
  "plant_details": {
    "plant_id": 456,
    "plant_name": "Cherry Tomato",
    "scientific_name": "Solanum lycopersicum",
    "plant_category": "vegetable"
  },
  "tracking_info": {
    "plant_nickname": "My First Tomato",
    "start_date": "2024-03-15",
    "expected_maturity_date": "2024-07-13",
    "current_stage": "flowering",
    "days_elapsed": 45,
    "progress_percentage": 60,
    "is_active": true,
    "user_notes": "Growing well in morning sun",
    "location_details": "Balcony - South side"
  },
  "timeline": {
    "stages": [
      {
        "stage_name": "germination",
        "start_day": 1,
        "end_day": 14,
        "description": "Seeds sprout and develop first leaves",
        "is_completed": true,
        "key_indicators": ["First green shoots appear"]
      }
    ]
  },
  "current_tips": [
    "Ensure 6-8 hours of direct sunlight daily",
    "Gently shake plants to aid pollination"
  ]
}
```

## 4) DELETE /tracking/instance/{instance_id} — Deactivate Plant Instance
- Purpose: Soft delete; mark instance inactive while preserving history.
- Response (200):
```json
{ "message": "Plant instance deactivated successfully", "data": { "instance_id": 789, "is_active": false } }
```

## 5) PUT /tracking/instance/{instance_id}/progress — Update Plant Progress
- Purpose: Update stage, notes, or location.
- Request Body (any field optional):
```json
{ "current_stage": "flowering", "user_notes": "First flowers appeared today!", "location_details": "Moved to sunnier spot" }
```
- Response (200):
```json
{
  "message": "Progress updated successfully",
  "data": {
    "instance_id": 789,
    "current_stage": "flowering",
    "user_notes": "First flowers appeared today!",
    "location_details": "Moved to sunnier spot"
  }
}
```

## 6) GET /tracking/requirements/{plant_id} — Get Plant Requirements
- Purpose: Return categorized requirements for a plant.
- Response (200):
```json
{ "plant_id": 456, "requirements": [ { "category": "Seeds & Plants", "items": [ { "item": "Cherry tomato seeds", "quantity": "1 packet", "optional": false } ] } ] }
```

## 7) GET /tracking/instructions/{plant_id} — Get Setup Instructions
- Purpose: Return categorized setup instructions.
- Response (200):
```json
{ "plant_id": 456, "instructions": [ { "step": 1, "title": "Prepare Seeds", "description": "Soak tomato seeds...", "duration": "2-4 hours", "tips": ["Use lukewarm water"] } ] }
```

## 8) GET /tracking/timeline/{plant_id} — Get Growth Timeline
- Purpose: Return growth stages and total days.
- Response (200):
```json
{ "plant_id": 456, "total_days": 120, "stages": [ { "stage_name": "germination", "start_day": 1, "end_day": 14, "description": "Seeds sprout...", "key_indicators": ["First green shoots"], "stage_order": 1 } ] }
```

## 9) GET /tracking/instance/{instance_id}/tips — Get Current Stage Tips
- Purpose: Return randomized tips for the current stage.
- Query: `limit` (default 3, max 10)
- Response (200):
```json
{ "instance_id": 789, "current_stage": "flowering", "tips": ["Ensure 6-8 hours of direct sunlight daily"] }
```

## 10) POST /tracking/checklist/complete — Complete Checklist Item
- Purpose: Mark a checklist item completed/uncompleted.
- Request Body:
```json
{ "instance_id": 789, "checklist_item_key": "seeds_cherry_tomato", "is_completed": true, "user_notes": "Bought from local nursery" }
```
- Response (200):
```json
{ "success": true, "message": "Checklist item marked as complete", "progress_summary": { "completed_items": 8, "total_items": 12, "completion_percentage": 67 } }
```

## 11) POST /tracking/instance/{instance_id}/initialize-checklist — Initialize Instance Checklist
- Purpose: Create tracking entries from requirements for the given instance.
- Response (200):
```json
{ "message": "Checklist initialized", "data": { "items_created": 12 } }
```

## 12) PUT /tracking/instance/{instance_id}/nickname — Update Plant Nickname
- Purpose: Update a plant instance nickname.
- Request Body:
```json
{ "plant_nickname": "Super Tomato" }
```
- Response (200):
```json
{ "message": "Nickname updated successfully", "data": { "instance_id": 789, "plant_nickname": "Super Tomato" } }
```

## 13) POST /tracking/instance/{instance_id}/auto-update-stage — Auto Update Growth Stage
- Purpose: Calculate days elapsed and update current stage if needed.
- Response (200):
```json
{ "message": "Plant stage automatically updated to: flowering", "data": { "instance_id": 789, "new_stage": "flowering", "updated": true } }
```

## 14) POST /tracking/instance/{instance_id}/start-growing — Start Growing (Official Start)
- Purpose: Mark an instance as officially started growing or restart it.
- Request Body (optional; can be omitted):
```json
{ "start_date": "2025-10-12" }
```
- Response (200):
```json
{
  "success": true,
  "message": "Instance activated and started",
  "data": { "instance_id": 789, "start_date": "2025-10-12", "expected_maturity_date": "2026-01-10", "current_stage": "germination", "is_active": true }
}
```
Notes:
- `is_active` is set to true only if `start_date` is provided in the request.

## 15) POST /tracking/user/upsert — Upsert User From Tracking
- Purpose: Create or update user and profile from a unified payload before/without starting tracking.
- Request Body (only `email` required; others optional):
```json
{ "email": "user@example.com", "name": "John Doe", "suburb_id": 123, "experience_level": "beginner", "garden_type": "balcony", "available_space": 5.0, "climate_goal": "sustainable gardening" }
```
- Response (200):
```json
{
  "success": true,
  "message": "User upserted successfully",
  "user": { "id": 1, "email": "user@example.com", "name": "John Doe", "suburb_id": 123, "created_at": "...", "updated_at": "...", "last_login": "..." },
  "profile": { "id": 1, "user_id": 1, "experience_level": "beginner", "garden_type": "balcony", "climate_goals": "sustainable gardening", "available_space_m2": 5.0, "created_at": "...", "updated_at": "..." }
}
```

---

### Error Semantics
- 422: Request validation failed (missing required fields, wrong types, invalid date format)
- 404: Resource not found (e.g., plant or instance not found)
- 400: Business rule violation (e.g., token limit in chat, invalid checklist key)
- 500: Internal server error (e.g., external AI failure, DB constraint error)

### Notes
- First-time data generation per `plant_id` may take a few seconds; subsequent reads are cached.
- `suburb_id` fallback: invalid/non-existent values default to 1; `suburb_name` can be provided instead.
