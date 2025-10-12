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
  "climate_goal": "sustainable gardening",
  "start_date": "2024-03-15"
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
- 'start_date' - The start date that the user is going to start their planting journey

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

Note on user_data persistence:
- On first or subsequent calls, backend will persist user_data into the database:
  - users table:
    - email → users.email
    - name → users.name
    - suburb_id → users.suburb_id
  - user_profiles table (created/updated automatically):
    - experience_level → user_profiles.experience_level
    - garden_type → user_profiles.garden_type
    - available_space → user_profiles.available_space_m2
    - climate_goal → user_profiles.climate_goals
- Non-model fields are ignored safely.

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

### 1.a Upsert User (Create/Update User & Profile)
**Endpoint**: `POST /tracking/user/upsert`

**Request Body**:
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

**Behavior**:
- Creates user if not exists; otherwise updates `name`/`suburb_id` (invalid `suburb_id` defaults to 1 or resolves from `suburb_name`).
- Creates/updates `user_profiles` with `experience_level`, `garden_type`, `available_space_m2`, `climate_goals`.
- Safe to call before `/tracking/start` to persist user context separately.

### 2. Get User's Plant Instances
**Endpoint**: `GET /tracking/user/{email}`

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
    "Ensure 6-8 hours of direct sunlight daily",
    "Gently shake plants to aid pollination"
  ]
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

---

## Implementation Notes (Backend)

### ✅ Completed Implementation - 2025-01-10

All endpoints described in this guide have been **fully implemented and tested**. The backend is production-ready for frontend integration.

### Actual Implementation Details

**Base URL:**
```
/api/v1  (prefix added by router registration)
```

**Key Differences from Original Spec:**

1. **User Data Field Naming:**
   - The backend uses snake_case consistently
   - Frontend can use camelCase and send to backend as-is
   - Example accepted user_data format:
     ```json
     {
       "experience_level": "beginner",
       "location": "Melbourne, VIC",
       "climate_zone": "10",
       "garden_type": "balcony",
       "available_space_m2": 5.0
     }
     ```

2. **Tips Endpoint Response:**
   - Actual response returns simpler format: `{"instance_id": 1, "current_stage": "germination", "tips": ["Tip 1", "Tip 2"]}`
   - Tips are returned as array of strings (not objects with category/importance)
   - Limit query parameter supported (default: 3, max: 10)

3. **Instructions Endpoint Response:**
   - Actual format: `{"plant_id": 1, "instructions": [{"category": "Planting", "steps": [{"step": "text", "details": "text"}]}]}`
   - Instructions grouped by category rather than numbered steps
   - No image_url or duration fields in initial implementation

4. **Additional Endpoints Implemented:**
   - `POST /tracking/instance/{instance_id}/initialize-checklist` - Creates checklist items from requirements
   - `POST /tracking/instance/{instance_id}/auto-update-stage` - Auto-calculates and updates stage based on days elapsed

### Gemini AI Integration

The backend uses **Google Gemini 2.0 Flash Exp** for generating personalized plant data:
- Requirements checklists
- Setup instructions
- Growth timelines (5-7 stages per plant)
- Care tips (15-20 tips per stage)

**Data Generation:**
- Happens on first tracking start per plant_id
- Cached in `plant_growth_data` table
- Personalized based on user_data sent in requests
- Cache invalidation available if needed

**Rate Limiting:**
- 15 requests/minute per API key
- 250K tokens/minute per API key
- 1000 requests/day per API key
- Automatic key rotation across 4-5 keys

### Database Schema

**Three New Tables:**

1. **plant_growth_data**
   - Primary key: plant_id
   - Stores AI-generated JSON data
   - Shared across all users for same plant

2. **user_plant_instances**
   - Tracks individual user's plants
   - Links to plant_id and user_id
   - Stores nickname, start_date, current_stage, etc.

3. **user_progress_tracking**
   - Tracks checklist completion
   - Links to user_plant_instance_id
   - Stores completion status and notes

### Testing

