# Iteration 3 - Testing & Validation Plan

**Purpose**: Comprehensive testing of all Iteration 3 features before frontend integration
**Date**: 2025-10-11
**Status**: Ready to Begin
**Estimated Time**: 4-6 hours

---

## Overview

This document outlines the complete testing strategy for Iteration 3, covering:
- Plant Tracking System (12 endpoints)
- AI Chat System (6 endpoints)
- Database migrations and schema validation
- Integration with existing features
- Performance and error handling

---

## Phase 1: Environment Setup & Validation

### 1.1 Database Setup ✓ Complete First
**Priority**: CRITICAL
**Time**: 15 minutes

**Tasks:**
- [ ] Pull latest changes from main branch
- [ ] Verify database connection string is correct
- [ ] Run migrations: `alembic upgrade head`
- [ ] Verify 5 new tables created:
  - plant_growth_data
  - user_plant_instances
  - user_progress_tracking
  - user_plant_chats
  - chat_messages
- [ ] Check all indexes are created
- [ ] Verify foreign key constraints

**Commands:**
```bash
git pull origin main
alembic current
alembic upgrade head
alembic current  # Should show: b9d2f7e8a3c1
```

**Database Verification Query:**
```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('plant_growth_data', 'user_plant_instances', 'user_progress_tracking', 'user_plant_chats', 'chat_messages');

-- Check indexes
SELECT tablename, indexname FROM pg_indexes
WHERE tablename IN ('user_plant_chats', 'chat_messages');
```

**Success Criteria:**
- ✓ All 5 tables exist
- ✓ 7 indexes created (5 for chats, 2 for messages)
- ✓ Foreign keys properly configured
- ✓ No migration errors

---

### 1.2 Gemini API Validation ✓ Complete Second
**Priority**: CRITICAL
**Time**: 10 minutes

**Tasks:**
- [ ] Verify `gemini_api_keys.txt` exists in project root
- [ ] Check file has 4-5 valid API keys (format: `user,key`)
- [ ] Test API key loading in service
- [ ] Verify key rotation works
- [ ] Check rate limiting configuration

**Test Script:**
```python
# test_gemini_setup.py
from app.services.external_api_service import get_gemini_service

service = get_gemini_service()
print(f"Loaded {len(service.api_keys)} API keys")
print(f"Current model: {service.model_name}")
print(f"Current key user: {service._get_current_key_id()}")

# Test key rotation
for i in range(len(service.api_keys)):
    service._rotate_key()
    print(f"Rotated to: {service._get_current_key_id()}")
```

**Success Criteria:**
- ✓ 4-5 keys loaded successfully
- ✓ Model name is "gemini-2.5-flash-lite"
- ✓ Key rotation cycles through all keys
- ✓ No import errors

---

### 1.3 Server Startup ✓ Complete Third
**Priority**: CRITICAL
**Time**: 5 minutes

**Tasks:**
- [ ] Start FastAPI server
- [ ] Verify no import errors
- [ ] Check all routers registered
- [ ] Access Swagger docs at /docs

**Commands:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Verify in Browser:**
- http://localhost:8000/docs
- Check for "plant-tracking" and "plant-chat" tags
- Count endpoints: Should see 18+ endpoints for Iteration 3

**Success Criteria:**
- ✓ Server starts without errors
- ✓ Swagger UI loads successfully
- ✓ All 18 endpoints visible
- ✓ No 500 errors on startup

---

## Phase 2: Plant Tracking System Testing

### 2.1 Start Plant Tracking (AI Generation)
**Priority**: HIGH
**Time**: 10 minutes
**Endpoint**: `POST /tracking/start`

