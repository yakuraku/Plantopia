# Chat Feature Testing Guide

## Overview
This document outlines the testing strategy for the AI Chat Feature (Iteration 3 - Session 3).

## Test Coverage Required

### 1. Repository Layer Tests (`tests/unit/test_chat_repository.py`)

**ChatRepository Methods to Test:**
- `create_chat()` - Creates chat session
- `get_chat_by_id()` - Retrieves chat with relationships
- `get_user_chats()` - Filters by user, type, active status
- `update_chat()` - Updates chat fields
- `delete_chat()` - Hard deletes chat (cascades to messages)
- `update_token_count()` - Increments tokens and message count
- `add_message()` - Creates new message
- `get_chat_messages()` - Retrieves messages with pagination
- `get_recent_messages()` - Gets last N messages for history buffer
- `count_messages()` - Counts total messages
- `delete_expired_chats()` - Cleanup job for expired chats
- `deactivate_chat()` - Soft delete (marks inactive)
- `get_chat_with_instance()` - Finds chat by user + instance
- `count_user_chats()` - Counts user's chats

**Key Test Scenarios:**
- Create general and plant-specific chats
- Validate expiration time calculation
- Test message retrieval ordering
- Verify cascade delete works (deleting chat deletes messages)
- Test cleanup job removes expired chats only
- Validate foreign key relationships

### 2. Service Layer Tests (`tests/unit/test_plant_chat_service.py`)

**PlantChatService Methods to Test:**
- `start_general_chat()` - Creates general Q&A session
- `start_plant_chat()` - Creates plant-specific session with validation
- `send_message()` - Processes message with AI, saves history
- `get_chat_history()` - Returns full conversation with ownership check
- `end_chat()` - Deactivates chat with ownership validation
- `cleanup_expired_chats()` - Background cleanup job
- `_build_chat_context()` - Builds plant context string (private)
- `_check_token_limit()` - Validates token limits (private)
- `_estimate_tokens()` - Token estimation (private)
- `_call_gemini_with_history()` - Gemini API integration (private)

**Key Test Scenarios:**
- Mock Gemini API calls to avoid actual API usage
- Test token limit enforcement (warn at 100k, reject at 120k)
- Validate agriculture guardrails applied in system prompt
- Test image upload decoding and processing
- Verify message history buffer limits (last 30 messages)
- Test chat expiration validation
- Validate ownership checks (user can't access other's chats)
- Test plant context building with full instance details

### 3. Integration Tests (`tests/integration/test_chat_endpoints.py`)

**Endpoints to Test:**
- POST `/chat/general/start` - Start general chat
- POST `/chat/general/message` - Send general message
- POST `/chat/plant/{instance_id}/start` - Start plant chat
- POST `/chat/plant/message` - Send plant message
- GET `/chat/{chat_id}/history` - Get full history
- DELETE `/chat/{chat_id}` - End chat

**Key Test Scenarios:**
- Test 201 status on chat creation
- Test 404 for non-existent chats/instances
- Test 403 for unauthorized access (wrong user)
- Test 400 for token limit exceeded
- Validate response schemas match Pydantic models
- Test query parameters (user_id for ownership)
- Test base64 image handling
- Verify error messages are descriptive

## Running Tests

```bash
# Run all chat tests
pytest tests/unit/test_chat_repository.py tests/unit/test_plant_chat_service.py tests/integration/test_chat_endpoints.py -v

# Run with coverage
pytest tests/ --cov=app.repositories.chat_repository --cov=app.services.plant_chat_service --cov=app.api.endpoints.plant_chat

# Run specific test file
pytest tests/unit/test_chat_repository.py -v
```

## Test Data Setup

**Required Fixtures:**
- Mock database session (AsyncMock)
- Sample User instances
- Sample UserPlantInstance instances
- Sample chat sessions (general + plant-specific)
- Sample messages (user + assistant)
- Mock Gemini API responses

## Mock Strategies

### Mocking Gemini API:
```python
@patch('app.services.plant_chat_service.genai.GenerativeModel')
async def test_send_message_with_ai_response(mock_model):
    mock_response = MagicMock()
    mock_response.text = "This is a test AI response"
    mock_model.return_value.generate_content.return_value = mock_response

    # Test send_message
    result = await service.send_message(chat_id=1, user_message="Test")
    assert result['ai_response'] == "This is a test AI response"
```

### Mocking Database:
```python
@pytest.fixture
async def mock_db_session():
    session = AsyncMock(spec=AsyncSession)
    # Configure session.execute() to return mock results
    return session
```

## Critical Edge Cases

1. **Token Limits:**
   - Chat at 99,999 tokens → allow with no warning
   - Chat at 100,000 tokens → allow with warning
   - Chat at 120,000 tokens → reject

2. **Expiration:**
   - Message sent before expiration → success
   - Message sent after expiration → 404 error
   - Cleanup job deletes only expired chats

3. **Ownership:**
   - User accessing own chat → success
   - User accessing other's chat → 403 error

4. **Image Upload:**
   - Valid base64 image → decoded and sent to Gemini
   - Invalid base64 → validation error
   - No image → text-only processing

5. **Chat Types:**
   - General chat: no instance_id, no plant context
   - Plant chat: has instance_id, includes full plant context

## Performance Considerations

- Message history buffer: Last 30 messages only (prevents memory issues)
- Token estimation: ~1.3x word count (fast approximation)
- Cleanup job: Should complete in <1 second for 1000 expired chats

## Manual Testing Checklist

- [ ] Start general chat and ask farming questions
- [ ] Test agriculture guardrails (ask non-farming question)
- [ ] Upload image of plant and get diagnosis
- [ ] Start plant-specific chat with instance
- [ ] Verify plant context appears in AI responses
- [ ] Send 50+ messages to test token tracking
- [ ] Wait 6+ hours and verify chat expires
- [ ] Try accessing expired chat (should fail)
- [ ] End chat manually and verify it's inactive
- [ ] Verify cleanup job runs successfully

## Future Test Additions

When implementing background cleanup job:
- Add scheduled job tests
- Test concurrent chat access
- Load testing for multiple simultaneous chats
- Test Gemini API rate limiting scenarios
