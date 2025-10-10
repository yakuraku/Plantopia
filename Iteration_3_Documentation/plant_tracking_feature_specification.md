# Plant Tracking Feature - Technical Specification

## Overview
This document outlines the technical specification for implementing a comprehensive plant tracking feature that allows users to monitor their gardening journey from seed to harvest.

## Feature Description
The plant tracking feature enables users to:
1. **Start Growing**: Select a plant and begin tracking its growth progress
2. **Requirements Checklist**: View and check off required materials (seeds, soil, tools, etc.)
3. **Setup Instructions**: Follow step-by-step growing instructions
4. **Growth Timeline**: Visual timeline showing current progress and upcoming stages
5. **Stage-based Tips**: Contextual gardening tips based on current growth stage

## Database Design

### New Tables Required

#### 1. plant_growth_data
**Purpose**: Cache external API-generated data per plant (shared across all users)

| Column | Type | Description |
|--------|------|-------------|
| plant_id | Integer (FK) | PRIMARY KEY - References plants.id |
| requirements_checklist | JSON | Array of required materials/tools |
| setup_instructions | JSON | Step-by-step growing instructions |
| growth_stages | JSON | Timeline stages with descriptions |
| care_tips | JSON | Stage-based care tips (15-20 per plant) |
| data_source_info | JSON | API metadata for tracking |
| last_updated | DateTime | When data was last generated |
| version | String | For cache invalidation |

#### 2. user_plant_instances
**Purpose**: Individual user's plant growing sessions

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| user_id | Integer (FK) | References users.id |
| plant_id | Integer (FK) | References plants.id |
| plant_nickname | String | User's custom name for this instance |
| start_date | Date | When user started growing |
| expected_maturity_date | Date | Calculated from start_date + time_to_maturity_days |
| current_stage | String | Current growth stage |
| is_active | Boolean | Whether still actively growing |
| user_notes | Text | User's personal notes |
| location_details | String | Where planted (e.g., "balcony pot 1") |
| created_at | DateTime | Record creation timestamp |

#### 3. user_progress_tracking
**Purpose**: Track checklist and milestone completion

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| user_plant_instance_id | Integer (FK) | References user_plant_instances.id |
| checklist_item_key | String | Maps to plant_growth_data.requirements_checklist |
| is_completed | Boolean | Whether item is completed |
| completed_at | DateTime | When completed |
| user_notes | Text | User's notes for this item |

## External API Integration

### API Context Data
For rich contextual responses, include these fields from existing plant data:
```
plant_name, scientific_name, plant_category, description,
care_instructions, water_requirements, sunlight_requirements,
soil_type, time_to_maturity_days, maintenance_level,
climate_zone, plant_spacing, sowing_depth, germination,
hardiness_life_cycle, companion_plants, characteristics
```

### API Call Strategy
Three separate API calls for maximum quality:

1. **Requirements API Call**
   - Input: Plant context data + user preferences
   - Output: JSON array of required materials/tools
   - Stored in: `plant_growth_data.requirements_checklist`

2. **Instructions API Call**
   - Input: Plant context data + requirements
   - Output: JSON array of step-by-step instructions
   - Stored in: `plant_growth_data.setup_instructions`

3. **Timeline API Call**
   - Input: Plant context + time_to_maturity_days
   - Output: JSON with growth stages and care tips
   - Stored in: `plant_growth_data.growth_stages` + `plant_growth_data.care_tips`

### API Response Format
All API responses must return structured JSON without explanatory text for direct database storage.

## User Data Requirements

### Frontend Data Input
Frontend will provide:
- `email` - User identification
- `name` - User's display name
- `suburb_id` - Location for climate-specific advice
- `experience_level` - Gardening expertise
- `garden_type` - Growing environment
- `available_space` - Space constraints
- `climate_goal` - Environmental preferences

### Data Enhancement
Backend will enhance with existing `user_profiles` data for personalized recommendations.

## Key Features & Edge Cases

### Multiple Plant Instances
- Users can grow multiple instances of the same plant
- Each instance has unique nickname and timeline
- Example: "Tomato - Balcony" (started Jan 1) vs "Tomato - Garden" (started Feb 15)

### Data Efficiency
- `plant_growth_data` generated once per plant type
- All users share same growth data but track individual progress
- API calls only made when data doesn't exist

### Stage-based Tips
- Display 1-2 tips randomly based on current stage
- Tips are stage-specific (flowering tips not shown during harvest)
- Prevent tip repetition within same session

### Progress Calculation
- Calculate days since start_date
- Map to appropriate growth stage
- Update current_stage automatically

## API Endpoints (Backend Requirements)

### Core Tracking Endpoints
1. `POST /api/v1/tracking/start` - Start tracking a new plant
2. `GET /api/v1/tracking/user/{user_id}` - Get all user's active plants
3. `GET /api/v1/tracking/instance/{instance_id}` - Get specific plant instance
4. `PUT /api/v1/tracking/instance/{instance_id}/progress` - Update progress
5. `GET /api/v1/tracking/instance/{instance_id}/tips` - Get current stage tips

### Data Management Endpoints
1. `GET /api/v1/tracking/requirements/{plant_id}` - Get requirements checklist
2. `GET /api/v1/tracking/instructions/{plant_id}` - Get setup instructions
3. `GET /api/v1/tracking/timeline/{plant_id}` - Get growth timeline
4. `POST /api/v1/tracking/checklist/complete` - Mark checklist item complete

## Frontend Integration Points

### Dashboard View
- Grid/list of all active plant instances
- Progress indicators for each plant
- Quick access to timeline and tips

### Individual Plant View
- Growth timeline visualization
- Current stage indicators
- Stage-specific tips display
- Progress tracking controls

### User Experience Flow
1. User selects plant from recommendations/favorites
2. "Start Growing" button appears
3. Requirements checklist phase
4. Setup instructions phase
5. Timeline tracking mode begins
6. Ongoing progress monitoring

## Development Considerations

### Performance
- Cache API responses to minimize external calls
- Implement efficient querying for user dashboards
- Consider pagination for users with many plants

### Error Handling
- Graceful fallbacks if API data unavailable
- Validation for user input data
- Proper error messages for frontend

### Testing
- Unit tests for all API endpoints
- Integration tests for external API calls
- Performance tests for dashboard queries

### Security
- Proper user authentication for tracking endpoints
- Data validation for all user inputs
- Rate limiting for API operations

## Success Metrics
- User engagement with tracking feature
- Completion rates for growth cycles
- API response times and reliability
- User retention in tracking workflows