**Test Case 1: Basic Plant Tracking Start**
```bash
curl -X POST "http://localhost:8000/tracking/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {
      "email": "test@plantopia.com",
      "name": "Test User",
      "suburb_id": 1,
      "experience_level": "beginner",
      "garden_type": "balcony",
      "available_space": 5.0,
      "climate_goal": "sustainable gardening"
    },
    "plant_id": 1,
    "plant_nickname": "My Test Tomato",
    "start_date": "2025-10-11",
    "location_details": "Balcony - South side"
  }'
```

**Expected Response:**
- Status: 201 Created
- Response time: 3-5 seconds (first call with AI generation)
- Fields: instance_id, plant_nickname, start_date, expected_maturity_date, current_stage, message

**Validation Checklist:**
- [ ] AI generation completes successfully
- [ ] plant_growth_data table has new entry
- [ ] user_plant_instances table has new entry
- [ ] instance_id returned is valid integer
- [ ] expected_maturity_date is calculated correctly
- [ ] current_stage is "germination"

**Test Case 2: Same Plant (Cached Data)**
```bash
# Start tracking same plant again (should use cached AI data)
curl -X POST "http://localhost:8000/tracking/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {...},
    "plant_id": 1,
    "plant_nickname": "My Second Tomato",
    "start_date": "2025-10-11"
  }'
```

**Expected:**
- Response time: <500ms (using cached data)
- New instance_id (different from first)
- Same plant_id

---

### 2.2 Get User Plant Instances
**Priority**: HIGH
**Time**: 5 minutes
**Endpoint**: `GET /tracking/user/{user_id}`

**Test Case 1: Get All Instances**
```bash
curl -X GET "http://localhost:8000/tracking/user/1?active_only=true&page=1&limit=20"
```

**Expected Response:**
- Status: 200 OK
- Fields: plants[], total_count, active_count, pagination{}
- Each plant has: instance_id, plant_name, plant_nickname, current_stage, days_elapsed, progress_percentage

**Validation Checklist:**
- [ ] Returns both test instances created above
- [ ] Pagination info is correct
- [ ] days_elapsed calculated from start_date
- [ ] progress_percentage is between 0-100
- [ ] active_only filter works (test with false)

**Test Case 2: Pagination**
```bash
curl -X GET "http://localhost:8000/tracking/user/1?page=1&limit=1"
curl -X GET "http://localhost:8000/tracking/user/1?page=2&limit=1"
```

**Expected:**
- Page 1 has 1 plant
- Page 2 has 1 plant
- total_pages matches total_count

---

### 2.3 Get Instance Details
**Priority**: HIGH
**Time**: 5 minutes
**Endpoint**: `GET /tracking/instance/{instance_id}`

**Test Case:**
```bash
# Use instance_id from 2.1
curl -X GET "http://localhost:8000/tracking/instance/1"
```

**Expected Response:**
- Status: 200 OK
- Sections: plant_details{}, tracking_info{}, timeline{stages[]}, current_tips[]

**Validation Checklist:**
- [ ] plant_details has plant_name, scientific_name, category
- [ ] tracking_info has all fields from start_tracking
- [ ] timeline has 5-7 growth stages
- [ ] Each stage has: stage_name, start_day, end_day, description, key_indicators
- [ ] current_tips array has 2-5 tips
- [ ] Timeline stages have is_completed and is_current flags

---

### 2.4 AI-Generated Content Endpoints
**Priority**: MEDIUM
**Time**: 10 minutes

**Test Case 1: Requirements Checklist**
```bash
curl -X GET "http://localhost:8000/tracking/requirements/1"
```

**Expected:**
- Status: 200 OK
- requirements[] with categories (Seeds & Plants, Tools, Growing Medium, etc.)
- Each item has: item, quantity, optional, notes

**Validation Checklist:**
- [ ] At least 3 categories
- [ ] At least 10 total items
- [ ] Some items marked optional: true
- [ ] Quantities are specified

**Test Case 2: Setup Instructions**
```bash
curl -X GET "http://localhost:8000/tracking/instructions/1"
```

**Expected:**
- instructions[] with numbered steps
- Each step has: step, title, description, duration, tips[]