**Comprehensive test suite included:**
- Unit tests: `tests/unit/test_plant_tracking_repositories.py` (repository layer)
- Unit tests: `tests/unit/test_plant_tracking_services.py` (service layer)
- Integration tests: `tests/integration/test_plant_tracking_endpoints.py` (API endpoints)

**To run tests:**
```bash
pytest tests/unit/test_plant_tracking_*.py
pytest tests/integration/test_plant_tracking_endpoints.py
```

### Deployment Checklist

**Before deploying to production:**

1. ✅ Run Alembic migration: `alembic upgrade head`
2. ✅ Ensure `gemini_api_keys.txt` is present in root with 4-5 valid API keys
3. ⚠️ Update environment variables if needed
4. ⚠️ Test all endpoints with real data on staging
5. ⚠️ Monitor Gemini API quota usage in first week

### Frontend Development Tips

**Quick Start:**
1. Start with `POST /tracking/start` to create a test instance
2. Use instance_id from response to test other endpoints
3. Use `GET /tracking/instance/{instance_id}` for comprehensive data
4. Test pagination with `GET /tracking/user/{email}?page=1&limit=5`

**Common Gotchas:**
- Always send user_data in start_tracking request (required for AI generation)
- Instance IDs are separate from plant IDs (don't confuse them)
- Use checklist_item_key format: `{category}_{item}` (e.g., "tools_garden_trowel")
- Progress percentage is auto-calculated from days_elapsed vs maturity_date
- Deactivate endpoint is soft-delete (can be reactivated if needed)

**Performance:**
- First call per plant_id will be slower (3-5 seconds for AI generation)
- Subsequent calls are fast (cached data)
- User dashboard endpoint supports pagination (use it!)

### API Response Formats

**Success Response (200/201):**
```json
{
  "data_field_1": "value",
  "data_field_2": "value"
}
```

**Error Response (4xx/5xx):**
```json
{
  "detail": "Error message here"
}
```

### Contact & Support

**For Questions:**
- Backend implemented by: Yash (dev-yash branch)
- Implementation docs: `IT3_PROGRESS.md` in repo root
- Detailed specs: `Iteration_3_Documentation/` folder

**Known Limitations:**
- Migration testing pending (will test on GCP deployment)
- Gemini API costs need monitoring in production

---

## AI Chat Feature (NEW - Session 3)

### Overview
The chat feature provides AI-powered agriculture Q&A with two modes:
1. **General Chat**: Ask any farming/gardening questions
2. **Plant-Specific Chat**: Get personalized advice for your tracked plants

### Chat Feature Capabilities
- **Gemini 2.5 Flash-Lite** AI model with agriculture expertise
- **Image Upload**: Upload plant photos for diagnosis (base64 encoded)
- **Agriculture Guardrails**: AI politely rejects non-farming questions
- **Token Tracking**: 120k limit per conversation (warns at 100k)
- **Auto-Expiration**: Chats expire after 6 hours
- **Context Memory**: Last 15 message pairs maintained in conversation

### Chat API Endpoints

#### 1. Start General Chat
**Endpoint**: `POST /chat/general/start`

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "chat_id": 456,
  "chat_type": "general",
  "expires_at": "2025-01-10T18:00:00",
  "message": "General agriculture chat started. Ask me anything about gardening, farming, or plant care!"
}
```

#### 2. Send General Message
**Endpoint**: `POST /chat/general/message`

**Request Body** (Text Only):
```json
{
  "chat_id": 456,
  "message": "How do I compost kitchen waste?"
}
```

**Request Body** (With Image):
```json
{
  "chat_id": 456,
  "message": "What's wrong with my plant leaves?",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA..."
}
```

**Response**:
```json
{
  "chat_id": 456,
  "user_message": "How do I compost kitchen waste?",
  "ai_response": "Composting kitchen waste is a great sustainable practice! Here's how...",
  "tokens_used": 250,
  "total_tokens": 1250,
  "token_warning": false,
  "message": null
}
```

**Response** (With Token Warning):
```json
{
  "chat_id": 456,
  "user_message": "...",
  "ai_response": "...",
  "tokens_used": 2500,
  "total_tokens": 105000,
  "token_warning": true,
  "message": "Warning: You have used 105000 tokens out of 120000. Consider starting a new conversation soon."
}
```

#### 3. Start Plant-Specific Chat
**Endpoint**: `POST /chat/plant/{instance_id}/start`

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "chat_id": 789,
  "chat_type": "plant_specific",
  "instance_id": 456,
  "plant_name": "Cherry Tomato",
  "plant_nickname": "My First Tomato",
  "expires_at": "2025-01-10T18:00:00",
  "message": "Plant-specific chat started for My First Tomato (Cherry Tomato). I have full context about your plant!"
}
```

