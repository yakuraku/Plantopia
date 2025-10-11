# Comprehensive Test Plan - Email Authentication & Plant Guide Features

**Date**: 2025-10-11
**Testing Focus**: Email-based authentication, Auto-user creation, Plant tracking, Chat, Favorites, Guide features

---

## 🎯 Test Objectives

1. Verify email-based authentication works across all endpoints
2. Test automatic user creation on first API interaction
3. Validate plant tracking workflow with real Gemini API calls
4. Test data reuse for same plants across different users
5. Verify chat functionality (general & plant-specific)
6. Test plant and guide favorites
7. Validate multi-plant tracking per user

---

## 👥 Test Users

### User 1: Sarah Johnson
**Profile**:
- Email: `sarah.johnson.test@plantopia.com`
- Name: Sarah Johnson
- Experience: Beginner
- Garden Type: Balcony
- Available Space: 5.0 m²
- Suburb: Melbourne CBD
- Climate Goal: Learn sustainable urban gardening

**Plants to Grow**:
1. **Carrot - Cosmic Purple** (Day 0 - Starting fresh)
   - Location: Balcony pot 1
   - First time growing this plant → Will call Gemini API

2. **Cherry Tomato** (Day 25 - Already growing)
   - Location: Balcony pot 2
   - Started 25 days ago

3. **Basil** (Day 15 - Recently started)
   - Location: Indoor windowsill
   - Started 15 days ago

**Expected Behaviors**:
- Auto-create user on first `/tracking/start` call
- Generate new plant data via Gemini API for Carrot
- Reuse existing Basil data if available
- Test checklist completion
- Test stage transitions
- Test chat with plant-specific context
- Add plants and guides to favorites

---

### User 2: Mike Chen
**Profile**:
- Email: `mike.chen.test@plantopia.com`
- Name: Mike Chen
- Experience: Advanced
- Garden Type: Backyard
- Available Space: 15.0 m²
- Suburb: Richmond
- Climate Goal: Maximize yield with crop rotation

**Plants to Grow**:
1. **Carrot - Cosmic Purple** (Day 10 - Started 10 days ago)
   - Location: Backyard raised bed 1
   - Same plant as Sarah → Will **reuse Gemini data** from Sarah's plant

2. **Capsicum - California Wonder** (Day 35 - Mature plant)
   - Location: Backyard raised bed 2
   - Mid-stage growth

3. **Lettuce - Mignonette** (Day 20 - Growing well)
   - Location: Backyard raised bed 3
   - Different location for crop rotation

4. **Zucchini - Black Beauty** (Day 5 - Just started)
   - Location: Backyard ground
   - Large space plant

**Expected Behaviors**:
- Auto-create user on first API call
- **Reuse Carrot data from Sarah** (no new Gemini call)
- Generate new data for other plants via Gemini
- Test multi-plant management
- Test advanced user workflows
- Test chat for plant advice
- Test favorites management

---

## 🧪 Test Scenarios

### Scenario 1: New User Registration & First Plant (Sarah)
**Endpoint Flow**:
1. `POST /api/v1/tracking/start` - Start tracking Carrot
   - **Expected**: Auto-create Sarah in database
   - **Expected**: Call Gemini API for plant data (checklists, timeline, care tips)
   - **Expected**: Create `plant_growth_data` entry
   - **Expected**: Create `user_plant_instances` entry
   - **Verify**: User exists in database with email
   - **Verify**: `plant_growth_data` has JSON for requirements, stages, tips
   - **Verify**: Instance has start_date, expected_maturity_date

2. `GET /api/v1/tracking/{instance_id}/details` - Get plant details
   - **Expected**: Return timeline with actual calendar dates
   - **Expected**: Show current stage as "germination"
   - **Expected**: Show care tips for germination stage
   - **Verify**: Timeline stages have actual dates from start_date
   - **Verify**: Progress percentage is calculated correctly

3. `GET /api/v1/tracking/{instance_id}/checklist` - Get requirements checklist
   - **Expected**: Return categorized checklist (tools, materials, preparation)
   - **Verify**: JSON structure matches schema
   - **Verify**: Items can be marked as completed

