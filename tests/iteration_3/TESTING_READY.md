# Testing Suite Ready ✅

**Date**: 2025-10-11
**Status**: Complete & Ready for Execution

---

## 📦 What's Included

### Documentation
- ✅ **TEST_PLAN.md** - Comprehensive test scenarios with expected behaviors
- ✅ **README_TESTING.md** - Quick start guide and troubleshooting
- ✅ **This file** - Summary and API endpoint reference

### Test Script
- ✅ **realistic_user_scenarios_test.py** - Complete test automation
  - 2 realistic users (Sarah & Mike)
  - 8 scenarios covering all features
  - ~25 test cases
  - Gemini API integration tests
  - Data reuse validation
  - Detailed logging and reporting

### Reports Folder
- ✅ **reports/** - Empty, ready for test results

---

## 🎯 Test Coverage

### Email Authentication (100%)
- ✅ Auto-user creation on first API call
- ✅ Email as identifier across all endpoints
- ✅ No Google OAuth dependencies

### Plant Tracking (100%)
- ✅ Start tracking with Gemini API
- ✅ Requirements checklist
- ✅ Setup instructions
- ✅ Timeline with calendar dates
- ✅ Multi-plant per user
- ✅ Stage tracking

### Data Reuse (100%)
- ✅ First user → Gemini API call
- ✅ Subsequent users → Reuse data
- ✅ Performance optimization validation

### Chat (100%)
- ✅ General agriculture Q&A
- ✅ Plant-specific chat with context
- ✅ Message history
- ✅ Token tracking

### Favorites (100%)
- ✅ Plant favorites (add, get, remove, check)
- ✅ Guide favorites (add, get, remove, check)

### Guides (100%)
- ✅ List categories
- ✅ Browse by category
- ✅ Get guide content
- ✅ Favorite guides

---

## 📊 API Endpoints Being Tested

### Plant Tracking (8 endpoints)
1. `POST /api/v1/tracking/start` - Start tracking plant
2. `GET /api/v1/tracking/user/{email}` - Get user's plants
3. `GET /api/v1/tracking/{instance_id}/details` - Get plant details
4. `GET /api/v1/tracking/{instance_id}/checklist` - Get requirements
5. `POST /api/v1/tracking/{instance_id}/checklist` - Complete checklist item
6. `GET /api/v1/tracking/{instance_id}/setup-guide` - Get setup instructions
7. `GET /api/v1/tracking/{instance_id}/timeline` - Get growth timeline
8. `PUT /api/v1/tracking/{instance_id}/progress` - Update progress

### Chat (5 endpoints)
1. `POST /api/v1/chat/general/start` - Start general chat
2. `POST /api/v1/chat/general/message` - Send general message
3. `POST /api/v1/chat/plant/{instance_id}/start` - Start plant chat
4. `POST /api/v1/chat/plant/message` - Send plant message
5. `GET /api/v1/chat/{chat_id}/history` - Get chat history

### Plant Favorites (4 endpoints)
1. `POST /api/v1/favorites` - Add favorite
2. `GET /api/v1/favorites` - Get favorites
3. `DELETE /api/v1/favorites/{plant_id}` - Remove favorite
4. `GET /api/v1/favorites/check/{plant_id}` - Check if favorited

### Guides (8 endpoints)
1. `GET /api/v1/guides` - List all guides
2. `GET /api/v1/guides/categories` - List categories
3. `GET /api/v1/guides/{category}` - List guides by category
4. `GET /api/v1/guides/{category}/{guide_name}` - Get guide content
5. `POST /api/v1/guides/favorites` - Add guide favorite
6. `GET /api/v1/guides/favorites/user` - Get guide favorites
7. `DELETE /api/v1/guides/favorites/{guide_name}` - Remove guide favorite
8. `GET /api/v1/guides/favorites/check/{guide_name}` - Check guide favorite

**Total**: 25 unique endpoints tested

---

## 👥 Test Users

### Sarah Johnson (`sarah.johnson.test@plantopia.com`)
**Profile**:
- Experience: Beginner
- Garden: Balcony (5.0 m²)
- Suburb: Melbourne CBD

**Journey**:
1. Starts Carrot (Day 0) → First user, triggers Gemini API
2. Gets checklist → Gemini-generated requirements
3. Completes checklist items → Progress tracking
4. Adds Cherry Tomato (Day 25) → Existing user
5. Adds Basil (Day 15) → Indoor plant
6. Starts general chat → Agriculture Q&A
7. Favorites plants → Carrot, Basil
8. Browses guides → Favorites Composting guide

**Expected API Calls**:
- Gemini API: 3 calls (Carrot, Cherry Tomato, Basil - if not existing)
- Total endpoint calls: ~15

### Mike Chen (`mike.chen.test@plantopia.com`)
**Profile**:
- Experience: Advanced
- Garden: Backyard (15.0 m²)
- Suburb: Richmond

**Journey**:
1. Starts Carrot (Day 10) → **REUSES Sarah's data** (no Gemini call)
2. Adds Capsicum (Day 35) → New plant, Gemini call
3. Adds Lettuce (Day 20) → New plant, Gemini call
4. Adds Zucchini (Day 5) → New plant, Gemini call
5. Starts plant-specific chat → Carrot advice
6. Browses guides → Favorites grow guide

**Expected API Calls**:
- Gemini API: 3 calls (Capsicum, Lettuce, Zucchini)
- Carrot: NO Gemini call (reuses Sarah's data)
- Total endpoint calls: ~12

---

## 🔍 Key Validations

### Data Reuse Test (Critical!)
```
Sarah starts Carrot (Day 0):
  ✅ Gemini API called
  ✅ plant_growth_data created
  ⏱️  Response time: 2-5 seconds

Mike starts Carrot (Day 10):
  ❌ NO Gemini API call
  ✅ Reuses Sarah's plant_growth_data
  ⏱️  Response time: < 1 second (fast!)
```

### Auto-User Creation
```
Sarah's first API call:
  ✅ User created in database
  ✅ email = sarah.johnson.test@plantopia.com
  ✅ google_id = NULL (frontend auth)

Mike's first API call:
  ✅ User created in database
  ✅ Different user_id than Sarah
  ✅ Separate plant instances
```

### Timeline Calculation
```
Sarah's Carrot (Day 0):
  ✅ Start date: 2025-10-11
  ✅ Expected maturity: 2025-10-11 + 70 days
  ✅ Current stage: germination
  ✅ Days elapsed: 0

Mike's Carrot (Day 10):
  ✅ Start date: 2025-10-01
  ✅ Expected maturity: 2025-10-01 + 70 days
  ✅ Current stage: early_growth (past germination)
  ✅ Days elapsed: 10
```

---

## 🚀 Quick Start

### 1. On GCP VM
```bash
# SSH into VM
ssh your-user@your-vm-ip

# Navigate to tests
cd /opt/plantopia/Plantopia/tests/iteration_3

# Activate environment
source ../../venv/bin/activate

# Run tests
python realistic_user_scenarios_test.py http://localhost:8000/api/v1

# View results
cat reports/realistic_scenarios_*.txt
```

### 2. Download Results
```bash
# From local machine
scp your-user@your-vm-ip:/opt/plantopia/Plantopia/tests/iteration_3/reports/* ./reports/
```

### 3. Review
- Check success rate (goal: > 95%)
- Verify data reuse working (Mike's Carrot < 1s)
- Review Gemini API call count (~6 expected)
- Check database integrity

---

## 📈 Expected Test Output

### Success Scenario
```
==========================================
REALISTIC USER SCENARIOS TEST SUMMARY
==========================================

Total Tests: 25
Passed: 25
Failed: 0
Success Rate: 100%

Key Metrics:
- Users created: 2
- Plant instances: 7
- Gemini API calls: 6
- Chat sessions: 2
- Plant favorites: 2
- Guide favorites: 2

Performance:
- Average response time: 245ms
- Gemini API calls: 2.8s avg
- Data reuse calls: 0.5s avg
```

### What to Look For
✅ **All 25 tests pass**
✅ **Mike's Carrot is fast** (< 1s, data reused)
✅ **No duplicate users** (exactly 2 users)
✅ **Gemini calls minimized** (~6 calls, not 7)
✅ **Favorites work** (separate per user)
✅ **Chat works** (AI responses received)

---

## 🐛 Common Issues

### Issue: Gemini API Key Not Found
**Symptom**: Tests fail on plant tracking
**Solution**: Set environment variable on VM:
```bash
export GEMINI_API_KEY="your-key"
```

### Issue: Data Not Reused
**Symptom**: Mike's Carrot takes 2-5 seconds (slow)
**Solution**: Check if Sarah's test completed successfully. `plant_growth_data` must exist.

### Issue: Connection Refused
**Symptom**: All tests fail immediately
**Solution**: Verify server running:
```bash
curl http://localhost:8000/api/v1/health
```

---

## 📝 Next Steps After Testing

1. **Review results** - Check success rate and performance
2. **Identify issues** - Document any failures
3. **Fix bugs** - Update code as needed
4. **Re-test** - Commit and let GitHub Actions deploy
5. **Iterate** - Repeat until 100% pass rate

---

## 💡 Tips

- **Run tests multiple times** - Ensure consistency
- **Check database** - Verify data integrity manually
- **Monitor Gemini quota** - Track API usage
- **Clean test data** - Remove test users between runs if needed
- **Check logs** - Review application logs for errors

---

**Everything is ready! Run the tests and let me know the results. 🚀**
