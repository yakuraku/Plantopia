# Frontend Integration Guide - Plant Tracking Feature

## Overview
This guide provides frontend developers with all necessary information to integrate with the plant tracking backend APIs.

## User Authentication & Data Flow

### User Data Requirements
The backend expects the following user data from the frontend:

**Required Fields** (sent in API requests):
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "suburb_id": 123,
  "experience_level": "beginner",
  "garden_type": "balcony",
  "available_space": 5.0,
  "climate_goal": "sustainable gardening"
}
```

**Field Descriptions**:
- `email` - User's email for identification (String)
- `name` - Display name (String)
- `suburb_id` - Location ID for climate data (Integer)
- `experience_level` - "beginner", "intermediate", "advanced" (String)
- `garden_type` - "balcony", "backyard", "indoor", "courtyard", "community_garden" (String)
- `available_space` - Space in square meters (Float)
- `climate_goal` - User's environmental preferences (String)

### Default Values
If user doesn't provide optional data, frontend should send these defaults:
- `experience_level`: "beginner"
- `garden_type`: "backyard"
- `available_space`: 10.0
- `climate_goal`: "general gardening"

## API Endpoints

### Base URL
```
https://api.plantopia.com/api/v1
```

### Authentication
All requests require authentication headers:
```
Authorization: Bearer {jwt_token}
```

## Core Tracking Endpoints

### 1. Start Plant Tracking
**Endpoint**: `POST /tracking/start`

**Request Body**:
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

**Response**:
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

### 2. Get User's Plant Instances
**Endpoint**: `GET /tracking/user/{user_id}`

**Query Parameters**:
- `active_only` (boolean, default: true) - Show only active plants
- `page` (int, default: 1) - Page number for pagination
- `limit` (int, default: 20) - Items per page

**Response**:
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
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_pages": 1
  }
}
```

### 3. Get Plant Instance Details
**Endpoint**: `GET /tracking/instance/{instance_id}`