4. `POST /api/v1/tracking/{instance_id}/checklist` - Complete checklist items
   - **Expected**: Mark items as completed in `user_progress_tracking`
   - **Verify**: `is_completed` = true, `completed_at` timestamp set

5. `GET /api/v1/tracking/{instance_id}/setup-guide` - Get setup instructions
   - **Expected**: Return step-by-step growing instructions
   - **Verify**: Instructions are plant-specific

6. `GET /api/v1/tracking/{instance_id}/timeline` - Get growth timeline
   - **Expected**: Return stages with calendar dates
   - **Expected**: Show current stage highlighted
   - **Verify**: Stages align with time_to_maturity_days

---

### Scenario 2: Existing User Adds More Plants (Sarah)
**Endpoint Flow**:
1. `POST /api/v1/tracking/start` - Start Cherry Tomato (with past start_date = 25 days ago)
   - **Expected**: Recognize existing user by email (no new user creation)
   - **Expected**: Calculate current stage based on days elapsed
   - **Expected**: Call Gemini if Cherry Tomato data doesn't exist
   - **Verify**: User has 2 plant instances now

2. `GET /api/v1/tracking/user/sarah.johnson.test@plantopia.com` - Get all Sarah's plants
   - **Expected**: Return 2 plants (Carrot day 0, Cherry Tomato day 25)
   - **Expected**: Different progress percentages
   - **Expected**: Different current stages
   - **Verify**: Pagination works
   - **Verify**: Active count = 2

3. `POST /api/v1/tracking/start` - Start Basil (indoor, 15 days ago)
   - **Expected**: Add 3rd plant instance
   - **Verify**: Location details saved correctly
   - **Verify**: Each plant has unique instance_id

---

### Scenario 3: Data Reuse for Same Plant (Mike + Carrot)
**Endpoint Flow**:
1. `POST /api/v1/tracking/start` - Mike starts Carrot (same as Sarah)
   - **Expected**: Auto-create Mike in database
   - **Expected**: **Check if `plant_growth_data` exists for Carrot plant_id**
   - **Expected**: **If exists, reuse data (NO Gemini API call)**
   - **Expected**: If not exists, call Gemini API
   - **Verify**: Mike's instance references same `plant_growth_data.plant_id` as Sarah
   - **Verify**: Mike's timeline dates calculated from his start_date (10 days ago)
   - **Verify**: Mike's current stage reflects 10 days of growth

2. `GET /api/v1/tracking/{mike_carrot_instance}/details` - Mike's Carrot details
   - **Expected**: Same checklists/tips as Sarah (shared data)
   - **Expected**: Different timeline dates (Mike started 10 days ago)
   - **Expected**: Different current stage (Mike is further along)
   - **Verify**: Data is personalized (dates, progress) but guidance is shared

---

### Scenario 4: Multi-Plant User (Mike - 4 plants)
**Endpoint Flow**:
1. `POST /api/v1/tracking/start` - Add Capsicum (35 days old)
2. `POST /api/v1/tracking/start` - Add Lettuce (20 days old)
3. `POST /api/v1/tracking/start` - Add Zucchini (5 days old)

4. `GET /api/v1/tracking/user/mike.chen.test@plantopia.com` - Get all Mike's plants
   - **Expected**: Return 4 plants with different stages
   - **Expected**: Proper sorting and pagination
   - **Verify**: Each has correct days_elapsed
   - **Verify**: Progress percentages are accurate

5. `PUT /api/v1/tracking/{instance_id}/progress` - Update stage manually
   - **Expected**: Update current_stage field
   - **Expected**: Save user_notes
   - **Verify**: Stage transition recorded

6. `PUT /api/v1/tracking/{instance_id}/nickname` - Rename plant
   - **Expected**: Update plant_nickname
   - **Verify**: Nickname saved correctly

---

### Scenario 5: Chat - General Agriculture Q&A (Sarah)
**Endpoint Flow**:
1. `POST /api/v1/chat/general/start` - Start general chat
   - **Expected**: Create chat session with chat_type='general'
   - **Expected**: Set expires_at = now + 6 hours
   - **Verify**: Chat session created for Sarah's user_id
   - **Verify**: total_tokens = 0 initially

