# Iteration 3 - Remaining Development Tasks

**Document Created**: 2025-01-10
**Session Context**: Continuation of IT3 Plant Tracking Feature
**Status**: Suburb Enhancement Partially Complete, Chat Feature Pending

---

## Session Summary - What Was Discussed

### User Requirements from Latest Session:

1. **CRITICAL FIX - Model Change** ✅ COMPLETED
   - Changed from `gemini-2.0-flash-exp` (deprecated) to `gemini-2.5-flash-lite`
   - Updated in `app/services/external_api_service.py` line 29

2. **Suburb & Climate Data Integration** ⏳ IN PROGRESS
   - Add suburb_id to user_data expectations
   - Fetch suburb details and climate data (temperature, UV, AQI, humidity)
   - Pass to Gemini API for more localized plant advice
   - Climate data should be fetched on-demand, NOT stored (changes daily)

3. **Start Date Usage** - CLARIFIED
   - `start_date` stored in `user_plant_instances` table (already implemented)
   - NOT sent to Gemini API
   - Used INTERNALLY to calculate actual calendar dates from timeline days
   - Example: start_date = Jan 1, 2026 + flowering at day 25 = Jan 25, 2026
   - Timeline data from Gemini (in days) stored in `plant_growth_data` (shared across users)
   - Actual calendar dates calculated per user instance

