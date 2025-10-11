# Email-Based Authentication Migration Plan
**Iteration 3 - Backend Refactor**
**Date**: 2025-10-11

---

## 📋 Overview

Migrating from Google OAuth authentication to frontend-managed authentication using email as the primary identifier. Backend will auto-create users on first API interaction.

---

## 🎯 Objectives

1. **Remove Google Authentication** - All auth handled by frontend
2. **Email as Primary ID** - Replace user_id with email in all API interactions
3. **Auto-Create Users** - Backend creates users automatically on first request
4. **Plant Guide Favorites** - New feature for favoriting markdown guides
5. **Realistic Test Data** - Create 2 users with varied plant journeys

---

## 📊 Change Phases

### **Phase 1: Core Schema & Model Updates** ✅ (COMPLETED)
- [x] Remove auth router from API endpoints
- [x] Update User model (make google_id nullable)
- [x] Add `get_or_create_user_by_email()` helper
- [x] Update StartTrackingRequest schema (remove user_id)
- [x] Update StartChatRequest schema (use email)

### **Phase 2: Service Layer Migration** (IN PROGRESS)
**Files to Update:**
- `app/services/plant_instance_service.py`
  - Change `start_tracking()` signature: `email` instead of `user_id`
  - Add user repository, call `get_or_create_user_by_email()`

- `app/services/plant_chat_service.py`
  - Update `start_general_chat()` and `start_plant_chat()` to use email
  - Add user lookup/creation logic

- `app/services/progress_tracking_service.py`
  - No changes needed (works with instance_id)

### **Phase 3: Endpoint Updates** (PENDING)
**Files to Update:**
- `app/api/endpoints/plant_tracking.py`
  - `/tracking/start`: Extract email from user_data, pass to service
  - `/tracking/user/{user_id}` → `/tracking/user/{email}`
  - Keep instance-based endpoints unchanged

- `app/api/endpoints/plant_chat.py`
  - Update all endpoints to use email from request body
  - Remove user_id query parameters

- `app/api/endpoints/favorites.py`
  - Remove auth dependency
  - Add email to request schemas
  - Update to work without authentication

### **Phase 4: Plant Guide Features** (PENDING)
**New Files to Create:**
- `app/models/database.py` - Add `UserGuideFavorite` model
- `app/repositories/guide_repository.py` - Guide operations
- `app/services/guide_service.py` - Guide business logic
- `app/api/endpoints/guides.py` - Guide API endpoints

**Endpoints to Create:**
- `GET /guides` - List all guides (from markdown files)
- `GET /guides/{category}` - List guides by category
- `GET /guides/{category}/{guide_name}` - Get specific guide content
- `POST /favorites/guides` - Add guide to favorites
- `DELETE /favorites/guides/{guide_name}` - Remove from favorites
- `GET /favorites/guides?email={email}` - Get user's favorite guides

### **Phase 5: Database Migration** (PENDING)
**Migration File to Create:**
```
alembic/versions/YYYYMMDD_email_authentication.py
```
**Changes:**
- ALTER users.google_id to nullable
- CREATE TABLE user_guide_favorites
- No data migration needed (compatible changes)

### **Phase 6: Comprehensive Testing** (PENDING)
**Test Script to Create:**
`tests/iteration_3/test_realistic_user_scenarios.py`

**Test Users:**

**User 1: Sarah (New Gardener)**
- Email: `sarah.garden@example.com`
- Name: Sarah Chen
- Suburb: Melbourne (CBD)
- Experience: beginner
- Garden type: balcony
- Plants:
  - Carrot - Cosmic Purple (Day 0 - Just started)
  - Cherry Tomato (Day 25 - Flowering stage)
  - Basil (Day 15 - Vegetative growth)

**User 2: Mike (Experienced)**
- Email: `mike.grows@example.com`
- Name: Mike Thompson
- Suburb: Frankston
- Experience: advanced
- Garden type: backyard
- Plants:
  - Carrot - Cosmic Purple (Day 10 - Reuse data from Sarah)
  - Capsicum (Day 35 - Fruiting stage)
  - Lettuce (Day 20 - Harvesting soon)
  - Zucchini (Day 5 - Just germinated)