2. `POST /api/v1/chat/general/message` - Ask: "What's the best way to water balcony plants?"
   - **Expected**: Send to Gemini API with agriculture Q&A prompt
   - **Expected**: Return AI response
   - **Expected**: Save message pair in `chat_messages`
   - **Expected**: Update `total_tokens`, `message_count`, `last_message_at`
   - **Verify**: Response is agriculture-related
   - **Verify**: Token count increases

3. `POST /api/v1/chat/general/message` - Ask: "How much sunlight do herbs need?"
   - **Expected**: Include previous message context (last 15 pairs)
   - **Expected**: AI response considers conversation history
   - **Verify**: Context maintained across messages

4. `GET /api/v1/chat/{chat_id}/history?email=sarah.johnson.test@plantopia.com` - Get history
   - **Expected**: Return all messages in order
   - **Verify**: Both user and assistant messages present
   - **Verify**: Timestamps are correct

5. `DELETE /api/v1/chat/{chat_id}?email=sarah.johnson.test@plantopia.com` - End chat
   - **Expected**: Set is_active = false
   - **Verify**: Chat marked as inactive

---

### Scenario 6: Chat - Plant-Specific Advice (Mike + Carrot)
**Endpoint Flow**:
1. `POST /api/v1/chat/plant/{carrot_instance_id}/start` - Start plant-specific chat
   - **Expected**: Create chat with chat_type='plant_specific'
   - **Expected**: Link to user_plant_instance_id
   - **Expected**: AI receives full plant context (stage, timeline, details)
   - **Verify**: Chat associated with specific plant instance

2. `POST /api/v1/chat/plant/message` - Ask: "My carrot leaves are yellowing, what should I do?"
   - **Expected**: AI receives plant context (Carrot, day 10, current stage, care tips)
   - **Expected**: AI provides plant-specific diagnosis
   - **Verify**: Response references plant stage and timeline
   - **Verify**: Advice is contextual to Carrot

3. `POST /api/v1/chat/plant/message` - Upload image (base64) of yellowing leaves
   - **Expected**: Process image with Gemini Vision API
   - **Expected**: AI analyzes image and provides diagnosis
   - **Expected**: Save image_url if uploaded to storage
   - **Verify**: has_image = true in message
   - **Verify**: Image analysis is relevant

---

### Scenario 7: Plant Favorites (Sarah)
**Endpoint Flow**:
1. `POST /api/v1/favorites` - Favorite Carrot plant
   - **Request**: `{"email": "sarah.johnson.test@plantopia.com", "plant_id": <carrot_id>, "notes": "Love purple carrots!"}`
   - **Expected**: Create entry in `user_favorites`
   - **Verify**: Favorite saved with notes

2. `POST /api/v1/favorites` - Favorite Basil plant
   - **Expected**: Add 2nd favorite
   - **Verify**: Unique constraint prevents duplicates

3. `GET /api/v1/favorites?email=sarah.johnson.test@plantopia.com` - Get favorites
   - **Expected**: Return 2 favorites with plant details
   - **Verify**: Includes plant_name, plant_category, notes

4. `GET /api/v1/favorites/check/{plant_id}?email=sarah.johnson.test@plantopia.com` - Check if favorited
   - **Expected**: Return `{"is_favorite": true}` for Carrot/Basil
   - **Expected**: Return `{"is_favorite": false}` for others

5. `DELETE /api/v1/favorites/{basil_plant_id}?email=sarah.johnson.test@plantopia.com` - Remove Basil
   - **Expected**: Delete favorite entry
   - **Verify**: Only Carrot remains in favorites

---

### Scenario 8: Guide Browsing & Favorites (Both Users)
**Endpoint Flow**:

**Sarah's Guide Journey**:
1. `GET /api/v1/guides/categories` - Browse categories
   - **Expected**: Return all categories (Composting, flowers, grow_guide, etc.)
   - **Verify**: Categories match folder structure

2. `GET /api/v1/guides/Composting` - Browse Composting guides
   - **Expected**: Return all guides in Composting category
   - **Verify**: Includes "Composting for Beginners.md"