**Validation Checklist:**
- [ ] At least 5 steps
- [ ] Steps are numbered sequentially
- [ ] Each step has 2-3 tips
- [ ] Durations are reasonable

**Test Case 3: Growth Timeline**
```bash
curl -X GET "http://localhost:8000/tracking/timeline/1"
```

**Expected:**
- total_days matches plant maturity
- stages[] ordered by stage_order

**Validation Checklist:**
- [ ] 5-7 stages
- [ ] No gaps in day ranges
- [ ] last stage end_day matches total_days

---

### 2.5 Progress Management
**Priority**: MEDIUM
**Time**: 10 minutes

**Test Case 1: Initialize Checklist**
```bash
curl -X POST "http://localhost:8000/tracking/instance/1/initialize-checklist"
```

**Expected:**
- Creates entries in user_progress_tracking table
- Returns count of items created

**Test Case 2: Mark Item Complete**
```bash
curl -X POST "http://localhost:8000/tracking/checklist/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": 1,
    "checklist_item_key": "seeds_tomato",
    "is_completed": true,
    "user_notes": "Purchased from local store"
  }'
```

**Expected:**
- success: true
- progress_summary shows updated counts

**Test Case 3: Update Progress**
```bash
curl -X PUT "http://localhost:8000/tracking/instance/1/progress" \
  -H "Content-Type: application/json" \
  -d '{
    "current_stage": "seedling",
    "user_notes": "First leaves appeared!",
    "location_details": "Moved to sunnier spot"
  }'
```

**Expected:**
- Instance updated successfully
- New stage reflected in get_instance_details

**Test Case 4: Update Nickname**
```bash
curl -X PUT "http://localhost:8000/tracking/instance/1/nickname" \
  -H "Content-Type: application/json" \
  -d '{"plant_nickname": "Super Tomato"}'
```

**Test Case 5: Auto-Update Stage**
```bash
curl -X POST "http://localhost:8000/tracking/instance/1/auto-update-stage"
```

**Expected:**
- Calculates days elapsed
- Updates stage if needed

---

### 2.6 Get Current Stage Tips
**Priority**: LOW
**Time**: 5 minutes
**Endpoint**: `GET /tracking/instance/{instance_id}/tips`

**Test Case:**
```bash
curl -X GET "http://localhost:8000/tracking/instance/1/tips?limit=3"
```

**Expected:**
- 3 tips for current stage
- Random selection each call

---

### 2.7 Deactivate Instance
**Priority**: LOW
**Time**: 3 minutes
**Endpoint**: `DELETE /tracking/instance/{instance_id}`

**Test Case:**
```bash
curl -X DELETE "http://localhost:8000/tracking/instance/1"
```

**Expected:**
- is_active set to false
- Still appears in database
- Doesn't appear in active_only=true queries

---

## Phase 3: AI Chat System Testing

### 3.1 General Chat - Start & Basic Messages
**Priority**: HIGH
**Time**: 10 minutes

**Test Case 1: Start General Chat**
```bash
curl -X POST "http://localhost:8000/chat/general/start" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

**Expected Response:**
- Status: 201 Created
- chat_id, chat_type: "general", expires_at (6 hours from now)

**Validation:**
- [ ] user_plant_chats table has new entry
- [ ] chat_type is "general"
- [ ] user_plant_instance_id is NULL
- [ ] expires_at is created_at + 6 hours
- [ ] total_tokens is 0

**Test Case 2: Send Text Message**
```bash
curl -X POST "http://localhost:8000/chat/general/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 1,
    "message": "How do I start composting at home?"
  }'