**Test Scenarios:**
1. ✅ User auto-creation on first API call
2. ✅ Plant tracking with Gemini API (new plant)
3. ✅ Plant tracking with cached data (same plant as another user)
4. ✅ Checklist completion workflow
5. ✅ Progress updates and stage transitions
6. ✅ Chat functionality (general and plant-specific)
7. ✅ Favorites (plants and guides)
8. ✅ Multi-plant management
9. ✅ Guide browsing and favoriting

---

## 🔄 API Request Flow Changes

### Before (Google Auth):
```
Frontend → Google OAuth → Backend validates → user_id
```

### After (Frontend Auth):
```
Frontend → Validates user → Sends email + user data → Backend auto-creates if needed
```

### Example Request Changes:

**OLD - Start Tracking:**
```json
POST /api/v1/tracking/start
{
  "user_id": 123,
  "user_data": { ... },
  "plant_id": 456
}
```

**NEW - Start Tracking:**
```json
POST /api/v1/tracking/start
{
  "user_data": {
    "email": "user@example.com",
    "name": "John Doe",
    "suburb_id": 123,
    ...
  },
  "plant_id": 456
}
```

**OLD - Get User Plants:**
```
GET /api/v1/tracking/user/123
```

**NEW - Get User Plants:**
```
GET /api/v1/tracking/user/user@example.com
```

---

## 📁 Files Modified Summary

### Core Changes (9 files):
1. ✅ `app/api/endpoints/__init__.py` - Remove auth router
2. ✅ `app/models/database.py` - Update User model
3. ✅ `app/repositories/user_repository.py` - Add get_or_create helper
4. ✅ `app/schemas/plant_tracking.py` - Update request schemas
5. ⏳ `app/services/plant_instance_service.py` - Use email
6. ⏳ `app/services/plant_chat_service.py` - Use email
7. ⏳ `app/api/endpoints/plant_tracking.py` - Update endpoints
8. ⏳ `app/api/endpoints/plant_chat.py` - Update endpoints
9. ⏳ `app/api/endpoints/favorites.py` - Remove auth

### New Features (6 files):
10. ⏳ `app/models/database.py` - Add UserGuideFavorite
11. ⏳ `app/repositories/guide_repository.py` - NEW
12. ⏳ `app/services/guide_service.py` - NEW
13. ⏳ `app/api/endpoints/guides.py` - NEW
14. ⏳ `app/schemas/guide.py` - NEW
15. ⏳ `alembic/versions/YYYYMMDD_email_authentication.py` - NEW

### Testing (1 file):
16. ⏳ `tests/iteration_3/test_realistic_user_scenarios.py` - NEW

**Total: 16 files to create/modify**

---

## ✅ Validation Checklist

After each phase:
- [ ] Phase 2: Services updated and imports work
- [ ] Phase 3: All endpoints return 200/201 for valid requests
- [ ] Phase 4: Guide endpoints return markdown content
- [ ] Phase 5: Migration runs without errors
- [ ] Phase 6: All test scenarios pass

---

## 🚀 Deployment Notes

- Changes are backward compatible (no breaking changes for existing data)
- google_id remains in database for historical data
- Email is enforced as unique (already exists in schema)
- No data migration required
- GitHub Actions will auto-deploy to GCP on push to main

---

## 📝 Next Steps

1. ✅ Complete Phase 1 (Done)
2. ⏳ Implement Phase 2 (Service layer migration)
3. Implement Phase 3 (Endpoint updates)
4. Implement Phase 4 (Guide features)
5. Create Phase 5 (Migration script)
6. Execute Phase 6 (Realistic testing)
7. Document API changes for frontend team
8. Update frontend integration guide

---

**Status**: Phase 1 Complete ✅ | Phase 2 In Progress ⏳