#### 4. Send Plant-Specific Message
**Endpoint**: `POST /chat/plant/message`

Same request/response format as general message endpoint.
AI will have full plant context: current stage, timeline, care tips, location.

#### 5. Get Chat History
**Endpoint**: `GET /chat/{chat_id}/history?email={email}`

**Response**:
```json
{
  "chat_id": 456,
  "chat_type": "general",
  "created_at": "2025-01-10T12:00:00",
  "expires_at": "2025-01-10T18:00:00",
  "total_tokens": 5250,
  "message_count": 10,
  "is_active": true,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "How do I compost?",
      "has_image": false,
      "created_at": "2025-01-10T12:01:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Composting is a natural process...",
      "has_image": false,
      "created_at": "2025-01-10T12:01:05"
    }
  ]
}
```

#### 6. End Chat
**Endpoint**: `DELETE /chat/{chat_id}?email={email}`

**Response**:
```json
{
  "success": true,
  "message": "Chat 456 ended successfully",
  "chat_id": 456
}
```

### Chat UI/UX Guidelines

#### Chat Interface Requirements
1. **Two Entry Points**:
   - "Ask AI" button in main navigation (general chat)
   - "Chat about this plant" in plant detail view (plant-specific)

2. **Message Display**:
   - User messages: Right-aligned, distinct color
   - AI messages: Left-aligned, different color
   - Timestamps for each message
   - Image thumbnails for messages with photos

3. **Input Controls**:
   - Text input field (multiline, auto-resize)
   - Image upload button (camera icon)
   - Send button (disabled while waiting for response)
   - Character/token counter (optional)

4. **Status Indicators**:
   - Typing indicator while AI responds ("AI is thinking...")
   - Token usage warning (at 100k tokens)
   - Expiration countdown (show when <30 mins left)
   - "Chat expired" message if expired

5. **Image Upload**:
   - Accept JPEG, PNG formats
   - Max size: 5MB
   - Preview before sending
   - Convert to base64 for API

#### Mobile Considerations
- Full-screen chat view on mobile
- "Back" button to exit chat
- Keyboard management (auto-focus, proper scrolling)
- Image camera/gallery selection

### Image Upload Implementation

**Frontend JavaScript Example**:
```javascript
async function uploadImage(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // Get base64 string (remove data:image/...;base64, prefix)
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Usage
const file = imageInput.files[0];
const base64Image = await uploadImage(file);

const response = await fetch('/api/v1/chat/general/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chat_id: currentChatId,
    message: "What's wrong with my plant?",
    image: base64Image
  })
});
```

### Agriculture Guardrails Behavior

**Accepted Topics**:
- Plant growing and care
- Gardening techniques
- Soil and composting
- Pest management
- Agriculture and farming
- Horticulture
- Plant diseases
- Harvesting

**Example of Rejection**:
```
User: "What's the weather tomorrow?"

AI: "I'm designed specifically to help with agriculture, farming, and plant-related questions. I cannot assist with other topics. Please ask me anything about growing plants, gardening techniques, or farming practices!"
```

### Token Management

**Token Estimation**:
- Input: ~1.3x word count
- Response: Tracked from AI
- Cumulative total stored per chat