```

**Expected Response:**
- Status: 200 OK
- ai_response with helpful composting advice
- tokens_used and total_tokens
- token_warning: false

**Validation:**
- [ ] AI response is relevant to composting
- [ ] 2 messages in chat_messages table (user + assistant)
- [ ] tokens_used > 0
- [ ] total_tokens updated in user_plant_chats
- [ ] Response time: 2-5 seconds

---

### 3.2 Agriculture Guardrails Testing
**Priority**: HIGH
**Time**: 10 minutes

**Test Case 1: Farming Question (Should Answer)**
```bash
curl -X POST "http://localhost:8000/chat/general/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 1,
    "message": "What are the best vegetables to grow in winter?"
  }'
```

**Expected:**
- Helpful answer about winter vegetables
- AI provides specific recommendations

**Test Case 2: Non-Farming Question (Should Reject)**
```bash
curl -X POST "http://localhost:8000/chat/general/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 1,
    "message": "What is the weather forecast for tomorrow?"
  }'
```

**Expected:**
- AI response: "I'm designed specifically to help with agriculture, farming, and plant-related questions..."
- Polite rejection message

**Validation:**
- [ ] Non-farming questions rejected consistently
- [ ] Rejection message is polite
- [ ] Still counts toward token usage

**Test Case 3: Edge Case Questions**
```bash
# Test borderline questions
"Tell me about urban farming" # Should answer (farming-related)
"What's the best car for farmers?" # Should reject (not farming)
"How do I cook tomatoes?" # Should reject (cooking, not growing)
"How do I preserve harvested vegetables?" # Should answer (post-harvest)
```

---

### 3.3 Plant-Specific Chat
**Priority**: HIGH
**Time**: 10 minutes

**Test Case 1: Start Plant Chat**
```bash
curl -X POST "http://localhost:8000/chat/plant/1/start" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

**Expected:**
- chat_type: "plant_specific"
- instance_id: 1
- plant_name and plant_nickname in response
- user_plant_instance_id is NOT NULL

**Test Case 2: Send Plant-Specific Message**
```bash
curl -X POST "http://localhost:8000/chat/plant/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 2,
    "message": "Why are my tomato leaves turning yellow?"
  }'
```

**Expected:**
- AI response includes context about user's specific plant
- May reference current stage or timeline
- Personalized advice

**Validation:**
- [ ] AI knows plant name and current stage
- [ ] Response is contextual to user's plant
- [ ] More specific than general chat responses

---

### 3.4 Image Upload Testing
**Priority**: HIGH
**Time**: 15 minutes

**Prerequisites:**
- Prepare test images:
  - Healthy plant image
  - Diseased plant image
  - Non-plant image (to test guardrails)

**Test Case 1: Upload Plant Image**
```bash
# First, convert image to base64
cat test_plant.jpg | base64 > image_base64.txt

# Send with message
curl -X POST "http://localhost:8000/chat/general/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 1,
    "message": "What is wrong with my plant?",
    "image": "<paste base64 string here>"
  }'
```

**Expected:**
- Response time: 5-10 seconds (image analysis)
- AI analyzes image and provides diagnosis
- has_image: true in chat_messages table

**Validation:**
- [ ] Image decoded successfully
- [ ] Gemini receives image
- [ ] AI provides image-specific analysis
- [ ] Message saved with has_image flag

**Test Case 2: Multiple Images in Conversation**
```bash
# Send several images in same chat
# Test if context maintained
```

**Test Case 3: Large Image (Edge Case)**
```bash
# Try 5MB+ image
# Should handle or return appropriate error
```

---

### 3.5 Token Limit Testing
**Priority**: MEDIUM
**Time**: 15 minutes

**Test Case 1: Normal Usage (Below Warning)**
```bash
# Send 10-15 normal messages
# Check total_tokens stays below 100k
```

**Expected:**
- token_warning: false
- Tokens accumulate normally

**Test Case 2: Approach Warning Threshold**
```bash
# Manually set total_tokens to 99,000 in database
UPDATE user_plant_chats SET total_tokens = 99000 WHERE id = 1;

# Send message
curl -X POST "http://localhost:8000/chat/general/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 1,
    "message": "Tell me about crop rotation and why it is important for soil health..."
  }'
```