4. **NEW FEATURE: AI Chat System** 🆕 NOT STARTED
   - General Q&A chat (agriculture/farming questions, no plant context)
   - Plant-specific chat (linked to user_plant_instance, includes full context)
   - Image upload support (see: https://ai.google.dev/gemini-api/docs/image-understanding)
   - Agriculture-only guardrails (reject non-farming questions politely)
   - Token tracking (120k limit per conversation, warn at 100k)
   - Auto-delete chat history after 6 hours
   - Chat history buffer for context (prompt + response pairs)

---

## Current Implementation Status

### ✅ Completed in This Session:

1. **Model Fix**
   - File: `app/services/external_api_service.py`
   - Changed `self.model_name = "gemini-2.5-flash-lite"` (line 29)

2. **Enhanced Context Builder**
   - File: `app/services/external_api_service.py`
   - Updated `_build_plant_context()` method (lines 234-291)
   - Now accepts optional `location_data` parameter
   - Adds LOCATION & CLIMATE section when suburb data available

3. **Location Context Fetcher**
   - File: `app/services/plant_growth_service.py`
   - Added `ClimateRepository` import and initialization
   - Created `_get_location_context()` method (lines 26-84)
   - Fetches suburb details and latest climate data
   - Returns formatted dict for Gemini context

### ⏳ Partially Complete (Needs Finishing):

1. **Update generate_complete_plant_data() to use location_data**
   - File: `app/services/external_api_service.py`
   - Methods `generate_requirements()`, `generate_instructions()`, `generate_timeline()`
   - Need to accept optional `location_data` parameter
   - Pass to `_build_plant_context()`

2. **Update PlantGrowthService.get_or_generate_growth_data()**
   - File: `app/services/plant_growth_service.py`
   - Extract `suburb_id` from `user_data`
   - Call `_get_location_context(suburb_id)`
   - Pass location_context to `gemini_service.generate_complete_plant_data()`

3. **Update Pydantic Schemas**
   - File: `app/schemas/plant_tracking.py`
   - Add `suburb_id: Optional[int]` to `UserDataInput` schema
   - Already has other fields, just add suburb_id

4. **Add Calendar Dates to Timeline Responses**
   - File: `app/services/plant_instance_service.py`
   - Method: `get_instance_details()`
   - For each stage in timeline, calculate actual dates:
     - `start_date_actual = instance.start_date + timedelta(days=stage["start_day"])`
     - `end_date_actual = instance.start_date + timedelta(days=stage["end_day"])`
   - Add to response: `actual_start_date`, `actual_end_date`

---

## Chat Feature - Complete Implementation Plan

### Overview:
- Two types of chat: **General Q&A** and **Plant-Specific**
- Uses Gemini 2.5 Flash-Lite API
- Supports text + image uploads
- Agriculture-only guardrails
- Token tracking and limits
- Auto-cleanup after 6 hours

### Database Schema:

#### 1. UserPlantChat Model
**Table**: `user_plant_chats`
**Purpose**: Store chat sessions

```python
class UserPlantChat(Base):
    __tablename__ = 'user_plant_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_plant_instance_id = Column(Integer, ForeignKey('user_plant_instances.id'), nullable=True)
    # NULL = general chat, NOT NULL = plant-specific chat

    chat_type = Column(String(20), nullable=False)  # 'general' or 'plant_specific'
    total_tokens = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # created_at + 6 hours

    # Relationships
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")
```

#### 2. ChatMessage Model
**Table**: `chat_messages`
**Purpose**: Store individual Q&A pairs

```python
class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('user_plant_chats.id', ondelete='CASCADE'), nullable=False)

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # Image support
    image_url = Column(String(500), nullable=True)  # GCS URL if image uploaded
    has_image = Column(Boolean, default=False)

    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat = relationship("UserPlantChat", back_populates="messages")
```

#### 3. Alembic Migration
**File**: `alembic/versions/{timestamp}_add_chat_tables.py`

Create migration with:
- Both tables with all columns
- Foreign key constraints
- Indexes on: user_id, chat_type, is_active, expires_at, created_at
- Cascade delete for messages when chat deleted

### Service Layer:

#### PlantChatService
**File**: `app/services/plant_chat_service.py`

**Key Methods:**

```python
class PlantChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ChatRepository(db)
        self.gemini_service = get_gemini_service()
        self.plant_instance_service = PlantInstanceService(db)
        self.growth_service = PlantGrowthService(db)

    async def start_general_chat(self, user_id: int) -> Dict[str, Any]:
        """Start a new general Q&A chat session"""
        # Create chat session with type='general'
        # Set expires_at = now + 6 hours
        # Return chat_id

    async def start_plant_chat(self, user_id: int, instance_id: int) -> Dict[str, Any]:
        """Start a new plant-specific chat session"""
        # Validate instance belongs to user
        # Fetch plant details, climate data, timeline
        # Create chat session with type='plant_specific'
        # Build initial context for first message
        # Return chat_id

    async def send_message(
        self,
        chat_id: int,
        user_message: str,
        image_data: Optional[bytes] = None,
        image_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message in an existing chat"""
        # Validate chat exists and not expired
        # Check token limit (warn if > 100k, reject if > 120k)
        # Build message history buffer (last N messages)
        # Build context (plant-specific or general)
        # Call Gemini API with history + new message + optional image
        # Save user message and AI response to database
        # Update chat total_tokens and last_message_at
        # Return response

    async def get_chat_history(self, chat_id: int, user_id: int) -> List[Dict]:
        """Get full chat history"""
        # Validate user owns chat
        # Return all messages with timestamps

    async def end_chat(self, chat_id: int, user_id: int) -> bool:
        """End a chat session manually"""
        # Mark chat as inactive
        # Don't delete yet (cleanup job handles that)

    async def cleanup_expired_chats(self) -> int:
        """Delete chats older than 6 hours (background job)"""
        # Find chats where expires_at < now
        # Delete them (cascade deletes messages)
        # Return count deleted

    async def _build_chat_context(
        self,
        chat: UserPlantChat,
        include_plant_context: bool = False
    ) -> str:
        """Build context for Gemini API call"""
        # For general: Basic agriculture expert context
        # For plant-specific: Include plant details, climate, timeline

    async def _check_token_limit(self, chat: UserPlantChat, estimated_new: int) -> Dict:
        """Check if adding new tokens would exceed limits"""
        # Return {"allowed": bool, "warning": bool, "current": int, "limit": 120000}

    async def _call_gemini_with_history(
        self,
        chat: UserPlantChat,
        new_message: str,
        message_history: List[Dict],
        image_data: Optional[bytes] = None
    ) -> str:
        """Call Gemini API with chat history and optional image"""
        # Build full prompt with system instruction + history + new message
        # If image: use Gemini image understanding API
        # Apply agriculture guardrails in system prompt
        # Return AI response
```

**Agriculture Guardrails - System Prompt:**

```
You are an expert horticulturist and agricultural advisor specializing in home gardening,
farming, and plant care. You MUST ONLY answer questions related to:
- Plant growing and care
- Gardening techniques
- Soil and composting
- Pest management
- Agriculture and farming
- Horticulture
- Plant diseases and health
- Harvesting and crop management

If the user asks about anything outside these topics, politely respond with:
"I'm designed specifically to help with agriculture, farming, and plant-related questions.
I cannot assist with other topics. Please ask me anything about growing plants,
gardening techniques, or farming practices!"

Be helpful, practical, and provide actionable advice. Adapt your explanations to the
user's experience level when known.
```

#### ChatRepository
**File**: `app/repositories/chat_repository.py`

**Key Methods:**

```python
class ChatRepository:
    async def create_chat(self, chat_data: Dict) -> UserPlantChat
    async def get_chat_by_id(self, chat_id: int) -> Optional[UserPlantChat]
    async def get_user_chats(self, user_id: int, active_only: bool) -> List[UserPlantChat]
    async def update_chat(self, chat_id: int, update_data: Dict) -> UserPlantChat
    async def delete_chat(self, chat_id: int) -> bool
    async def add_message(self, message_data: Dict) -> ChatMessage
    async def get_chat_messages(self, chat_id: int, limit: Optional[int]) -> List[ChatMessage]
    async def delete_expired_chats(self) -> int
    async def update_token_count(self, chat_id: int, tokens: int) -> None
```

### API Endpoints:

**File**: `app/api/endpoints/plant_chat.py`

#### 1. POST /chat/general/start
**Request**: `{"user_id": 1}`
**Response**: `{"chat_id": 123, "expires_at": "2025-01-10T18:00:00", "message": "General chat started"}`

#### 2. POST /chat/general/message
**Request**:
```json
{
  "chat_id": 123,
  "message": "How do I compost kitchen waste?",
  "image": "base64_encoded_image_optional"
}
```
**Response**:
```json
{
  "chat_id": 123,
  "user_message": "How do I compost kitchen waste?",
  "ai_response": "Composting kitchen waste is a great sustainable practice...",
  "tokens_used": 250,
  "total_tokens": 1250,
  "token_warning": false
}
```

#### 3. POST /chat/plant/{instance_id}/start
**Request**: `{"user_id": 1}`
**Response**:
```json
{
  "chat_id": 124,
  "instance_id": 456,
  "plant_name": "Basil",
  "expires_at": "2025-01-10T18:00:00",
  "message": "Plant-specific chat started"
}
```

#### 4. POST /chat/plant/{instance_id}/message
**Request**:
```json
{
  "chat_id": 124,
  "message": "Why are my basil leaves turning yellow?",
  "image": "base64_encoded_image_optional"
}
```
**Response**: Same as general message

#### 5. GET /chat/{chat_id}/history
**Query Params**: `?user_id=1`
**Response**:
```json
{
  "chat_id": 123,
  "chat_type": "general",
  "created_at": "2025-01-10T12:00:00",
  "expires_at": "2025-01-10T18:00:00",
  "total_tokens": 1250,
  "message_count": 5,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "How do I compost?",
      "created_at": "2025-01-10T12:01:00",
      "has_image": false
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Composting is...",
      "created_at": "2025-01-10T12:01:05"
    }
  ]
}
```

#### 6. DELETE /chat/{chat_id}
**Query Params**: `?user_id=1`
**Response**: `{"message": "Chat ended successfully", "chat_id": 123}`

### Pydantic Schemas:

**File**: `app/schemas/plant_tracking.py` (add to existing file)

```python
# Chat Schemas
class StartChatRequest(BaseModel):
    user_id: int

class ChatMessageRequest(BaseModel):
    chat_id: int
    message: str
    image: Optional[str] = None  # Base64 encoded

class ChatMessageResponse(BaseModel):
    chat_id: int
    user_message: str
    ai_response: str
    tokens_used: int
    total_tokens: int
    token_warning: bool
    message: Optional[str] = None

class ChatHistoryMessage(BaseModel):
    id: int
    role: str
    content: str
    has_image: bool
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    chat_id: int
    chat_type: str
    created_at: datetime
    expires_at: datetime
    total_tokens: int
    message_count: int
    messages: List[ChatHistoryMessage]

class StartChatResponse(BaseModel):
    chat_id: int
    instance_id: Optional[int] = None
    plant_name: Optional[str] = None
    expires_at: datetime
    message: str
```

### Image Upload Support:

**Gemini API Reference**: https://ai.google.dev/gemini-api/docs/image-understanding

**Implementation in PlantChatService:**

```python
async def _call_gemini_with_image(
    self,
    prompt: str,
    image_bytes: bytes,
    image_filename: str
) -> str:
    """Call Gemini API with image"""
    import PIL.Image
    import io

    # Convert bytes to PIL Image
    image = PIL.Image.open(io.BytesIO(image_bytes))

    # Configure model
    model = genai.GenerativeModel(self.gemini_service.model_name)

    # Generate content with image + text
    response = await asyncio.to_thread(
        model.generate_content,
        [prompt, image]
    )

    return response.text
```

**Frontend expects:**
- Base64 encoded image in request
- Backend decodes and sends to Gemini
- Response includes AI analysis of image

### Background Job - Cleanup:

**File**: `app/services/cleanup_service.py` or add to existing scheduler

```python
async def cleanup_expired_chats():
    """Background job to delete chats older than 6 hours"""
    async with get_async_db() as db:
        chat_service = PlantChatService(db)
        deleted_count = await chat_service.cleanup_expired_chats()
        logger.info(f"Deleted {deleted_count} expired chat sessions")
```

**Schedule**: Run every hour via cron or APScheduler

---

## Implementation Checklist

### Step 1: Complete Suburb Enhancement
- [ ] Update `generate_requirements()`, `generate_instructions()`, `generate_timeline()` in external_api_service.py to accept location_data
- [ ] Update `get_or_generate_growth_data()` in plant_growth_service.py to call _get_location_context() and pass to Gemini
- [ ] Add `suburb_id: Optional[int]` to UserDataInput schema
- [ ] Update `get_instance_details()` to add actual calendar dates to timeline stages
- [ ] Test suburb enhancement with real suburb_id

### Step 2: Chat Database Models
- [ ] Add UserPlantChat model to database.py
- [ ] Add ChatMessage model to database.py
- [ ] Create Alembic migration for chat tables
- [ ] Test migration locally (if possible)

### Step 3: Chat Repository
- [ ] Create chat_repository.py
- [ ] Implement all CRUD methods
- [ ] Implement cleanup_expired_chats()

### Step 4: Chat Service
- [ ] Create plant_chat_service.py
- [ ] Implement start_general_chat()
- [ ] Implement start_plant_chat() with plant context
- [ ] Implement send_message() with history buffer
- [ ] Implement image upload support
- [ ] Implement agriculture guardrails
- [ ] Implement token tracking and limits
- [ ] Implement get_chat_history()
- [ ] Implement end_chat()

### Step 5: Chat API Endpoints
- [ ] Create plant_chat.py endpoints file
- [ ] POST /chat/general/start
- [ ] POST /chat/general/message
- [ ] POST /chat/plant/{instance_id}/start
- [ ] POST /chat/plant/{instance_id}/message
- [ ] GET /chat/{chat_id}/history
- [ ] DELETE /chat/{chat_id}
- [ ] Register router in __init__.py

### Step 6: Chat Schemas
- [ ] Add chat schemas to plant_tracking.py
- [ ] StartChatRequest, ChatMessageRequest
- [ ] ChatMessageResponse, ChatHistoryResponse
- [ ] StartChatResponse

### Step 7: Background Cleanup
- [ ] Implement cleanup_expired_chats background job
- [ ] Schedule to run every hour

### Step 8: Testing
- [ ] Unit tests for chat_repository
- [ ] Unit tests for plant_chat_service
- [ ] Integration tests for chat endpoints
- [ ] Test image upload functionality
- [ ] Test agriculture guardrails
- [ ] Test token limits
- [ ] Test 6-hour expiration

### Step 9: Documentation
- [ ] Update frontend_integration_guide.md with chat endpoints
- [ ] Add chat examples and usage patterns
- [ ] Document image upload format
- [ ] Update IT3_PROGRESS.md

---

## Key Technical Notes

### Token Estimation:
- Input tokens ≈ word count * 1.3
- Response tokens tracked from Gemini response
- Store cumulative total in chat.total_tokens
- Warn at 100k, reject at 120k

### Chat History Buffer:
- Don't send ALL messages to Gemini (too many tokens)
- Send last 10-15 message pairs (20-30 messages total)
- Format: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`

### Image Processing:
- Accept base64 from frontend
- Decode to bytes
- Convert to PIL Image
- Send to Gemini with text prompt
- Return combined text response

### Agriculture Guardrails:
- Implemented in system prompt
- Gemini will self-filter non-agriculture questions
- No backend validation needed (trust AI)
- Log rejected attempts for monitoring

### Expiration Logic:
- Set expires_at = created_at + timedelta(hours=6)
- Check on every message send
- Background job deletes WHERE expires_at < NOW()
- Cascade delete removes all messages

---

## Files That Need Changes

### New Files to Create:
1. `app/models/database.py` - Add UserPlantChat and ChatMessage models
2. `alembic/versions/{timestamp}_add_chat_tables.py` - Migration
3. `app/repositories/chat_repository.py` - New file
4. `app/services/plant_chat_service.py` - New file
5. `app/api/endpoints/plant_chat.py` - New file
6. `tests/unit/test_chat_repository.py` - New file
7. `tests/unit/test_plant_chat_service.py` - New file
8. `tests/integration/test_chat_endpoints.py` - New file

### Existing Files to Modify:
1. `app/services/external_api_service.py` - Update generate methods for location_data
2. `app/services/plant_growth_service.py` - Use _get_location_context() in get_or_generate
3. `app/schemas/plant_tracking.py` - Add suburb_id to UserDataInput, add chat schemas
4. `app/api/endpoints/__init__.py` - Register plant_chat router
5. `app/services/plant_instance_service.py` - Add calendar dates to timeline
6. `Iteration_3_Documentation/frontend_integration_guide.md` - Document chat feature
7. `IT3_PROGRESS.md` - Update with chat implementation

---

## Important Reminders for Next Session

1. **Model Name**: `gemini-2.5-flash-lite` (NOT 2.0-flash-exp - deprecated)
2. **Start Date**: Already stored, used for calendar date calculations, NOT sent to Gemini
3. **Suburb Data**: Fetch on-demand from existing endpoints, don't store climate data
4. **Chat Types**: Two separate flows - general and plant-specific
5. **Image Upload**: Use Gemini image understanding API
6. **Guardrails**: Agriculture-only, polite rejection for off-topic
7. **Token Limits**: 120k max, warn at 100k
8. **Auto-Delete**: 6 hours from created_at
9. **Message Buffer**: Last 10-15 pairs sent to Gemini, not entire history

---

## Questions to Resolve (if any)

*None currently - all requirements clarified in this session*

---

**End of Document**
