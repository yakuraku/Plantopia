# Phase 1 API Documentation - Enhanced Journal Tracking

## Overview
This document provides comprehensive documentation for the Phase 1 backend endpoints that enable the three-step journal tracking flow in the Profile section.

---

## Endpoints Summary

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `/api/v1/tracking/instance/{instance_id}/checklist` | GET | ⭐⭐⭐⭐⭐ | Retrieve checklist state with completion status |
| `/api/v1/tracking/instance/{instance_id}/complete-setup` | POST | ⭐⭐⭐⭐⭐ | Mark setup instructions as complete |
| `/api/v1/tracking/instance/{instance_id}/status` | GET | ⭐⭐⭐⭐ | Get comprehensive status summary |

---

## 1. GET /api/v1/tracking/instance/{instance_id}/checklist

### Purpose
Retrieve the saved checklist state for a plant instance, allowing users to see their progress when reopening the journal.

### Endpoint
```
GET /api/v1/tracking/instance/{instance_id}/checklist
```

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instance_id` | integer | Yes | Plant instance ID |

### Response Schema (200 OK)
```json
{
  "instance_id": 123,
  "checklist_items": [
    {
      "item_key": "tools_garden-trowel",
      "category": "Tools",
      "item_name": "Garden Trowel",
      "quantity": "1",
      "optional": false,
      "is_completed": true,
      "completed_at": "2025-10-14T10:30:00Z",
      "user_notes": "Purchased from local store"
    },
    {
      "item_key": "materials_potting-mix",
      "category": "Materials",
      "item_name": "Potting Mix",
      "quantity": "5L",
      "optional": false,
      "is_completed": false,
      "completed_at": null,
      "user_notes": null
    }
  ],
  "progress_summary": {
    "total_items": 15,
    "completed_items": 8,
    "completion_percentage": 53.33
  }
}
```

### Field Descriptions

**ChecklistItem Fields:**
- `item_key` (string): Unique identifier for the checklist item (format: `category_itemname`)
- `category` (string): Category name (e.g., "Tools", "Materials", "Seeds & Plants")
- `item_name` (string): Display name of the item
- `quantity` (string): Quantity needed (e.g., "1", "5L", "10 seeds")
- `optional` (boolean): Whether the item is optional
- `is_completed` (boolean): Completion status
- `completed_at` (datetime | null): ISO 8601 timestamp when item was completed
- `user_notes` (string | null): User's notes about this item

**ProgressSummary Fields:**
- `total_items` (integer): Total number of checklist items
- `completed_items` (integer): Number of completed items
- `completion_percentage` (float): Completion percentage (0-100)

### Error Responses

**404 Not Found**
```json
{
  "detail": "Plant instance with ID 999 not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Error loading checklist: <error message>"
}
```

### Frontend Integration Example

```typescript
async function loadChecklistState(instanceId: number) {
  try {
    const response = await fetch(
      `/api/v1/tracking/instance/${instanceId}/checklist`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // Hydrate checklist state
    const completedSet = new Set(
      data.checklist_items
        .filter(item => item.is_completed)
        .map(item => item.item_key)
    );

    // Update UI
    updateProgressBar(data.progress_summary.completion_percentage);
    renderChecklistItems(data.checklist_items);

    return data;
  } catch (error) {
    console.error('Failed to load checklist:', error);
    // Fallback to localStorage if needed
  }
}
```

### Notes
- Returns all checklist items from requirements data, merged with tracking state
- Items not yet tracked will have `is_completed: false` and null timestamps
- If no growth data exists for the plant, returns empty checklist with 0% progress
- Call this endpoint when opening the journal detail view in Step 1

---

## 2. POST /api/v1/tracking/instance/{instance_id}/complete-setup

### Purpose
Mark setup instructions as complete for a plant instance. This is separate from starting growth (`is_active` status) and allows tracking setup completion independently.

### Endpoint
```
POST /api/v1/tracking/instance/{instance_id}/complete-setup
```

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instance_id` | integer | Yes | Plant instance ID |

### Request Body
No request body required. The completion timestamp is automatically set to the current time.

### Response Schema (200 OK)
```json
{
  "instance_id": 123,
  "setup_completed": true,
  "setup_completed_at": "2025-10-14T10:45:00Z",
  "message": "Setup instructions marked as complete"
}
```

### Field Descriptions
- `instance_id` (integer): Plant instance ID
- `setup_completed` (boolean): Setup completion status (always `true` after this call)
- `setup_completed_at` (datetime): ISO 8601 timestamp when setup was marked complete
- `message` (string): Success message

### Error Responses

**404 Not Found**
```json
{
  "detail": "Plant instance with ID 999 not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Error completing setup: <error message>"
}
```

### Frontend Integration Example

```typescript
async function completeSetup(instanceId: number) {
  try {
    const response = await fetch(
      `/api/v1/tracking/instance/${instanceId}/complete-setup`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    console.log('Setup completed:', data.setup_completed_at);

    // Update UI to show Step 2 completed
    markStepComplete(2);

    // Optionally move to Step 3 (Timeline)
    navigateToStep(3);

    return data;
  } catch (error) {
    console.error('Failed to complete setup:', error);
    throw error;
  }
}
```

### Usage Flow
1. User views and completes setup instructions in Step 2
2. User clicks "Mark Setup Complete" button
3. Frontend calls this endpoint
4. Backend sets `setup_completed = true` and records timestamp
5. Frontend shows Step 3 (Timeline) or remains on Step 2 until growth starts

### Notes
- This endpoint is **idempotent** - calling it multiple times updates the timestamp
- Does NOT set `is_active = true` (use `/tracking/instance/{id}/start-growing` for that)
- Allows distinguishing between "setup done" and "growth started"
- Can be called before or after starting growth

---

## 3. GET /api/v1/tracking/instance/{instance_id}/status

### Purpose
Get a comprehensive status summary for a plant instance across all three tracking steps. Helps determine which step to display in the UI.

### Endpoint
```
GET /api/v1/tracking/instance/{instance_id}/status
```

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instance_id` | integer | Yes | Plant instance ID |

### Response Schema (200 OK)
```json
{
  "instance_id": 123,
  "checklist_status": {
    "total_items": 15,
    "completed_items": 12,
    "completion_percentage": 80.0,
    "meets_threshold": true
  },
  "setup_status": {
    "completed": true,
    "completed_at": "2025-10-14T10:45:00Z"
  },
  "growing_status": {
    "is_active": true,
    "start_date": "2025-10-14",
    "days_elapsed": 5,
    "current_stage": "Germination",
    "progress_percentage": 15.5
  }
}
```

### Field Descriptions

**ChecklistStatus Fields:**
- `total_items` (integer): Total checklist items
- `completed_items` (integer): Number of completed items
- `completion_percentage` (float): Completion percentage (0-100)
- `meets_threshold` (boolean): Whether completion is ≥ 80% (threshold for Step 2)

**SetupStatus Fields:**
- `completed` (boolean): Whether setup instructions are marked complete
- `completed_at` (datetime | null): When setup was completed (null if not completed)

**GrowingStatus Fields:**
- `is_active` (boolean): Whether plant is actively growing
- `start_date` (date): Start date of growing
- `days_elapsed` (integer): Days since start_date
- `current_stage` (string): Current growth stage name
- `progress_percentage` (float): Overall growth progress (0-100)

### Error Responses

**404 Not Found**
```json
{
  "detail": "Plant instance with ID 999 not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Error loading instance status: <error message>"
}
```

### Frontend Integration Example

```typescript
async function determineStepToShow(instanceId: number): Promise<number> {
  try {
    const response = await fetch(
      `/api/v1/tracking/instance/${instanceId}/status`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const status = await response.json();

    // Decision logic for which step to show
    if (status.growing_status.is_active) {
      // Plant is actively growing - show timeline
      return 3;
    } else if (status.setup_status.completed) {
      // Setup is done but not growing yet - show setup/timeline
      return 2;
    } else if (status.checklist_status.meets_threshold) {
      // Checklist is 80%+ complete - allow moving to setup
      return 2;
    } else {
      // Checklist incomplete - show checklist
      return 1;
    }
  } catch (error) {
    console.error('Failed to load status:', error);
    // Fallback to step 1
    return 1;
  }
}

// Usage in modal open
async function openJournalModal(instanceId: number) {
  const step = await determineStepToShow(instanceId);
  navigateToStep(step);

  // Also load details for the current step
  if (step === 1) {
    await loadChecklistState(instanceId);
  } else if (step === 2) {
    await loadSetupInstructions(instanceId);
  } else {
    await loadTimeline(instanceId);
  }
}
```

### Notes
- Call this endpoint when opening the journal modal to determine initial step
- Use `meets_threshold` flag to enable/disable "Start Setup" button
- `growing_status.is_active` indicates plant is in growth phase (show timeline)
- This endpoint combines data from multiple sources for a complete picture

---

## Database Schema Changes

### user_plant_instances Table

**New Columns:**
```sql
setup_completed BOOLEAN NOT NULL DEFAULT FALSE
setup_completed_at TIMESTAMP NULL
```

**Migration:**
- File: `alembic/versions/f9e4d3b2a1c0_add_setup_completed_fields.py`
- Applied: ✅ Yes
- Date: 2025-10-14

---

## Step-by-Step Frontend Integration Guide

### Step 1: Opening the Journal Modal

```typescript
async function openJournal(instanceId: number) {
  // 1. Get status to determine which step to show
  const status = await fetch(
    `/api/v1/tracking/instance/${instanceId}/status`
  ).then(r => r.json());

  // 2. Determine initial step
  let currentStep = 1;
  if (status.growing_status.is_active) {
    currentStep = 3;
  } else if (status.setup_status.completed ||
             status.checklist_status.meets_threshold) {
    currentStep = 2;
  }

  // 3. Navigate to determined step
  showStep(currentStep);

  // 4. Load step-specific data
  if (currentStep === 1) {
    const checklist = await fetch(
      `/api/v1/tracking/instance/${instanceId}/checklist`
    ).then(r => r.json());

    renderChecklist(checklist);
  }
}
```

### Step 2: Handling Checklist Completion

```typescript
async function handleChecklistItemToggle(
  instanceId: number,
  itemKey: string,
  isCompleted: boolean
) {
  // Mark item complete/incomplete (existing endpoint)
  await fetch('/api/v1/tracking/checklist/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      instance_id: instanceId,
      checklist_item_key: itemKey,
      is_completed: isCompleted
    })
  });

  // Reload checklist to get updated progress
  const updated = await fetch(
    `/api/v1/tracking/instance/${instanceId}/checklist`
  ).then(r => r.json());

  // Update UI
  updateProgressBar(updated.progress_summary.completion_percentage);

  // Enable "Start Setup" button if threshold met
  if (updated.progress_summary.completion_percentage >= 80) {
    enableStartSetupButton();
  }
}
```

### Step 3: Marking Setup Complete

```typescript
async function handleSetupComplete(instanceId: number) {
  // Mark setup as complete
  await fetch(
    `/api/v1/tracking/instance/${instanceId}/complete-setup`,
    { method: 'POST' }
  );

  // Show success notification
  showNotification('Setup instructions completed!');

  // Move to timeline step
  showStep(3);
}
```

### Step 4: Starting Growth

```typescript
async function handleStartGrowing(instanceId: number) {
  // Start growing (existing endpoint)
  await fetch(
    `/api/v1/tracking/instance/${instanceId}/start-growing`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_date: new Date().toISOString().split('T')[0]
      })
    }
  );

  // Reload status
  const status = await fetch(
    `/api/v1/tracking/instance/${instanceId}/status`
  ).then(r => r.json());

  // Show timeline
  if (status.growing_status.is_active) {
    showStep(3);
    loadTimeline(instanceId);
  }
}
```

---

## Testing Checklist

### Manual Testing

1. **Checklist Endpoint**
   - [ ] GET with valid instance_id returns checklist
   - [ ] Response includes all items from requirements
   - [ ] Completion status reflects tracking data
   - [ ] Progress percentage calculates correctly
   - [ ] Returns empty checklist if no growth data exists
   - [ ] Returns 404 for invalid instance_id

2. **Complete Setup Endpoint**
   - [ ] POST marks setup as complete
   - [ ] Timestamp is set correctly
   - [ ] Idempotent (can call multiple times)
   - [ ] Returns 404 for invalid instance_id
   - [ ] Does NOT set is_active flag

3. **Status Endpoint**
   - [ ] GET returns comprehensive status
   - [ ] meets_threshold flag correct (80% threshold)
   - [ ] growing_status reflects is_active flag
   - [ ] setup_status reflects setup_completed flag
   - [ ] Returns 404 for invalid instance_id

### Integration Testing

```bash
# 1. Get an instance ID (replace with real ID from your DB)
INSTANCE_ID=1