**Expected:**
- total_tokens crosses 100k
- token_warning: true
- message: "Warning: You have used X tokens out of 120000..."

**Test Case 3: Exceed Hard Limit**
```bash
# Set total_tokens to 119,000
UPDATE user_plant_chats SET total_tokens = 119000 WHERE id = 1;

# Send message
curl -X POST "http://localhost:8000/chat/general/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 1,
    "message": "Very long message to exceed limit..."
  }'
```

**Expected:**
- Status: 400 Bad Request
- Error: "Token limit exceeded"
- Message NOT saved

**Validation:**
- [ ] Warning triggers at 100k
- [ ] Hard limit enforced at 120k
- [ ] Error message is clear

---

### 3.6 Chat History & Management
**Priority**: MEDIUM
**Time**: 10 minutes

**Test Case 1: Get Chat History**
```bash
curl -X GET "http://localhost:8000/chat/1/history?user_id=1"
```

**Expected:**
- All messages in chronological order
- Both user and assistant messages
- has_image flags correct
- Timestamps for each message

**Validation:**
- [ ] All messages returned
- [ ] Correct order (oldest to newest)
- [ ] Message count matches database

**Test Case 2: Ownership Validation**
```bash
# Try to access chat owned by different user
curl -X GET "http://localhost:8000/chat/1/history?user_id=999"
```

**Expected:**
- Status: 403 Forbidden
- Error: "User does not own chat"

**Test Case 3: End Chat**
```bash
curl -X DELETE "http://localhost:8000/chat/1?user_id=1"
```

**Expected:**
- is_active set to false
- Chat still exists in database
- Messages preserved

---

### 3.7 Chat Expiration Testing
**Priority**: MEDIUM
**Time**: 10 minutes

**Test Case 1: Expired Chat Detection**
```bash
# Manually set expires_at to past time
UPDATE user_plant_chats SET expires_at = NOW() - INTERVAL '1 hour' WHERE id = 1;

# Try to send message
curl -X POST "http://localhost:8000/chat/general/message" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 1,
    "message": "This should fail"
  }'
```

**Expected:**
- Status: 404 Not Found
- Error: "Chat has expired"

**Test Case 2: Cleanup Job (Manual Test)**
```python
# Run cleanup manually
from app.services.plant_chat_service import PlantChatService
from app.core.database import get_async_db

async def test_cleanup():
    async with get_async_db() as db:
        service = PlantChatService(db)
        count = await service.cleanup_expired_chats()
        print(f"Deleted {count} expired chats")

# Run and verify expired chats are deleted
```

**Validation:**
- [ ] Expired chats are deleted
- [ ] Messages cascade deleted
- [ ] Active chats preserved

---

## Phase 4: Integration Testing

### 4.1 Suburb & Climate Integration
**Priority**: HIGH
**Time**: 10 minutes

**Test Case:**
```bash
# Start tracking with valid suburb_id
curl -X POST "http://localhost:8000/tracking/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {
      "suburb_id": 5,
      "experience_level": "beginner",
      ...
    },
    "plant_id": 2,
    ...
  }'
```

**Validation:**
- [ ] Suburb data fetched from database
- [ ] Climate data (temp, UV, AQI) retrieved
- [ ] AI recommendations include location context
- [ ] Check plant_growth_data.data_source_info for location data

**Test AI Output:**
- AI should mention local conditions
- Advice should be tailored to climate
- UV/temperature warnings if applicable

---

### 4.2 Calendar Dates in Timeline
**Priority**: MEDIUM
**Time**: 5 minutes

**Test Case:**
```bash
# Start tracking on specific date
curl -X POST "http://localhost:8000/tracking/start" \
  -d '{"start_date": "2025-01-01", ...}'

# Get instance details
curl -X GET "http://localhost:8000/tracking/instance/{instance_id}"
```