3. `GET /api/v1/guides/Composting/Composting for Beginners.md` - Read guide
   - **Expected**: Return full markdown content
   - **Verify**: Content is properly formatted

4. `POST /api/v1/guides/favorites` - Favorite "Composting for Beginners"
   - **Request**: `{"email": "sarah.johnson.test@plantopia.com", "guide_name": "Composting for Beginners.md", "category": "Composting", "notes": "Great starter guide"}`
   - **Expected**: Create entry in `user_guide_favorites`
   - **Verify**: Favorite saved

5. `GET /api/v1/guides/favorites/user?email=sarah.johnson.test@plantopia.com` - Get Sarah's guide favorites
   - **Expected**: Return favorited guides with details
   - **Verify**: Includes guide title, category, notes

**Mike's Guide Journey**:
1. `GET /api/v1/guides/grow_guide` - Browse grow guides
   - **Expected**: Return all grow guides
   - **Verify**: Includes specific plant grow guides

2. `POST /api/v1/guides/favorites` - Favorite "carrot_seeds_grow_guide.md"
   - **Expected**: Add to Mike's favorites
   - **Verify**: Different user can favorite same guide

3. `GET /api/v1/guides/favorites/check/Composting for Beginners.md?email=mike.chen.test@plantopia.com`
   - **Expected**: Return `{"is_favorite": false}` (Mike didn't favorite it)
   - **Verify**: Favorites are user-specific

---

## 🔍 Validation Checks

### Database Validation
- [ ] Users table: Sarah and Mike created with correct emails
- [ ] Users table: google_id is NULL for both (frontend auth)
- [ ] plant_growth_data: Shared data for same plants
- [ ] user_plant_instances: Separate instances per user per plant
- [ ] user_progress_tracking: Checklist completion tracked
- [ ] user_plant_chats: Chat sessions tracked correctly
- [ ] chat_messages: Messages stored with token counts
- [ ] user_favorites: Plant favorites stored
- [ ] user_guide_favorites: Guide favorites stored

### API Behavior Validation
- [ ] Auto-user creation works on first API call
- [ ] Email is accepted instead of user_id everywhere
- [ ] Gemini API called only when plant data doesn't exist
- [ ] Data reuse works for same plants across users
- [ ] Token limits enforced (120k per chat)
- [ ] Chat expiration works (6 hours)
- [ ] Stage auto-updates based on days elapsed
- [ ] Timeline dates calculated from start_date
- [ ] Favorites prevent duplicates (unique constraints)

### Error Handling Validation
- [ ] Invalid email returns 404
- [ ] Duplicate favorites return 400
- [ ] Token limit exceeded returns 400
- [ ] Expired chat returns 404
- [ ] Invalid plant_id returns 404
- [ ] Guide not found returns 404

---

## 📊 Expected Test Output

### Success Metrics
- **All users auto-created**: ✅ 2 users
- **Plant instances created**: ✅ 7 total (Sarah: 3, Mike: 4)
- **Gemini API calls**: ✅ ~6 calls (new plants only, Carrot reused)
- **Chat sessions**: ✅ 2 sessions (1 general, 1 plant-specific)
- **Chat messages**: ✅ ~10 messages total
- **Plant favorites**: ✅ ~3 favorites
- **Guide favorites**: ✅ ~3 favorites
- **All endpoints tested**: ✅ ~35 endpoint calls

### Performance Metrics
- **Response times**: < 500ms for non-Gemini calls
- **Gemini API calls**: 2-5 seconds (acceptable)
- **Database queries**: Efficient (no N+1 queries)
- **Token usage**: Tracked correctly
- **Memory usage**: Stable

---

## 🚀 Running Tests

```bash
# On GCP VM
cd /opt/plantopia/Plantopia/tests/iteration_3

# Run comprehensive test
python realistic_user_scenarios_test.py

# Output will be in reports/
ls -la reports/

# View results
cat reports/test_report_YYYYMMDD_HHMMSS.json
cat reports/test_summary_YYYYMMDD_HHMMSS.txt
```

---

**Test Plan Status**: Ready for Implementation ✅