# 2. Check initial status
curl http://localhost:8000/api/v1/tracking/instance/$INSTANCE_ID/status

# 3. Load checklist
curl http://localhost:8000/api/v1/tracking/instance/$INSTANCE_ID/checklist

# 4. Mark some items complete (use existing endpoint)
curl -X POST http://localhost:8000/api/v1/tracking/checklist/complete \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": 1,
    "checklist_item_key": "tools_garden-trowel",
    "is_completed": true
  }'

# 5. Reload checklist to see updated progress
curl http://localhost:8000/api/v1/tracking/instance/$INSTANCE_ID/checklist

# 6. Mark setup complete
curl -X POST http://localhost:8000/api/v1/tracking/instance/$INSTANCE_ID/complete-setup

# 7. Verify status updated
curl http://localhost:8000/api/v1/tracking/instance/$INSTANCE_ID/status
```

---

## Performance Considerations

### Endpoint Efficiency

1. **Checklist Endpoint**
   - Makes 2 DB queries: instance details + progress tracking entries
   - Fetches requirements from growth data (cached JSON field)
   - O(n) merge operation where n = number of checklist items (~15-30)
   - **Expected response time**: < 100ms

2. **Complete Setup Endpoint**
   - Single UPDATE query
   - **Expected response time**: < 50ms

3. **Status Endpoint**
   - Makes 3 DB queries: instance + progress counts
   - No heavy computations
   - **Expected response time**: < 100ms

### Optimization Tips

- Call `/status` endpoint once when opening modal
- Cache checklist data client-side, only reload after updates
- Use optimistic UI updates for checklist toggles
- Consider adding Redis caching for frequently accessed growth data

---

## Error Handling Best Practices

### Frontend Error Handling

```typescript
async function safeApiCall<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);

    // Show user-friendly error message
    showErrorNotification('Failed to load data. Please try again.');

    // Fallback to localStorage if applicable
    if (url.includes('/checklist')) {
      return loadChecklistFromLocalStorage();
    }

    throw error;
  }
}
```

### Common Error Scenarios

1. **Instance Not Found (404)**
   - User deleted the instance in another tab
   - Invalid instance_id from URL
   - **Action**: Close modal, show error, refresh plant list

2. **No Growth Data (Empty Checklist)**
   - Plant doesn't have AI-generated data yet
   - **Action**: Show "Generating data..." message, retry after delay

3. **Network Error**
   - Backend unreachable
   - **Action**: Fall back to localStorage, show offline indicator

---

## Migration Guide for Existing Instances

### Backward Compatibility

All existing plant instances will have:
- `setup_completed = false` (default)
- `setup_completed_at = null`

### Data Migration Strategy

If you need to retroactively mark setup as complete for active instances:

```sql
-- Mark setup complete for all actively growing plants
UPDATE user_plant_instances
SET
  setup_completed = true,
  setup_completed_at = start_date
WHERE
  is_active = true
  AND setup_completed = false;
```

---

## Future Enhancements (Phase 2)

The following enhancements from the requirements document are not yet implemented:

1. **Batch Checklist Updates** (`POST /api/v1/tracking/instance/{id}/checklist/batch`)
2. **Stage-Specific Tips** (`GET /api/v1/tracking/instance/{id}/tips?stage={stage}`)
3. **Instance Notes** (`PUT /api/v1/tracking/instance/{id}/notes`)
4. **Photo Upload** (`POST /api/v1/tracking/instance/{id}/photos`)
5. **Timeline Events** (`POST /api/v1/tracking/instance/{id}/events`)

These can be prioritized based on user feedback and usage patterns.

---

## Support and Questions

For questions or issues with these endpoints:
1. Check this documentation first
2. Review the backend code in `app/api/endpoints/plant_tracking.py`
3. Check service layer logic in `app/services/plant_instance_service.py`
4. Review database models in `app/models/database.py`

---

**Document Version**: 1.0
**Last Updated**: October 14, 2025
**Status**: ✅ Production Ready