**Validation:**
- [ ] Timeline stages include actual_start_date and actual_end_date
- [ ] Dates calculated correctly: start_date + start_day = actual_start_date
- [ ] Example: Jan 1 + day 25 = Jan 25
- [ ] All stages have calendar dates

---

### 4.3 Message History Buffer
**Priority**: MEDIUM
**Time**: 10 minutes

**Test Case:**
```bash
# Send 50+ messages to same chat
# Verify only last 30 sent to Gemini
```

**Validation:**
- [ ] Chat has 50+ messages in database
- [ ] Gemini receives only last 30
- [ ] Older messages not included in context
- [ ] No memory issues

---

## Phase 5: Error Handling & Edge Cases

### 5.1 Invalid Requests
**Priority**: HIGH
**Time**: 15 minutes

**Test Cases:**

1. **Invalid Plant ID**
```bash
curl -X POST "http://localhost:8000/tracking/start" \
  -d '{"plant_id": 99999, ...}'
```
Expected: 404 Not Found

2. **Invalid Instance ID**
```bash
curl -X GET "http://localhost:8000/tracking/instance/99999"
```
Expected: 404 Not Found

3. **Invalid Chat ID**
```bash
curl -X POST "http://localhost:8000/chat/general/message" \
  -d '{"chat_id": 99999, ...}'
```
Expected: 404 Not Found

4. **Missing Required Fields**
```bash
curl -X POST "http://localhost:8000/tracking/start" \
  -d '{"plant_id": 1}'  # Missing user_data
```
Expected: 422 Validation Error

5. **Empty Nickname**
```bash
curl -X PUT "http://localhost:8000/tracking/instance/1/nickname" \
  -d '{"plant_nickname": ""}'
```
Expected: 400 Bad Request

---

### 5.2 Gemini API Failure Scenarios
**Priority**: MEDIUM
**Time**: 10 minutes

**Test Cases:**

1. **Temporary API Failure (Retry Logic)**
```bash
# Temporarily make API keys invalid
# Send tracking start request
# Should retry and eventually fail gracefully
```

2. **Rate Limit Reached**
```bash
# Make 20+ rapid requests
# Should rotate keys
# Should handle rate limiting
```

**Validation:**
- [ ] Retry logic works (3 attempts)
- [ ] Exponential backoff applied
- [ ] Key rotation on failure
- [ ] Clear error messages

---

### 5.3 Database Constraint Violations
**Priority**: LOW
**Time**: 5 minutes

**Test Cases:**

1. **Duplicate Checklist Item**
```bash
# Mark same item complete twice
# Should update, not create duplicate
```

2. **Orphaned Chat Messages**
```bash
# Delete chat
# Verify messages cascade deleted
```

**Validation:**
- [ ] Unique constraints enforced
- [ ] Cascade deletes work
- [ ] Foreign keys prevent orphans

---

## Phase 6: Performance Testing

### 6.1 Response Times
**Priority**: MEDIUM
**Time**: 10 minutes

**Benchmarks:**

| Endpoint | First Call | Cached | Target |
|----------|-----------|--------|---------|
| Start Tracking (AI gen) | 3-5s | N/A | <10s |
| Start Tracking (cached) | <500ms | N/A | <1s |
| Get Instance Details | <200ms | N/A | <500ms |
| General Chat Message | 2-5s | N/A | <10s |
| Chat with Image | 5-10s | N/A | <15s |

**Test:**
```bash
# Measure response times
time curl -X POST "http://localhost:8000/tracking/start" ...
```

**Validation:**
- [ ] All endpoints within target times
- [ ] No timeouts
- [ ] Consistent performance

---

### 6.2 Database Query Performance
**Priority**: MEDIUM
**Time**: 10 minutes

