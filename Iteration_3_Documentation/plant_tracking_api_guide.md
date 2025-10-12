# Plant Tracking API Guide

- Base path: `/api/v1`
- Purpose: Track user's plant instances, compute days elapsed and stages, and manage tips/checklists

## Quick Start

1) Upsert user (optional but recommended)
```http
POST /api/v1/tracking/user/upsert
```
Request:
```json
{ "email": "user@example.com", "name": "Alex" }
```

2) Start tracking an instance
```http
POST /api/v1/tracking/start
```
Request:
```json
{
  "user_data": { "email": "user@example.com" },
  "plant_id": 42,
  "plant_nickname": "Balcony Tomato",
  "start_date": "2025-10-12",
  "location_details": "balcony pot 1"
}
```

3) Officially start growing (or correct the start date later)
```http
POST /api/v1/tracking/instance/{instance_id}/start-growing
```
Request (optional date; omitting uses today):
```json
{ "start_date": "2025-10-01" }
```

4) Update stage and optionally snap days_elapsed to stage start
```http
PUT /api/v1/tracking/instance/{instance_id}/progress
```
Request:
```json
{
  "current_stage": "Bud Formation and Flowering",
  "align_to_stage_start": true
}
```
- Behavior: When `align_to_stage_start=true`, backend adjusts `start_date` so that `days_elapsed == start_day` of the chosen stage, and recalculates `expected_maturity_date`. Example: if stage start is day 71, `days_elapsed` becomes 71.

5) Allow backend to auto-update stage by current days
```http
POST /api/v1/tracking/instance/{instance_id}/auto-update-stage
```

---

## Endpoint Catalog

### User and Instances

- GET `/tracking/user/{email}` — List user's plant instances
  - Query: `active_only` (default true), `page`, `limit`
  - Response excerpt:
  ```json
  {
    "plants": [
      {
        "instance_id": 1,
        "plant_id": 42,
        "plant_name": "Tomato",
        "plant_nickname": "Balcony Tomato",
        "start_date": "2025-10-01",
        "expected_maturity_date": "2025-12-01",
        "current_stage": "vegetative",
        "days_elapsed": 23,
        "progress_percentage": 38.33,
        "location_details": "balcony pot 1",
        "image_url": null
      }
    ],
    "total_count": 1,
    "active_count": 1,
    "pagination": { "page": 1, "limit": 20, "total_pages": 1 }
  }
  ```

- GET `/tracking/instance/{instance_id}` — Get one instance with details
  - Response excerpt:
  ```json
  {
    "instance_id": 1,
    "plant_details": { "plant_id": 42, "plant_name": "Tomato" },
    "tracking_info": {
      "plant_nickname": "Balcony Tomato",
      "start_date": "2025-10-01",
      "expected_maturity_date": "2025-12-01",
      "current_stage": "vegetative",
      "days_elapsed": 23,
      "progress_percentage": 38.33,
      "is_active": true
    },
    "timeline": { "stages": [ { "stage_name": "germination", "start_day": 1, "end_day": 20, "is_current": false } ] },
    "current_tips": ["Keep soil moist"]
  }
  ```

- PUT `/tracking/instance/{instance_id}/progress` — Update stage/notes/location
  - Body fields:
    - `current_stage` (string, optional)
    - `user_notes` (string, optional)
    - `location_details` (string, optional)
    - `align_to_stage_start` (boolean, optional; default false)
  - Notes:
    - If `align_to_stage_start=true` and `current_stage` provided, server aligns `start_date` to the stage start.

- POST `/tracking/instance/{instance_id}/start-growing` — Set or reset `start_date`
  - Body: `{ "start_date": "YYYY-MM-DD" }` (optional)
  - Side effects: sets `is_active=true`, resets stage to first stage if needed, recomputes `expected_maturity_date`.

- PUT `/tracking/instance/{instance_id}/nickname` — Update nickname
- DELETE `/tracking/instance/{instance_id}` — Delete instance (hard delete)
  - Permanently removes the instance and its tracking entries
  - Response: `{ "success": true, "data": { "instance_id": 1, "deleted": true } }`

### AI-Generated Growth Data

- GET `/tracking/requirements/{plant_id}` — Requirements checklist
- GET `/tracking/instructions/{plant_id}` — Setup instructions
- GET `/tracking/timeline/{plant_id}` — Growth timeline and total days
- GET `/tracking/instance/{instance_id}/tips` — Tips for current stage

### Checklist Management

- POST `/tracking/instance/{instance_id}/initialize-checklist` — Initialize checklist from requirements
- POST `/tracking/checklist/complete` — Mark item complete/incomplete
  - Body:
  ```json
  {
    "instance_id": 1,
    "checklist_item_key": "tools_garden_trowel",
    "is_completed": true,
    "user_notes": "Purchased"
  }
  ```

### User Upsert (for profile/context)

- POST `/tracking/user/upsert`
  - Body contains at least `email`, others optional.

---

## Stage Alignment Details

- When you manually set a stage from the frontend and want the timeline to jump to that stage's first day, send:
```json
{ "current_stage": "<stage_name>", "align_to_stage_start": true }
```
- Backend logic:
  - Look up the stage by name in the plant's timeline
  - Compute `new_start_date = today - start_day`
  - Recompute `expected_maturity_date` using timeline `total_days` (fallback to previous remaining days or 90)
  - Set `is_active=true`
- If the stage name is not in the timeline, server only updates the stage without aligning the start date.

---

## Errors

- 404: user/instance/plant not found
- 400: validation errors (e.g., empty nickname)
- 500: server/internal errors

---

## Testing Tips

- After changing stage with alignment, call `GET /tracking/instance/{instance_id}` to verify `tracking_info.days_elapsed` equals the stage `start_day`.
- To let backend auto-adjust stage based on new days, call `POST /tracking/instance/{instance_id}/auto-update-stage`.