**Limits**:
- **100,000 tokens**: Warning displayed
- **120,000 tokens**: New messages rejected

**Frontend Recommendations**:
- Show token usage in chat header: "5,250 / 120,000 tokens used"
- Yellow warning at 100k
- Red warning + disable input at 120k
- "Start New Chat" button when limit reached

### Error Handling

**Chat Errors**:
- `404` - Chat not found or expired
- `403` - User doesn't own this chat
- `400` - Token limit exceeded
- `500` - AI processing failed

**Example Error Handling**:
```javascript
try {
  const response = await sendChatMessage(chatId, message);
  displayAIResponse(response.ai_response);

  if (response.token_warning) {
    showTokenWarning(response.total_tokens);
  }
} catch (error) {
  if (error.status === 404) {
    showError("This chat has expired. Please start a new conversation.");
    disableChatInput();
  } else if (error.status === 400 && error.message.includes('token limit')) {
    showError("Token limit reached. Please start a new chat.");
    disableChatInput();
  } else {
    showError("Failed to send message. Please try again.");
  }
}
```

### Performance Optimization

**Chat Loading**:
- Load only recent messages on chat open (last 20-30)
- Implement "Load More" for older messages
- Cache chat list locally

**Image Optimization**:
- Compress images before base64 encoding
- Show thumbnail in chat, full size on tap
- Lazy load message images

**Real-time Updates**:
- Poll for new messages if multi-device support needed
- Or use WebSocket for real-time chat (future enhancement)

### Testing Checklist

- [ ] Start general chat successfully
- [ ] Send text messages and get AI responses
- [ ] Upload image and get analysis
- [ ] Test agriculture guardrails (ask non-farming question)
- [ ] Start plant-specific chat from plant detail page
- [ ] Verify plant context appears in AI responses
- [ ] Send 50+ messages to test token tracking
- [ ] Verify warning appears at 100k tokens
- [ ] Verify rejection at 120k tokens
- [ ] Get chat history (all messages appear)
- [ ] End chat manually
- [ ] Try accessing expired chat (should fail)
- [ ] Verify expired chat shows in inactive list

### Chat Database Schema

**Two New Tables**:

1. **user_plant_chats**
   - Stores chat sessions
   - Links to user_id and optionally user_plant_instance_id
   - Tracks total_tokens, message_count, expires_at

2. **chat_messages**
   - Stores individual messages
   - Links to chat_id (cascade delete)
   - Stores role (user/assistant), content, has_image

### Deployment Notes

**Before Deploying Chat Feature**:
1. Run migration: `alembic upgrade head`
2. Verify Gemini API keys are valid
3. Test agriculture guardrails work correctly
4. Monitor token usage in first week
5. Set up cleanup job for expired chats (cron: hourly)

**Cleanup Job** (Run hourly):
```bash
# Deletes chats where expires_at < NOW()
# Automatically cascades to delete all messages
# Returns count of deleted chats
```

### Known Chat Limitations
- No multi-device sync (chat tied to session)
- No push notifications for AI responses
- No voice input/output
- Image analysis may be slower than text (5-10 seconds)
- English language only (for now)

### Future Chat Enhancements
- Voice input for questions
- Multi-language support
- Chat sharing/export
- AI proactive suggestions
- Integration with plant disease database

---

## Documentation Sync Policy

Any integration-impacting change must update this guide in the same PR. Keep the API contract and docs in sync:

- Endpoint paths and prefixes: add/modify/deprecate (including version/group changes)
- Request contract: body/query/path parameters added/removed/changed
- Defaults and fallbacks: e.g., invalid `user_data.suburb_id` defaults to `1`
- Response contract: fields, types, enums, pagination
- Auth and rate limits: auth method, required headers, limit changes
- Error codes: add/modify/deprecate and semantics

Minimum process:
1. Update code and the relevant sections in this file (examples, field notes, errors)
2. For breaking changes, add a migration note in "Version Information"
3. Update frontend mocks/examples so they work copy-paste