**Test:**
```sql
-- Enable query timing
\timing

-- Test key queries
SELECT * FROM user_plant_instances WHERE user_id = 1;
SELECT * FROM chat_messages WHERE chat_id = 1 ORDER BY created_at;
SELECT * FROM user_plant_chats WHERE expires_at < NOW();
```

**Validation:**
- [ ] Queries use indexes (check EXPLAIN)
- [ ] Sub-second response times
- [ ] No table scans on large tables

---

### 6.3 Concurrent Requests
**Priority**: LOW
**Time**: 10 minutes

**Test:**
```bash
# Use Apache Bench or similar
ab -n 100 -c 10 http://localhost:8000/tracking/user/1
```

**Validation:**
- [ ] No errors under load
- [ ] Response times stay reasonable
- [ ] No database deadlocks

---

## Phase 7: Automated Test Suite

### 7.1 Run Unit Tests
**Priority**: HIGH
**Time**: 5 minutes

**Commands:**
```bash
# Run all plant tracking tests
pytest tests/unit/test_plant_tracking_repositories.py -v
pytest tests/unit/test_plant_tracking_services.py -v

# Run integration tests
pytest tests/integration/test_plant_tracking_endpoints.py -v
```

**Expected:**
- All 85+ tests pass
- No failures
- Coverage report shows good coverage

**Validation:**
- [ ] Repository tests: 40+ pass
- [ ] Service tests: 20+ pass
- [ ] Endpoint tests: 25+ pass
- [ ] No skipped tests

---

### 7.2 Chat Feature Tests (When Written)
**Priority**: MEDIUM
**Time**: 5 minutes

**Note:** Tests are documented in CHAT_TESTING_GUIDE.md but not yet implemented.

**Action Items:**
- [ ] Review CHAT_TESTING_GUIDE.md
- [ ] Decide if tests needed before frontend integration
- [ ] Create tests if needed (3-4 hours)

---

## Phase 8: Documentation Validation

### 8.1 API Documentation Review
**Priority**: HIGH
**Time**: 15 minutes

**Tasks:**
- [ ] Review Swagger docs at /docs
- [ ] Verify all 18 endpoints documented
- [ ] Test "Try it out" for each endpoint
- [ ] Check request/response schemas
- [ ] Verify examples are accurate

---

### 8.2 Frontend Integration Guide
**Priority**: HIGH
**Time**: 10 minutes

**Tasks:**
- [ ] Review frontend_integration_guide.md
- [ ] Verify examples match actual API behavior
- [ ] Check error codes are correct
- [ ] Test provided curl commands
- [ ] Validate response formats

---

## Phase 9: Final Checks

### 9.1 Code Quality
**Priority**: MEDIUM
**Time**: 10 minutes

**Tasks:**
- [ ] Run linter: `pylint app/`
- [ ] Check for TODO comments
- [ ] Verify no hardcoded credentials
- [ ] Check console for warnings

---

### 9.2 Security Checks
**Priority**: HIGH
**Time**: 10 minutes

**Tasks:**
- [ ] Verify gemini_api_keys.txt in .gitignore
- [ ] Check no API keys in code
- [ ] Verify ownership checks work
- [ ] Test SQL injection prevention (parameterized queries)
- [ ] Check CORS settings if needed

---

### 9.3 Deployment Readiness
**Priority**: HIGH
**Time**: 10 minutes

**Checklist:**
- [ ] Migrations tested and working
- [ ] API keys configured correctly
- [ ] All endpoints functional
- [ ] Error handling tested
- [ ] Documentation complete
- [ ] Tests passing (or documented)
- [ ] Performance acceptable
- [ ] No blocking bugs found

---

## Phase 10: Test Results Documentation

### 10.1 Create Test Results Report
**Priority**: HIGH
**Time**: 20 minutes