**Response**:
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
      },
      {
        "stage_name": "flowering",
        "start_day": 61,
        "end_day": 85,
        "description": "Flower buds form and bloom",
        "is_completed": false,
        "is_current": true,
        "key_indicators": ["Yellow flowers appear"]
      }
    ]
  },
  "current_tips": [
    "Ensure 6-8 hours of direct sunlight daily",
    "Gently shake plants to aid pollination"
  ]
}
```

## Data Access Endpoints

### 4. Get Requirements Checklist
**Endpoint**: `GET /tracking/requirements/{plant_id}`

**Response**:
```json
{
  "plant_id": 456,
  "requirements": [
    {
      "category": "Seeds & Plants",
      "items": [
        {
          "item": "Cherry tomato seeds",
          "quantity": "1 packet",
          "optional": false
        }
      ]
    },
    {
      "category": "Growing Medium",
      "items": [
        {
          "item": "Potting soil",
          "quantity": "20L bag",
          "optional": false
        },
        {
          "item": "Compost",
          "quantity": "5L",
          "optional": true
        }
      ]
    }
  ]
}
```

### 5. Get Setup Instructions
**Endpoint**: `GET /tracking/instructions/{plant_id}`

**Response**:
```json
{
  "plant_id": 456,
  "instructions": [
    {
      "step": 1,
      "title": "Prepare Seeds",
      "description": "Soak tomato seeds in warm water for 2-4 hours",
      "duration": "2-4 hours",
      "tips": ["Use lukewarm water", "Seeds should swell slightly"],
      "image_url": "https://storage.googleapis.com/plantopia/instructions/seed-prep.jpg"
    },
    {
      "step": 2,
      "title": "Plant Seeds",
      "description": "Plant seeds 1/4 inch deep in moist potting mix",
      "duration": "15 minutes",
      "tips": ["Cover lightly with soil", "Keep soil moist"],
      "image_url": null
    }
  ]
}
```

### 6. Get Growth Timeline
**Endpoint**: `GET /tracking/timeline/{plant_id}`

**Response**:
```json
{
  "plant_id": 456,
  "total_days": 120,
  "stages": [
    {
      "stage_name": "germination",
      "start_day": 1,
      "end_day": 14,
      "description": "Seeds sprout and develop first leaves",
      "key_indicators": ["First green shoots", "Seed leaves emerge"],
      "stage_order": 1
    },
    {
      "stage_name": "flowering",
      "start_day": 61,
      "end_day": 85,
      "description": "Flower buds form and bloom",
      "key_indicators": ["Yellow flowers appear"],
      "stage_order": 4
    }
  ]
}
```

### 7. Get Current Stage Tips
**Endpoint**: `GET /tracking/instance/{instance_id}/tips`

**Response**:
```json
{
  "instance_id": 789,
  "current_stage": "flowering",
  "tips": [
    {
      "tip": "Ensure 6-8 hours of direct sunlight daily",
      "category": "sunlight",
      "importance": "high"
    },
    {
      "tip": "Gently shake plants to aid pollination",
      "category": "care",
      "importance": "medium"
    }
  ],
  "stage_info": {
    "stage_name": "flowering",
    "description": "Flower buds form and bloom",
    "days_in_stage": 15,
    "estimated_days_remaining": 25
  }
}
```

## Progress Management Endpoints

### 8. Mark Checklist Item Complete
**Endpoint**: `POST /tracking/checklist/complete`

**Request Body**:
```json
{
  "instance_id": 789,
  "checklist_item_key": "seeds_cherry_tomato",
  "is_completed": true,
  "user_notes": "Bought from local nursery"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Checklist item marked as complete",
  "progress_summary": {
    "completed_items": 8,
    "total_items": 12,
    "completion_percentage": 67
  }
}
```

### 9. Update Plant Progress
**Endpoint**: `PUT /tracking/instance/{instance_id}/progress`

**Request Body**:
```json
{
  "current_stage": "flowering",
  "user_notes": "First flowers appeared today!",
  "location_details": "Moved to sunnier spot"
}
```

### 10. Update Plant Nickname
**Endpoint**: `PUT /tracking/instance/{instance_id}/nickname`

**Request Body**:
```json
{
  "plant_nickname": "Super Tomato"
}
```

## UI/UX Integration Guidelines

### Dashboard View Requirements
1. **Grid/List Toggle**: Support both grid and list views for plant instances
2. **Progress Indicators**: Show visual progress bars or circular progress
3. **Quick Actions**: Provide shortcuts for common actions (view details, update progress)
4. **Filtering**: Allow filtering by stage, plant type, or activity status

### Individual Plant View Requirements
1. **Timeline Visualization**: Interactive timeline showing past, current, and future stages
2. **Progress Tracking**: Clear indicators of current stage and next milestones
3. **Tips Display**: Contextual tips that refresh based on current stage
4. **Photo Integration**: Support for user photos of their plants

### Responsive Design Considerations
- Timeline should adapt to mobile screens (vertical layout)
- Touch-friendly controls for progress updates
- Swipe gestures for navigating between plant instances

## Error Handling

### Common Error Responses
```json
{
  "error": {
    "code": "PLANT_NOT_FOUND",
    "message": "Plant with ID 456 not found",
    "details": "The specified plant ID does not exist in the database"
  }
}
```

### Error Codes
- `PLANT_NOT_FOUND` (404) - Plant doesn't exist
- `INSTANCE_NOT_FOUND` (404) - Plant instance doesn't exist
- `UNAUTHORIZED` (401) - Invalid authentication
- `FORBIDDEN` (403) - User doesn't own this plant instance
- `VALIDATION_ERROR` (400) - Invalid request data
- `RATE_LIMITED` (429) - Too many requests
- `SERVER_ERROR` (500) - Internal server error

### Recommended Error Handling
```javascript
try {
  const response = await fetch('/api/v1/tracking/instance/123');
  const data = await response.json();

  if (!response.ok) {
    switch (data.error.code) {
      case 'PLANT_NOT_FOUND':
        showError('Plant not found. Please check your selection.');
        break;
      case 'UNAUTHORIZED':
        redirectToLogin();
        break;
      default:
        showError('Something went wrong. Please try again.');
    }
    return;
  }

  // Handle successful response
  updateUI(data);
} catch (error) {
  showError('Network error. Please check your connection.');
}
```

## Performance Optimization

### Caching Strategy
- Cache plant growth data (requirements, instructions, timeline) for 24 hours
- Cache user dashboard data for 5 minutes
- Implement optimistic updates for progress tracking

### Pagination
- Use pagination for users with many plant instances
- Implement infinite scroll or "load more" patterns
- Default page size: 20 items

### Image Loading
- Implement lazy loading for plant images
- Use placeholder images while loading
- Support responsive image sizes

## Testing Guidelines

### Test Scenarios
1. **Happy Path**: Complete plant tracking workflow
2. **Error Scenarios**: Handle API failures gracefully
3. **Edge Cases**: Users with no plants, completed plants
4. **Performance**: Large datasets, slow network conditions

### Mock Data
The backend team will provide mock data files for frontend development:
- `mock_plant_instances.json`
- `mock_growth_timeline.json`
- `mock_requirements.json`

## Support & Documentation

### API Documentation
- Full API documentation available at `/docs` (Swagger UI)
- Interactive testing available through Swagger interface

### Contact Information
- Backend Team Lead: [Contact Info]
- API Support: [Support Channel]
- Bug Reports: [Issue Tracker]

### Version Information
- Current API Version: v1
- Breaking Changes: Will be communicated 2 weeks in advance
- Deprecation Policy: 6 months notice for deprecated endpoints