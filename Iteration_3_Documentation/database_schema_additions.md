# Database Schema Additions for Plant Tracking

## Overview
This document details the new database tables required for the plant tracking feature, designed to work alongside existing Plantopia tables.

## Existing Tables (No Modifications)
The following existing tables will be used without modification:
- `plants` - Source plant data with `time_to_maturity_days`
- `users` - User authentication and basic info
- `user_profiles` - User preferences and gardening details
- `suburbs` - Location data for climate-specific advice

## New Tables

### 1. plant_growth_data
**Purpose**: Store external API-generated growth data shared across all users

```sql
CREATE TABLE plant_growth_data (
    plant_id INTEGER PRIMARY KEY REFERENCES plants(id),
    requirements_checklist JSON NOT NULL,
    setup_instructions JSON NOT NULL,
    growth_stages JSON NOT NULL,
    care_tips JSON NOT NULL,
    data_source_info JSON,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version VARCHAR(50) DEFAULT '1.0'
);

-- Index for performance
CREATE INDEX idx_plant_growth_data_updated ON plant_growth_data(last_updated);
```

**JSON Structure Examples**:

**requirements_checklist**:
```json
[
  {
    "category": "Seeds & Plants",
    "items": ["Tomato seeds", "Seed starting trays"]
  },
  {
    "category": "Growing Medium",
    "items": ["Potting soil", "Compost", "Perlite"]
  },
  {
    "category": "Tools",
    "items": ["Small hand trowel", "Watering can", "Plant labels"]
  },
  {
    "category": "Containers",
    "items": ["6-inch pots", "Drainage saucers"]
  }
]
```

**setup_instructions**:
```json
[
  {
    "step": 1,
    "title": "Prepare Seeds",
    "description": "Soak tomato seeds in warm water for 2-4 hours before planting",
    "duration": "2-4 hours",
    "tips": ["Use lukewarm water", "Seeds should swell slightly"]
  },
  {
    "step": 2,
    "title": "Fill Containers",
    "description": "Fill seed trays with moist potting mix, leaving 1/4 inch from top",
    "duration": "10 minutes",
    "tips": ["Soil should be damp but not soggy", "Gentle compression is fine"]
  }
]
```

**growth_stages**:
```json
[
  {
    "stage_name": "germination",
    "start_day": 1,
    "end_day": 14,
    "description": "Seeds sprout and develop first leaves",
    "key_indicators": ["First green shoots appear", "Seed leaves (cotyledons) emerge"],
    "stage_order": 1
  },
  {
    "stage_name": "seedling",
    "start_day": 15,
    "end_day": 35,
    "description": "True leaves develop and plant establishes",
    "key_indicators": ["True leaves appear", "Plant height 2-4 inches"],
    "stage_order": 2
  },
  {
    "stage_name": "vegetative",
    "start_day": 36,
    "end_day": 60,
    "description": "Rapid leaf and stem growth",
    "key_indicators": ["Bushy growth", "Strong stem development"],
    "stage_order": 3
  },
  {
    "stage_name": "flowering",
    "start_day": 61,
    "end_day": 85,
    "description": "Flower buds form and bloom",
    "key_indicators": ["Yellow flowers appear", "Pollination occurs"],
    "stage_order": 4
  },
  {
    "stage_name": "fruiting",
    "start_day": 86,
    "end_day": 110,
    "description": "Fruits develop and mature",
    "key_indicators": ["Small green tomatoes form", "Fruits begin to size up"],
    "stage_order": 5
  },
  {
    "stage_name": "harvest",
    "start_day": 111,
    "end_day": 130,
    "description": "Fruits ripen and are ready for harvest",
    "key_indicators": ["Fruits change color", "Fruits are firm but give slightly"],
    "stage_order": 6
  }
]
```

**care_tips**:
```json
[
  {
    "stage_name": "germination",
    "tips": [
      "Keep soil consistently moist but not waterlogged",
      "Maintain temperature between 65-75°F",
      "Provide bright, indirect light",
      "Cover with plastic wrap to maintain humidity",
      "Check daily for first signs of sprouting"
    ]
  },
  {
    "stage_name": "seedling",
    "tips": [
      "Gradually introduce direct sunlight",
      "Water when top inch of soil feels dry",
      "Consider gentle fertilizer every 2 weeks",
      "Thin weaker seedlings if overcrowded"
    ]
  },
  {
    "stage_name": "flowering",
    "tips": [
      "Ensure 6-8 hours of direct sunlight daily",
      "Reduce nitrogen, increase phosphorus fertilizer",
      "Gently shake plants to aid pollination",
      "Monitor for pests during flowering period"
    ]
  }
]
```