**Template:**
```markdown
# Iteration 3 Testing Results

## Summary
- **Date**: [Date]
- **Tester**: [Name]
- **Duration**: [Hours]
- **Status**: [PASS/FAIL/PARTIAL]

## Test Results by Phase

### Phase 1: Environment Setup
- [✓] Database migrations successful
- [✓] Gemini API keys loaded
- [✓] Server starts without errors

### Phase 2: Plant Tracking
- [✓] Start tracking works
- [✓] AI generation successful
- [✓] Cached data works
- [Issues]: None

### Phase 3: AI Chat
- [✓] General chat functional
- [✓] Plant-specific chat works
- [✓] Image upload successful
- [✓] Guardrails working
- [Issues]: None

### Known Issues
1. [Description]
   - Severity: High/Medium/Low
   - Steps to reproduce:
   - Expected:
   - Actual:

### Recommendations
1. [Recommendation]

## Sign-off
Ready for frontend integration: YES/NO
```

---

### 10.2 Create Bug Reports (If Issues Found)
**Priority**: HIGH
**Time**: As needed

**Bug Report Template:**
```markdown
# Bug Report: [Title]

**Severity**: Critical/High/Medium/Low
**Component**: Plant Tracking / Chat / Database / Integration

## Description
[Clear description of the issue]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- Branch: main
- Commit: ee9a6e6
- Database: PostgreSQL
- Python: 3.x

## Additional Context
- Error messages:
- Screenshots:
- Logs:
```

---

## Phase 11: Frontend Handoff

### 11.1 Create API Testing Guide for Frontend
**Priority**: HIGH
**Time**: 30 minutes

**Include:**
- Quick start guide (5 min setup)
- Example requests for each endpoint
- Common scenarios walkthrough
- Error handling examples
- Tips and gotchas

---

### 11.2 Frontend Team Briefing Document
**Priority**: HIGH
**Time**: 20 minutes

**Create:**
```markdown
# Frontend Integration - Iteration 3 Features

## Ready to Use
- ✓ 18 API endpoints live and tested
- ✓ Swagger docs available
- ✓ Example requests provided
- ✓ Error codes documented

## Getting Started
1. Access API docs: http://[server]/docs
2. Review frontend_integration_guide.md
3. Test with provided curl examples
4. Start with plant tracking, then chat

## Key Points
- Plant tracking requires AI generation on first use
- Chat images must be base64 encoded
- Token limits enforced (120k max)
- Chats expire after 6 hours

## Support
- API questions: [Contact]
- Bug reports: [GitHub Issues]
- Documentation: [Link]
```

---

## Appendix: Quick Reference

### Essential Commands
```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Run migrations
alembic upgrade head

# Run tests
pytest tests/ -v

# Check database
psql -d plantopia -c "SELECT * FROM user_plant_chats LIMIT 5;"

# View logs
tail -f logs/app.log
```

### Common Issues & Solutions

**Issue**: Migration fails
**Solution**: Check database connection, verify previous migrations applied

**Issue**: Gemini API errors
**Solution**: Verify API keys valid, check rate limits

**Issue**: 500 errors on startup
**Solution**: Check imports, verify all dependencies installed

**Issue**: Slow response times
**Solution**: Check database indexes, verify Gemini API responding

---

## Testing Progress Tracker

Use this checklist to track overall progress:

- [ ] Phase 1: Environment Setup (30 min)
- [ ] Phase 2: Plant Tracking (60 min)
- [ ] Phase 3: AI Chat (90 min)
- [ ] Phase 4: Integration (25 min)
- [ ] Phase 5: Error Handling (30 min)
- [ ] Phase 6: Performance (30 min)
- [ ] Phase 7: Automated Tests (10 min)
- [ ] Phase 8: Documentation (25 min)
- [ ] Phase 9: Final Checks (30 min)
- [ ] Phase 10: Test Results (20 min)
- [ ] Phase 11: Frontend Handoff (50 min)

**Total Estimated Time**: 6-7 hours

---

**Document Version**: 1.0
**Last Updated**: 2025-10-11
**Status**: Ready for Testing