### 2. user_plant_instances
**Purpose**: Track individual user's plant growing sessions

```sql
CREATE TABLE user_plant_instances (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plant_id INTEGER NOT NULL REFERENCES plants(id),
    plant_nickname VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    expected_maturity_date DATE NOT NULL,
    current_stage VARCHAR(50) DEFAULT 'germination',
    is_active BOOLEAN DEFAULT TRUE,
    user_notes TEXT,
    location_details VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_user_plant_instances_user_active ON user_plant_instances(user_id, is_active);
CREATE INDEX idx_user_plant_instances_plant ON user_plant_instances(plant_id);
CREATE INDEX idx_user_plant_instances_stage ON user_plant_instances(current_stage);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_plant_instances_updated_at
    BEFORE UPDATE ON user_plant_instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3. user_progress_tracking
**Purpose**: Track checklist completion and milestones

```sql
CREATE TABLE user_progress_tracking (
    id SERIAL PRIMARY KEY,
    user_plant_instance_id INTEGER NOT NULL REFERENCES user_plant_instances(id) ON DELETE CASCADE,
    checklist_item_key VARCHAR(200) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    user_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_user_progress_tracking_instance ON user_progress_tracking(user_plant_instance_id);
CREATE INDEX idx_user_progress_tracking_completed ON user_progress_tracking(user_plant_instance_id, is_completed);

-- Unique constraint to prevent duplicate entries
CREATE UNIQUE INDEX idx_user_progress_tracking_unique
    ON user_progress_tracking(user_plant_instance_id, checklist_item_key);
```

## Relationships

### Foreign Key Relationships
- `plant_growth_data.plant_id` → `plants.id` (ONE-TO-ONE)
- `user_plant_instances.user_id` → `users.id` (MANY-TO-ONE)
- `user_plant_instances.plant_id` → `plants.id` (MANY-TO-ONE)
- `user_progress_tracking.user_plant_instance_id` → `user_plant_instances.id` (MANY-TO-ONE)

### Data Flow
1. **Plant Selection**: User selects from existing `plants` table
2. **Data Generation**: If `plant_growth_data` doesn't exist, generate via API
3. **Instance Creation**: Create `user_plant_instances` record
4. **Progress Tracking**: Create `user_progress_tracking` records for checklist items
5. **Timeline Updates**: Update `current_stage` based on days elapsed

## Migration Strategy

### Phase 1: Create Tables
```sql
-- Create tables in dependency order
-- 1. plant_growth_data (depends on plants)
-- 2. user_plant_instances (depends on users, plants)
-- 3. user_progress_tracking (depends on user_plant_instances)
```

### Phase 2: Initial Data Population
- No immediate data population required
- Data will be generated on-demand via API calls

### Phase 3: Validation
- Verify foreign key constraints
- Test cascade deletions
- Validate JSON structure constraints

## Performance Considerations

### Indexing Strategy
- Primary keys for all tables
- Foreign key indexes for joins
- Composite indexes for common query patterns
- JSON field indexes for frequent JSON queries

### Query Optimization
- Use appropriate JOINs for related data
- Implement pagination for user dashboards
- Cache frequently accessed plant growth data

### Storage Estimates
- `plant_growth_data`: ~500 plants × 50KB JSON ≈ 25MB
- `user_plant_instances`: ~1000 users × 10 plants × 200 bytes ≈ 2MB
- `user_progress_tracking`: ~10,000 instances × 10 items × 100 bytes ≈ 10MB

Total additional storage: ~37MB (manageable)

## Backup and Maintenance

### Backup Strategy
- Include new tables in existing backup routines
- Consider JSON field compression for long-term storage
- Regular cleanup of inactive plant instances

### Data Integrity
- Regular foreign key constraint validation
- JSON schema validation for API responses
- Cleanup of orphaned progress tracking records

## Security Considerations

### Data Access
- Ensure users can only access their own plant instances
- Validate user permissions for all operations
- Sanitize JSON input to prevent injection

### API Rate Limiting
- Implement rate limiting for external API calls
- Cache plant growth data to minimize API usage
- Handle API failures gracefully